"""
ADAPT - Adapter Detection and Processing Tool

Copyright (c) 2023 Wiep K. van der Toorn (w.vandertoorn@fu-berlin.de)

"""


from typing import List
from collections import namedtuple

import pandas as pd


class detectResults(namedtuple("detectResults", ("adapter_start", "adapter_end",),)):
    """Adapter detection results.

    Parameters
    ----------
    adapter_start : int
        Adapter start coordinate in original, full-length signal data.
    adapter_end : int
        Adapter end coordinate in original, full-length signal data.

    """


class extractResults(
    namedtuple(
        "extractResults",
        (
            "adapter_start",
            "adapter_end",
            "extract_buffer",
            "digitisation",
            "pA_range",
            "offset",
            "adapter_signal",
        ),
    )
):
    """Adapter extraction results.

    Parameters
    ----------
    adapter_start : int
        Adapter start coordinate in original (full-length) signal data.
    adapter_end : int
        Adapter end coordinate in original (full-length) signal data.
    extract_buffer " int
        Buffer used during adapter extraction (extraction start is `max(0, adapter_start - buffer))`,
        extraction end is `min(signal_length, adapter_end + buffer)`. 
    digitisation : float 
        Signal digitisation as stored in read channel info
    pA_range : float 
        Signal range as stored in read channel info
    offset : float 
        Signal offset as stored in read channel info
    adapter_signal : np.ndarray
        Extracted adapter signal of length at most 
        `adapter_end` - `adapter_start` + 2* `extract_buffer`, can be shorter if 
        signal surrounding the adapter is less than the `extract_buffer`.  
        This can only happen is `extract_buffer` > `border_trim=500` used in detecting
        the adatper. Adapter signal is in np.int16 format, it can be scaled to pA values using 
        `np.array(pA_range/digitisation * (adapter_signal + offset), dtype=np.float32)`   

    """

class processResults(
    namedtuple("processResults", ("filepath", "read_id", "results",),)
):
    """Processed fast5 file results.

    Parameters
    ----------
    filepath : str
        Path of processed fast5 file.
    read_id : str
        Read id as stored in fast5 read entry.
    results : detectResults or extractResults
        Results object returned by the processing function.

    """
    
def detect_results_to_df(detect_results: List[processResults]) -> pd.DataFrame:
    """Transform list of adapter detection processing results to a pandas DataFrame format. 

    Parameters
    ----------
    detect_results : List[processResults]
        List of adapter detection processing results, see adapt.io.process_fast5_file .

    Returns
    -------
    pd.DataFrame
        Dataframe of adapter detection processing results.
    """    
    return pd.DataFrame(
        [
            (x.filepath, x.read_id, x.results.adapter_start, x.results.adapter_end)
            for x in detect_results
        ],
        columns=["rel_filepath", "read_id", "adapter_start", "adapter_end"],
    )


def extract_results_to_df(extract_results: List[processResults]) -> pd.DataFrame:
    """Transform list of adapter extraction processing results to a pandas DataFrame format. 

    Parameters
    ----------
    extract_results : List[processResults]
        List of adapter extraction processing results, see adapt.io.process_fast5_file .

    Returns
    -------
    pd.DataFrame
        Dataframe of adapter extraction processing results.
    """    
    df = pd.DataFrame(
        [
            (
                x.filepath,
                x.read_id,
                x.results.adapter_end > x.results.adapter_start,
                x.results.extract_buffer,
                x.results.digitisation,
                x.results.pA_range,
                x.results.offset,
                x.results.adapter_signal.tolist(),
            )
            for x in extract_results
        ],
        columns=[
            "rel_filepath",
            "read_id",
            "detected",
            "extraction_buffer",
            "digitisation",
            "range",
            "offset",
            "adapter_signal",
        ],
    )
    return df.loc[df.detected].drop(columns=["detected"])

