"""
Unit test support
=================

The way the JITX python framework is designed makes testing a bit more
complicated than one would normally expect. The reason for this is how it
handles instantiation of class members. This package provides a base
:py:class:`TestCase` class that sets up the JITX framework for testing by
enabling objects to be instantiated within a test case. The main issue to note
here is that if a class is created inside the test case, its members will
_also_ be instantiated, as class members, and will not go through the
instantiation process, which will likely lead to unexpected behavior, where
normally an object would be expected to be an instantiated attribute (e.g. a
:class:`~jitx.net.Port`).
"""

from dataclasses import dataclass
import unittest
from jitx._structural import instantiation
from jitx.context import Context


class TestCase(unittest.TestCase):
    """Base test case class with JITX context setup.

    This class sets up instantiation inside the test case, and registers a
    :py:class:`TestContext` which can be interrogated inside the design if
    desired. For the vast majority of cases, this class should be used as a
    base class instead of :py:class:`unittest.TestCase` when testing code that
    generates JITX design elements.
    """

    @classmethod
    def setUpClass(cls):
        cls.enterClassContext(instantiation.activate())
        TestContext(cls).set()
        super().setUpClass()


@dataclass(frozen=True)
class TestContext(Context):
    """Context for test execution. Will be set automatically if using
    :py:class:`jitx.test.TestCase` as a base class for your unit tests."""

    testClass: type[TestCase]
    """The test class being executed."""
