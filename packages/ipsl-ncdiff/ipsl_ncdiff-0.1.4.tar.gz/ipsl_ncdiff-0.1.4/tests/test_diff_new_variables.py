from ipsl_ncdiff.diff import diff
from ipsl_ncdiff.frontend.auto import open_dataset


def test_var1d_v1():
    with open_dataset(f"tests/example_data/empty.nc") as f1:
        with open_dataset(f"tests/example_data/var1d_v1.nc") as f2:
            diffs = diff(f1, f2)
            assert diffs
            assert not diffs.new_variables.new_left
            assert diffs.new_variables.new_right == ["/v"]
            assert not diffs.global_attributes
            assert len(diffs.variables) == 0


def test_var1d_v2():
    with open_dataset(f"tests/example_data/var1d_v2.nc") as f1:
        with open_dataset(f"tests/example_data/empty.nc") as f2:
            diffs = diff(f1, f2)
            assert diffs
            assert not diffs.new_variables.new_right
            assert diffs.new_variables.new_left == ["/v"]
            assert not diffs.global_attributes
            assert len(diffs.variables) == 0
