from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from h5py import is_hdf5

from ipsl_ncdiff.loader._h5netcdf import load as h5load
from ipsl_ncdiff.loader._netcdf4 import load as nc4load
from ipsl_ncdiff.model.dataset import NcDataset


@contextmanager
def open_dataset(filepath: str | Path) -> Iterator[NcDataset]:
    if is_hdf5(str(filepath)):
        yield h5load(Path(filepath))
    else:
        yield nc4load(Path(filepath))
