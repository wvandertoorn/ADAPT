"""
ADAPT - Adapter Detection and Processing Tool

Copyright (c) 2023 Wiep K. van der Toorn (w.vandertoorn@fu-berlin.de)

"""

import os
import shutil

from adapt.io import remove_reads_from_fast5

from ont_fast5_api.fast5_interface import get_fast5_file

test_data = os.path.join(os.path.dirname(__file__), "data")


def test_remove_reads_from_fast5_single():
    f5path = os.path.join(test_data, "read0.fast5")
    f5path_trim = f5path + ".tmp"
    shutil.copy(f5path, f5path_trim)

    read_id = None
    with get_fast5_file(f5path_trim, mode="a") as f5:
        read = next(f5.get_reads())
        read_id = read.read_id

    # should remove whole file
    remove_reads_from_fast5(f5path_trim, [read_id])
    assert not os.path.isfile(f5path_trim)


def test_remove_reads_from_fast5_multi():
    f5path = os.path.join(test_data, "batch0.fast5")
    f5path_trim = f5path + ".tmp"
    shutil.copy(f5path, f5path_trim)

    read_ids = []
    with get_fast5_file(f5path_trim, mode="r") as f5:
        for read in f5.get_reads():
            read_ids.append(read.read_id)

    assert len(read_ids) == 5

    remove_reads_from_fast5(f5path_trim, read_ids[:3])

    remaining_read_ids = []
    with get_fast5_file(f5path_trim, mode="a") as f5:
        for read in f5.get_reads():
            remaining_read_ids.append(read.read_id)

    assert len(read_ids) - len(remaining_read_ids) == 3

    # should remove whole file
    remove_reads_from_fast5(f5path_trim, remaining_read_ids)
    assert not os.path.isfile(f5path_trim)
