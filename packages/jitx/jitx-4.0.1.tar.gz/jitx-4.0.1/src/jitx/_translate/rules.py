from jitx._structural import RefPath, pathstring
from jitx._translate.enums import translate_builtin_tag
from jitx._translate.layerindex import translate_layer_index
from jitx._translate.via import translate_fence_via
from jitx.constraints import (
    BinaryDesignConstraint,
    BuiltinTag,
    DesignConstraint,
    OnLayer,
    Tag,
    TraceWidth,
    Clearance,
    ThermalRelief,
    SquareViaStitchGrid,
    TriangularViaStitchGrid,
    BoolExpr,
    TrueExpr,
    AtomExpr,
    NotExpr,
    OrExpr,
    AndExpr,
    UnaryDesignConstraint,
)
import jitxcore._proto.design_pb2 as dpb2
import jitxcore._proto.design_rules_pb2 as drpb2


def translate_binary_design_rule(
    rule: BinaryDesignConstraint,
    into: drpb2.DesignRule,
) -> None:
    translate_bool_expr(rule.first, into.conditions.add())
    translate_bool_expr(rule.second, into.conditions.add())
    if rule.clearance_constraint is not None:
        ce = into.effects.add()
        ce.clearance.clearance = rule.clearance_constraint.clearance


def translate_unary_design_rule(
    rule: UnaryDesignConstraint,
    into: drpb2.DesignRule,
) -> None:
    translate_bool_expr(rule.condition, into.conditions.add())
    if rule.trace_width_constraint is not None:
        ce = into.effects.add()
        ce.trace_width.width = rule.trace_width_constraint.width

    if rule.stitch_via_constraint is not None:
        ce = into.effects.add()
        ce.stitch_via.definition = rule.stitch_via_constraint.definition.__name__
        if isinstance(rule.stitch_via_constraint.pattern, SquareViaStitchGrid):
            ce.stitch_via.pattern.square.pitch = (
                rule.stitch_via_constraint.pattern.pitch
            )
            ce.stitch_via.pattern.square.inset = (
                rule.stitch_via_constraint.pattern.inset
            )
        elif isinstance(rule.stitch_via_constraint.pattern, TriangularViaStitchGrid):
            ce.stitch_via.pattern.triangular.pitch = (
                rule.stitch_via_constraint.pattern.pitch
            )
            ce.stitch_via.pattern.triangular.inset = (
                rule.stitch_via_constraint.pattern.inset
            )
        else:
            raise Exception(
                f"Unknown via stitch pattern type: {type(rule.stitch_via_constraint.pattern)}"
            )

    if rule.fence_via_constraint is not None:
        ce = into.effects.add()
        translate_fence_via(rule.fence_via_constraint, ce.fence_via)

    if rule.thermal_relief_constraint is not None:
        ce = into.effects.add()
        ce.thermal_relief.gap_distance = rule.thermal_relief_constraint.gap_distance
        ce.thermal_relief.spoke_width = rule.thermal_relief_constraint.spoke_width
        ce.thermal_relief.num_spokes = rule.thermal_relief_constraint.num_spokes


def translate_design_rule(
    rule: DesignConstraint,
    into_design: dpb2.DesignV1,
    path: RefPath,
) -> None:
    into = into_design.design_rules.add()
    if rule.name is not None:
        into.name = rule.name
    else:
        into.name = pathstring(path)
    into.priority = rule.priority

    if isinstance(rule, UnaryDesignConstraint):
        translate_unary_design_rule(rule, into)
    elif isinstance(rule, BinaryDesignConstraint):
        translate_binary_design_rule(rule, into)
    else:
        raise TypeError(f"Unhandled design rule type {rule}")


def translate_trace_width(tw: TraceWidth, into: drpb2.TraceWidthEffect):
    """Translate a TraceWidth constraint to protobuf format."""
    into.width = tw.width


def translate_clearance(cl: Clearance, into: drpb2.ClearanceEffect):
    """Translate a Clearance constraint to protobuf format."""
    into.clearance = cl.clearance


def translate_thermal_relief(tr: ThermalRelief, into: drpb2.ThermalReliefEffect):
    """Translate a ThermalRelief constraint to protobuf format."""
    into.gap_distance = tr.gap_distance
    into.spoke_width = tr.spoke_width
    into.num_spokes = tr.num_spokes


def translate_tag(tag: Tag, into: drpb2.Tag) -> None:
    """Translate a Tag to a protobuf Tag message."""
    # Handle predefined tags
    if isinstance(tag, OnLayer):
        translate_layer_index(tag.index, into.builtin.layer.layer)
    elif isinstance(tag, BuiltinTag):
        into.builtin.object.type = translate_builtin_tag(tag)
    else:
        translate_user_tag(tag, into.user)


def translate_user_tag(tag: Tag, into: drpb2.UserTag) -> None:
    """Translate a UserTag to a protobuf UserTag message."""

    def fqname(cls: type[Tag]) -> str:
        return f"{cls.__module__}.{cls.__qualname__}"

    # Get fully qualified name using module and qualname
    into.name = fqname(tag.__class__)
    for parent in tag.__class__.__bases__:
        if issubclass(parent, Tag) and parent is not Tag:
            into.parents.append(fqname(parent))


def translate_bool_expr(expr: BoolExpr, into: drpb2.BoolExpr) -> None:
    """Translate a BoolExpr to a protobuf BoolExpr message."""
    if isinstance(expr, TrueExpr):
        into.true_expr.SetInParent()
    elif isinstance(expr, AtomExpr):
        translate_tag(expr.atom, into.atom_expr.atom)
    elif isinstance(expr, NotExpr):
        translate_bool_expr(expr.expr, into.not_expr.expr)
    elif isinstance(expr, OrExpr):
        translate_bool_expr(expr.left, into.or_expr.left)
        translate_bool_expr(expr.right, into.or_expr.right)
    elif isinstance(expr, AndExpr):
        translate_bool_expr(expr.left, into.and_expr.left)
        translate_bool_expr(expr.right, into.and_expr.right)
    else:
        raise Exception(f"Unknown BoolExpr type: {type(expr)}")
