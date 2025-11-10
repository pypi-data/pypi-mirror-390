from dataclasses import dataclass
from typing import Union
import re

try:
    from icecream import ic # pyright: ignore[reportMissingImports]
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa

from enum import Enum, auto
class FigAction(Enum):
    INTERACT = auto()
    SAVE = auto()

cm = 1./2.54 

size_re= re.compile(r"(-?[\d\.]+)(\s*)([a-z]+)")
units = {"cm": 1./2.54, 
         "mm": 0.1/2.54,
         "in": 1.}
#%%

class Size(float):
    def __new__(cls, value: Union[float, str]):
        if isinstance(value, str):
            if value.isnumeric():
                value = float(value)
            else:
                m = size_re.match(value)
                if m is None: 
                    raise ValueError("Invalid size")
                val, _, unit = m.groups()
                value = float(val) * units[unit]
        return float.__new__(cls, value)
    def __init__(self, value: Union[float, str]):
        """Initialize a new size object. It represents sizes or positions in a
        SFigure object. It is initialized with a float (size in inches) or with
        a string (e.g. "3cm" or "300 mm")

        Args:
            value (Union[float, str]): Numeric value (size in inches) or a string for a
                size with units. Allowed units are "cm", "mm", "in".
        """
        self._init_as = str(value)
    def __repr__(self):
        return self._init_as
    __str__ = __repr__
    @classmethod
    def as_cm(cls, value: float):
        return cls(f"{round(value/cm, 3)}cm")

@dataclass(frozen=True)
class Point:
    x: Size
    y: Size
    def args(self):
        return self.x, self.y
