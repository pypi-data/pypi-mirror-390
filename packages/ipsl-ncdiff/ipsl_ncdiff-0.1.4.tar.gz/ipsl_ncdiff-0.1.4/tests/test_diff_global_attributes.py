# test difference of attributes on the dataset and variable levels
from pathlib import Path

import numpy as np

from ipsl_ncdiff.diff import diff, diff_global_attributes
from ipsl_ncdiff.frontend.auto import open_dataset
from ipsl_ncdiff.model.diff import GlobalAttributeReport

example_dir = Path(__file__).absolute().parent.joinpath("example_data")


def _test_assertions(report: GlobalAttributeReport) -> None:
    assert not report.new_left
    assert report.new_right == ["attrib_pi"]
    assert len(report.not_eq) == 1
    name, left_val, right_val = report.not_eq[0]
    assert name == "attrib_const"
    assert (left_val == np.array([1.0, 3.0, 3.14, 14.13])).all()
    assert (right_val == np.array([1.0, 2.0, 3.14, 13.14])).all()


def test_main_diff():
    with open_dataset(example_dir.joinpath("attributes_v1.nc")) as f1:
        with open_dataset(example_dir.joinpath("attributes_v2.nc")) as f2:
            diff_report = diff(f1, f2)
            _test_assertions(diff_report.global_attributes)


def test_diff_global_attributes():
    with open_dataset(example_dir.joinpath("attributes_v1.nc")) as f1:
        with open_dataset(example_dir.joinpath("attributes_v2.nc")) as f2:
            _test_assertions(diff_global_attributes(f1, f2))
