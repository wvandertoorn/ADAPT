"""
ADAPT - Adapter Detection and Processing Tool

Copyright (c) 2023 Wiep K. van der Toorn (w.vandertoorn@fu-berlin.de)

"""

import glob
import os
import sys
from functools import partial
from multiprocessing import Pool

import pandas as pd

from .detect import detect_adapter_in_read
from .extract import extract_adapter_from_read
from .io import copy_and_process_fast5_file, process_fast5_file, write_results_to_csv
from .parser import parser
from .trim import trim_adapter_from_read


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    args = parser.parse_args(args)

    os.makedirs(args.save_path, exist_ok=True)

    # parse files to process
    if args.fast5_subset_txt is not None:
        files_df = pd.read_csv(args.fast5_subset_txt, header=None, names=["filename"])
        files_df["src"] = files_df.filename.apply(
            lambda fname: os.path.join(args.input_path, fname)
        )

    elif args.fast5_subset is not None:
        files_df = pd.DataFrame(args.fast5_subset, columns=["filename"])
        files_df["src"] = files_df.filename.apply(
            lambda fname: os.path.join(args.input_path, fname)
        )
    else:
        flist_src = glob.glob(os.path.join(args.input_path, "*.fast5"))
        fnames_src = [os.path.basename(x) for x in flist_src]
        files_df = pd.DataFrame(dict(filename=fnames_src, src=flist_src))

    process_args = []
    process_call = lambda x: None

    # execute different modes
    if args.mode == "trim":
        trim_kwargs = {"buffer": args.trimming_buffer}

        files_df["dst"] = files_df.src.apply(
            lambda x: x.replace(args.input_path, args.save_path)
        )

        process_args = files_df[["src", "dst"]].values.tolist()
        process_call = partial(
            copy_and_process_fast5_file,
            process_fn=trim_adapter_from_read,
            process_kwargs=trim_kwargs,
        )
        mp_map_fn = lambda pool_obj: pool_obj.starmap

    elif args.mode == "detect":
        detect_kwargs = {
            "max_obs": args.max_obs,
            "min_obs_adapter": args.min_obs_adapter,
            "border_trim": args.border_trim,
        }

        process_args = files_df["src"].values.tolist()
        process_call = partial(
            process_fast5_file,
            mode="r",
            process_fn=detect_adapter_in_read,
            process_kwargs=detect_kwargs,
        )
        mp_map_fn = lambda pool_obj: pool_obj.map

    else:  # "extract"
        extract_kwargs = {
            "extract_buffer": args.extraction_buffer,
        }

        process_args = files_df["src"].values.tolist()
        process_call = partial(
            process_fast5_file,
            mode="r",
            process_fn=extract_adapter_from_read,
            process_kwargs=extract_kwargs,
        )
        mp_map_fn = lambda pool_obj: pool_obj.map

    if len(process_args) > 1:
        with Pool(args.j) as p:
            res = mp_map_fn(p)(
                process_call, process_args
            )  # list (files) of lists (processResults)

    elif len(process_args) == 1:
        if type(process_args[0]) == list:
            res = [process_call(*process_args[0])]
        else:
            res = [process_call(process_args[0])]
    else:
        raise ValueError(
            f"Provided `--input_path`={args.input_path} contains no fast5 files."
        )

    # save results
    write_results_to_csv(
        res,
        args.save_path,
        "detect",
        [args.save_path, args.input_path],
        args.global_output_csv,
    )

    if args.mode == "extract":
        write_results_to_csv(
            res,
            args.save_path,
            "extract",
            [args.save_path, args.input_path],
            args.global_output_csv,
        )


if __name__ == "__main__":
    main()
