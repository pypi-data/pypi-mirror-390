"""
Common port bundles
===================

This module provides commonly used port bundle types for typical electronic
interfaces like power, differential pairs, GPIO, and communication lanes.

Note that due to its tight integration in the net system, the
:py:class:`~jitx.net.DiffPair` bundle is defined in the :py:mod:`jitx.net`
module.
"""

from __future__ import annotations
from jitx.net import DiffPair, Port


class DualPair(Port):
    """
    Two Differential Pairs - a Dual Pair

    The dual pair is useful for cases where there is a pass-through
    differential pair through a component - for example, an ESD
    diode protection device like a TI, TPD4E05.

    No directionality is implied by this bundle.
    """

    A = DiffPair()
    B = DiffPair()


class LanePair(Port):
    """
    Two Differential Pairs - a Lane Pair

    It is very common in communication standards to have a
    TX diff-pair and an RX diff-pair with
    The lane pair is a directed differential pair lane
    """

    TX = DiffPair()
    "Transmit Pair"
    RX = DiffPair()
    "Receive Pair"


class PassThrough(Port):
    """
    Pass Through Bundle Type

    This provides a mechanism of describing a pass through
    connection through a device, primarily for implementing
    the ``provide/require`` statements.

    Example:

    ESD Protection devices often have two pins that are intended
    to be shorted together to provide an ESD protected trace with
    minimal effect on the impedance of the trace.
    """

    A = Port()
    B = Port()


class Power(Port):
    """
    Power Bundle define a DC power source

    The power bundle defines the two reference voltages
    of a DC power source.
    """

    Vp = Port()
    "Positive Voltage of the Power Bundle"
    Vn = Port()
    "Negative Voltage of the Power Bundle"


class Polarized(Port):
    """
    Standardized polarized bundle for common naming and ordering of polarized
    cathode and anode ports.
    """

    a = Port()
    "Anode port"
    c = Port()
    "Cathode port"


class GPIO(Port):
    """
    Common GPIO Interface Bundle
    """

    gpio = Port()
    "GPIO Pin"


class Timer(Port):
    """
    Timer Interface Bundle
    """

    timer = Port()
    "Timer Pin"


class ADC(Port):
    """
    Single-Ended ADC Interface Bundle
    """

    adc = Port()
    "ADC Pin"
