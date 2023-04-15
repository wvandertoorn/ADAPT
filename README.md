
# ADAPT

ADAPT stands for Adapter Detection and Processing Tool, it is a software tool that detects the presence of DNA adapters in dRNA-seq data, and offers two options for processing the identified adapters. First, it can extract the adapter signal from the read, allowing the researcher to analyze the adapter sequence. Second, it can trim the adapter signal from the read to improve data quality and increase the accuracy of downstream analyses.

## Installation

ADAPT requires Python 3.8 to be installed.

```
git clone https://github.com/wvandertoorn/ADAPT.git
pip install ./ADAPT
```

## Usage

```
adapt detect --input_path INPUT_PATH --save_path SAVE_PATH
adapt trim --input_path INPUT_PATH --save_path SAVE_PATH
adapt extract --input_path INPUT_PATH --save_path SAVE_PATH
```

Where `INPUT_PATH` contains the fast5 files to process. These can be single fast5, multi fast5 or a mix thereof. The outputs will be written to `SAVE_PATH`.

Although ADAPT can handle both single and multi fast5 files, we advise the user to use multi fast5 files to limit the disk I/O load on the system.

### Optional arguments for all modes

```
--fast5_subset_txt FAST5_SUBSET_TXT
                      Path to txt file containing entries `XYZ.fast5` (one per line)
                      describing a subset of the fast5 files present in `--input_path`.
--fast5_subset FAST5_SUBSET [FAST5_SUBSET ...]
                      Filenames '`XYZ.fast5` ...' describing a subset of the fast5 files 
                      present in `--input_path`.
--j J                 Size of pool used for multiprocessing read files.
--global_output_csv   Output csv's describing all processed files, instead of a csv per 
                      file. Use this option if the files you are processing are single 
                      fast5 files, rather than multi fast5 files.
```

### detect

```
adapt detect [-h] --input_path INPUT_PATH --save_path SAVE_PATH [--fast5_subset_txt FAST5_SUBSET_TXT | --fast5_subset FAST5_SUBSET [FAST5_SUBSET ...]] [--j J] [--global_output_csv]
                    [--max_obs MAX_OBS] [--min_obs_adapter MIN_OBS_ADAPTER] [--border_trim BORDER_TRIM]


detect-specific optional arguments:
  --max_obs MAX_OBS     Look for adapter in first `max_obs` data points of the raw signal. Dafult value of 40000 taken from default params in Tombo.
  --min_obs_adapter MIN_OBS_ADAPTER
                        Minimal length of the adapter signal, by default 1000
  --border_trim BORDER_TRIM
                        Ignore outer `border_trim` data points, a boundary can be detected between `border_trim` and `max_obs`-`border_trim` observations, by default 500
```

### trim

```
usage: adapt trim [-h] --input_path INPUT_PATH --save_path SAVE_PATH [--fast5_subset_txt FAST5_SUBSET_TXT | --fast5_subset FAST5_SUBSET [FAST5_SUBSET ...]] [--j J] [--global_output_csv]
                  [--trimming_buffer TRIMMING_BUFFER]


trim-specific optional arguments:
  --trimming_buffer TRIMMING_BUFFER
                        Trimming buffer, retain `trimming_buffer` number of DNA observation prior to the detected boundary, by default 500.
```

### extract

```
usage: adapt extract [-h] --input_path INPUT_PATH --save_path SAVE_PATH [--fast5_subset_txt FAST5_SUBSET_TXT | --fast5_subset FAST5_SUBSET [FAST5_SUBSET ...]] [--j J] [--global_output_csv] [--extraction_buffer EXTRACTION_BUFFER]


extract-specific optional arguments:
  --extraction_buffer EXTRACTION_BUFFER
                        Extraction buffer, include `extraction_buffer` number of observation before and after the detected adapter signal, by default 100
```

## Outputs

In all three modes ADAPT outputs detected_adapter_boundaries_[FILENAME].csv files. These files are semicolon separated.

```{csv}
rel_filepath;read_id;adapter_start;adapter_end
/batch0.fast5;03b6ac8e-48dd-4773-8557-713d044c8bb8;860;5060
/batch0.fast5;03ce1e1a-f4c7-4778-b73c-55c9fa27f116;1138;7135
/batch0.fast5;0505d55c-78ff-464e-9edc-d872fe58fa49;0;0
...
```

* `rel_filepath`: contains the filepath of the fast5 file relative to INPUT_PATH
* `read_id`: the read_ids of the entries in the fast5 file
* `adapter_start`: Coordinate of the start of the adapter signal
* `adapter_end`: Coordinate of the end of the adapter signal

`adapter_start`=`adapter_end`=0 indicates that no adapter sequence was detected in this read.

### trim

In mode `trim`, the output directory will additionally contain copies of the input fast5 files in which the signal dataset attribute of the read is modified (adapter is trimmed off). In this case, the output directory can directly be used as the input path of the basecaller.
Reads for which no adapter was detected are removed from the multi fast5 files, and in the case of single fast5 files, no file is created.

### extract

In mode `extract`, semicolon-separated extracted_adapter_[FILENAME].csv files are created in addition.
This file contains the extracted adapter signal per read in integer16 format and the relevant signal parameters to transform the extracted signal to pA using `raw_pA = np.array(parange / digitisation * (raw_int + offset), dtype=np.float32)`.

If no adapter was detected in a read, there is no entry for this read (read id) in this file.

```{csv}
rel_filepath;read_id;extraction_buffer;digitisation;range;offset;adapter_signal
/read0.fast5;0a3bcebd-b594-4a10-8c5c-fa1b75ced59a;100;8192.0;1194.820068359375;4.0;[784, 790, 839, 798, 814, 785, 753 ... ]
...
```

* `rel_filepath`: contains the filepath of the fast5 file relative to INPUT_PATH
* `read_id`: the read_ids of the entries in the fast5 file
* `extraction_buffer`: padding used in extracting the adapter, i.e. `|adapter_signal| = (adapter_end + extraction_buffer)-(adapter_start-extraction_buffer)`.
* `digitisation`: As reported in fast5 file. The digitisation is the number of quantisation levels in the Analog to Digital
Converter (ADC). That is, if the ADC is 12 bit, digitisation is 4096 (2^12).
* `range`: As reported in fast5 file. The full scale measurement range in pico amperes.
* `offset`: As reported in fast5 file. The ADC offset error. This value is added when converting the signal to pico ampere.
* `adapter_signal`: The extracted adapter signal in integer16 format.

## Run tests

Running tests requires installing `pytest` and `cython`.

```
cd ADAPT
pip install pytest cython
CC=gcc python setup.py build_ext --inplace
pytest
```
