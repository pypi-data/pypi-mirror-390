"""
Interval arithmetic for ranges
==============================

This module provides the Interval class for representing ranges of values
that can be bounded or unbounded on either end.
"""


class Interval:
    """
    Interval Type for defining inclusive ranges of values, supporting infinite intervals.
    An interval may be bounded or unbounded on either end.
    """

    def __init__(self, lo: float | None = None, hi: float | None = None):
        """
        Constructor for an Interval type.

        Args:
            lo: Inclusive min value if not None. Otherwise, unbounded below.
            hi: Inclusive max value if not None. Otherwise, unbounded above.
        Raises:
            ValueError: If lo > hi (when both are not None).
        """
        if lo is not None and hi is not None and lo > hi:
            raise ValueError("Interval error: min must be less than or equal to max")
        self._lo = lo
        self._hi = hi

    @property
    def min_value(self) -> float | None:
        """Returns the minimum value of the interval, or None if unbounded below."""
        return self._lo

    @property
    def max_value(self) -> float | None:
        """Returns the maximum value of the interval, or None if unbounded above."""
        return self._hi

    def __eq__(self, other):
        if not isinstance(other, Interval):
            return NotImplemented
        return self.min_value == other.min_value and self.max_value == other.max_value

    def __hash__(self):
        return hash((self.min_value, self.max_value))

    def __repr__(self):
        return f"Interval({self.min_value}, {self.max_value})"


def AtLeast(value: float) -> Interval:
    """
    Interval with unbounded maximum and bounded minimum

    This is a helper function for creating a interval that
    is bounded from below only.

    Args:
        value: Inclusive low end bound for the interval

    >>> AtLeast(1)
    Interval(1, None)
    """
    return Interval(lo=value)


def AtMost(value: float) -> Interval:
    """
    Interval with unbounded minimum and bounded maximum

    This is a helper function for creating a interval that
    is bounded from above only.

    Args:
        value: Inclusive high end bound for the interval

    >>> AtMost(2)
    Interval(None, 2)
    """
    return Interval(hi=value)
