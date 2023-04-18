"""
ADAPT - Adapter Detection and Processing Tool

Copyright (c) 2023 Wiep K. van der Toorn (w.vandertoorn@fu-berlin.de)

"""


import os
import shutil
from ont_fast5_api.fast5_interface import get_fast5_file

from adapt.trim import slice_signal_in_read

test_data = os.path.join(os.path.dirname(__file__), "data")


def test_slice_signal_single():
    f5path = os.path.join(test_data, "read0.fast5")
    f5path_trim = f5path + ".tmp"
    shutil.copy(f5path, f5path_trim)

    with get_fast5_file(f5path_trim, mode="a") as f5:
        read = next(f5.get_reads())

        slice_signal_in_read(read, start=500, stop=1500)

        duration = read.handle[read.raw_dataset_group_name].attrs["duration"]

        assert read.get_raw_data().size == 1000
        assert duration == 1000

        os.remove(f5path_trim)


def test_slice_signal_multi():
    f5path = os.path.join(test_data, "batch0.fast5")
    f5path_trim = f5path + ".tmp"
    shutil.copy(f5path, f5path_trim)

    with get_fast5_file(f5path_trim, mode="a") as f5:
        read = next(f5.get_reads())

        slice_signal_in_read(read, start=500, stop=1500)

        duration = read.handle[read.raw_dataset_group_name].attrs["duration"]

        assert read.get_raw_data().size == 1000
        assert duration == 1000

        os.remove(f5path_trim)
