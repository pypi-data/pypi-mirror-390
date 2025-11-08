from dataclasses import dataclass, field
from typing import Any


@dataclass
class GlobalAttributeReport:
    """Report of global attribute differences"""

    new_left: list[str] = field(default_factory=list)
    new_right: list[str] = field(default_factory=list)
    not_eq: list[tuple[str, Any, Any]] = field(default_factory=list)

    def __bool__(self):
        return bool(self.new_left) or bool(self.new_right) or bool(self.not_eq)


@dataclass
class NewVariables:
    """Totally new variables"""

    new_left: list[str] = field(default_factory=list)
    new_right: list[str] = field(default_factory=list)

    def __bool__(self):
        return bool(self.new_left) or bool(self.new_right)


@dataclass
class VariableReport:
    name: str
    compression: tuple | None = None
    datatype: tuple | None = None
    dimension: tuple | None = None
    shape: tuple | None = None
    value: dict | None = None

    def __bool__(self) -> bool:
        different_values: bool = self.value is not None and not self.value["is_close"]
        return (
            bool(self.compression)
            or bool(self.datatype)
            or bool(self.dimension)
            or bool(self.shape)
            or different_values
        )


@dataclass
class DiffReport:
    # Global attributes on the file level
    global_attributes: GlobalAttributeReport = field(
        default_factory=GlobalAttributeReport
    )
    # Variables which are present in one file, but not the other
    new_variables: NewVariables = field(default_factory=NewVariables)
    # Differences between variables of the same name
    variables: list[VariableReport] = field(default_factory=list)

    def __bool__(self):
        return (
            bool(self.global_attributes)
            or bool(self.new_variables)
            or any(self.variables)
        )
