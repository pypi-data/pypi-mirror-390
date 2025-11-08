from dataclasses import dataclass, field
from pathlib import PurePath
from typing import Iterable

from ipsl_ncdiff.model.dimension import Dimension
from ipsl_ncdiff.model.variable import Variable


@dataclass
class NcDataset:
    """NetCDF dataset representation of a single file"""

    attributes: dict = field(default_factory=dict)
    variables: dict[str, Variable] = field(default_factory=dict)
    dimensions: dict[str, Dimension] = field(default_factory=dict)


def split_variable_name(name: str) -> tuple[str, str]:
    """Split full variable name `[/a/b/]c` into the group `/a/b` and the variable `c`"""
    p = PurePath(name)
    return str(p.parent), str(p.name)


def canonical_variable_name(names: str | Iterable[str]) -> str | Iterable[str]:
    """
    Convert variable name(s) to their canonical form:
        a -> /a
        /a -> /a
        /a/b -> /a/b
    """

    def canonicalize(name: str) -> str:
        return name if name.startswith("/") else "/" + name

    if isinstance(names, str):
        return canonicalize(names)
    return [canonicalize(item) for item in names]
