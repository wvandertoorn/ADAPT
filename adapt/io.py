"""
ADAPT - Adapter Detection and Processing Tool

Copyright (c) 2023 Wiep K. van der Toorn (w.vandertoorn@fu-berlin.de)

"""

import os
import shutil
from typing import Callable, List

import pandas as pd
from ont_fast5_api.fast5_interface import get_fast5_file, is_multi_read

from .utils import processResults, detect_results_to_df, extract_results_to_df


def process_fast5_file(
    fast5_filepath: str,
    mode: str,
    process_fn: Callable,
    process_kwargs: dict = dict(),
) -> List[processResults]:

    results = []
    with get_fast5_file(fast5_filepath, mode=mode) as f5:
        for read in f5.get_reads():

            read_id = read.read_id
            processed = process_fn(read, **process_kwargs)
            results.append(processResults(fast5_filepath, read_id, processed))

    return results


def copy_and_process_fast5_file(
    fast5_filepath_src: str,
    fast5_filepath_dst: str,
    process_fn: Callable,
    mode: str = "a",
    process_kwargs: dict = dict(),
):

    shutil.copy(fast5_filepath_src, fast5_filepath_dst)
    return process_fast5_file(fast5_filepath_dst, mode, process_fn, process_kwargs)

def remove_reads_from_multi_fast5(multifast5_filepath: str, read_ids: List[str]) -> None:
    """Remove read entries from a multi fast5 file. 
    Removes multi fast5 file if all read entries are removed. 

    Parameters
    ----------
    multifast5_filepath : str
        Path to multi fast5 file.
    read_ids : List[str]
        List of read ids to be removed from file. This list should be ordered in the 
        same way as the read entries in the multifast5 file.
    """    
    _read_ids = read_ids.copy()
    _read_ids.reverse()

    with get_fast5_file(multifast5_filepath, mode="a") as f5:
        n_reads = 0

        read_handles = []
        for read in f5.get_reads():
            n_reads += 1

            try:
                if read.read_id == _read_ids[-1]:
                    read_handles.append(read.handle.name)
                    _read_ids.pop()

            except IndexError:  # read_ids list empty
                pass

        for read in read_handles:
            del f5.handle[read]

    if len(read_handles) == n_reads:
        os.remove(multifast5_filepath)

def remove_reads_from_fast5(fast5_filepath: str, read_ids: List[str]) -> None:
    """Remove read entries from a fast5 file. 
    If fast5 file is single fast5, the file is removed. For multi fast files,
    the file itself is removed if all read entries were removed. 

    Parameters
    ----------
    fast5_filepath : str
        Path to the fast5 file to remove reads from.
    read_ids : List[str]
        List of read ids to be removed from file. In case of a multi fast5 file, this list should be ordered in the 
        same way as the read entries in the multi fast5 file. 
        In case of a single fast5 file, this list should have length 1.

    Raises
    ------
    RuntimeError
        If `fast5_filepath` is a single fast5 file (as opposed to a multi fast5) and multiple read ids are provided.
    """    

    if is_multi_read(fast5_filepath):
        remove_reads_from_multi_fast5(fast5_filepath, read_ids)
    elif len(read_ids) > 1:
        raise RuntimeError("single fast5 files only contain one read!")
    else:
        os.remove(fast5_filepath)


def write_results_to_csv(
    process_results: List[List[processResults]],
    outdir: str,
    mode: str,
    remove_from_filepath=[],
    global_output=False,
):
    def _write_results_to_csv_mode_aux(mode: str):
        results_to_df_fn = {
            "detect": detect_results_to_df,
            "extract": extract_results_to_df,
        }[mode]
        outname = {
            "detect": "detected_adapter_boundaries",
            "extract": "extracted_adapters",
        }[mode]

        return results_to_df_fn, outname

    def _write_to_csv(
        results_df: pd.DataFrame,
        outdir: str,
        outname: str,
        remove_from_filepath=[],
        global_output=False,
    ):

        suffix = ""
        for rem_str in remove_from_filepath:
            results_df.rel_filepath = results_df.rel_filepath.apply(
                lambda x: x.replace(rem_str, "")
            )

        if not global_output:
            filename = os.path.splitext(
                os.path.basename(results_df.rel_filepath.unique().item())
            )[0]
            subdirname = os.path.basename(os.path.dirname(results_df.rel_filepath.unique().item()))
            if len (subdirname):
                filename = subdirname + "_" + filename
            suffix = "_" + filename

        results_df.to_csv(
            os.path.join(outdir, f"{outname}{suffix}.csv"), sep=";", index=False,
        )

    to_df_fn, outname = _write_results_to_csv_mode_aux(mode)

    results_dfs = [to_df_fn(r) for r in process_results]

    if global_output:
        results_df = pd.concat(results_dfs)
        _write_to_csv(results_df, outdir, outname, remove_from_filepath, global_output)
    else:
        for results_df in results_dfs:
            _write_to_csv(
                results_df, outdir, outname, remove_from_filepath, global_output
            )

