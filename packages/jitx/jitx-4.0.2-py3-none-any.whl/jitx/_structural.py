from __future__ import annotations

from collections.abc import Callable, Generator, Iterable, Mapping, Sequence
from concurrent.futures import Future
from contextlib import contextmanager
from functools import reduce
from itertools import chain
from typing import TYPE_CHECKING, Any, ClassVar, Self, cast

from jitx.error import InstantiationException

from ._instantiation import instantiation, passive_representation
from .refpath import RefPath, Item

import inspect
import operator
import dataclasses

# import os.path
# import warnings

from logging import getLogger

# NOTE Do not add imports to other jitx modules here. If they're needed, import
# them inside functions.

# _warn_skips = (os.path.dirname(__file__),)

_list_like: tuple[type[Iterable], ...] = (list, tuple)
_dict_like: tuple[type[Mapping], ...] = (dict,)
_future_like = (Future,)
_constructor: dict[type, Callable] = {}

logger = getLogger(__name__)

try:
    import numpy  # type: ignore

    # traverse numpy arrays as well
    _list_like += (numpy.ndarray,)
    _constructor[numpy.ndarray] = numpy.array
except ImportError:
    pass


type Deferred = dict["Instantiable", Any]


class InstantiableOperand:
    def __op(self, op, other):
        return Instantiable(op, (self, other), {})

    def __add__(self, other):
        return self.__op(operator.add, other)

    def __iadd__(self, other):
        return self.__op(operator.iadd, other)

    def __sub__(self, other):
        return self.__op(operator.sub, other)

    def __isub__(self, other):
        return self.__op(operator.isub, other)

    def __mul__(self, other):
        return self.__op(operator.mul, other)

    def __matmul__(self, other):
        return self.__op(operator.matmul, other)

    def __truediv__(self, other):
        return self.__op(operator.truediv, other)

    def __floordiv__(self, other):
        return self.__op(operator.floordiv, other)

    def __mod__(self, other):
        return self.__op(operator.mod, other)

    def __pow__(self, other):
        return self.__op(operator.pow, other)

    def __lshift__(self, other):
        return self.__op(operator.lshift, other)

    def __rshift__(self, other):
        return self.__op(operator.rshift, other)

    def __and__(self, other):
        return self.__op(operator.and_, other)

    def __or__(self, other):
        return self.__op(operator.or_, other)


class Instantiable[T](InstantiableOperand):
    __post: None | list[Callable[[T, Deferred], None]] = None
    _repr_args_: Sequence[Any] | None = None
    _repr_kwargs_: Mapping[str, Any] | None = None

    def __init__(self, instantiable: Callable[..., T], args, kwargs):
        self.__instantiable = instantiable
        self.__args = args
        self.__kwargs = kwargs
        self.__file_info = _find_file_info()
        self.__post = []

    def _instantiable_(self) -> Callable[..., T]:
        return self.__instantiable

    def _instantiate_(self, deferred: Deferred) -> T:
        if self in deferred:
            return deferred[self]
        try:
            instance = self.__instantiable(
                *_instantiate(self.__args, deferred),
                **_instantiate(self.__kwargs, deferred),
            )
        except Exception as e:
            if self.__file_info:
                loc = f" at {self.__file_info}"
            else:
                loc = ""
            raise InstantiationException(
                f"Failed to instantiate {self.__call_representation()}{loc}"
            ) from e

        deferred[self] = instance
        if self.__post:
            for p in self.__post:
                p(instance, deferred)
        if issubclass(Proxy.type(instance), Sourced) and self.__file_info:
            self.__file_info.assign(instance)
        return instance

    def __getattr__(self, attr):
        if attr.startswith("__") and attr.endswith("__"):
            raise AttributeError(attr)
        return InstantiableAttribute(self, (attr,))

    def __setattr__(self, attr, value):
        if not hasattr(self.__class__, attr) and self.__post is not None:
            self.__post.append(
                lambda inst, defer: setattr(inst, attr, _instantiate(value, defer))
            )
        else:
            super().__setattr__(attr, value)

    def __call_representation(self):
        if isinstance(self.__instantiable, type):
            name = self.__instantiable.__name__
        elif hasattr(self.__instantiable, "__name__"):
            name = self.__instantiable.__name__
        else:
            name = "Instantiable"
        args = chain(
            map(repr, self._repr_args_ or self.__args),
            (f"{k}={v!r}" for k, v in (self._repr_kwargs_ or self.__kwargs).items()),
        )
        return f"{name}({', '.join(args)})"

    if passive_representation:

        def __repr__(self):
            return self.__call_representation()
    else:

        def __repr__(self):
            return f"Instantiable({self.__instantiable!r}, {self.__args!r}, {self.__kwargs!r})"


def InstanceField[T](factory: Callable[[], T]):
    return cast(T, Instantiable(factory, (), {}))


class InstantiableAttribute(InstantiableOperand):
    __post = False

    def __init__(
        self, instantiable: Instantiable, attribute: tuple[str | Item | int, ...]
    ):
        self.__instantiable = instantiable
        self.__attribute = attribute
        self.__post = True

    if passive_representation:

        def __repr__(self):
            return f"{self.__instantiable!r}.{RefPath(self.__attribute)}"
    else:

        def __repr__(self):
            return f"InstantiableAttribute({self.__instantiable}.{RefPath(self.__attribute)})"

    def __call__(self, *args, **kwargs):
        def call(method, *args, **kwargs):
            return method(*args, **kwargs)

        inst = Instantiable(call, (self,) + args, kwargs)
        if passive_representation:
            call.__name__ = repr(self)
            inst._repr_args_ = args
            inst._repr_kwargs_ = kwargs
        return inst

    def __getattr__(self, attr):
        return InstantiableAttribute(self.__instantiable, self.__attribute + (attr,))

    def __getitem__(self, key: str | int):
        step: str | int | Item
        if isinstance(key, str):
            step = Item(key)
        else:
            step = key
        return InstantiableAttribute(self.__instantiable, self.__attribute + (step,))

    def __setattr__(self, attr, value):
        if self.__post:
            raise NotImplementedError(
                "Setting deferred instantable attribute value is not implemented"
            )
        super().__setattr__(attr, value)

    def get(self, deferred: Deferred):
        inst = self.__instantiable._instantiate_(deferred)

        def reducer(inst, attr: str | int | Item):
            if isinstance(attr, Item):
                return inst[attr.value]
            elif isinstance(attr, int):
                return inst[attr]
            else:
                return getattr(inst, attr)

        return reduce(reducer, self.__attribute, inst)


class PrePostInit[T, S]:
    def __init__(
        self,
        before: Callable[[T, Deferred], S],
        after: Callable[[T, S], S],
        representing: Callable | None = None,
    ):
        self.__before = before
        self.__after = after
        self.__representing = representing

    def before(self, instance: T, deferred: Deferred) -> S:
        return self.__before(instance, deferred)

    def after(self, instance: T, before: S) -> S:
        return self.__after(instance, before)

    def __repr__(self):
        # for some reason pyright doesn't like conditional declaration of
        # _this_ particular __repr__, the other ones are fine.
        if passive_representation:
            if self.__representing is not None:
                return repr(self.__representing)
            return "PrePostInit"
        else:
            if self.__representing is not None:
                return f"PrePostInit({self.__representing})"
            return "PrePostInit"


def preinit(x: Callable, representing: Any = None):
    return PrePostInit(
        before=lambda _, deferred: x(deferred),
        after=lambda _, before: before,
        representing=representing or x,
    )


unknown_refpath: RefPath = RefPath(("unknown",))
empty_refpath: RefPath = RefPath(())


def _is_magic(name: str):
    return name.startswith("__") and name.endswith("__")


def _is_structurable(name: str):
    return name.startswith("_Structurable__") or name.startswith("_Proxy__")


def _instantiate(field, deferred: Deferred) -> Any:
    if field is None:
        return None
    if isinstance(field, Instantiable):
        return field._instantiate_(deferred)
    if isinstance(field, InstantiableAttribute):
        return field.get(deferred)
    # class definitions inside other classes is a common pattern for structuring code
    # and is indistinguishable from a variable with a class type assigned to it;
    # so we're silencing this warning. If we find a better way to detect a
    # mistake, we should revisit this.
    # if isinstance(field, type) and issubclass(field, Structurable):
    #     if not getattr(field, "_Structurable__allow_class_assignment", False):
    #         warnings.warn(
    #             f"Assigning instantiable class {field.__name__}, did you mean to create an object of that class?",
    #             skip_file_prefixes=_warn_skips,
    #             stacklevel=0,
    #         )
    #     return field
    if isinstance(field, _list_like):
        typed = type(field)
        constructor = _constructor.get(typed, typed)
        result = constructor(_instantiate(ob, deferred) for ob in field)
        if all(x is y for x, y in zip(result, field, strict=True)):
            return field
        return result
    if isinstance(field, _dict_like):
        result = [
            (_instantiate(key, deferred), key, _instantiate(ob, deferred), ob)
            for key, ob in field.items()
        ]
        if all(u is v and x is y for u, v, x, y in result):
            return field
        typed = type(field)
        constructor = _constructor.get(typed, typed)
        return constructor((k, v) for k, _, v, _ in result)
    return field


def _find_file_info():
    # avoid load time dependencies for jitx._structural.
    from jitx.fileinfo import FileInfo

    frame = inspect.currentframe()
    if frame is not None:
        # Walk up the frame stack until we find a frame outside src/jitx
        # TODO: Revisit how to filter the stacktrace / filename.
        name = frame and frame.f_globals.get("__name__")
        while (
            frame is not None
            and name
            and (name.startswith("jitx.") or name.startswith("importlib."))
        ):
            frame = frame.f_back
            name = frame and frame.f_globals.get("__name__")
        # TODO: Revisit with preserving the stacktrace.
        if frame is not None:
            filename = frame.f_code.co_filename
            line_number = frame.f_lineno
            return FileInfo(filename=filename, line=line_number)
    return None


class Sourced:
    if not (TYPE_CHECKING or passive_representation):
        # hide this from the type checker and docs
        def __new__(cls, *args, **kwargs):
            fi = _find_file_info()
            ob = super().__new__(cls)
            if fi:
                fi.assign(ob)
            return ob


class Critical(Sourced):
    """Marker base class to detect unexpected elements in the object tree.
    Critical objects must be handled when encountered, or it's considered an
    error."""


class Ref:
    """Marker base class for objects used to explicitly block traversal."""


class RefTuple(tuple, Ref):
    pass


class StructureMeta(type):
    def __instancecheck__(self, instance: Any) -> bool:
        if isinstance(instance, Proxy):
            return self.__instancecheck__(Proxy.of(instance))
        return super().__instancecheck__(instance)


class Structurable(metaclass=StructureMeta):
    __deferred: Deferred | None = None
    __frozen = False
    __freeze: ClassVar[bool] = False
    __preinit: ClassVar[bool] = False
    __memoized: ClassVar[
        dict[tuple[type, tuple[Any, ...], tuple[tuple[str, Any], ...]], Any] | None
    ] = None
    __prepost: ClassVar[list[str] | None] = None
    __disposed = False

    def __init_subclass__(cls, *, frozen=False, early=False, **kwargs) -> None:
        from jitx.context import Context

        if dataclasses.is_dataclass(cls):
            raise TypeError("Structural elements cannot be dataclasses.")

        if frozen:
            cls.__freeze = True
        if early:
            cls.__preinit = True
        prepost: list[str] = []
        contexts: list[Context | Instantiable] = []
        for key in chain.from_iterable(
            c.__dict__ for c in cls.__mro__ if c is not Structurable
        ):
            if _is_magic(key) or _is_structurable(key):
                continue
            field = getattr(cls, key)
            if isinstance(field, PrePostInit):
                prepost.append(key)
            if isinstance(field, Context):
                contexts.append(field)
            if isinstance(field, Instantiable):
                inst = field._instantiable_()
                if isinstance(inst, type) and issubclass(inst, Context):
                    contexts.append(field)
        if contexts:

            def before(ob, deferred):
                for i, c in enumerate(contexts):
                    if isinstance(c, Instantiable):
                        contexts[i] = (c := _instantiate(c, deferred))
                    c.__enter__()

            def after(ob, none):
                for c in reversed(contexts):
                    c.__exit__(None, None, None)

            # context initializations are run first
            cls.__context_init = PrePostInit(before, after)
            prepost.insert(0, "_Structurable__context_init")
        init_sig = inspect.signature(cls.__init__)
        cls.__signature__ = inspect.Signature(
            list(init_sig.parameters.values())[1:],
            return_annotation=init_sig.return_annotation,
        )
        if prepost:
            cls.__prepost = prepost
            wrapped_init = cls.__init__

            def __init__(self, *args, **kwargs):
                wrapped_init(self, *args, **kwargs)
                if type(self) is cls:
                    # only run these if we're the class being instantiated,
                    # otherwise both sub and superclasses will run pre/post fields.
                    for attr in reversed(prepost):
                        field: PrePostInit = getattr(cls, attr)
                        before = getattr(self, attr)
                        setattr(self, attr, field.after(self, before))
                if cls.__freeze:
                    self.__frozen = True

            cls.__init__ = __init__
        return super().__init_subclass__(**kwargs)

    def __new__(cls: type[Self], *args, **kwargs) -> Self:
        if not instantiation.active():
            # test-bind the __init__ method signature to ensure the call is valid
            signature = inspect.signature(cls.__init__)
            # object() is a "dummy" self argument, cls.__init__ has not been bound.
            signature.bind(object(), *args, **kwargs)
            # pretend this is a Self for the sake of class level fields, it will be
            # an instance level Self once instantiated
            if cls.__preinit:
                instantiable = Instantiable(cls, args, kwargs)
                return cast(Self, preinit(instantiable._instantiate_, instantiable))
            return cast(Self, Instantiable(cls, args, kwargs))
        else:
            memoized = cls.__memoized
            if memoized is not None:

                def memorable(o: Any) -> Any:
                    o = Proxy.forkbase(o)
                    if dataclasses.is_dataclass(o) and not isinstance(o, type):
                        o = dataclasses.astuple(o)
                    return o

                baseargs = tuple(map(memorable, args))
                basekwargs = tuple(
                    (memorable(k), memorable(v)) for k, v in kwargs.items()
                )
                memokey = (cls, baseargs, basekwargs)
                try:
                    memos = memoized.get(memokey)
                    if memos:
                        # find a memoized object that used the same contexts,
                        # contexts are, however, possibly not hashable, so
                        # can't rely on that.
                        for ctxs, instance in memos:
                            for key, value in ctxs.items():
                                if instantiation.get(key) != value:
                                    break
                            else:
                                proxy = Proxy.construct(instance)
                                with Proxy.override():
                                    proxy.__instantiation_generation = (
                                        instantiation.generation
                                    )
                                return cast(Self, proxy)
                except TypeError:
                    import sys

                    logger.debug(
                        "Unable to memoize object as arguments are not hashable",
                        exc_info=sys.exc_info(),
                    )
                    memokey = None
            else:
                memokey = None

            ob = super().__new__(cls)
            post = False

            deferred = {}
            prepost = {}
            if cls.__prepost:
                for attr in cls.__prepost:
                    field = getattr(cls, attr)
                    prepost[attr] = field.before(ob, deferred)
            for key in chain.from_iterable(
                c.__dict__ for c in reversed(cls.__mro__) if c is not Structurable
            ):
                if _is_magic(key) or _is_structurable(key):
                    continue
                force = False
                if key in prepost:
                    field = prepost[key]
                    force = True
                else:
                    field = getattr(cls, key)
                instantiated = _instantiate(field, deferred)
                if force or instantiated is not field:
                    setattr(ob, key, instantiated)
            ob.__deferred = deferred
            if not post:
                if cls.__freeze:
                    ob.__frozen = True

            if memoized is not None and memokey is not None:
                # ensure we don't actually return the "og" memoized object, in
                # case it's mutated later.
                ctxs = {}
                frame = instantiation.current_frame
                try:
                    frame.tracker.append(ctxs)
                    ob.__init__(*args, **kwargs)
                finally:
                    frame.tracker.pop()

                if not (memos := memoized.get(memokey)):
                    memoized[memokey] = (memos := [])
                memos.append((ctxs, ob))

                ob = Proxy.construct(ob)
            with Proxy.override():
                ob.__instantiation_generation = instantiation.generation
            return cast(Self, ob)

    def __init__(self):
        # only here to ensure no extraneous arguments are passed in.
        pass

    def __setattr__(self, key, value):
        # we have been instantiated, instantiate assignments that are done after
        # the fact.
        if self.__frozen:
            raise ValueError("This element has been frozen")
        if self.__deferred:
            return super().__setattr__(key, _instantiate(value, self.__deferred))
        return super().__setattr__(key, value)

    def __repr__(self):
        return self.__class__.__name__

    @classmethod
    def _memoize(cls, active: bool):
        cls.__memoized = {} if active else None

    @staticmethod
    def _dispose(ob: Structurable):
        rval = ob.__disposed
        ob.__disposed = True
        return rval

    @staticmethod
    def _disposed(ob: Structurable) -> bool:
        return ob.__disposed

    def __dir__(self):
        for f in super().__dir__():
            # hide these fields in the debugger.
            if not _is_structurable(f) and not f == "_memoize":
                yield f


def dispose(ob: Structurable):
    return Structurable._dispose(ob)


class Structural(Structurable, Critical):
    def __del__(self):
        # if structural objects are GCd during instantiation, chances are it's
        # an error, since pretty much all structural objects are supposed to be
        # attached to something. An object can be explicitly disposed of by
        # calling `Structurable._dispose(ob)` to suppress the warning.
        if instantiation.active() and not Structurable._dispose(self):
            # instantiation is active for the entirety of a test, so there are
            # bound to be some GCd objects before the instantiation closes;
            # thus we check whether there's a test running before logging a
            # warning.
            # This can be improved to check if we're currently in a test
            # method, but even then there might be some temporary objects
            # created for test purposes that are expected to be GC so at most
            # you'd log a debug level message there.
            gen = instantiation.generation
            if gen == getattr(self, "_Structurable__instantiation_generation", None):
                from jitx.test import TestContext

                if TestContext.get() is None:
                    from jitx.fileinfo import FileInfo

                    fi = FileInfo.get(self)
                    logger.warning(
                        "Reference to structural object %s%s lost during instantiation, it likely needs to be assigned to an object.",
                        self,
                        f" at {fi}" if fi else "",
                    )


class Container(Structurable):
    """Namespace-like container object, will be traversed in all introspection."""


def _proximate(other, parent):
    if isinstance(other, Structurable):
        return Proxy.construct(other, parent)
    elif isinstance(other, _list_like):
        return tuple(_proximate(o, parent) for o in other)
    elif isinstance(other, _dict_like):
        return Proxy.Dict(other, parent)
    else:
        return other


class Proxy[T: Structurable | Proxy]:
    __of: T
    __parent: Proxy | None
    __tainted: bool | None = None
    __pool: dict[Any, Proxy] | None = None
    __ref = False
    # FIXME: override should be thread-local.
    __override: ClassVar[bool] = False

    def __init__(self, of: T, parent: Proxy | None, pool: dict[Any, Proxy] | None):
        self.__of = of
        self.__parent = parent
        self.__pool = pool
        self.__tainted = False

    @staticmethod
    def construct(of: T, parent: Proxy | None = None, ref=False) -> Proxy[T]:
        ancestor = parent
        if ancestor and not ref:
            while ancestor.__parent:
                ancestor = ancestor.__parent
            assert ancestor.__pool is not None
            proxy = ancestor.__pool.get(of)
            # XXX should this be wrapped in its own proxy?
            if proxy is None:
                proxy = Proxy(of, parent, None)
                ancestor.__pool[of] = proxy
            return proxy
        else:
            pool = {}
            ancestor = Proxy(of, parent, pool)
            pool[of] = ancestor
            if ref:
                ancestor.__ref = True
            return ancestor

    def __dir__(self):
        overrides = set(super().__dir__())
        for f in self.__of.__dir__():
            if f not in overrides:
                yield f
        for f in super().__dir__():
            if f not in ("_Proxy__of", "_Proxy__parent", "_Proxy__tainted"):
                yield f

    def __repr__(self):
        return f"Proxy({repr(self.__of)})[{id(self)}]"

    def __str__(self):
        return f"<{str(self.__of)}>"

    class Dict(Mapping):
        def __init__(self, other: Mapping, parent: Proxy):
            self.__of = {
                _proximate(k, parent): _proximate(v, parent) for k, v in other.items()
            }

        def __getitem__(self, key):
            return self.__of[key]

        def __bool__(self):
            return bool(self.__of)

        def __len__(self):
            return len(self.__of)

        def __iter__(self):
            return iter(self.__of)

        def items(self):
            return self.__of.items()

    def __getattr__(self, attr):
        if Proxy.__override:
            raise AttributeError(attr)
        other = getattr(self.__of, attr)
        if inspect.ismethod(other):
            bound = other.__func__.__get__(self, Proxy)
            object.__setattr__(self, attr, bound)
            return bound
        elif isinstance(other, Structural | Container | Proxy):
            proxy = Proxy.construct(other, self)
            object.__setattr__(self, attr, proxy)
            return proxy
        elif isinstance(other, _list_like):
            proxy = tuple(_proximate(o, self) for o in other)
            object.__setattr__(self, attr, proxy)
            return proxy
        elif isinstance(other, _dict_like):
            proxy = Proxy.Dict(other, self)
            object.__setattr__(self, attr, proxy)
            return proxy
        return other

    def __setattr__(self, attr, value):
        Proxy.taint(self)
        object.__setattr__(self, attr, value)

    def __getitem__(self, key):
        # if the proxy base has __getitem__ defined.
        return Proxy.type(self).__getitem__(self, key)

    def __bool__(self):
        # XXX we might get in trouble if we need to forward this due to the
        # implicit __len__ call in boolean context if __bool__ is not defined.
        # Since Proxy can only wrap a Structural at this time, simply returning
        # True here should be fine.
        return True

    def __len__(self):
        return Proxy.type(self).__len__(self)

    @staticmethod
    def create[S: Structural](base: S, *, ref=False) -> S:
        return cast(S, Proxy.construct(base, ref=ref))

    @staticmethod
    def fork(base: T) -> T:
        p = Proxy.construct(base)
        p.__tainted = True
        return cast(T, p)

    @staticmethod
    def is_tainted(proxy: Proxy):
        return proxy.__tainted

    @staticmethod
    def is_ref(proxy):
        return isinstance(proxy, Proxy) and proxy.__ref

    @staticmethod
    def taint(proxy: Proxy):
        # __tained is None until the proxy is initialized
        if Proxy.__override or proxy.__tainted is None:
            return
        object.__setattr__(proxy, "_Proxy__tainted", True)
        parent = proxy.__parent
        if parent:
            Proxy.taint(parent)

    @staticmethod
    def of(proxy: Proxy):
        return proxy.__of

    @staticmethod
    def parent(proxy: Proxy):
        return proxy.__parent

    @staticmethod
    def type(ob):
        while isinstance(ob, Proxy):
            ob = ob.__of
        return type(ob)

    @staticmethod
    def forkbase(ob: T) -> T:
        while isinstance(ob, Proxy):
            p = ob.__parent
            while p:
                if p.__tainted:
                    # parent is tainted; stop here.
                    return cast(T, ob)
                p = p.__parent
            if ob.__tainted:
                break
            ob = ob.__of
        return cast(T, ob)

    @staticmethod
    @contextmanager
    def override():
        Proxy.__override = True
        try:
            yield
        finally:
            Proxy.__override = False

    def __add__(self, other):
        return Proxy.type(self).__add__(self, other)

    def __sub__(self, other):
        return Proxy.type(self).__sub__(self, other)

    def __mul__(self, other):
        return Proxy.type(self).__mul__(self, other)

    def __matmul__(self, other):
        return Proxy.type(self).__matmul__(self, other)

    def __truediv__(self, other):
        return Proxy.type(self).__truediv__(self, other)

    def __floordiv__(self, other):
        return Proxy.type(self).__floordiv__(self, other)

    def __mod__(self, other):
        return Proxy.type(self).__mod__(self, other)

    def __pow__(self, other):
        return Proxy.type(self).__pow__(self, other)

    def __lshift__(self, other):
        return Proxy.type(self).__lshift__(self, other)

    def __rshift__(self, other):
        return Proxy.type(self).__rshift__(self, other)

    def __and__(self, other):
        return Proxy.type(self).__and__(self, other)

    def __or__(self, other):
        # FIXME adding type ignore here, as the signature seems busted
        return Proxy.type(self).__or__(self, other)  # type: ignore


_dict_like += (Proxy.Dict,)


def traverse(
    ob, types: tuple[type, ...], subclasses: tuple[type, ...], path: RefPath, refs: bool
) -> Generator[tuple[RefPath, Any], None, None]:
    if not refs and Proxy.is_ref(ob):
        # ref proxies can be accessed, but not enumerated.
        return
    elif isinstance(ob, types):
        yield path, ob
    elif isinstance(ob, type) and issubclass(ob, subclasses):
        yield path, ob
    elif not refs and isinstance(ob, Ref):
        # Ref objects can be found, but their contents not traversed
        return
    elif isinstance(ob, _list_like):
        for i, f in enumerate(ob):
            yield from traverse(f, types, subclasses, path + (i,), refs)
    elif isinstance(ob, _dict_like):
        for k, f in ob.items():
            yield from traverse(f, types, subclasses, path + (Item(k),), refs)
    elif isinstance(ob, _future_like):
        # traverse Future's as if they're the object themselves.
        yield from traverse(ob.result(), types, subclasses, path, refs)
    elif issubclass(Proxy.type(ob), Container):
        yield from traverse_base(ob, types, subclasses, path, refs)


def traverse_base(
    ob,
    types: tuple[type, ...],
    subclasses: tuple[type, ...],
    path: RefPath = empty_refpath,
    refs=False,
):
    if isinstance(ob, _future_like):
        ob = ob.result()
    # collect entire list here in case it's a generator; access to proxies will
    # cause the underlying object to change
    for key in list(ob.__dir__()):
        if _is_magic(key) or _is_structurable(key):
            continue
        field = getattr(ob, key)
        yield from traverse(field, types, subclasses, path + (key,), refs=refs)


def fieldref(path: RefPath) -> RefPath:
    return path.attribute()


def relativeref(path: RefPath, base: RefPath) -> RefPath:
    return path - base


def pathstring(path: RefPath):
    return str(path)
