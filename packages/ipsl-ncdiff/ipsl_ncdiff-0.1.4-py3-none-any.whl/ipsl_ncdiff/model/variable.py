from __future__ import annotations

import numpy as np
from more_itertools import one, replace

from ipsl_ncdiff.model.dimension import Dimension


class Variable:
    def __init__(
        self,
        name: str,
        values: np.ndarray,
        dimensions: list[Dimension],
        compression: str | None = None,
        compression_opts: str | None = None,
    ):
        self.name = name
        self.values = values
        # When adding dimensions, make sure the value shape is correct
        self.dimensions = dimensions
        self.compression = compression
        self.compression_opts = compression_opts

    def __str__(self):
        return f"variable '{self.name}' of shape {self.shape} with dimensions: {self.dimensions}>"

    def __repr__(self):
        return f"Variable(name='{self.name}', shape={self.values.shape}, dtype={self.values.dtype}, dimensions={self.dimensions})"

    def __getitem__(self, key):
        return self.values[key]

    @property
    def size(self):
        return self.values.size

    @property
    def shape(self):
        return self.values.shape

    @property
    def dtype(self):
        return self.values.dtype

    def intersection(self, other: Dimension | Variable) -> Variable:
        """Align variable with a new dimension (usually, this means shrinking)"""
        # Variable-distance intersection (variable must have this dimension)
        if isinstance(other, Dimension):
            # Match other dimension to variable dimensions by name
            # This is an easy case, because we are acting on a single dimension only
            try:
                match = one([d for d in self.dimensions if d.name == other.name])
                # Find indices where dimension values intersect
                _, indices, _ = np.intersect1d(
                    match.values, other.values, return_indices=True
                )
                axis_index = self.dimensions.index(match)
                return Variable(
                    self.name,
                    np.take(self.values, indices=indices, axis=axis_index),
                    list(
                        replace(
                            self.dimensions,
                            lambda x: x.name == other.name,
                            [match & other],
                        )
                    ),
                )
            except ValueError:
                return self
        # Variable-variable intersection (both variables must have the same dimensions)
        elif isinstance(other, Variable):
            raise NotImplementedError(
                "Variable-variable intersection is not implemented"
            )

    def __and__(self, other: Variable | Dimension) -> Variable | None:
        return self.intersection(other)

    def __rand__(self, other: Variable | Dimension) -> Variable | None:
        return self.intersection(other)
