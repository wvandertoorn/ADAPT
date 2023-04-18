"""
ADAPT - Adapter Detection and Processing Tool

Copyright (c) 2023 Wiep K. van der Toorn (w.vandertoorn@fu-berlin.de)

"""

import os

from adapt.extract import extract_adapter_from_read

from ont_fast5_api.fast5_interface import get_fast5_file

test_data = os.path.join(os.path.dirname(__file__), "data")


def test_extract_adapter_multi():
    f5path = os.path.join(test_data, "batch0.fast5")

    with get_fast5_file(f5path, mode="a") as f5:
        read = next(f5.get_reads())
        res = extract_adapter_from_read(read)

    print(res)
    assert res.adapter_end != 0
    assert (
        res.adapter_signal.size
        == (res.adapter_end - res.adapter_start) + 2 * res.extract_buffer
    )


def test_extract_adapter_single():
    f5path = os.path.join(test_data, "read0.fast5")

    with get_fast5_file(f5path, mode="a") as f5:
        read = next(f5.get_reads())
        res = extract_adapter_from_read(read)

    assert res.adapter_end != 0
    assert (
        res.adapter_signal.size
        == (res.adapter_end - res.adapter_start) + 2 * res.extract_buffer
    )

    assert res.digitisation == 8192.0
    assert res.offset == 4.0
    assert res.pA_range == 1194.820068359375
