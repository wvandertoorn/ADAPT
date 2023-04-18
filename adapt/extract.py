"""
ADAPT - Adapter Detection and Processing Tool

Copyright (c) 2023 Wiep K. van der Toorn (w.vandertoorn@fu-berlin.de)

"""


from ont_fast5_api.fast5_read import Fast5Read

from .detect import detect_adapter_in_read
from .utils import extractResults


def extract_signal_slice_from_read(
    read: Fast5Read,
    start: int,
    stop: int,
    extract_buffer: int = 0,
):
    """Extract a slice of signal from the raw signal attribute of a fast5 read.

    Parameters
    ----------
    read : Fast5Read
        The read to process.
    start : int
        Start of the slice to extract.
    stop : int
        End of the slice to extract.
    extract_buffer : int, optional
        Number of observation to include pre and post detected adapter, by default 0

    Returns
    -------
    np.ndarray
        Slice of signal
    """
    signal = read.get_raw_data(scale=False)
    slice_start = max(0, start - extract_buffer)
    slice_stop = min(signal.size, stop + extract_buffer)

    return signal[slice_start:slice_stop]


def extract_adapter_from_read(
    read: Fast5Read,
    extract_buffer: int = 100,
) -> extractResults:
    """Extract adapter signal from read entry.

    Parameters
    ----------
    read : Fast5Read
        The read to process
    extract_buffer : int, optional
        Number of observation to include pre and post detected adapter, by default 100

    Returns
    -------
    extractResults
        Wrapper class containing all relevant results
    """
    start, stop = detect_adapter_in_read(read)
    adapter_signal = extract_signal_slice_from_read(
        read, start, stop, extract_buffer=extract_buffer
    )

    channel_info = read.get_channel_info()

    return extractResults(
        adapter_start=start,
        adapter_end=stop,
        extract_buffer=extract_buffer,
        digitisation=channel_info["digitisation"],
        pA_range=channel_info["range"],
        offset=channel_info["offset"],
        adapter_signal=adapter_signal,
    )
