import inspect
from collections import namedtuple
from json import load as json_load
from pathlib import Path
from typing import Any, Callable

import numpy as np

ToleranceOpts = namedtuple("ToleranceOpts", ["rtol", "atol", "equal_nan"])


def get_default_arg_val(func: Callable, arg: str) -> Any:
    """
    Return default argument value of a function.
    URL: https://stackoverflow.com/a/12627202/1319478
    """
    return inspect.signature(func).parameters[arg].default


def value_or_default(value: Any | None, default_value: Any) -> Any:
    return value if value is not None else default_value


# Default tolerance options come from the numpy.allclose() argument values
DEFAULT_RTOL = get_default_arg_val(np.allclose, "rtol")
DEFAULT_ATOL = get_default_arg_val(np.allclose, "atol")
DEFAULT_EQUAL_NAN = get_default_arg_val(np.allclose, "equal_nan")


class ToleranceDict:
    """
    Mapping of default and per-variable tolerances used for value comparison.
    These values are primarly used by the numpy.isclose/allclose functions.

    If global default values are not provided, some defaults will be taken from
    the numpy.allclose().
    If per-variable default value are not provided, they will be
    taken from global default values.
    """

    def __init__(
        self,
        rtol: float | None = None,
        atol: float | None = None,
        equal_nan: bool | None = None,
    ) -> None:
        self.global_opts = ToleranceOpts(
            rtol=value_or_default(rtol, DEFAULT_RTOL),
            atol=value_or_default(atol, DEFAULT_ATOL),
            equal_nan=value_or_default(equal_nan, DEFAULT_EQUAL_NAN),
        )
        self.per_variable_tolerances: dict[str, ToleranceOpts] = {}

    def add(
        self,
        variable: str,
        rtol: float | None = None,
        atol: float | None = None,
        equal_nan: bool | None = None,
    ) -> None:
        """
        Add tolerance options for a given variable (including optional: rtol, atol, equal_nan).
        """
        self.per_variable_tolerances[variable] = ToleranceOpts(
            rtol=value_or_default(rtol, self.global_opts.rtol),
            atol=value_or_default(atol, self.global_opts.atol),
            equal_nan=value_or_default(equal_nan, self.global_opts.equal_nan),
        )

    def __getitem__(self, variable: str) -> ToleranceOpts:
        """
        Get tolerance options for a given variable.

        Note: this method never throws KeyError as normal dictionary does.
              If the item is not found, a default ToleranceOpts is returned instead.
        """
        return self.per_variable_tolerances.get(
            variable,
            ToleranceOpts(
                rtol=self.global_opts.rtol,
                atol=self.global_opts.atol,
                equal_nan=self.global_opts.equal_nan,
            ),
        )

    @staticmethod
    def from_file(filename: str | Path) -> "ToleranceDict":
        """
        Load tolerance options from a *.json file.
        """
        with open(filename, "r") as f:
            data = json_load(f)
            # Setup global/default tolerance options
            td = ToleranceDict(
                rtol=data.get("rtol", None),
                atol=data.get("atol", None),
                equal_nan=data.get("equal_nan", None),
            )
            # Setup per-variable tolerance options
            for var, opts in data.get("variables", {}).items():
                td.add(
                    var,
                    rtol=opts.get("rtol", None),
                    atol=opts.get("atol", None),
                    equal_nan=opts.get("equal_nan", None),
                )
            return td


if __name__ == "__main__":
    d1 = ToleranceDict.from_file("tests/example_data/tolerance.json")
    print(d1["V850"])
