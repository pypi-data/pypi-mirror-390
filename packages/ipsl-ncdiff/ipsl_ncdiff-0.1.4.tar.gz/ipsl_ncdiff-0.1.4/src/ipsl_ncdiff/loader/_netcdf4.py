import logging as log
from collections import deque
from pathlib import Path

import netCDF4 as nc4
import numpy as np

from ipsl_ncdiff.model.dataset import NcDataset
from ipsl_ncdiff.model.dimension import Dimension
from ipsl_ncdiff.model.variable import Variable


def collect_variables(dataset: nc4.Dataset) -> dict[str, nc4.Variable]:
    """
    Collect variables with their names in the canonical form:
        * always starts with '/': /v
        * contains groups, if exist: /g1/g2/.../v

    This function is quite similar to the _h5netcdf version, however,
    there are many differences, e.g. netcdf4 doesn't support global
    variable indexing, so `dataset[full_var_name]` will not work.
    """
    vars = {}
    # Add top level variables and groups in their canonical form
    to_analyze = deque([f"/{item}" for item in dataset.variables])
    to_analyze.extend([f"/{item}" for item in dataset.groups])
    while to_analyze:
        path = to_analyze.popleft()
        obj = dataset[path]
        if isinstance(obj, nc4.Group):
            to_analyze.extend([f"{path}/{item}" for item in obj.variables])
            to_analyze.extend([f"{path}/{item}" for item in obj.groups])
        elif isinstance(obj, nc4.Variable):
            # Append the full canonical name reconstructed from recursive path
            vars[path] = obj
    return vars


def load(filepath: Path) -> NcDataset:
    ds = NcDataset()
    with nc4.Dataset(filepath, "r") as dataset:
        # Collect dataset attributes
        attributes = {}
        for attr_key in dataset.ncattrs():
            attributes[attr_key] = getattr(dataset, attr_key)
        if attributes:
            ds.attributes = attributes
        # Fill dimensions
        extracted = {}
        for name in dataset.dimensions:
            dimension = dataset.dimensions[name]
            # Link to a variable
            if name in dataset.variables:
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
        ds.dimensions = extracted
        # ds.variables = _extract_variables(file, ds.dimensions)
        # ds.dimensions = _extract_dimensions(file)
        extracted = {}
        for name, variable in collect_variables(dataset).items():
            extracted[name] = Variable(
                name=name,
                values=variable[:],
                # Transform dimension name to an object: str -> Dimension()
                dimensions=[ds.dimensions[dim] for dim in variable.dimensions],
            )
        ds.variables = extracted
    return ds
