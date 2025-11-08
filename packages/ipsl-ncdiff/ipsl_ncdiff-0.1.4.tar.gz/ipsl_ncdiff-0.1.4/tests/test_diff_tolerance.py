from ipsl_ncdiff.diff import diff
from ipsl_ncdiff.frontend.auto import open_dataset
from ipsl_ncdiff.model.diff import VariableReport
from ipsl_ncdiff.tolerance import ToleranceDict


def test_tolerance():
    with open_dataset("tests/example_data/var1d_v1.nc") as f1:
        with open_dataset("tests/example_data/var1d_v2.nc") as f2:
            diffs = diff(f1, f2)
            assert diffs
            assert not diffs.global_attributes
            assert not diffs.new_variables
            assert len(diffs.variables) == 1
            v: VariableReport = diffs.variables[0]
            assert not v.value["is_close"]
            # Values in v1/v2 fiels are in the range [0.0, 1.0)
            # atol=1.0 is enough to for equality!
            tolerances = ToleranceDict(atol=1.0, rtol=0.0)
            diffs = diff(f1, f2, tolerances=tolerances)
            print(diffs)
            assert not diffs
            assert not diffs.global_attributes
            assert not diffs.new_variables
            assert len(diffs.variables) == 0
