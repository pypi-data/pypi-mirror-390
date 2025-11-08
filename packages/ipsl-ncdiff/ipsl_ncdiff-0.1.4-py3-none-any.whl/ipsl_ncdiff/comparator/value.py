"""
Value comparator analyzes if two variables have the same values.
"""

from ipsl_ncdiff.tolerance import DEFAULT_ATOL, DEFAULT_EQUAL_NAN, DEFAULT_RTOL
import numpy as np


def compare_equal_shape_arrays(
    left: np.ndarray,
    right: np.ndarray,
    rtol: float = DEFAULT_RTOL,
    atol: float = DEFAULT_ATOL,
    equal_nan: bool = DEFAULT_EQUAL_NAN,
) -> dict:
    """
    Compare two NumPy arrays by enumerating their differences and properties,
    i.e. min/max/mean/median/sum/std/var of differences, size, shape,
    and counts of NaNs.

    TODO: add absolute and relative tolerance equality comparison
    """
    assert left.shape == right.shape, "Shapes of left and right arrays are not equal"
    # print(left)
    # print(right)
    diff = left - right
    min_diff = np.nanmin(diff)
    max_diff = np.nanmax(diff)
    count_all = np.size(left)
    count_equal = np.sum(np.equal(left, right))
    return {
        "shape": list(left.shape),
        "count_all": count_all,
        "count_equal": count_equal,
        "count_not_equal": count_all - count_equal,
        "count_shared_nan": np.sum(np.logical_and(np.isnan(left), np.isnan(right))),
        "is_close": np.allclose(left, right, rtol=rtol, atol=atol, equal_nan=equal_nan),
        "min_diff": min_diff,
        "max_diff": max_diff,
        "mean_diff": np.nanmean(diff),
        "median_diff": np.nanmedian(diff),
        "abs_sum_diff": np.nansum(np.abs(diff)),
        "sum_diff": np.nansum(diff),
        "range_diff": max_diff - min_diff,
        "std_diff": np.nanstd(diff),
        "var_diff": np.nanvar(diff),
        "left": {
            "count_nan": np.sum(np.isnan(left)),
        },
        "right": {
            "count_nan": np.sum(np.isnan(right)),
        },
    }
