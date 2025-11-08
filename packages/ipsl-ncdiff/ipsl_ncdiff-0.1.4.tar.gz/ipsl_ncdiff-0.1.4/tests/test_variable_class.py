import numpy as np
from numpy.testing import assert_equal

from ipsl_ncdiff.model.dimension import Dimension
from ipsl_ncdiff.model.variable import Variable


class TestVariableClass:
    def test_dimension_intersection(self):
        d1 = Dimension("x", np.arange(5))
        v1 = Variable("t", np.arange(5), [d1])
        assert_equal(v1[:], [0, 1, 2, 3, 4])
        d2 = Dimension("x", np.arange(3))
        i1 = v1.intersection(d2)
        assert i1 is not None
        assert_equal(i1[:], [0, 1, 2])

        d3 = Dimension("x", [5, 6, 7, 8])
        d4 = Dimension("x", [7, 8, 9])
        v2 = Variable("t", np.arange(4), [d3])
        i2 = v2.intersection(d4)
        assert i2 is not None
        assert_equal(i2[:], [2, 3])
