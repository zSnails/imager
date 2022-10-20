from dataclasses import dataclass
from numpy import array
from typing import Optional


@dataclass
class RGB:
    R: int
    G: int
    B: int
    A: Optional[int] = None

    def increment(self, r, g, b, a=None):
        self.R += r
        self.G += g
        self.B += b

    def map(self, func):
        # TODO: un hard code this lmao
        attrs = ["R", "G", "B"]

        for attr in attrs:
            setattr(self, attr, round(self.__getattribute__(attr)))

    def __array__(self, dtype=None):
        # return ndarray(buffer=(self.R, self.G, self.B), shape=(1, 1, 1), dtype=int)
        return array([self.R, self.G, self.B])

    def __hash__(self):
        # NOTE: NEVER do this, this is probably the worst possible way of hashing something
        return int((((self.R << 8) | self.G) << 8) | self.B)
