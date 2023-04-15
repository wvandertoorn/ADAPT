"""
ADAPT - Adapter Detection and Processing Tool

Copyright (c) 2023 Wiep K. van der Toorn (w.vandertoorn@fu-berlin.de)

"""

from ont_fast5_api.fast5_read import Fast5Read

from .detect import detect_adapter_in_read, detectResults


def slice_signal_in_read(read: Fast5Read, start: int = 0, stop: int = -1) -> None:
    """Modify the raw dataset group of a Fast5Read object.
    The raw data signal is changed to the slice signal[start:stop], the
    duration attribute is changed accordingly. 

    Parameters
    ----------
    read : Fast5Read
        The read to be modified. Should be writable and open
    start : int, optional
        Start of the slice, by default 0
    stop : int, optional
        Stop of the half-open interval slice. Value -1 indicates the signal end, by default -1
    """
    signal = read.get_raw_data(scale=False)
    attrs = dict(read.handle[read.raw_dataset_group_name].attrs)

    del read.handle[read.raw_dataset_group_name]

    slice_start = max(0, start)
    slice_stop = signal.size if stop == -1 else min(stop, signal.size)

    attrs["duration"] = slice_stop - slice_start
    read.add_raw_data(signal[slice_start:slice_stop], attrs)


def trim_adapter_from_read(read: Fast5Read, buffer: int = 100,) -> detectResults:

    """Detect and trim the adapter signal from a read.
    The raw signal dataset of the read is changed to the slice `signal[adapter_end - buffer :]`, the
    duration attribute of the raw data group is changed accordingly. 

    Parameters
    ----------
    read : Fast5Read
        The read to be modified. Should be writable and open.
    buffer : int, optional
        Trimming buffer, retain `buffer` number of DNA observation prior to the detected boundary, by default 0.
    """

    start, stop = detect_adapter_in_read(read)
    slice_signal_in_read(read, start=max(0, stop - buffer))

    return detectResults(start, stop)
