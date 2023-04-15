"""
ADAPT - Adapter Detection and Processing Tool

Copyright (c) 2023 Wiep K. van der Toorn (w.vandertoorn@fu-berlin.de)

"""

import argparse
from argparse import RawTextHelpFormatter


class SubcommandHelpFormatter(argparse.RawDescriptionHelpFormatter):
    def _format_action(self, action):
        parts = super(SubcommandHelpFormatter, self)._format_action(action)
        if action.nargs == argparse.PARSER:
            parts = "\n".join(parts.split("\n")[1:])
        return parts


parser = argparse.ArgumentParser(
    prog="adapt",
    description="********** ADAPT *********\n"
    + "ADAPT stands for Adapter Detection and Processing Tool, it "
    + "is a software tool that detects the presence of DNA adapters in "
    + "dRNA-seq data, and offers two options for processing the identified "
    + "adapters. First, it can extract the adapter signal from the read, "
    + "allowing the researcher to analyze the adapter sequence. Second, it "
    + "can trim the adapter signal from the read to improve data quality and "
    + "increase the accuracy of downstream analyses. \n\n"
    + "Please refer to the help messages of the individual commands for more "
    + "info, e.g. `adapt detect --help`.",
    formatter_class=RawTextHelpFormatter,
)


parent_parser = argparse.ArgumentParser(add_help=False)

parent_parser.add_argument(
    "--input_path",
    type=str,
    required=True,
    help="Directory with fast5 files to process. Can be single fast5, multi fast5 or both.",
)
parent_parser.add_argument(
    "--save_path",
    type=str,
    required=True,
    help="Directory where output files will be saved. ",
)

subset_group = parent_parser.add_mutually_exclusive_group()

subset_group.add_argument(
    "--fast5_subset_txt",
    type=str,
    help="Path to txt file containing entries `XYZ.fast5` (one per line) describing "
    "a subset of the fast5 files present in `input_path`.",
)

subset_group.add_argument(
    "--fast5_subset",
    type=str,
    nargs="+",
    help="Filenames '`XYZ.fast5` ...' describing "
    "a subset of the fast5 files present in `input_path`.",
)

parent_parser.add_argument(
    "--j",
    type=int,
    default="24",
    help="Size of pool used for multiprocessing read files.",
)

parent_parser.add_argument(
    "--global_output_csv",
    action="store_true",
    help="Output csv's describing all processed files, instead of a csv per file. Use this option "
    "\nif the files you are processing are single fast5 files, rather than multi fast5 files. ",
)

subparsers = parser.add_subparsers(dest="mode", required=True)
parser_detect = subparsers.add_parser(
    "detect",
    parents=[parent_parser],
    description="Outputs detected_adapter_boundaries.csv files to `save_path`.",
)

parser_detect.add_argument(
    "--max_obs",
    type=int,
    default=40000,
    help="Look for adapter in first `max_obs` data points of the raw signal. Dafult value of 40000 taken from default params in Tombo.",
)
parser_detect.add_argument(
    "--min_obs_adapter",
    type=int,
    default=1000,
    help="Minimal length of the adapter signal, by default 1000",
)
parser_detect.add_argument(
    "--border_trim",
    type=int,
    default=500,
    help="Ignore outer `border_trim` data points, a boundary can be detected between `border_trim` and `max_obs`-`border_trim` observations, by default 500",
)

parser_trim = subparsers.add_parser(
    "trim",
    parents=[parent_parser],
    description="Detects the adapters and also outputs fast5 files to `save_path` for which the raw signal group only contains the RNA signal after the detected adapter sequence.",
)
parser_trim.add_argument(
    "--trimming_buffer",
    type=int,
    default=500,
    help="Trimming buffer, retain `trimming_buffer` number of DNA observation prior to the detected boundary, by default 500.",
)

parser_extract = subparsers.add_parser(
    "extract",
    parents=[parent_parser],
    description="Detects the adapters and also outputs extracted_adapters.csv to `save_path`.",
)

parser_extract.add_argument(
    "--extraction_buffer",
    type=int,
    default=100,
    help="Extraction buffer, include `extraction_buffer` number of observation before and after the detected adapter signal, by default 100.",
)
