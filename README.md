# sum-stats-formatter
* Formatting and harmonising scripts for scoring files that will be imported into the PGS Catalog database.
* Validating format and data types of the scoring files



## File Formatter

```
usage: run_formatter.py [-h] [-f SCORING_FILE_NAME] [--dir DIR]

optional arguments:
  -h, --help            show this help message and exit
  -f SCORING_FILE_NAME  The name of the file to be processed
  --dir DIR             The name of the directory containing the files that
                        need to processed
```

### Examples
```
# Text-tabulated file
python run_formatter.py -f <file_to_format>.txt
python run_formatter.py -f <file_to_format>.tsv

# Comma-separated file
python run_formatter.py -f <file_to_format>.csv

# Directory
python run_formatter.py --dir <scoring_file_directory>
```


## File Validator

```
usage: run_validator.py [-h] [-f SCORING_FILE_NAME] [--dir DIR] --log_dir
                        LOG_DIR

optional arguments:
  -h, --help            show this help message and exit
  -f SCORING_FILE_NAME  The path to the polygenic scoring file to be validated
                        (no need to use the [--dir] option)
  --dir DIR             The name of the directory containing the files that
                        need to processed (no need to use the [-f] option
  --log_dir LOG_DIR     The name of the log directory where the log file(s)
                        will be stored
```

### Examples
```
## Single file
# Compressed file
python run_validator.py -f <file_to_valid>.txt.gz --log_dir <log_directory>

# Uncompressed file
python run_validator.py -f <file_to_valid>.txt --log_dir <log_directory>

## Directory
python run_validator.py --dir <scoring_file_directory> --log_dir <log_directory>
```


## Pipeline (formatter + validator)

```
usage: run_pipeline.py [-h] [-f SCORING_FILE_NAME] [--dir DIR] --log_dir
                       LOG_DIR

optional arguments:
  -h, --help            show this help message and exit
  -f SCORING_FILE_NAME  The path to the polygenic scoring file to be formatted
                        and validated (no need to use the [--dir] option)
  --dir DIR             The name of the directory containing the mutiple files
                        that need to processed (no need to use the [-f]
                        option)
  --log_dir LOG_DIR     The name of the log directory where the log file(s)
                        will be stored
```

```
# Single file
python run_pipeline.py -f <file_to_format_and_valid>.txt --log_dir <log_directory>
python run_pipeline.py -f <file_to_format_and_valid>.tsv --log_dir <log_directory>
python run_pipeline.py -f <file_to_format_and_valid>.csv --log_dir <log_directory>

# Multiple files
python run_pipeline.py --dir <scoring_file_directory> --log_dir <log_directory>
```
