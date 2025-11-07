from dataclasses import dataclass
from enum import Enum
from jitx.property import Property


class AltiumSymbol(Enum):
    """
    Enum for different symbols that can be used in Altium.
    If this enum is assigned to a Symbol through an AltiumSymbolProperty, the symbol will
    be exported as the corresponding symbol in Altium.

    >>> class MyGroundSymbol(Symbol):
    ...     gnd = Pin(at=(0, 0), direction=Direction.Up)
    ...     vertical = Polyline(width=0.1, points=[(0, 0), (0, -1)])
    ...     horizontals = [
    ...         Polyline(width=0.1, points=[(-0.5, -1), (0.5, -1)])
    ...         Polyline(width=0.1, points=[(-0.3, -1.75), (0.3, -1.75)])
    ...         Polyline(width=0.1, points=[(-0.1, -1.5), (0.1, -1.5)])
    ...     ]
    ...     def __init__(self):
    ...         AltiumSymbolProperty(AltiumSymbol.PowerGndPower).assign(self)
    """

    PowerArrow = 0
    PowerCircle = 1
    PowerBar = 2
    PowerWave = 3
    PowerGndPower = 4
    PowerGndSignal = 5
    PowerGndEarth = 6
    GostPowerArrow = 7
    GostGndPower = 8
    GostGndEarth = 9
    GostBar = 10


@dataclass
class AltiumSymbolProperty(Property):
    """Property that can be assigned to a Symbol to set the corresponding symbol in Altium."""

    symbol: AltiumSymbol
