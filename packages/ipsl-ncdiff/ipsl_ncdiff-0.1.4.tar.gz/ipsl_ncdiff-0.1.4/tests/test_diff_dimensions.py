from ipsl_ncdiff.diff import diff
from ipsl_ncdiff.frontend.auto import open_dataset


# TODO: finish comparison of dimmensions
def test_new_variable_dimension():
    with open_dataset(f"tests/example_data/var1d_v1.nc") as f1:
        with open_dataset(f"tests/example_data/var2d_v1.nc") as f2:
            diffs = diff(f1, f2)
            assert diffs
            v = diffs.variables[0]
            assert tuple(d.name for d in v.dimension[0]) == ("x", )
            assert tuple(d.name for d in v.dimension[1]) == ("x", "y")
