"""
Design discovery and execution
==============================

This module provides tools for discovering, building, and executing
JITX designs, including communication with the JITX runtime. Normally this
module is not used directly, but rather through the `jitx` command line, or
through the VSCode extension.

.. warning::
    The API in this module is still experimental and may change significantly
    without notice.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
import asyncio
from collections.abc import Awaitable, Callable, Mapping, Sequence
from logging import getLogger
import sys
from typing import Any, Protocol, overload, override

import jitx.design
from jitx.error import InstantiationException, UserCodeException

from .._websocket import (
    on_websocket_message as _on_websocket_message,
    set_websocket_uri as _set_websocket_uri,
)
from .pyproject import PyProject


logging = getLogger("jitx.run")

STATUS = "status"
MESSAGE = "message"
ERRORS = "errors"
IMPORTFAILED = "import failed"
INSTANTIATIONFAILED = "instantiation failed"
TRANSLATEFAILED = "translation failed"
HINTS = "hints"
LOG = "log"
OK = "ok"


class DesignFactory:
    def __init__(
        self,
        finder: DesignFinder | None = None,
        builder: BaseDesignBuilder | None = None,
        *,
        formatter: Formatter | None = None,
        dump: str | None = None,
    ):
        self.finder = finder or DesignFinder()
        self.builder = builder or DesignBuilder()
        self.formatter: Formatter = formatter or text_formatter
        self.dump = dump
        self.queue: dict[str, type[jitx.design.Design]] = {}
        self.success = True

    def by_name(self, name: str):
        self.add(self.finder.find_by_name(name))

    def by_file(self, name: str):
        for design in self.finder.find_by_file(name):
            self.add(design)

    def add_all(self):
        for design in self.finder.find_all():
            self.add(design)

    def add(self, design: type[jitx.design.Design], *, name: str | None = None):
        if not name:
            name = design.__module__ + "." + design.__name__
        self.queue[name] = design

    def build(self):
        aggregate = {}
        for name, design in self.queue.items():
            result = self.builder.build(
                design, name=name, dump=self.dump, formatter=self.formatter
            )
            aggregate[name] = result
            if ERRORS in result:
                self.success = False
        if self.finder.exceptions:
            self.success = False
            aggregate[ERRORS] = {
                IMPORTFAILED: {
                    name: repr(e) for name, e in self.finder.exceptions.items()
                }
            }
        self.formatter(aggregate)

    def list(self):
        result = {}
        df = self.finder
        result["designs"] = [d.__module__ + "." + d.__name__ for d in df.find_all()]
        if df.exceptions:
            if ERRORS not in result:
                result[ERRORS] = {}
            if IMPORTFAILED not in result[ERRORS]:
                result[ERRORS][IMPORTFAILED] = {}
            result[ERRORS][IMPORTFAILED].update(
                (name, repr(e)) for name, e in df.exceptions.items()
            )
        self.formatter(result)


class DesignFinder:
    def __init__(self, roots: str | Sequence[str] | None = None):
        if isinstance(roots, str):
            roots = (roots,)
        self.roots = roots or (".",)
        self.exceptions: dict[str, Exception] = {}

    def find_all(self):
        import os

        for root in self.roots:
            project = PyProject(root)
            tool = project.jitxtool
            for dirpath, dirnames, filenames in os.walk(root):
                path = os.path.relpath(dirpath, root)
                if path in tool.exclude:
                    dirnames[:] = []
                else:
                    dirnames[:] = [
                        d
                        for d in dirnames
                        if not d.startswith("_")
                        and not d.startswith(".")
                        and not any(d == ex for ex in tool.exclude)
                    ]
                for filename in filenames:
                    if filename.startswith("_") or filename.startswith("."):
                        continue
                    if any(filename == ex for ex in tool.exclude):
                        continue
                    if not filename.endswith(".py"):
                        continue
                    yield from self.find_by_file(os.path.join(path, filename))
        # NOTE walk_packages struggles with namespace packages, so we have to
        # resort to look for python files for now. This doesn't support things
        # like eggs, which is probably fine anyway.
        # import pkgutil
        # for mi in pkgutil.walk_packages(self.roots):
        #     try:
        #         yield from self.find_by_module(mi.name)
        #     except Exception as e:
        #         self.exceptions[mi.name] = e

    def find_by_name(self, name: str):
        import importlib

        ns = name.rsplit(".", 1)
        if len(ns) != 2:
            raise ValueError(f"Invalid design name: {name}")
        modulename, classname = ns
        m = importlib.import_module(modulename)
        design = getattr(m, classname, None)
        if design is None:
            raise ValueError(f"{classname} not found in {modulename}")
        if not issubclass(design, jitx.design.Design):
            raise ValueError(f"{classname} in {modulename} is not a Design")
        return design

    def find_by_module(self, name: str):
        import importlib
        import jitx.sample

        try:
            m = importlib.import_module(name)
        except Exception as e:
            self.exceptions[name] = e
            return

        for elem in dir(m):
            field = getattr(m, elem, None)
            if (
                isinstance(field, type)
                and issubclass(field, jitx.design.Design)
                and field not in (jitx.design.Design, jitx.sample.SampleDesign)
            ):
                yield field

    def find_by_file(self, path: str):
        import os.path
        import importlib

        path, filename = os.path.split(os.path.normpath(path))
        module, _ = os.path.splitext(filename)
        steps = []
        while path:
            rem, last = os.path.split(path)
            if rem == path:
                break
            path = rem
            steps.append(last)

        steps.reverse()
        steps.append(module)
        # attempt to find the longest matching module path to avoid accidentally
        # importing a "shadowed" module
        candidate = module
        for i in range(len(steps)):
            if steps[i] == "src":
                # do not accept "src" as top-level module, this is common in the
                # so called "src-layout" pattern, and it could technically be a
                # valid top level package, it's exceedingly unlikely.
                continue
            candidate = ".".join(steps[i:])
            try:
                importlib.import_module(candidate)
                break
            except ModuleNotFoundError as e:
                if e.name != candidate and e.name != steps[i]:
                    self.exceptions[candidate] = e
                    # only continue trying if the error is about the candidate,
                    # otherwise it's probably an error _inside_ the module.
                    return
            except Exception as e:
                # some other error happening on import here, so we're probably
                # in the right spot.
                self.exceptions[candidate] = e
                return
        yield from self.find_by_module(candidate)


class BaseDesignBuilder(ABC):
    @abstractmethod
    def __init__(self):
        pass

    def build(
        self,
        design: type[jitx.design.Design],
        *,
        name: str | None = None,
        dump: str | None = None,
        formatter: Formatter,
    ) -> Mapping[str, Any]:
        """Build the design. This is a base class, where the design gets sent
        is determined by the specific subclass implementation.

        Args:
            design: The Design class to build.
            name: Optional name for the design.
            dump: Optional file path to dump the design data.
            formatter: Function to format and output results.
        """
        import jitx._structural
        import jitx._translate.design
        import gc

        name = name or design.__module__ + "." + design.__name__
        result: dict[str, Any] = {"design": name}

        with jitx._structural.instantiation.activate():
            try:
                instantiated = design()
            except Exception as e:
                logging.exception(f"Unable to instantiate design {design}")
                errors: list[BaseException] = [e]
                while e.__cause__ is not None:
                    e = e.__cause__
                    errors.insert(0, e)
                    if (tb := e.__traceback__) is not None:
                        tb = tb.tb_next

                def formatexc(e: BaseException):
                    if isinstance(e, UserCodeException | InstantiationException):
                        return str(e)
                    loc = ""
                    if tb := e.__traceback__:
                        while tb.tb_next:
                            tb = tb.tb_next
                        loc = f" at {tb.tb_frame.f_code.co_filename}:{tb.tb_lineno}"
                        pass
                    return str(e) + loc

                result[ERRORS] = {INSTANTIATIONFAILED: [formatexc(e) for e in errors]}
                return result

            # try to force detection of lost elements.
            gc.collect()

            # callbacks during packaging need active instantiation.
            try:
                packaged = jitx._translate.design.package_design(instantiated)
            except UserCodeException as e:
                result[ERRORS] = {TRANSLATEFAILED: [str(e)]}
                if e.hint:
                    result[HINTS] = [e.hint]
                return result
            except Exception as e:
                logging.exception(f"Unable to translate design {design}")
                result[ERRORS] = {TRANSLATEFAILED: [str(e)]}
                return result

            # and again, in case something happened in translation callbacks.
            gc.collect()

        del instantiated

        from google.protobuf.json_format import MessageToDict

        body = MessageToDict(packaged, use_integers_for_enums=True)
        if dump:
            with open(dump, "w") as f:
                formatter(body, file=f)

        def log_message(ob, file=None):
            if file is None:
                formatter(ob, sys.stdout)
            else:
                formatter(ob, file)

        try:
            result.update(asyncio.run(self._send_design(name, body, log_message)))
        except Exception as e:
            result[STATUS] = "error"
            result[MESSAGE] = str(e)

        return result

    async def _send_design(
        self, name: str, body, formatter: Formatter
    ) -> Mapping[str, Any]:
        raise NotImplementedError


class DryRunBuilder(BaseDesignBuilder):
    def __init__(self):
        super().__init__()

    async def _send_design(self, name: str, body, formatter: Formatter):
        return {STATUS: OK}


class DesignBuilder(BaseDesignBuilder):
    @overload
    def __init__(self, *, spec: str | None = None): ...
    @overload
    def __init__(self, *, uri: str): ...
    @overload
    def __init__(self, *, port: int, host: str = "localhost"): ...

    def __init__(
        self,
        *,
        spec: str | None = None,
        uri: str | None = None,
        port: int | None = None,
        host: str | None = None,
    ):
        super().__init__()

        def lazy_setup():
            if uri is None:
                if port is None:
                    if spec is not None:
                        _set_websocket_uri(file=spec)
                    else:
                        _set_websocket_uri()
                else:
                    _set_websocket_uri(uri=f"ws://{host or 'localhost'}:{port}")
            self.__setup = lambda: None

        self.__setup = lazy_setup

    @override
    def build(
        self,
        design: type[jitx.design.Design],
        *,
        name: str | None = None,
        dump: str | None = None,
        formatter: Formatter,
    ) -> Mapping[str, Any]:
        self.__setup()
        return super().build(design, name=name, formatter=formatter, dump=dump)

    async def _send_design(self, name: str, body, formatter: Formatter):
        formatter(f"Running design {name}...")

        async def on_response_in_progress(
            message: dict[str, Any],
            send_message: Callable[[str, dict[str, Any]], Awaitable[None]],
        ):
            match message.get("type"):
                # Prompt user for input.
                case "stdin":
                    answer = input()
                    # Send user answer back to server.
                    await send_message("stdin", {"message": answer})
                # Forward stdout line by line from server.
                case "stdout":
                    formatter(message["body"]["message"])
                case _:
                    raise RuntimeError(
                        f"Unhandled response in progress type: {message}"
                    )

        def on_error(body: dict[str, Any]):
            if "message" in body:
                error_msg = body["message"]
                raise RuntimeError(error_msg)
            else:
                raise RuntimeError(f"Error. Received: {body}")

        def on_success(body: dict[str, Any]):
            if "message" in body:
                return body["message"]
            return None

        def on_connection_closed(e: Exception):
            raise RuntimeError("Connection closed while running design") from e

        message = await _on_websocket_message(
            "load",
            body,
            on_response_in_progress,
            on_error,
            on_success,
            on_connection_closed,
            "client",
        )
        if message is not None:
            return {
                STATUS: OK,
                MESSAGE: message,
            }
        else:
            return {STATUS: OK}


class Formatter(Protocol):
    def __call__(self, ob: Mapping[str, Any] | str, file=None) -> None: ...


def json_formatter(ob, file=sys.stdout):
    import json

    json.dump(ob, file)
    file.write("\n")


def text_formatter(ob, file=sys.stdout, indent=0):
    # not great but better than nothing, could use yaml or something.
    ind = "  " * indent
    if isinstance(ob, dict):
        for key, value in ob.items():
            if isinstance(value, list | dict):
                print(ind + key + ":", file=file)
                text_formatter(value, file, indent + 1)
            else:
                print(ind + key + ":" + " " + str(value), file=file)
    elif isinstance(ob, list):
        if not ob:
            print(ind + "[]", file=file)
        for el in ob:
            if isinstance(el, list | dict):
                text_formatter(el, file, indent + 1)
            else:
                text_formatter(el, file, indent)
    else:
        print(ind + str(ob), file=file)
