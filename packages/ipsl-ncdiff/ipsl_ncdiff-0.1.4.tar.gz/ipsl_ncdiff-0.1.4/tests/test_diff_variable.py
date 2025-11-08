from ipsl_ncdiff.diff import diff
from ipsl_ncdiff.frontend.auto import open_dataset


def test_diff_dtype():
    with open_dataset(f"tests/example_data/dtype_float16.nc") as f1:
        with open_dataset(f"tests/example_data/dtype_float64.nc") as f2:
            diffs = diff(f1, f2)
            assert diffs
            assert len(diffs.variables) == 1
            assert diffs.variables[0].datatype == ("float16", "float64")
            assert not diffs.global_attributes
            assert not diffs.new_variables


def test_variable_dimension():
    with open_dataset(f"tests/example_data/var1d_v1.nc") as f1:
        with open_dataset(f"tests/example_data/var2d_v1.nc") as f2:
            diffs = diff(f1, f2)
            assert diffs
            assert not diffs.new_variables
            assert not diffs.global_attributes
            assert len(diffs.variables) == 1
            v = diffs.variables[0]
            assert tuple(d.name for d in v.dimension[0]) == ("x",)
            assert tuple(d.name for d in v.dimension[1]) == ("x", "y")


def test_variable_shape():
    with open_dataset(f"tests/example_data/time_full.nc") as f1:
        with open_dataset(f"tests/example_data/time_half.nc") as f2:
            diffs = diff(f1, f2)
            assert diffs
            assert not diffs.new_variables
            assert not diffs.global_attributes
            assert len(diffs.variables) == 1
            v = diffs.variables[0]
            assert v.shape == ((10, 2), (5, 2))
