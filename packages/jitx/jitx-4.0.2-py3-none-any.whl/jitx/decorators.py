from collections.abc import Callable

from jitx._structural import PrePostInit


def early(method: Callable):
    """Call this method before calling other initializers in this class."""
    return PrePostInit(
        lambda inst, _: method.__get__(inst, type(inst))(),
        lambda _, before: before,
        representing=method,
    )


def late(method: Callable):
    """Call this method after calling all other initializers in this class."""
    return PrePostInit(
        lambda _, __: None,
        lambda inst, before: method.__get__(inst, type(inst))(),
        representing=method,
    )
