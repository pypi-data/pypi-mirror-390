from __future__ import annotations

import numpy as np


class Dimension:
    """Dimension with values"""

    def __init__(
        self, name: str, values: np.ndarray | list | int, is_unlimited: bool = False
    ):
        """
        Construct a dimension object with given values or the dimensions size.
        If the dimension size is given, the values are in the range of [0, 1, ..., size - 1].
        """
        self.name = name
        self.values = np.arange(values) if isinstance(values, int) else np.array(values)
        self.is_unlimited = is_unlimited

    def intersection(self, other: Dimension, strict=False) -> Dimension:
        """
        Intersection of two dimensions.
        If dimensions have different name, then a new name, composed of them both, is constructed.
        Intersected dimensions is never unlimited.
        """
        if strict and self.name != other.name:
            raise ValueError(
                f"In strict intersection, names of intersected dimensions must be the same: {self.name} != {other.name}"
            )
        return Dimension(
            name=self.name if self.name == other.name else f"{self.name}_{other.name}",
            values=np.intersect1d(self.values, other.values),
            is_unlimited=False,
        )

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Dimension):
            return (
                self.name == other.name
                and self.size == other.size
                # Dimension values must be bit-to-bit equal
                and all(self.values == other.values)
                and self.is_unlimited == other.is_unlimited
            )
        else:
            return False

    def __and__(self, other: Dimension) -> Dimension:
        """Overloaded & opertor to the intersection method"""
        return self.intersection(other)

    def __rand__(self, other: Dimension) -> Dimension:
        """Overloaded & opertor to the intersection method"""
        return self.intersection(other)

    def isdisjoint(self, other: Dimension) -> bool:
        """Check if two dimensions don't intersect"""
        return self.intersection(other).size == 0

    def __str__(self):
        """Simplified string representation"""
        return f"dimension '{self.name}' of size {self.size}"

    def __repr__(self):
        """Detailed string representation with values"""
        return f"Dimension(name='{self.name}', shape={self.values.shape}, is_unlimited={self.is_unlimited})"

    @property
    def size(self):
        """Dimension size is the number of its values"""
        return self.values.size

    def __len__(self):
        return self.size

    def __getitem__(self, key):
        """Access dimension values"""
        return self.values[key]


def select_dimension(
    name: str, dimensions: list[Dimension]
) -> tuple[int, Dimension] | None:
    """Select the first dimension with the name"""
    for idx, dim in enumerate(dimensions):
        if dim.name == name:
            return idx, dim
    return None


if __name__ == "__main__":
    d = Dimension(name="ads", values=[1, 2, 3])
    print(str(d))
    print(repr(d))
    d1 = Dimension(name="ads", values=[1, 2, 3], is_unlimited=False)
    print(str(d1))
    print(repr(d1))
