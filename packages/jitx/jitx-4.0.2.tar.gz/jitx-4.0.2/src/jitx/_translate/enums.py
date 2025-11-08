from jitx.anchor import Anchor
from jitx.layerindex import Side

from jitx.paper import Paper
from jitx.constraints import BuiltinTag
import jitxcore._proto.enums_pb2 as epb2

from jitx.via import ViaType


def translate_side(side: Side):
    if side == Side.Top:
        return epb2.Side.TOP
    elif side == Side.Bottom:
        return epb2.Side.BOTTOM


def translate_anchor(anchor: Anchor):
    if anchor == Anchor.NW:
        return epb2.Anchor.NW
    elif anchor == Anchor.N:
        return epb2.Anchor.N
    elif anchor == Anchor.NE:
        return epb2.Anchor.NE
    elif anchor == Anchor.W:
        return epb2.Anchor.W
    elif anchor == Anchor.C:
        return epb2.Anchor.C
    elif anchor == Anchor.E:
        return epb2.Anchor.E
    elif anchor == Anchor.SW:
        return epb2.Anchor.SW
    elif anchor == Anchor.S:
        return epb2.Anchor.S
    elif anchor == Anchor.SE:
        return epb2.Anchor.SE


def translate_via_drill_type(viaType: ViaType):
    if viaType == ViaType.LaserDrill:
        return epb2.ViaDrillType.LASER_DRILL
    elif viaType == ViaType.MechanicalDrill:
        return epb2.ViaDrillType.MECHANICAL_DRILL


def translate_paper(paper: Paper):
    if paper == Paper.ISO_A0:
        return epb2.Paper.ISO_A0
    elif paper == Paper.ISO_A1:
        return epb2.Paper.ISO_A1
    elif paper == Paper.ISO_A2:
        return epb2.Paper.ISO_A2
    elif paper == Paper.ISO_A3:
        return epb2.Paper.ISO_A3
    elif paper == Paper.ISO_A4:
        return epb2.Paper.ISO_A4
    elif paper == Paper.ISO_A5:
        return epb2.Paper.ISO_A5
    elif paper == Paper.ANSI_A:
        return epb2.Paper.ANSI_A
    elif paper == Paper.ANSI_B:
        return epb2.Paper.ANSI_B
    elif paper == Paper.ANSI_C:
        return epb2.Paper.ANSI_C
    elif paper == Paper.ANSI_D:
        return epb2.Paper.ANSI_D
    elif paper == Paper.ANSI_E:
        return epb2.Paper.ANSI_E


def translate_builtin_tag(type: BuiltinTag):
    if type == BuiltinTag.IsCopper:
        return epb2.ObjectTagType.IsCopper
    elif type == BuiltinTag.IsTrace:
        return epb2.ObjectTagType.IsTrace
    elif type == BuiltinTag.IsPour:
        return epb2.ObjectTagType.IsPour
    elif type == BuiltinTag.IsVia:
        return epb2.ObjectTagType.IsVia
    elif type == BuiltinTag.IsPad:
        return epb2.ObjectTagType.IsPad
    elif type == BuiltinTag.IsBoardEdge:
        return epb2.ObjectTagType.IsBoardEdge
    elif type == BuiltinTag.IsThroughHole:
        return epb2.ObjectTagType.IsThroughHole
    elif type == BuiltinTag.IsNeckdown:
        return epb2.ObjectTagType.IsNeckdown
    elif type == BuiltinTag.IsHole:
        return epb2.ObjectTagType.IsHole
