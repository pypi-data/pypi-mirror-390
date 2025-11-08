from ipsl_ncdiff.diff import diff
from ipsl_ncdiff.frontend.auto import open_dataset


def _test_equal_netcdf(filename):
    with open_dataset(f"tests/example_data/{filename}.nc") as f:
        assert not diff(f, f)


def test_attributes():
    _test_equal_netcdf("attributes_v1")
    _test_equal_netcdf("attributes_v2")


def test_empty_nc():
    _test_equal_netcdf("empty")


def test_groups():
    _test_equal_netcdf("groups_v1")
    _test_equal_netcdf("groups_v2")


def test_time():
    _test_equal_netcdf("time_full")
    _test_equal_netcdf("time_half")


def test_var1d():
    _test_equal_netcdf("var1d_v1")
    _test_equal_netcdf("var1d_v2")


def test_var2d():
    _test_equal_netcdf("var2d_v1")
    _test_equal_netcdf("var2d_v2")


def test_var_mix():
    _test_equal_netcdf("var_mix_v1")
    _test_equal_netcdf("var_mix_v2")
