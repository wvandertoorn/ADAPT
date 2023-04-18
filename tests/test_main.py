"""
ADAPT - Adapter Detection and Processing Tool

Copyright (c) 2023 Wiep K. van der Toorn (w.vandertoorn@fu-berlin.de)

"""

import os
import shutil
import pytest

from adapt.__main__ import main

test_data = os.path.join(os.path.dirname(__file__), "data")
if os.path.isdir(os.path.join(test_data, 'tmp')):
    shutil.rmtree(os.path.join(test_data, 'tmp'))

def test_main_detect_single_f5_single_file():
    args = (
        "detect "
        + f"--input_path {test_data} "
        + f"--save_path {test_data}/tmp "
        + "--fast5_subset read0.fast5 "
    )    
    
    args = [x for x in args.split(" ") if len(x)]
    main(args)
    
    os.remove(f"{test_data}/tmp/detected_adapter_boundaries_read0.csv")
    os.rmdir(f"{test_data}/tmp") 

def test_main_detect_multi_f5_single_file():
    args = (
        "detect "
        + f"--input_path {test_data} "
        + f"--save_path {test_data}/tmp "
        + "--fast5_subset batch0.fast5 "
    )    
    
    args = [x for x in args.split(" ") if len(x)]
    main(args)
    
    os.remove(f"{test_data}/tmp/detected_adapter_boundaries_batch0.csv")
    os.rmdir(f"{test_data}/tmp") 
    
    
def test_main_detect_mixed_multi_file():
    args = (
        "detect "
        + f"--input_path {test_data} "
        + f"--save_path {test_data}/tmp "
    )    
    
    args = [x for x in args.split(" ") if len(x)]
    main(args)
    
    os.remove(f"{test_data}/tmp/detected_adapter_boundaries_read0.csv")
    os.remove(f"{test_data}/tmp/detected_adapter_boundaries_batch0.csv")
    os.rmdir(f"{test_data}/tmp") 

    
def test_main_detect_no_file():
    args = (
        "detect "
        + f"--input_path {test_data}/empty "
        + f"--save_path {test_data}/tmp "
    )    
    
    args = [x for x in args.split(" ") if len(x)]
    with pytest.raises(ValueError):
        main(args)
    os.rmdir(f"{test_data}/tmp") 
    
def test_main_detect_global_output_csv():
    args = (
        "detect "
        + f"--input_path {test_data} "
        + f"--save_path {test_data}/tmp "
        + f"--global_output_csv"
    )    
    
    args = [x for x in args.split(" ") if len(x)]
    main(args)

    os.remove(f"{test_data}/tmp/detected_adapter_boundaries.csv")
    os.rmdir(f"{test_data}/tmp") 
    
def test_main_detect_fast5_subset_txt():
    args = (
        "detect "
        + f"--input_path {test_data} "
        + f"--save_path {test_data}/tmp "
        + f"--fast5_subset_txt {test_data}/fast5_subset.txt"
    )    
    
    args = [x for x in args.split(" ") if len(x)]
    main(args)
    
    os.remove(f"{test_data}/tmp/detected_adapter_boundaries_read0.csv")
    os.rmdir(f"{test_data}/tmp") 
    

def test_main_trim_single_f5_single_file():
    args = (
        "trim "
        + f"--input_path {test_data} "
        + f"--save_path {test_data}/tmp "
        + "--fast5_subset read0.fast5"
    )

    args = [x for x in args.split(" ") if len(x)]
    main(args)

    os.remove(f"{test_data}/tmp/detected_adapter_boundaries_read0.csv")
    os.remove(f"{test_data}/tmp/read0.fast5")
    os.rmdir(f"{test_data}/tmp")    

def test_main_trim_multi_f5_single_file():
    args = (
        "trim "
        + f"--input_path {test_data} "
        + f"--save_path {test_data}/tmp "
        + "--fast5_subset batch0.fast5"
    )

    args = [x for x in args.split(" ") if len(x)]
    main(args)

    os.remove(f"{test_data}/tmp/detected_adapter_boundaries_batch0.csv")
    os.remove(f"{test_data}/tmp/batch0.fast5")
    os.rmdir(f"{test_data}/tmp")


def test_main_extract_single_f5_single_file():
    args = (
        "extract "
        + f"--input_path {test_data} "
        + f"--save_path {test_data}/tmp "
        + "--fast5_subset read0.fast5"
    )

    args = [x for x in args.split(" ") if len(x)]
    main(args)

    os.remove(f"{test_data}/tmp/detected_adapter_boundaries_read0.csv")
    os.remove(f"{test_data}/tmp/extracted_adapters_read0.csv")
    os.rmdir(f"{test_data}/tmp")
    
def test_main_extract_multi_f5_single_file():
    args = (
        "extract "
        + f"--input_path {test_data} "
        + f"--save_path {test_data}/tmp "
        + "--fast5_subset batch0.fast5"
    )

    args = [x for x in args.split(" ") if len(x)]
    main(args)

    os.remove(f"{test_data}/tmp/detected_adapter_boundaries_batch0.csv")
    os.remove(f"{test_data}/tmp/extracted_adapters_batch0.csv")
    os.rmdir(f"{test_data}/tmp")