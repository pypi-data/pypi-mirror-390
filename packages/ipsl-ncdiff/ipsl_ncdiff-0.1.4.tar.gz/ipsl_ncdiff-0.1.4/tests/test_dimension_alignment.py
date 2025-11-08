from ipsl_ncdiff.diff import diff
from ipsl_ncdiff.frontend.auto import open_dataset


def test_without_dimension_alignment():
    with open_dataset("tests/example_data/time_full.nc") as f1:
        with open_dataset("tests/example_data/time_half.nc") as f2:
            diffs = diff(f1, f2)
            assert diffs
            assert not diffs.new_variables
            assert not diffs.global_attributes
            assert len(diffs.variables) == 1
            v = diffs.variables[0]
            assert v.shape == ((10, 2), (5, 2))


def test_with_dimension_alignment():
    with open_dataset("tests/example_data/time_full.nc") as f1:
        with open_dataset("tests/example_data/time_half.nc") as f2:
            diffs = diff(f1, f2, align_dimensions=["time"])
            assert not diffs


def test_with_dimension_alignment_the_same_dataset():
    with open_dataset("tests/example_data/time_full.nc") as f1:
        with open_dataset("tests/example_data/time_full.nc") as f2:
            diffs = diff(f1, f2, align_dimensions=["time"])
            assert not diffs
