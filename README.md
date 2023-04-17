
# ADAPT - Adapter Detection and Processing Tool

ADAPT is a software tool that detects and processes DNA adapters in dRNA-seq data. The tool offers two options for processing the adapters: it can extract the adapter signal from the read or trim the adapter signal from the read to improve data quality and increase the accuracy of downstream analyses.

## Installation

To install ADAPT, Python 3.8 must be installed first. Then, run the following command:

```
git clone https://github.com/wvandertoorn/ADAPT.git
pip install ./ADAPT
```

## Usage

You can use ADAPT by running the following command:

```
adapt <mode> --input_path <input_path> --save_path <save_path>
```

Where `mode` can be `detect`, `trim`, or `extract`, `input_path` contains the fast5 files to process, and `save_path` specifies the location to save the output files.

Although ADAPT can handle both single and multi fast5 files, we recommend using multi fast5 files to limit the disk I/O load on the system.

### Optional arguments for all modes

You can also use the following optional arguments for all modes:

```
--fast5_subset_txt <fast5_subset_txt>
                      Path to a txt file containing a list of fast5 file names (one per line) 
                      describing a subset of the fast5 files present in `input_path`.
--fast5_subset <fast5_subset> [<fast5_subset> ...]
                      A space-separated list of fast5 file names describing a subset of the fast5 
                      files present in `input_path`.
--j <j>               Size of the pool used for multiprocessing read files.
--global_output_csv   Output csv's describing all processed files instead of a csv per 
                      file. Use this option if the files you are processing are single 
                      fast5 files, rather than multi fast5 files.
```

### detect

You can use the `detect` mode to detect adapters in the input files by running the following command:

```
adapt detect --input_path <input_path> --save_path <save_path>
```

The following optional arguments can be used in the `detect` mode:

```
--max_obs <max_obs>   Look for the adapter in the first `max_obs` data points of the raw signal.
                      The default value is 40000, taken from default params in Tombo.
--min_obs_adapter <min_obs_adapter>
                      Set the minimum length of the adapter signal. The default value is 1000.
--border_trim <border_trim>
                      Ignore the outer `border_trim` data points. A boundary can be detected
                      between `border_trim` and `max_obs`-`border_trim` observations.
                      The default value is 500.

```

To get a full overview of the `detect` mode, run:

```
adapt detect --help
```

### trim

You can use the `trim` mode to remove the adapter signal from the input files by running the following command:

```
adapt trim --input_path <input_path> --save_path <save_path>
```

The following optional argument can be used in the `trim` mode:

```
--trimming_buffer <trimming_buffer>
                      Retain `trimming_buffer` number of DNA observation prior to the
                      detected boundary. The default value is 500.
```

In the trim mode, the output directory will contain modified copies of the input fast5 files. Reads for which no adapter was detected are removed from the multi fast5 files, and no file is created in the case of single fast5 files.

To get a full overview of the `trim` mode, run:

```
adapt trim --help
```

### extract

The `extract` mode allows you to extract the adapter signal from the input files. To do so, run the following command:

```
adapt extract --input_path <input_path> --save_path <save_path>
```

The following optional argument can be used in the `extract` mode:

```
--extraction_buffer <extraction_buffer>
                      Include `extraction_buffer` number of observation before and after the detected adapter signal. The default value is 100.
```

To get a full overview of the `extract` mode, run:

```
adapt extract --help
```

## Outputs

In all three modes ADAPT outputs a `detected_adapter_boundaries_[FILENAME].csv` file for for each input file, which is semicolon-separated. The file contains the following columns:

* `rel_filepath`: the relative filepath of the fast5 file with respect to `input_path`.
* `read_id`: the read IDs of the entries in the fast5 file.
* `adapter_start`: the coordinate of the start of the adapter signal.
* `adapter_end`: the coordinate of the end of the adapter signal.

An entry with `adapter_start`=`adapter_end`=0 indicates that no adapter sequence was detected in the corresponding read.

An example of `detected_adapter_boundaries_[FILENAME].csv`:

```{csv}
rel_filepath;read_id;adapter_start;adapter_end
/batch0.fast5;03b6ac8e-48dd-4773-8557-713d044c8bb8;860;5060
/batch0.fast5;03ce1e1a-f4c7-4778-b73c-55c9fa27f116;1138;7135
/batch0.fast5;0505d55c-78ff-464e-9edc-d872fe58fa49;0;0
...
```

### trim

In mode `trim`, the output directory contains modified copies of the input fast5 files in which the adapter signal is trimmed off. In this case, the output directory can be directly used as the input path of the basecaller. For multi fast5 files, reads for which no adapter was detected are removed. For single fast5 files, no file is created.

### extract

In mode `extract`, semicolon-separated `extracted_adapter_[FILENAME].csv` files are created in the output directory.

This file contains the extracted adapter signal per read in integer16 format, as well as the relevant signal parameters to transform the extracted signal to pA using `raw_pA = np.array(parange / digitisation * (raw_int + offset), dtype=np.float32)`.

The file contains the following columns:

* `rel_filepath`:  the relative filepath of the fast5 file with respect to `input_path`.
* `read_id`: the read IDs of the entries in the fast5 file.
* `extraction_buffer`:the padding used in extracting the adapter, i.e. `|adapter_signal| = (adapter_end + extraction_buffer)-(adapter_start-extraction_buffer)`.
* `digitisation`: as reported in fast5 file. The digitisation is the number of quantisation levels in the Analog to Digital
Converter (ADC). That is, if the ADC is 12 bit, digitisation is 4096 (2^12).
* `range`: as reported in fast5 file. The full scale measurement range in pico amperes.
* `offset`: as reported in fast5 file. The ADC offset error. This value is added when converting the signal to pico ampere.
* `adapter_signal`: the extracted adapter signal in integer16 format.

Reads for which no adapter was detected are excluded in this file.

An example of `extracted_adapter_[FILENAME].csv` :

```{csv}
rel_filepath;read_id;extraction_buffer;digitisation;range;offset;adapter_signal
/read0.fast5;0a3bcebd-b594-4a10-8c5c-fa1b75ced59a;100;8192.0;1194.820068359375;4.0;[784, 790, 839, 798, 814, 785, 753 ... ]
...
```

## Run tests

To run tests, you need to install `pytest` and `cython`. You can run the following commands:

```
cd ADAPT
pip install pytest cython
CC=gcc python setup.py build_ext --inplace
pytest
```
