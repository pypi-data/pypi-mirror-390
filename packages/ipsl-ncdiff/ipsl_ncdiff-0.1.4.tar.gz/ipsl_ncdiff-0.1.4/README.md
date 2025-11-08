# IPSL-ncdiff

Easy comparison of NetCDF files.
Similar to [nccmp](https://gitlab.com/remikz/nccmp), [recursive_diff/ncdiff](https://github.com/crusaderky/recursive_diff/blob/main/doc/ncdiff.rst), and [ncompare](https://github.com/nasa/ncompare), more tools: https://lguez.github.io/Max_diff_nc/other_utils/!

## Why another tool?

Each tool for NetCDF comparison that we have analysed, has lacked in some feature which would be appreciated by us: - No structured output (e.g. json, csv, html): nccmp, ncompare - No comparison of partial files (e.g. only 5 days out of 1 year): all tools - No multi-backend (e.g. handling various formats)

| Feature                            | IPSL-ncdiff | nccmp | recursive_diff/ncdiff | ncompare | cdo diff | nco diff |
| ---------------------------------- | ----------- | ----- | --------------------- | -------- | -------- | -------- |
| Time-aware comparison              |             |       |                       |          |          |          |
| Partial file comparison            |             |       |                       |          |          |          |
| Per-variable tolerance             |             |       |                       |          |          |          |
| Various NetCDF versions            |             |       |                       |          |          |          |
| Structured output (e.g. json, csv) |             |       |                       |          |          |          |

- It semes that ncdiff doesn't support groups/nested variables

## How it works?

ipsl-ncdiff compares two NetCDF files on the dataset and variable level.
Two dataset might have dissimilar attributes, dimension list or variable list.

On the variable level, two variables might have dissimilar attributes, compression settings, datatype, dimension, shape or value.

The tool tries to analyse both files and display all found differences!

Furthermore, ipsl-ncdiff provides several options changing the comparison and allowing, e.g. to compare variables of different name or shape.

### Performed comparisons

- Dataset (file) level
  - Global attributes (new or different): `diff_global_attributes`
  - New variables (left or right side): `diff_new_variables`
- Variable level: `diff_variable`
  - Attributes (not implemented)
  - Dimensions
  - Shape
  - Datatype
  - Values
  - Compression

### Other operations

- Alignment of dimensions (when dataset is a subset of bigger file, we can still compare it by matching specified dimensions - usually it's time)

## Usage

### Installation

ipsl-ncdiff is hosted on official PyPI Python package repository.
The installation is as easy as typing:

```shell
pip install ipsl-ncdiff
```

Also, you can install the latest version directly from the repository:

```shell

```

Furthermore, generic linux binary is available here:

```wget

```

### Using as a tool

```shell
ipsl-ncdiff <NETCDF1> <NETCDF2>
```

### Using as a library

In your Python code:

```python
from ipsl_ncdiff.diff import diff, diff_files, diff_datasets

are_equal, differences = diff(Path("<NETCDF1>"), Path("<NETCDF2>"))
```
