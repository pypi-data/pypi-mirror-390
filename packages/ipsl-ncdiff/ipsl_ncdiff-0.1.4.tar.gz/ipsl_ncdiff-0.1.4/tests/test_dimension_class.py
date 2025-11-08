import pytest

from ipsl_ncdiff.model.dimension import Dimension


class TestDimensionClass:
    def test_intersection(self):
        d1, d2, d3 = (
            Dimension("lat", 5, False),
            Dimension("lon", [3, 4, 5, 6], True),
            Dimension("lat", [-5, -4, -3, -2, -1, 0, 1], True),
        )
        d12 = d1 & d2
        assert isinstance(d12, Dimension)
        assert d12.size == 2
        assert d12.name == "lat_lon"
        assert not d12.is_unlimited

        # Check commutativity
        d21 = d2 & d1
        assert isinstance(d21, Dimension)
        assert d21.size == 2
        assert d21.name == "lon_lat"
        assert not d21.is_unlimited

        # Check disjointness
        assert not d1.isdisjoint(d2)
        assert not d1.isdisjoint(d3)
        assert d2.isdisjoint(d3)

        # Check empty intersections
        d23 = d2 & d3
        assert d23.name == "lon_lat"
        assert d23.size == 0
        # The result of intersection is always "limited" as it is finite
        assert not d23.is_unlimited

        d13 = d1 & d3
        assert d13.name == "lat"
        assert d13.size == 2

        # Test strict intersection
        d1.intersection(d3, strict=True)  # OK: the same names
        with pytest.raises(ValueError, match="intersected dimensions must be the same"):
            d1.intersection(d2, strict=True)  # Error!

    def test_values(self):
        d0 = Dimension("d", 0)
        assert d0.size == 0
        d1 = Dimension("d", 5)
        assert d1.size == 5
        assert (d1[:] == [0, 1, 2, 3, 4]).all()
