"""
Design constraints and effects
==============================

This module provides classes for defining design rule constraints
and their effects on routing, spacing, and via placement.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
from typing import Any, Self, overload

from .via import Via
from .property import Property


@dataclass
class TraceWidth:
    """A constraint effect specifying the exact trace width to be used in routing.

    See :py:meth:`~UnaryDesignConstraint.trace_width` for usage.
    """

    width: float
    "The trace width in millimeters"


@dataclass
class Clearance:
    """A constraint effect specifying the clearance between two objects.

    See :py:meth:`~BinaryDesignConstraint.clearance` for usage.
    """

    clearance: float
    "The clearance in millimeters"


@dataclass
class ViaStitchPattern:
    """Base class for via stitch patterns used in StitchVia constraints.

    Via stitch patterns arrange vias within copper regions.
    """

    pitch: float
    "The spacing between via centers in millimeters"
    inset: float
    "Minimum distance from the stitched region's boundary to the outermost via centers in millimeters"


@dataclass
class SquareViaStitchGrid(ViaStitchPattern):
    """A square grid pattern for via stitching.

    Places vias in a regular square grid pattern within the target area.
    Used in the StitchVia design rule constraint.

    >>> pattern = SquareViaStitchGrid(pitch=2.0, inset=0.5)
    """


@dataclass
class TriangularViaStitchGrid(ViaStitchPattern):
    """A triangular grid pattern for via stitching.

    Places vias in a triangular (hexagonal close-packed) pattern within
    the target area. Used in the StitchVia design rule constraint.

    >>> pattern = TriangularViaStitchGrid(pitch=1.5, inset=1.0)
    """


@dataclass
class StitchVia:
    """A constraint effect specifying that vias should be arranged within copper areas
    in a pattern.

    See :py:meth:`~UnaryDesignConstraint.stitch_via` for usage.
    """

    definition: type[Via]
    "The Via class to use for stitching"
    pattern: SquareViaStitchGrid | TriangularViaStitchGrid
    "The geometric pattern for via placement"


@dataclass
class ViaFencePattern:
    """A pattern configuration for via fencing around routes or copper features.

    Via fencing places vias around the perimeter of routes or copper areas. The
    pattern controls how these vias are arranged. Used in the FenceVia design
    rule constraint.

    See :py:meth:`~UnaryDesignConstraint.fence_via` for usage.

    >>> fence_pattern = ViaFencePattern(
    ...     pitch=1.0,
    ...     offset=0.5,
    ...     num_rows=2,
    ...     min_pitch=0.5,
    ...     max_pitch=2.0
    ... )
    """

    pitch: float
    "The preferred center-to-center spacing between vias in millimeters"
    offset: float
    """The center-to-center distance between fence via rows, and the default initial offset in millimeters

    Positive values indicate an outwards offset, negative values an inwards
    offset. The offset for routes must be positive. If ``initial_offset`` is not
    specified, this value serves as the default initial offset.
    """
    num_rows: int | None = None
    "The number of rows of fence vias to generate, default is 1"
    min_pitch: float | None = None
    "The minimum allowed center-to-center pitch between vias in millimeters"
    max_pitch: float | None = None
    "The maximum allowed center-to-center pitch between vias in millimeters"
    initial_offset: float | None = None
    """The initial offset of the first row of fence vias

    The initial offset is the perpendicular distance from the boundary of the
    route or copper feature to the centers of the first row of fence vias.
    Positive values indicate an outwards offset, while negative values indicate
    an inwards offset (inset). The offset must be positive for routes. Defaults
    to the same value as ``offset`` if unspecified.
    """
    input_shape_only: bool | None = None
    """For pours only, whether to fence the original pour outline

    If true, the pre-isolation outline shape of the pour is used to generate the
    fence vias. If false, the post-isolation shape is used. Defaults to true if
    not specified.
    """


@dataclass
class FenceVia:
    """A constraint effect specifying that fencing vias should be generated

    The vias are generated around perimeter of the copper region or route which
    this constraint is applied to. The vias will be given the same net as the copper
    region.

    See :py:meth:`~UnaryDesignConstraint.fence_via` for usage.
    This constraint can also be given to :py:class:`jitx.si.RoutingStructure.Layer` and
    :py:class:`jitx.si.DifferentialRoutingStructure.Layer`. See there for usage.
    """

    definition: type[Via]
    "The Via class to use for fencing"
    pattern: ViaFencePattern
    "The geometric pattern for fence placement"


@dataclass
class ThermalRelief:
    """A constraint effect specifying thermal connections between pours and objects.

    Thermal reliefs control how pours connect to objects with gaps and spokes.

    See :py:meth:`~UnaryDesignConstraint.thermal_relief` for usage.
    """

    gap_distance: float
    "The distance between pours and affected objects in millimeters"
    spoke_width: float
    "The width of the connecting spokes in millimeters"
    num_spokes: int
    "The number of thermal relief spokes (typically 2 or 4)"


class Tag:
    """Tags are the fundamental building blocks for design rules.

    Tags are applied to design objects, and are then used by the rule system
    to determine which rules apply to which objects.

    Tags form a hierarchy through class inheritance, and thus a rule applied
    to a tag will apply to all tags that are a subclass of that tag. The name
    of a tag is derived from its class name.

    Tags can be combined using logical operators to create complex conditions:
    - & (AND): Both conditions must be true
    - | (OR): Either condition can be true
    - ~ (NOT): Inverts the condition

    >>> class PowerTag(Tag):
    ...     "This is a power net, or some appropriate docstring for this tag"

    >>> class SignalTag(Tag):
    ...     "This is a signal net"

    >>> class HighSpeedTag(SignalTag):
    ...     "This is a high speed signal"

    >>> # This rule applies to ALL Signal tags (including HighSpeed)
    >>> signal_rule = UnaryDesignConstraint(SignalTag()).trace_width(0.2)

    >>> # This rule applies only to HighSpeed signals
    >>> high_speed_rule = UnaryDesignConstraint(HighSpeedTag()).trace_width(0.1)

    Tags can be assigned to objects and used in rule conditions:

    >>> # Assign tags to nets
    >>> PowerTag().assign(power_net)
    >>> GroundTag().assign(ground_net)
    >>>
    >>> # Create rules using tag combinations
    >>> rule1 = UnaryDesignConstraint(PowerTag()).trace_width(0.5)
    >>> rule2 = UnaryDesignConstraint(PowerTag() & HighSpeedTag()).clearance(0.3)
    >>> rule3 = UnaryDesignConstraint(PowerTag() | SignalTag()).stitch_via(MyVia, pattern)
    >>> rule4 = UnaryDesignConstraint(~HighSpeedTag()).trace_width(0.2)
    """

    def __repr__(self):
        return self.__class__.__name__

    def __and__(self, other: Any) -> AndExpr:
        """Logical AND operation between the tag and another tag or expression.

        Args:
            other: Another Tag or BoolExpr to combine with

        Returns:
            AndExpr representing the logical AND of both conditions

        >>> condition = PowerTag() & HighSpeedTag()
        """
        if not isinstance(other, Tag) and not isinstance(other, BoolExpr):
            raise ValueError(
                "Cannot create a boolean expression with a tag and a non-tag or non-boolean expression."
            )
        return AndExpr(AtomExpr(self), _ensure_expr(other))

    def __or__(self, other: Any) -> OrExpr:
        """Logical OR operation between the tag and another tag or expression.

        Args:
            other: Another Tag or BoolExpr to combine with

        Returns:
            OrExpr representing the logical OR of both conditions

        >>> condition = PowerTag() | SignalTag()
        """
        if not isinstance(other, Tag) and not isinstance(other, BoolExpr):
            raise ValueError(
                "Cannot create a boolean expression with a tag and a non-tag or non-boolean expression."
            )
        return OrExpr(AtomExpr(self), _ensure_expr(other))

    def __invert__(self) -> NotExpr:
        """Logical NOT operation on the tag.

        Returns:
            NotExpr representing the logical negation of this tag

        >>> condition = ~HighSpeedTag()
        """
        return NotExpr(AtomExpr(self))

    def assign(self, *other):
        """Assign this tag to an object.

        Args:
            other: The object to assign this tag to

        Returns:
            The tag instance for method chaining

        >>> ports = [Port(), Port()]
        >>> net = Net(ports)
        >>> PowerTag().assign(net)
        """
        Tags(self).assign(*other)
        return self

    @staticmethod
    def any(*tgs: Tag):
        """Construct a new tag that is the logical OR
        of all the passed tags.
        """
        ret = NotExpr(TrueExpr())  # False
        for tg in tgs:
            ret |= tg
        return ret

    @staticmethod
    def all(*tgs: Tag):
        """Construct a new tag that is the logical AND
        of all the passed tags.
        """
        ret = TrueExpr()
        for tg in tgs:
            ret &= tg
        return ret


class BuiltinTag(Tag, Enum):
    IsCopper = "IsCopper"
    IsTrace = "IsTrace"
    IsPour = "IsPour"
    IsVia = "IsVia"
    IsPad = "IsPad"
    IsBoardEdge = "IsBoardEdge"
    IsThroughHole = "IsThroughHole"
    IsNeckdown = "IsNeckdown"
    IsHole = "IsHole"


# Aliases for direct import
IsCopper = BuiltinTag.IsCopper
IsTrace = BuiltinTag.IsTrace
IsPour = BuiltinTag.IsPour
IsVia = BuiltinTag.IsVia
IsPad = BuiltinTag.IsPad
IsBoardEdge = BuiltinTag.IsBoardEdge
IsThroughHole = BuiltinTag.IsThroughHole
IsNeckdown = BuiltinTag.IsNeckdown
IsHole = BuiltinTag.IsHole


class OnLayer(Tag):
    """Tag for specifying layer-specific rules."""

    index: int

    def __init__(self, index: int):
        self.index = index

    @staticmethod
    def external():
        """Retrieve a tag that matches to the top and bottom
        external copper layers of a board.
        """
        return OnLayer(0) | OnLayer(-1)

    @staticmethod
    def internal():
        """Retrieve a tag that matches any of non-external
        layers (ie, inner layers) of the board. This is effectively
        the inverse of `OnLayer.external()`.
        """
        return ~OnLayer.external()


class Tags(Property):
    """A collection of tags assigned to an object, as a property.

    Tags are markers on design objects that are then used by the rule system
    to determine which rules apply to which objects.

    Args:
        tags: A single Tag or sequence of Tags to assign
        *more: Additional tags to assign

    >>> # Assign a single tag
    >>> Tags(PowerTag()).assign(power_net)
    >>>
    >>> # Assign multiple tags
    >>> Tags([PowerTag(), HighSpeedTag()]).assign(signal_net)
    >>>
    >>> # Assign using multiple arguments
    >>> Tags(PowerTag(), HighSpeedTag(), CriticalTag()).assign(clock_net)
    """

    tags: list[Tag]

    def __init__(self, tags: Tag | Iterable[Tag], *more: Tag):
        if isinstance(tags, Tag):
            tags = [tags]
        else:
            tags = list(tags)
        if more:
            tags.extend(more)

        for tag in tags:
            if isinstance(tag, BuiltinTag):
                raise TypeError("Cannot call assign() on a BuiltinTag")
        self.tags = tags

    def _set(self, other: Self | None):
        if other:
            other.tags.extend(self.tags)
            # leave the already assigned tag in place.
            return other
        else:
            return Tags(self.tags)


@dataclass
class BoolExpr:
    """Base class for boolean expressions used in design rule conditions.

    Boolean expressions are created by combining Tags using logical operators.
    They form the condition part of design rules that determine when the rule
    should be applied.

    Boolean expressions support the same logical operators as Tags:
    - & (AND): Both expressions must be true
    - | (OR): Either expression can be true
    - ~ (NOT): Inverts the expression

    >>> expr1 = PowerTag() & HighSpeedTag()
    >>> expr2 = GroundTag() | SignalTag()
    >>> complex_expr = expr1 | (expr2 & ~CriticalTag())
    """

    def __and__(self, other: Any) -> AndExpr:
        """Logical AND operation between expressions.

        Args:
            other: Another Tag or BoolExpr to combine with

        Returns:
            AndExpr representing the logical AND of both expressions
        """
        if not isinstance(other, Tag) and not isinstance(other, BoolExpr):
            raise ValueError(
                "Cannot create a boolean expression with a boolean expression and a non-tag or non-boolean expression."
            )
        return AndExpr(self, _ensure_expr(other))

    def __or__(self, other: Any) -> OrExpr:
        """Logical OR operation between expressions.

        Args:
            other: Another Tag or BoolExpr to combine with

        Returns:
            OrExpr representing the logical OR of both expressions
        """
        if not isinstance(other, Tag) and not isinstance(other, BoolExpr):
            raise ValueError(
                "Cannot create a boolean expression with a boolean expression and a non-tag or non-boolean expression."
            )
        return OrExpr(self, _ensure_expr(other))

    def __invert__(self) -> NotExpr:
        """Logical NOT operation on an expression.

        Returns:
            NotExpr representing the logical negation of this expression
        """
        return NotExpr(self)


@dataclass
class TrueExpr(BoolExpr):
    """Always true boolean expression.

    This expression always evaluates to true and can be used to create
    rules that apply to all objects regardless of their tags.

    >>> # Rule that applies to everything
    >>> rule = design_constraint(TrueExpr()).trace_width(0.2)
    """

    def __str__(self):
        return "True"


AnyObject: TrueExpr = TrueExpr()
"""A convenience constant alias for TrueExpr, representing a boolean
expression that is always true, thus applying to any object."""


@dataclass
class AtomExpr(BoolExpr):
    """Atomic boolean expression containing a single tag.

    This is the simplest form of boolean expression, containing just
    a single tag. It's created automatically when a Tag is used in
    a rule condition.

    Args:
        atom: The Tag this expression represents
    """

    atom: Tag

    def __str__(self):
        return f"{self.atom}"


@dataclass
class NotExpr(BoolExpr):
    """Negation of a boolean expression.

    Represents the logical NOT of another boolean expression.

    Args:
        expr: The boolean expression to negate

    >>> not_power = NotExpr(AtomExpr(PowerTag()))
    >>> # Or more commonly: ~PowerTag()
    """

    expr: BoolExpr

    def __str__(self):
        return f"~({self.expr})"


@dataclass
class OrExpr(BoolExpr):
    """Logical OR of two boolean expressions.

    Represents a condition where either the left OR right expression
    (or both) must be true.

    Args:
        left: Left side of the OR operation
        right: Right side of the OR operation

    >>> power_or_ground = OrExpr(AtomExpr(PowerTag()), AtomExpr(GroundTag()))
    >>> # Or more commonly:
    >>> power_or_ground = PowerTag() | GroundTag()
    """

    left: BoolExpr
    right: BoolExpr

    def __str__(self):
        return f"({self.left}) | ({self.right})"


@dataclass
class AndExpr(BoolExpr):
    """Logical AND of two boolean expressions.

    Represents a condition where both the left AND right expressions
    must be true.

    Args:
        left: Left side of the AND operation
        right: Right side of the AND operation

    >>> power_and_critical = AndExpr(AtomExpr(PowerTag()), AtomExpr(CriticalTag()))
    >>> # Or more commonly:
    >>> power_and_critical = PowerTag() & CriticalTag()
    """

    left: BoolExpr
    right: BoolExpr

    def __str__(self):
        return f"({self.left}) & ({self.right})"


def _ensure_expr(arg: Tag | BoolExpr | bool) -> BoolExpr:
    """Convert a Tag or BoolExpr into a BoolExpr.

    This utility function ensures that both Tags and BoolExprs can be used
    interchangeably in rule conditions by converting Tags to AtomExpr when needed.

    Args:
        arg: value to convert

    Returns:
        An equivalent BoolExpr if it wasn't one already.

    >>> tag = PowerTag()
    >>> expr = _ensure_expr(tag)  # Returns AtomExpr(PowerTag())
    >>> expr2 = _ensure_expr(tag & GroundTag())  # Returns the AndExpr as-is
    """
    if arg is True:
        return TrueExpr()
    elif arg is False:
        return NotExpr(TrueExpr())
    elif isinstance(arg, Tag):
        return AtomExpr(arg)
    return arg


@overload
def design_constraint(
    condition: Tag | BoolExpr | bool,
    /,
    *,
    priority: int = 0,
    name: str | None = None,
) -> UnaryDesignConstraint: ...


@overload
def design_constraint(
    condition1: Tag | BoolExpr | bool,
    condition2: Tag | BoolExpr | bool,
    /,
    *,
    priority: int = 0,
    name: str | None = None,
) -> BinaryDesignConstraint: ...


def design_constraint(
    condition1: Tag | BoolExpr | bool,
    condition2: Tag | BoolExpr | bool | None = None,
    /,
    *,
    priority: int = 0,
    name: str | None = None,
):
    """Syntactic helper function for creating the correct type of class. The
    overloads will generate :py:class:`UnaryDesignConstraint` or
    :py:class:`BinaryDesignConstraint` depending on the number of conditions, and
    should provide correct method completion in the editor."""

    condition1 = _ensure_expr(condition1)
    if condition2 is None:
        return UnaryDesignConstraint(condition1, priority=priority, name=name)
    else:
        condition2 = _ensure_expr(condition2)
        return BinaryDesignConstraint(
            condition1, condition2, priority=priority, name=name
        )


class DesignConstraint(ABC):
    """Top-level design constraint that defines manufacturing and electrical rules.

    A DesignConstraint combines conditional logic (based on Tags) with constraint effects
    controlling the physical layout. Rules can specify trace widths, clearances, via stitches,
    via fences, and thermal reliefs.

    Rules are prioritized - higher priority numbers take precedence when multiple
    rules could apply to the same object. Rules can have single conditions or
    pairs of conditions (for rules that apply between two different objects).

    Single condition rules (apply to objects matching the condition):

    >>> # Basic trace width rule for power nets
    >>> power_rule = design_constraint(PowerTag()).trace_width(0.5)

    >>> # Complex condition with priority
    >>> critical_rule = design_constraint(PowerTag() & CriticalTag(), priority=10).trace_width(1.0)

    >>> # Via stitching for ground planes
    >>> stitch_pattern = SquareViaStitchGrid(pitch=2.0, inset=0.5)
    >>> ground_rule = design_constraint(GroundTag()).stitch_via(GroundVia, stitch_pattern)

    Dual condition rules (apply between objects matching different conditions):

    >>> # Clearance between power and signal nets
    >>> clearance_rule = design_constraint(PowerTag(), SignalTag()).clearance(0.3)

    >>> # Clearance between any ground and non-critical nets
    >>> ground_clearance = design_constraint(GroundTag(), ~CriticalTag()).clearance(0.2)

    Method chaining for complex rules:

    >>> complex_rule = (
    ...     design_constraint(PowerTag(), priority=5)
    ...     .trace_width(0.8)
    ...     .stitch_via(PowerVia, SquareViaStitchGrid(pitch=1.5, inset=0.3))
    ...     .thermal_relief(gap_distance=0.15, spoke_width=0.1, num_spokes=4)
    ... )

    Via fencing example:

    >>> fence_pattern = ViaFencePattern(
    ...     pitch=1.0,
    ...     offset=0.5,
    ...     num_rows=2,
    ...     min_pitch=0.5,
    ...     max_pitch=2.0
    ... )
    >>> shield_rule = design_constraint(HighSpeedTag()).fence_via(ShieldVia, fence_pattern)

    Universal rules using a true (or TrueExpr) condition:

    >>> # Default trace width for all nets
    >>> default_rule = design_constraint(true).trace_width(0.2)
    """

    priority: int = 0
    """Priority level - higher numbers take precedence if multiple rules apply"""
    name: str | None = None
    """Name of this rule to identify it at runtime"""

    @abstractmethod
    def __init__(self, *, priority: int = 0, name: str | None = None):
        self.priority = priority
        self.name = name


class UnaryDesignConstraint(DesignConstraint):
    condition: BoolExpr
    trace_width_constraint: TraceWidth | None = None
    stitch_via_constraint: StitchVia | None = None
    fence_via_constraint: FenceVia | None = None
    thermal_relief_constraint: ThermalRelief | None = None

    def __repr__(self):
        r = [
            f"UnaryDesignConstraint({self.condition}, name={self.name!r}, priority={self.priority})"
        ]
        if self.trace_width_constraint:
            r.append(f"trace_width({self.trace_width_constraint})")
        if self.stitch_via_constraint:
            r.append(f"stitch_via({self.stitch_via_constraint})")
        if self.fence_via_constraint:
            r.append(f"fence_via({self.fence_via_constraint})")
        if self.thermal_relief_constraint:
            r.append(f"thermal_relief({self.thermal_relief_constraint})")
        return ".".join(r)

    def __init__(
        self, condition: BoolExpr | Tag, *, priority: int = 0, name: str | None = None
    ):
        super().__init__(name=name, priority=priority)
        self.condition = _ensure_expr(condition)

    def trace_width(self, width: float) -> Self:
        """Set the trace width constraint for this rule.

        Args:
            width: Trace width in millimeters

        Returns:
            Self for method chaining

        >>> rule = UnaryDesignConstraint(PowerTag()).trace_width(0.5)
        """
        self.trace_width_constraint = TraceWidth(width)
        return self

    def stitch_via(
        self,
        definition: type[Via],
        pattern: SquareViaStitchGrid | TriangularViaStitchGrid,
    ) -> Self:
        """Set the via stitching constraint for this rule.

        Args:
            definition: The Via class to use in the stitch
            pattern: The geometric pattern for arranging the vias

        Returns:
            Self for method chaining

        >>> pattern = SquareViaStitchGrid(pitch=2.0, inset=0.5)
        >>> rule = design_constraint(GroundTag()).stitch_via(GroundVia, pattern)
        """
        self.stitch_via_constraint = StitchVia(definition, pattern)
        return self

    def fence_via(self, definition: type[Via], pattern: ViaFencePattern) -> Self:
        """Set the via fencing constraint for this rule.

        Args:
            definition: The Via class to use in the fence
            pattern: The geometric pattern for arranging the vias

        Returns:
            Self for method chaining

        >>> fence_pattern = ViaFencePattern(pitch=1.0, offset=0.5, num_rows=2)
        >>> rule = design_constraint(HighSpeedTag()).fence_via(ShieldVia, fence_pattern)
        """
        self.fence_via_constraint = FenceVia(definition, pattern)
        return self

    def thermal_relief(
        self, gap_distance: float, spoke_width: float, num_spokes: int
    ) -> Self:
        """Set the thermal relief constraint for this rule.

        Args:
            gap_distance: The distance between pours and affected objects in millimeters
            spoke_width: Width of the connecting spokes in millimeters
            num_spokes: Number of thermal relief spokes (typically 2 or 4)

        Returns:
            Self for method chaining

        >>> rule = design_constraint(ComponentPadTag()).thermal_relief(
        ...     gap_distance=0.2, spoke_width=0.15, num_spokes=4
        ... )
        """
        self.thermal_relief_constraint = ThermalRelief(
            gap_distance, spoke_width, num_spokes
        )
        return self


class BinaryDesignConstraint(DesignConstraint):
    first: BoolExpr
    second: BoolExpr
    clearance_constraint: Clearance | None = None

    def __init__(
        self,
        first: BoolExpr | Tag,
        second: BoolExpr | Tag,
        *,
        priority: int = 0,
        name: str | None = None,
    ):
        super().__init__(name=name, priority=priority)
        self.first = _ensure_expr(first)
        self.second = _ensure_expr(second)

    def __repr__(self):
        r = [
            f"BinaryDesignConstraint({self.first}, {self.second}, name={self.name!r}, priority={self.priority})"
        ]
        if self.clearance_constraint:
            r.append(f"clearance({self.clearance_constraint})")
        return ".".join(r)

    def clearance(self, clearance: float) -> Self:
        """Set the clearance constraint for this rule.

        Args:
            clearance: Clearance in millimeters

        Returns:
            Self for method chaining

        >>> rule = design_constraint(PowerTag(), SignalTag()).clearance(0.3)
        """
        self.clearance_constraint = Clearance(clearance)
        return self
