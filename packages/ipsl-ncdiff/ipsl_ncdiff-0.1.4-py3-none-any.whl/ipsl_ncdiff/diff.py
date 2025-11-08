from typing import Any, Iterable

import numpy as np

from ipsl_ncdiff.comparator.value import compare_equal_shape_arrays
from ipsl_ncdiff.model.dataset import NcDataset, canonical_variable_name
from ipsl_ncdiff.model.diff import (
    DiffReport,
    GlobalAttributeReport,
    NewVariables,
    VariableReport,
)
from ipsl_ncdiff.model.variable import Variable
from ipsl_ncdiff.tolerance import (
    DEFAULT_ATOL,
    DEFAULT_EQUAL_NAN,
    DEFAULT_RTOL,
    ToleranceDict,
)
from ipsl_ncdiff.transformation import align_variables


def diff(
    ds1,
    ds2,
    exclude_variables=None,
    skip_attributes=False,  # True or a list of attributes to skip
    skip_new_variables=False,
    skip_dimension_variables=True,
    # TODO: align any dimension by name?
    # align_dimensions=False,  # bool or a list of dimensions to align
    align_dimensions=None,
    tolerances: ToleranceDict | None = None,
) -> DiffReport:
    """
    Main comparison function. Call this one in your code
    """
    diff_report = DiffReport()

    # 0. TODO: add check of file format (HDF5, CDF, NetCDF4-classic etc.)
    # Compare attributes
    if isinstance(skip_attributes, list) or (
        isinstance(skip_attributes, bool) and not skip_attributes
    ):
        diff_report.global_attributes = diff_global_attributes(
            ds1, ds2, skip_attributes=skip_attributes
        )

    # 2. Check if variables are the same in both datasets
    vars1, vars2 = set(ds1.variables.keys()), set(ds2.variables.keys())
    # TODO: skip_variables should take into consideration included/excluded variables
    if not skip_new_variables:
        diff_report.new_variables = diff_new_variables(ds1, ds2)
    if exclude_variables is None:
        exclude_variables = []
    # Normalize variable names (add / if missing)
    else:
        exclude_variables = canonical_variable_name(exclude_variables)
    # Don't analyse variables which represent dimensions
    if skip_dimension_variables:
        dims_to_skip = set(ds1.dimensions).union(ds2.dimensions)
        exclude_variables.extend(dims_to_skip)

    # 3. Compare common variables minus the excluded variables
    common_vars = vars1.intersection(vars2).difference(exclude_variables)
    for v in sorted(common_vars):
        v1, v2 = ds1.variables[v], ds2.variables[v]
        # Time-alignment needs to be done once per each variable
        if align_dimensions:
            if vars := align_variables(v1, v2, align_dimensions[0]):
                v1, v2 = vars

        tol = tolerances[v] if tolerances is not None else []
        if vd := diff_variable(v1, v2, *tol):
            diff_report.variables.append(vd)

    return diff_report


def compare_keys(left_keys, right_keys) -> tuple[set, set, set]:
    """
    Compare two sets of keys by finding (in order):
        * new keys on the left side
        * keys common the left and the right sides
        * new keys on the right side
    """
    return (
        left_keys.difference(right_keys),  # Only left keys
        left_keys.intersection(right_keys),  # Common keys
        right_keys.difference(left_keys),  # Only right keys
    )


def equal_values(left_value, right_value) -> bool:
    if isinstance(left_value, (list, tuple, np.ndarray)):
        left_value = np.array(left_value)
    if isinstance(right_value, (list, tuple, np.ndarray)):
        right_value = np.array(right_value)
    if isinstance(left_value, np.ndarray) and isinstance(right_value, np.ndarray):
        return np.array_equal(left_value, right_value)
    if isinstance(left_value, np.ndarray) or isinstance(right_value, np.ndarray):
        return False
    return left_value == right_value


def diff_global_attributes(
    left_ds: NcDataset,
    right_ds: NcDataset,
    skip_attributes: Iterable[str] | None = None,
) -> GlobalAttributeReport:
    """
    Find differences in global attributes of two datasets. Possible results:
        - One dataset have new attribute (DiffType.GLOBAL_ATTRIBUTE_NEW)
        - Value of common attribute are different (DiffType.GLOBAL_ATTRIBUTE_NOT_EQ)

    Result: {
        "new_left": [],
        "new_right": [],
        "not_eq": [("X", left_val, right_val)]
    """
    skip_attributes = skip_attributes or []

    # Prepare attributes keys by converting them to sets
    left_attributes = set(left_ds.attributes.keys())
    right_attributes = set(right_ds.attributes.keys())

    # Find new attributes
    left_attributes, common_keys, right_attributes = compare_keys(
        # Skip attributes if needed
        left_keys=left_attributes.difference(skip_attributes),
        right_keys=right_attributes.difference(skip_attributes),
    )
    # Find unequal attributes
    not_eq = []
    for name in common_keys:
        left_val, right_val = left_ds.attributes[name], right_ds.attributes[name]

        if not equal_values(left_val, right_val):
            not_eq.append((name, left_val, right_val))

    return GlobalAttributeReport(list(left_attributes), list(right_attributes), not_eq)


def diff_new_variables(
    left_ds: NcDataset, right_ds: NcDataset, skip_variables: Iterable[str] | None = None
) -> Any:
    skip_variables = skip_variables or []
    vars1 = set(left_ds.variables.keys()).difference(skip_variables)
    vars2 = set(right_ds.variables.keys()).difference(skip_variables)
    left_vars = vars1.difference(vars2)
    right_vars = vars2.difference(vars1)
    return NewVariables(new_left=list(left_vars), new_right=list(right_vars))


def diff_variable(
    left_var: Variable,
    right_var: Variable,
    # TODO: always perform comparison with tolerance?
    rtol: float = DEFAULT_RTOL,
    atol: float = DEFAULT_ATOL,
    equal_nan: bool = DEFAULT_EQUAL_NAN,
) -> VariableReport:
    """
    Find differences between corresponding variables (e.g. shape, values)
    """
    assert left_var.name == right_var.name, (
        "Compared variables must have the same name"
    )  # TODO: at least for the moment!
    report = VariableReport(name=left_var.name)
    # Compare datatypes
    dtype1, dtype2 = left_var.dtype, right_var.dtype
    if dtype1 != dtype2:
        report.datatype = (dtype1, dtype2)
    # Compare dimensions
    dims1, dims2 = left_var.dimensions, right_var.dimensions
    if dims1 != dims2:
        report.dimension = (dims1, dims2)
    # Compare shape
    shape1, shape2 = left_var.shape, right_var.shape
    if shape1 != shape2:
        report.shape = (shape1, shape2)
    # Compare values when shapes are equal
    else:
        array1, array2 = left_var.values, right_var.values
        report.value = compare_equal_shape_arrays(
            array1, array2, rtol=rtol, atol=atol, equal_nan=equal_nan
        )
    # Compare compression
    comp1 = (left_var.compression, left_var.compression_opts)
    comp2 = (right_var.compression, right_var.compression_opts)
    if comp1 != comp2:
        report.compression = (comp1, comp2)
    return report
