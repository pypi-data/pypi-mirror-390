from pathlib import Path

import numpy as np
from h5netcdf import File

example_dir = Path(__file__).absolute().parent

# This is just an empty file! Nothing to see here
with File(example_dir.joinpath("empty.nc"), "w") as f:
    pass

# Generate two files with different global attributes
with File(example_dir.joinpath("attributes_v1.nc"), "w") as f:
    f.attrs["attrib_str"] = "this is just some text"
    f.attrs["attrib_const"] = np.array([1, 3, 3.14, 14.13])

with File(example_dir.joinpath("attributes_v2.nc"), "w") as f:
    f.attrs["attrib_str"] = "this is just some text"
    f.attrs["attrib_pi"] = 3.1415
    f.attrs["attrib_const"] = np.array([1, 2, 3.14, 13.14])

# Two files with 1d variables of equal dimensions and random values
# except for some starting values which are 1 in both cases
with File(example_dir.joinpath("var1d_v1.nc"), "w") as f:
    f.dimensions = {"x": 10}
    v = f.create_variable(
        "v", ("x",), float, data=np.array([1, 1, 1, *np.random.random(7)])
    )

with File(example_dir.joinpath("var1d_v2.nc"), "w") as f:
    f.dimensions = {"x": 10}
    v = f.create_variable(
        "v", ("x",), float, data=np.array([1, 1, 1, *np.random.random(7)])
    )

# Two files with 2d variables of eqeual dimensions and random values
# except for some values which are 1 in both cases
with File(example_dir.joinpath("var2d_v1.nc"), "w") as f:
    f.dimensions = {"x": 5, "y": 5}
    v = f.create_variable("v", ("x", "y"), float, data=np.random.random((5, 5)))
    v[:, 1:4] = np.ones((5, 3))

with File(example_dir.joinpath("var2d_v2.nc"), "w") as f:
    f.dimensions = {"x": 5, "y": 5}
    v = f.create_variable("v", ("x", "y"), float, data=np.random.random((5, 5)))
    v[:, 1:4] = np.ones((5, 3))

# Two files with completely different variables
with File(example_dir.joinpath("var_mix_v1.nc"), "w") as f:
    f.dimensions = {"x": 5, "y": 5}
    a = f.create_variable("a", ("x",), float)
    b = f.create_variable("b", ("x", "y"), float)

with File(example_dir.joinpath("var_mix_v2.nc"), "w") as f:
    f.dimensions = {"x": 5, "y": 5}
    k = f.create_variable("k", ("x",), float)
    l = f.create_variable("l", ("x", "y"), float)

# Two files with being identical to the other one, but after some time
with File(example_dir.joinpath("time_full.nc"), "w") as f:
    f.dimensions = {"time": 10, "x": 2}
    a = f.create_variable("a", ("time", "x"), float)

# This file covers second half of the time_full.nc file
with File(example_dir.joinpath("time_half.nc"), "w") as f:
    f.dimensions = {"time": 5, "x": 2}
    a = f.create_variable("a", ("time", "x"), float)

# Create variables in groups
with File(example_dir.joinpath("groups_v1.nc"), "w") as f:
    f.dimensions = {"x": 10}
    a = f.create_variable("a", ("x",), float)
    b = f.create_variable("/container1/b", ("x",), float)
    c = f.create_variable("/container2/nested/c", ("x",), float)
    a[:] = np.random.random(10)
    b[:] = np.random.random(10)
    c[:] = np.random.random(10)

with File(example_dir.joinpath("groups_v2.nc"), "w") as f:
    f.dimensions = {"x": 10}
    a = f.create_variable("a", ("x",), float)
    b = f.create_variable("/container1/b", ("x",), float)
    c = f.create_variable("/container2/nested/c", ("x",), float)
    a[:] = np.random.random(10)
    b[:] = np.random.random(10)
    c[:] = np.random.random(10)

# Create files with different datatypes
with File(example_dir.joinpath("dtype_float64.nc"), "w") as f:
    f.dimensions = {"x": 10}
    # float64 will be converted to float in NetCDF
    a = f.create_variable("a", ("x",), np.float64)
    a[:] = np.random.random(10)

with File(example_dir.joinpath("dtype_float16.nc"), "w") as f:
    f.dimensions = {"x": 10}
    # float16 will be converted to float in NetCDF
    a = f.create_variable("a", ("x",), np.float16)
    a[:] = np.random.random(10)
