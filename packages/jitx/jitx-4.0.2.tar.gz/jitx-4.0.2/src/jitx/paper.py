"""
Paper size definitions
======================

This module provides standard paper size enumerations for the schematic.
"""

from enum import Enum


class Paper(Enum):
    """Standard paper sizes for schematic pages."""

    ISO_A0 = "ISO_A0"
    ISO_A1 = "ISO_A1"
    ISO_A2 = "ISO_A2"
    ISO_A3 = "ISO_A3"
    ISO_A4 = "ISO_A4"
    ISO_A5 = "ISO_A5"
    ANSI_A = "ANSI_A"
    ANSI_B = "ANSI_B"
    ANSI_C = "ANSI_C"
    ANSI_D = "ANSI_D"
    ANSI_E = "ANSI_E"
