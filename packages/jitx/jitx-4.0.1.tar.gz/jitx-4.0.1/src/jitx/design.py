"""
Design definition
=================

This module provides the Design class, which is the root of a JITX design.
"""

from dataclasses import dataclass

from jitx.board import Board
from jitx.circuit import Circuit
from jitx.substrate import Substrate
from .context import Context
from .events import Event, EventContext
from ._structural import Structural
from jitx.decorators import early, late


class Design(Structural):
    """To create a JITX design, create a subclass of this class. It will need a
    :py:class:`~jitx.board.Board`, a :py:class:`~jitx.substrate.Substrate` and
    a :py:class:`~jitx.circuit.Circuit`.

    >>> class MyDesign(Design):
    ...     board = MyBoard()
    ...     substrate = MySubstrate()
    ...     circuit = MyCircuit()
    """

    board: Board
    substrate: Substrate
    circuit: Circuit

    @dataclass
    class Initialized(Event):
        """Event that is fired once the entire design has been gone through
        the initial construction and initialization. The design has not yet
        been dispatched for processing, and can still be modified if needed.

        >>> class MyComponent(Component):
                @Design.Initialized.on
                def on_initialized(self, init: Design.Initialized):
                    ... # do something after initialization
        """

        design: "Design"
        """The initialized design."""

    @early
    def setup(self):
        DesignContext(self).set()
        EventContext().set()

    @late
    def finalize(self):
        self.Initialized(self).fire()

    def __init_subclass__(cls):
        super().__init_subclass__()
        if cls.__module__ == "__main__":
            global _main_module_catch
            if not _main_module_catch:
                import atexit

                @atexit.register
                def _():
                    import os
                    import sys

                    if "jitx.run" not in sys.modules:
                        # File with a design was run directly, but never
                        # imported jitx.run to run it manually. Let's be
                        # helpful to someone who presses the play button.
                        print(
                            "It appears we're attempting to run a JITX",
                            "design file. We'll try to run it from the proper",
                            "entry point. If this was unintended, please import",
                            "jitx.run to suppress this behavior.",
                            file=sys.stderr,
                        )
                        main = sys.modules["__main__"]
                        path: str | None = None
                        if hasattr(main, "__file__") and main.__file__:
                            path = main.__file__
                        else:
                            loader = main.__loader__
                            if loader and hasattr(loader, "path"):
                                # pyright does not do hasattr type narrowing
                                path = loader.path  # type: ignore

                        if not path:
                            print(
                                "Unable to determine design file path", file=sys.stderr
                            )
                            return

                        os.execl(
                            sys.executable, sys.executable, "-m", "jitx", "build", path
                        )
                        # if exec failed (unsupported on some weird platform constellations)
                        import subprocess

                        p = subprocess.Popen([sys.executable, "jitx", "build", path])
                        p.wait()

            _main_module_catch = True


_main_module_catch = False


@dataclass
class DesignContext(Context):
    """Context object representing the currently active design. Should not be used directly, but rather accessed through
    :py:data:`jitx.current`'s :py:attr:`~jitx.Current.design` instead.

    >>> def design_elements() -> tuple[Board, Substrate, Circuit]:
    ...    design = jitx.current.design
    ...    return (design.board, design.substrate, design.circuit)
    """

    design: Design


def name(design: Design) -> str:
    """Get the fully qualified name of a design.

    Args:
        design: The design instance.

    Returns:
        The fully qualified name, or just the class name if from __main__.
    """
    cls = type(design)
    if cls.__module__ == "__main__":
        return cls.__name__
    return f"{cls.__module__}.{cls.__name__}"
