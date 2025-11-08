import logging as log
from collections import deque
from pathlib import Path

import h5netcdf as h5
import numpy as np

from ipsl_ncdiff.model.dataset import NcDataset
from ipsl_ncdiff.model.dimension import Dimension
from ipsl_ncdiff.model.variable import Variable


def list_variables(dataset: h5.File) -> list[str]:
    """
    List all dataset variables in their canonical form:
        * always starts with '/': /v
        * contains groups, if exist: /g1/g2/.../v
    """
    vars = []
    # Add top level variables and groups in their canonical form
    to_analyze = deque([f"/{item}" for item in dataset])
    while to_analyze:
        path = to_analyze.popleft()
        obj = dataset[path]
        if isinstance(obj, h5.Group):
            to_analyze.extend([f"{path}/{item}" for item in obj.variables])
            to_analyze.extend([f"{path}/{item}" for item in obj.groups])
        elif isinstance(obj, h5.Variable):
            # Append full canonical name directly from Variable class
            vars.append(obj.name)
    return vars


# TODO: this should go to the fronted I guess?
def load(filepath: Path) -> NcDataset:
    ds = NcDataset()
    with h5.File(filepath, "r") as file:
        # Collect dataset attributes
        attributes = {}
        for attr_key in file.attrs:
            attributes[attr_key] = file.attrs[attr_key]
        if attributes:
            ds.attributes = attributes
        # Fill dimensions
        ds.dimensions = _extract_dimensions(file)
        ds.variables = _extract_variables(file, ds.dimensions)
    return ds


def _extract_dimensions(dataset: h5.File) -> dict[str, Dimension]:
    """
    Extract dimensions from the NetCDF dataset while validating their correctness.
    """
    extracted = {}
    for name in dataset.dimensions:
        dimension = dataset.dimensions[name]
        # Link to a variable
        if name in dataset.variables:
            # Check if classical variable-dimensions (has only one dimension of the same name)
            variable = dataset.variables[name]
            if len(variable.dimensions) == 0:
                log.warning(
                    f"Skipping dimension {name} with a linked variable "
                    f"that has no dimensions"
                )
                continue
            elif len(variable.dimensions) > 1:
                log.warning(
                    f"Variable linked to the dimension {name} has many "
                    f"dimensions {variable.dimensions}. "
                    f"Only the first one will be used"
                )
            if name != variable.dimensions[0]:
                log.warning(
                    f"Skpping dimension {name} with a linked variable that has "
                    f"a dimension of different name: {variable.dimensions[0]}"
                )
                continue
            # Check if variable size is the same as the dimensions size
            values = variable[:]
            if dimension.size != values.size:
                # In this case, there is not good solution:
                #  1) Take all variable values
                #  2) Take only #size number of values
                #  3) Recreate values from the dimension size [0, 1, ..., size - 1]
                raise ValueError(
                    f"Variable linked to the dimension has different "
                    f"size than the dimension: {values.size} != {dimension.size}"
                )
        else:
            # In case of a dimension with only a size, the values become [0, 1, ..., size - 1]
            values = np.array(range(dimension.size))
        extracted[name] = Dimension(name, values, dimension.isunlimited())
    return extracted


def _extract_variables(
    dataset: h5.File, dimensions: dict[str, Dimension]
) -> dict[str, Variable]:
    """
    Extract variables from NetCDF datset with the use of already analysed dimensions.
    """
    extracted = {}
    # Easy lookup of dimensions
    for name in list_variables(dataset):
        variable = dataset[name]
        extracted[name] = Variable(
            name=name,
            values=variable[:],
            # Transform dimension name to an object: str -> Dimension()
            dimensions=[dimensions[dim] for dim in variable.dimensions],
        )
    return extracted
