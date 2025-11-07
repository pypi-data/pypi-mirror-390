"""
Toleranced values and interval arithmetic
=========================================

This module provides the Toleranced class for representing values
with tolerances and performing interval arithmetic operations.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Self, overload
from .interval import Interval


class Unspecified:
    """:meta private:"""

    def __repr__(self):
        return "Unspecified"


_UNSPECIFIED = Unspecified()


_Unspecified = Unspecified
del Unspecified


class Toleranced(Interval):
    """
    Interval Arithmetic Type for values with tolerances.

    Args:
        typ: Typical value (average/nominal)
        plus: Relative positive increment (max bound, or None for unbounded)
        minus: Relative negative increment (min bound, or None for unbounded),
            If this argument is unspecified, the range will be symmetric.

    >>> # Create a resistor with ±5% tolerance
    >>> r1 = Toleranced.percent(10_000, 5)  # 10kΩ ± 5%
    >>> print(r1)
    10000 ± 5%

    >>> # Create a voltage with asymmetric bounds
    >>> v1 = Toleranced.min_typ_max(2.7, 3.3, 3.6)  # 2.7V to 3.6V, typical 3.3V
    >>> print(v1)
    Toleranced(2.7 <= 3.3 <= 3.6)

    >>> # Arithmetic with tolerances
    >>> r2 = Toleranced.percent(1_000, 1)  # 1kΩ ± 1%
    >>> total = r1 + r2
    >>> print(f"Total: {total.min_value:.0f}Ω to {total.max_value:.0f}Ω")
    Total: 10490Ω to 11510Ω

    >>> # Voltage divider calculation
    >>> v_out = v1 * r2 / (r1 + r2)
    >>> print(v_out)
    Toleranced(0.3, 0.0466158, 0.0677672)
    """

    typ: float
    """The typical/nominal value."""
    plus: float | None
    """Positive tolerance from typical to maximum value. None indicates unbounded maximum."""
    minus: float | None
    """Negative tolerance from typical to minimum value. None indicates unbounded minimum."""
    __used_percent: tuple[float, float] | None = None

    @overload
    def __init__(self, typ: float, plusminus: float | None, /): ...
    @overload
    def __init__(self, typ: float, plus: float | None, minus: float | None): ...

    def __init__(
        self,
        typ: float,
        plus: float | None,
        minus: float | None | _Unspecified = _UNSPECIFIED,
    ):
        if isinstance(minus, _Unspecified):
            minus = plus
        self.typ = typ
        self.plus = plus
        self.minus = minus

        assert self.plus is None or self.plus >= 0.0
        assert self.minus is None or self.minus >= 0.0

    def __str__(self):
        # Both bounds present
        typ = self.typ
        plus = self.plus
        minus = self.minus
        if plus == minus:
            if plus is None:
                return f"{typ:g} ± ∞"
            elif self.__used_percent:
                return f"{typ:g} ± {self.__used_percent[0]}%"
            return f"{typ:g} ± {plus:g}"
        # Only min bound present
        elif self.plus is None:
            return f"Toleranced({self.min_value:g} <= typ:{self.typ:g})"
        # Only max bound present
        elif self.minus is None:
            return f"Toleranced(typ:{self.typ:g} <= {self.max_value:g})"
        return f"Toleranced({self.min_value:g} <= {self.typ:g} <= {self.max_value:g})"

    def __repr__(self):
        return f"Toleranced({self.typ:g}, {self.plus:g}, {self.minus:g})"

    @property
    def max_value(self) -> float:
        """The maximum value of the tolerance range (typ + plus)."""
        if self.plus is not None:
            return self.typ + self.plus
        raise ValueError("plus must be specified to compute max_value")

    @property
    def min_value(self) -> float:
        """The minimum value of the tolerance range (typ - minus)."""
        if self.minus is not None:
            return self.typ - self.minus
        raise ValueError("minus must be specified to compute min_value")

    def center_value(self) -> float:
        """Calculate the geometric center of the range (midpoint between min and max)."""
        return self.min_value + 0.5 * (self.max_value - self.min_value)

    def plus_percent(self) -> float:
        """Calculate the positive tolerance as a percentage of the typical value.

        Returns:
            Percentage value (e.g., 5.0 for 5%).

        Raises:
            ValueError: If plus is None or typ is zero.
        """
        if self.plus is None:
            raise ValueError("plus must be specified to compute tol+%(Toleranced)")
        if self.typ == 0.0:
            raise ValueError("typ() != 0.0 to compute tol+%(Toleranced)")
        return 100.0 * self.plus / self.typ

    def minus_percent(self) -> float:
        """Calculate the negative tolerance as a percentage of the typical value.

        Returns:
            Percentage value (e.g., 5.0 for 5%).

        Raises:
            ValueError: If minus is None or typ is zero.
        """
        if self.minus is None:
            raise ValueError("minus must be specified to compute tol-%(Toleranced)")
        if self.typ == 0.0:
            raise ValueError("typ() != 0.0 to compute tol-%(Toleranced)")
        return 100.0 * self.minus / self.typ

    def in_range(self, value: float | Toleranced) -> bool:
        """Check if a value or range is contained within this tolerance range.

        Args:
            value: A float or another Toleranced value to check.

        Returns:
            True if the value/range is completely within this range.

        >>> tol = Toleranced(10, 1, 1)  # 9 to 11
        >>> tol.in_range(10.5)
        True
        >>> tol.in_range(Toleranced(10, 0.5, 0.5))  # 9.5 to 10.5
        True
        """
        if isinstance(value, Toleranced):
            return (
                value.min_value >= self.min_value and value.max_value <= self.max_value
            )
        elif isinstance(value, float | int):
            return self.min_value <= value <= self.max_value
        else:
            raise ValueError("in_range() requires a Toleranced or float value.")

    def range(self) -> float:
        """Calculate the total range (max - min)."""
        return self.max_value - self.min_value

    def _full_tolerance(self):
        """Return True if typ, plus, and minus are all specified (not None). 0.0 is valid and means exact."""
        return self.plus is not None and self.minus is not None

    def __add__(self, other: Toleranced | float) -> Toleranced:
        """Add two toleranced values or a toleranced value and a float.

        When adding two Toleranced values, tolerances propagate: the resulting
        tolerance is the sum of the individual tolerances.

        Args:
            other: Another Toleranced value or a float.

        Returns:
            New Toleranced value representing the sum.

        Raises:
            ValueError: If either value has unbounded tolerances (None).

        >>> a = Toleranced(10, 1, 1)  # 9 to 11
        >>> b = Toleranced(5, 0.5, 0.5)  # 4.5 to 5.5
        >>> c = a + b
        >>> print(c)
        15 ± 1.5
        """
        if isinstance(other, Toleranced):
            if (self.plus is None or self.minus is None) or (
                other.plus is None or other.minus is None
            ):
                raise ValueError(
                    "Toleranced() arithmetic operations require fully specified arguments (None is not allowed, 0.0 is valid)"
                )
            return Toleranced(
                self.typ + other.typ,
                self.plus + other.plus,
                self.minus + other.minus,
            )
        elif isinstance(other, int | float):
            return Toleranced(self.typ + other, self.plus, self.minus)
        return NotImplemented

    def __radd__(self, other: float) -> Toleranced:
        return self.__add__(other)

    def __sub__(self, other: Toleranced | float) -> Toleranced:
        """Subtract two toleranced values or subtract a float from a toleranced value.

        When subtracting two Toleranced values, tolerances propagate: the resulting
        tolerance accounts for the worst-case combination of bounds.

        Args:
            other: Another Toleranced value or a float to subtract.

        Returns:
            New Toleranced value representing the difference.

        Raises:
            ValueError: If either value has unbounded tolerances (None).

        >>> v_in = Toleranced.percent(12, 5)  # 12V ± 5%
        >>> v_drop = Toleranced(0.7, 0.1, 0.1)  # 0.7V ± 0.1V
        >>> v_out = v_in - v_drop
        >>> print(v_out)
        11.3 ± 0.7
        """
        if isinstance(other, Toleranced):
            if (self.plus is None or self.minus is None) or (
                other.plus is None or other.minus is None
            ):
                raise ValueError(
                    "Toleranced() arithmetic operations require fully specified arguments (None is not allowed, 0.0 is valid)"
                )
            return Toleranced(
                self.typ - other.typ,
                self.plus + other.minus,
                self.minus + other.plus,
            )
        elif isinstance(other, int | float):
            return Toleranced(self.typ - other, self.plus, self.minus)
        return NotImplemented

    def __rsub__(self, other: float) -> Toleranced:
        return Toleranced(other, 0.0, 0.0) - self

    def __mul__(self, other: float | Toleranced) -> Toleranced:
        """Multiply two toleranced values or a toleranced value and a float.

        When multiplying two Toleranced values, computes the product of all
        combinations of min/max values to determine the resulting range.

        Args:
            other: Another Toleranced value or a float.

        Returns:
            New Toleranced value representing the product.

        Raises:
            ValueError: If either value has unbounded tolerances (None) when
                multiplying two Toleranced values.

        >>> r = Toleranced.percent(1000, 5)  # 1kΩ ± 5%
        >>> i = Toleranced(0.001, 0.0001, 0.0001)  # 1mA ± 0.1mA
        >>> power = r * i * i  # P = I²R
        """
        if isinstance(other, Toleranced):
            if (self.plus is None or self.minus is None) or (
                other.plus is None or other.minus is None
            ):
                raise ValueError(
                    "Toleranced() arithmetic operations require fully specified arguments (None is not allowed, 0.0 is valid)"
                )
            typ = self.typ * other.typ
            variants = [
                self.min_value * other.min_value,
                self.min_value * other.max_value,
                self.max_value * other.min_value,
                self.max_value * other.max_value,
            ]
            plus = max(variants) - typ
            minus = typ - min(variants)
            return Toleranced(typ, plus, minus)
        elif isinstance(other, int | float):
            plus = abs(self.plus * other) if self.plus is not None else None
            minus = abs(self.minus * other) if self.minus is not None else None
            return Toleranced(self.typ * other, plus, minus)
        return NotImplemented

    def __rmul__(self, other: float) -> Toleranced:
        return self.__mul__(other)

    def __truediv__(self, other: Toleranced | float) -> Toleranced:
        """Divide two toleranced values or divide a toleranced value by a float.

        When dividing two Toleranced values, computes the inverse of the
        denominator and multiplies. Division by zero is detected and raises an error.

        Args:
            other: Another Toleranced value or a float to divide by.

        Returns:
            New Toleranced value representing the quotient.

        Raises:
            ValueError: If either value has unbounded tolerances (None) when
                dividing two Toleranced values, or if dividing by a negative float.
            ZeroDivisionError: If the denominator range includes zero.

        >>> v = Toleranced.percent(3.3, 5)  # 3.3V ± 5%
        >>> r = Toleranced.percent(1000, 1)  # 1kΩ ± 1%
        >>> i = v / r  # Current in amps
        """
        if isinstance(other, Toleranced):
            if (self.plus is None or self.minus is None) or (
                other.plus is None or other.minus is None
            ):
                raise ValueError(
                    "Toleranced() arithmetic operations require fully specified arguments (None is not allowed, 0.0 is valid)"
                )
            if other.in_range(0.0):
                raise ZeroDivisionError("Cannot divide by zero for Toleranced values.")
            typ = 1.0 / other.typ
            inv = Toleranced(
                typ, 1.0 / other.min_value - typ, typ - 1.0 / other.max_value
            )
            return self * inv
        elif isinstance(other, int | float):
            if other == 0:
                raise ZeroDivisionError("Cannot divide by zero.")
            elif other < 0:
                raise ValueError("Cannot divide Toleranced by negative value.")
            plus = self.plus / other if self.plus is not None else None
            minus = self.minus / other if self.minus is not None else None
            return self.__class__(self.typ / other, plus, minus)
        return NotImplemented

    def __rtruediv__(self, other: float) -> Toleranced:
        return Toleranced.exact(other) / self

    def apply(self, f: Callable[[float], float]) -> Self:
        """Apply a function to the toleranced value.

        Applies the given function to min, typ, and max values and creates
        a new Toleranced from the results. Useful for non-linear transformations.

        Args:
            f: A function that takes a float and returns a float.

        Returns:
            New Toleranced value with the function applied.

        >>> import math
        >>> v = Toleranced(4.0, 0.5, 0.5)  # 3.5 to 4.5
        >>> sqrt_v = v.apply(math.sqrt)  # sqrt applied to range
        >>> print(f"{sqrt_v.min_value:.2f} to {sqrt_v.max_value:.2f}")
        1.87 to 2.12
        """
        tv = f(self.typ)
        minv = f(self.min_value)
        maxv = f(self.max_value)
        return self.min_typ_max(minv, tv, maxv)

    @classmethod
    def min_typ_max(
        cls, min_val: float | None, typ_val: float | None, max_val: float | None
    ) -> Self:
        """Create a Toleranced value from min, typ, and max values.

        At least two of the three values must be specified. If typ is not
        provided, it will be calculated as the midpoint of min and max.

        Args:
            min_val: Minimum value (or None if unbounded below).
            typ_val: Typical/nominal value (or None to use midpoint).
            max_val: Maximum value (or None if unbounded above).

        Returns:
            New Toleranced value.

        Raises:
            ValueError: If fewer than two values are specified, or if
                min > typ, typ > max, or min > max.

        >>> # Supply voltage specification
        >>> vdd = Toleranced.min_typ_max(2.7, 3.3, 3.6)
        >>> print(vdd)
        Toleranced(2.7 <= 3.3 <= 3.6)

        >>> # Temperature range without typical
        >>> temp = Toleranced.min_typ_max(-40, None, 85)
        >>> print(f"Center temp: {temp.typ}°C")
        Center temp: 22.5°C
        """
        if typ_val is not None and min_val is not None and max_val is not None:
            if typ_val < min_val or max_val < typ_val:
                raise ValueError("min-typ-max() should be [min] <= [typ] <= [max]")
            return cls(typ_val, max_val - typ_val, typ_val - min_val)
        elif min_val is not None and max_val is not None:
            if max_val < min_val:
                raise ValueError("min-typ-max() should have max >= min.")
            t = min_val + 0.5 * (max_val - min_val)
            return cls(t, max_val - t, t - min_val)
        elif typ_val is not None and min_val is not None:
            if typ_val < min_val:
                raise ValueError("min-typ-max() should have min <= typ")
            return cls(typ_val, None, typ_val - min_val)
        elif typ_val is not None and max_val is not None:
            if typ_val > max_val:
                raise ValueError("min-typ-max() should have typ <= max")
            return cls(typ_val, max_val - typ_val, None)
        else:
            raise ValueError(
                "min-typ-max() should have at least two of min, typ, max values"
            )

    @classmethod
    def min_max(cls, min_val: float, max_val: float) -> Self:
        """Create a Toleranced defined by absolute min and max values.

        The typical value will be set to the midpoint of min and max.

        Args:
            min_val: Minimum value.
            max_val: Maximum value.

        Returns:
            New Toleranced value.

        >>> # Operating frequency range
        >>> freq = Toleranced.min_max(10e6, 20e6)  # 10-20 MHz
        >>> print(f"Center: {freq.typ/1e6} MHz")
        Center: 15.0 MHz
        """
        return cls.min_typ_max(min_val, None, max_val)

    @classmethod
    def min_typ(cls, min_val: float, typ_val: float) -> Self:
        """Create a Toleranced defined by an absolute minimum and typical value.

        The maximum is unbounded (None).

        Args:
            min_val: Minimum value.
            typ_val: Typical/nominal value.

        Returns:
            New Toleranced value with unbounded maximum.

        >>> # Minimum load current
        >>> i_load = Toleranced.min_typ(0.1, 0.5)  # At least 100mA, typ 500mA
        """
        return cls.min_typ_max(min_val, typ_val, None)

    @classmethod
    def typ_max(cls, typ_val: float, max_val: float) -> Self:
        """Create a Toleranced defined by a typical and absolute maximum value.

        The minimum is unbounded (None).

        Args:
            typ_val: Typical/nominal value.
            max_val: Maximum value.

        Returns:
            New Toleranced value with unbounded minimum.

        >>> # Maximum current consumption
        >>> i_max = Toleranced.typ_max(50e-6, 100e-6)  # Typ 50µA, max 100µA
        """
        return cls.min_typ_max(None, typ_val, max_val)

    @classmethod
    def percent(
        cls, typ: float, plus: float, minus: float | _Unspecified = _UNSPECIFIED
    ) -> Self:
        """Create a Toleranced based on symmetric or asymmetric percentages of the typical value.

        If the `minus` argument is unspecified, the range will be symmetric.

        Args:
            typ: Typical/nominal value.
            plus: Positive tolerance as a percentage (0-100).
            minus: Negative tolerance as a percentage (0-100).
                If unspecified, uses the same value as plus.

        Returns:
            New Toleranced value.

        Raises:
            ValueError: If plus or minus is not in the range 0-100.

        >>> # 10kΩ resistor with ±5% tolerance
        >>> r1 = Toleranced.percent(10_000, 5)
        >>> print(r1)
        10000 ± 5%

        >>> # Voltage with asymmetric tolerance
        >>> v = Toleranced.percent(3.3, 10, 5)  # +10%, -5%
        >>> print(f"{v.min_value}V to {v.max_value}V")
        3.135V to 3.63V
        """
        if isinstance(minus, _Unspecified):
            minus = plus
        if not (0.0 <= plus <= 100.0):
            raise ValueError("tol+ must be in range 0.0 <= tol+ <= 100.0")
        if not (0.0 <= minus <= 100.0):
            raise ValueError("tol- must be in range 0.0 <= tol- <= 100.0")
        abstyp = abs(typ)
        aplus = abstyp * plus / 100.0
        aminus = abstyp * minus / 100.0
        tol = cls(typ, aplus, aminus)
        tol.__used_percent = plus, minus
        return tol

    @classmethod
    def sym(cls, typ: float, plusminus: float) -> Self:
        """Create a Toleranced with symmetric bounds.

        Effectively an alias of the two-argument constructor.

        Args:
            typ: Typical/nominal value.
            plusminus: Symmetric tolerance (both plus and minus).

        Returns:
            New Toleranced value with symmetric tolerance.

        >>> # Component with ±0.1mm tolerance
        >>> dim = Toleranced.sym(5.0, 0.1)  # 4.9 to 5.1 mm
        """
        return cls(typ, plusminus)

    @overload
    @classmethod
    def exact(cls, typ: float) -> Self: ...

    @overload
    @classmethod
    def exact(cls, typ: Toleranced) -> Toleranced: ...

    @classmethod
    def exact(cls, typ: float | Toleranced) -> Self | Toleranced:
        """Create a Toleranced with zero tolerance (exact value).

        If given a Toleranced value, returns it unchanged. If given a float,
        creates a Toleranced with plus=0 and minus=0.

        Args:
            typ: Value to wrap as exact, or existing Toleranced.

        Returns:
            Toleranced value with zero tolerance, or the input if already Toleranced.

        >>> # Ideal reference voltage (no tolerance)
        >>> v_ref = Toleranced.exact(2.5)
        >>> print(v_ref)
        2.5 ± 0
        """
        if isinstance(typ, Toleranced):
            return typ
        return cls(typ, 0.0)
