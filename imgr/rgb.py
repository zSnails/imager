from dataclasses import dataclass
from numpy import array
from typing import Optional


@dataclass
class RGB:
    R: int
    G: int
    B: int
    A: Optional[int] = 255

    def increment(self, r, g, b, a=None):
        self.R += r
        self.G += g
        self.B += b

    def map(self, func):
        attrs = ["R", "G", "B"]

        for attr in attrs:
            setattr(self, attr, func(self.__getattribute__(attr)))

    def __array__(self, dtype=None):
        return array([self.R, self.G, self.B])

    def __hash__(self):
        return hash(self.R + self.G + self.B)
