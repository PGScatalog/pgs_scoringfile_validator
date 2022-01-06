import sys
import gzip
import csv
import os
import argparse
import pathlib
import logging
import gzip
import re
import pandas as pd
from pandas_schema import Schema
#from validator.schema import *
from .schema import *

"""
GWAS Summary statistics file validator
- using pandas_schema https://github.com/TMiguelT/PandasSchema
It can be run on files pre- ('standard') or post- harmonisation ('harmonised')
and also in the 'curator' format.
File names and numbers of fields on each row are checked.
Fields validated in the standard and harmonised stage are all the required fields
for HDF5 convertion. The curator format validation only checks the file name,
the table shape and the pvalue.
"""


csv.field_size_limit(sys.maxsize)

logging.basicConfig(level=logging.INFO, format='(%(levelname)s): %(message)s')
logger = logging.getLogger(__name__)


class Validator:
    def __init__(self, file, filetype='pgs-upload', logfile="VALIDATE.log", error_limit=0):
        self.file = file
        self.filetype = filetype
        self.schema = None
        self.header = []
        self.comment_lines_count = 1 # Counting the header line
        self.cols_to_validate = []
        self.cols_to_read = []
        self.sep = get_seperator(self.file)
        self.bad_rows = []
        self.row_errors = []
        self.errors_seen = {}
        #self.required_fields = STD_COLS
        self.valid_extensions = VALID_FILE_EXTENSIONS
        self.logfile = logfile
        self.error_limit = int(error_limit)
        self.handler = logging.FileHandler(self.logfile)
        self.handler.setLevel(logging.INFO)

        self.global_errors = 0
        self.variants_number = 0

        logger.addHandler(self.handler)

    def setup_field_validation(self):
        self.header = self.get_header()
        if self.filetype == 'curated':
            self.required_fields = [key for key, value in CURATOR_STD_MAP.items() if value == EFFECT_WEIGHT_DSET]
            self.cols_to_validate = [CURATOR_STD_MAP[h] for h in self.header if h in self.required_fields]
        else:
            self.cols_to_validate = [h for h in self.header if h in VALID_COLS]
        self.cols_to_read = [h for h in self.header if h in VALID_COLS]


    def get_and_check_variants_number(self):
        ''' Verify that the number of variant lines corresponds to the number of variants in the headers '''
        variant_lines = 0
        
        with gzip.open( self.file, 'rb') as f:
            line_number = 0
            for line in f:
                line_number += 1
                line = line.decode('utf-8').rstrip()
                if line.startswith('#'):
                    match_variants_number = re.search(r'#variants_number=(\d+)', line)
                    if match_variants_number:
                        self.variants_number = int(match_variants_number.group(1))
                else:
                    variant_lines += 1
                    if re.search('\w+', line): # Line not empty
                        cols = line.split(self.sep)
                        has_trailing_spaces = self.check_leading_trailing_spaces(cols,line_number)
                        if has_trailing_spaces:
                            self.global_errors += 1
                    else:
                        logger.error(f'- Line {line_number} is empty')
                        self.global_errors += 1
                            
        if self.variants_number:
            variant_lines -= 1 # Remove the header line from the count
            if self.variants_number != variant_lines:
                logger.error(f'- The number of variants lines in the file ({variant_lines}) and the number of variants declared in the headers ({self.variants_number}) are different')
                self.global_errors += 1
        else:
            logger.error("- Can't retrieve the number of variants from the headers")
            self.global_errors += 1


    def get_header(self):
        first_row = pd.read_csv(self.file, sep=self.sep, comment='#', nrows=1, index_col=False)
        # Check if the column headers have leading and/or trailing spaces
        # The leading/trailing spaces should raise an error during the header validation
        has_trailing_spaces = self.check_leading_trailing_spaces(first_row.columns.values)
        if has_trailing_spaces:
            self.global_errors += 1

        return first_row.columns.values


    def detect_duplicated_rows(self,dataframe_chunk):
        ''' Detect duplicated rows in the scoring file. '''
        # Columns of interest to compare the different rows
        cols_sel = []
        for col in ['rsID','chr_name','chr_position','effect_allele']:
            if col in self.cols_to_validate:
                cols_sel.append(col)

        duplicate_status = dataframe_chunk.duplicated(cols_sel)
        if any(duplicate_status):
            duplicated_rows = dataframe_chunk[duplicate_status]
            logger.error(f'Duplicated row(s) found: {len(duplicated_rows.index)}\n\t-> {duplicated_rows.to_string(header=False,index=False)}')
            self.global_errors += 1
            for index in duplicated_rows.index:
                self.bad_rows.append(index)


    def validate_data(self):
        if not self.open_file_and_check_for_squareness():
            logger.error("Please fix the table. Some rows have different numbers of columns to the header")
            logger.info("Rows with different numbers of columns to the header are not validated")
        # Check the consitence between the declared variants number and the actual number of variants in the file
        self.get_and_check_variants_number()

        for chunk in self.df_iterator():
            to_validate = chunk[self.cols_to_read]
            to_validate.columns = self.cols_to_validate # sets the headers to standard format if neeeded

            # Detect duplicated rows
            self.detect_duplicated_rows(to_validate)

            # validate the snp column if present
            if SNP_DSET in self.header:
                if CHR_DSET and BP_DSET in self.header:
                    self.schema = Schema([SNP_EMPTY_VALIDATORS[h] for h in self.cols_to_validate])
                    errors = self.schema.validate(to_validate)
                    self.store_errors(errors)
                else:
                    self.schema = Schema([SNP_VALIDATORS[h] for h in self.cols_to_validate])
                    errors = self.schema.validate(to_validate)
                    self.store_errors(errors)

            if CHR_DSET and BP_DSET in self.header:
                self.schema = Schema([POS_VALIDATORS[h] for h in self.cols_to_validate])
                errors = self.schema.validate(to_validate)
                self.store_errors(errors)
            if OR_DSET in self.header:
                self.schema = Schema([OR_VALIDATOR[h] for h in self.cols_to_validate])
                errors = self.schema.validate(to_validate)
                self.store_errors(errors)
            if HR_DSET in self.header:
                self.schema = Schema([HR_VALIDATOR[h] for h in self.cols_to_validate])
                errors = self.schema.validate(to_validate)
                self.store_errors(errors)
            self.process_errors()
            if len(self.bad_rows) >= self.error_limit:
                break
        if not self.bad_rows and not self.global_errors:
            logger.info("File is valid")
            return True

        else:
            logger.info("File is invalid - {} bad rows, limit set to {}".format(len(self.bad_rows), self.error_limit))
            return False

    def process_errors(self):
        for error in self.row_errors:
            if len(self.bad_rows) < self.error_limit or self.error_limit < 1:
                logger.error(error)
                if error.row not in self.bad_rows:
                    self.bad_rows.append(error.row)
        self.row_errors = []

    def store_errors(self, errors):
        for error in errors:
            seen = 0
            row_number = error.row
            file_line_number = row_number + self.comment_lines_count + 1 # rows are 0 indexes
            error.row = str(row_number) + " (line "+str(file_line_number)+")"
            col = error.column
            # Avoid duplication as the errors can be detected several times
            if row_number in self.errors_seen.keys():
                if col in self.errors_seen[row_number].keys():
                    seen = 1
                else:
                    self.errors_seen[row_number][col] = 1
            else:
                self.errors_seen[row_number] = { col : 1 }
            if seen == 0:
                self.row_errors.append(error)

    def write_valid_lines_to_file(self):
        newfile = self.file + ".valid"
        first_chunk = True
        for chunk in self.df_iterator():
            chunk.drop(self.bad_rows, inplace=True, errors='ignore')
            if first_chunk:
                chunk.to_csv(newfile, mode='w', sep='\t', index=False, na_rep='NA')
                first_chunk = False
            else:
                chunk.to_csv(newfile, mode='a', header=False, sep='\t', index=False, na_rep='NA')

    def validate_file_extension(self):
        check_exts = [check_ext(self.file, ext) for ext in self.valid_extensions]
        if not any(check_exts):
            self.valid_ext = False
            logger.error("File extension should be in {}".format(self.valid_extensions))
            return False
        else:
            self.valid_ext = True
        return True

    def validate_filename(self):
        self.validate_file_extension()
        pmid, study, trait, build = None, None, None, None
        filename = self.file.split('/')[-1].split('.')[0]
        filename_parts = filename.split('-')
        if len(filename_parts) != 4:
            logger.error("Filename: {} should follow the pattern <pmid>-<study>-<trait>-build>.tsv".format(filename))
            return False
        else:
            pmid, study, trait, build = filename_parts
        if not check_build_is_legit(build):
            logger.error("Build: {} is not an accepted build value".format(build))
            return False
        logger.info("Filename looks good!")
        return True

    def df_iterator(self):
        df = pd.read_csv(self.file,
                         sep=self.sep,
                         dtype=str,
                         comment='#',
                         chunksize=1000000)
        return df

    def check_file_is_square(self, csv_file):
        square = True
        dialect = csv.Sniffer().sniff(csv_file.readline())
        csv_file.seek(0)
        #reader = csv.reader(csv_file, dialect)
        reader = csv.reader(csv_file, delimiter=self.sep)
        count = 1
        for row in reader:
            if len(row) != 0:
                if row[0].startswith('#'):
                    self.comment_lines_count += 1
                    continue
            if (len(row) != len(self.header)):
                logger.error("Length of row {c} is: {l} instead of {h}".format(c=count, l=str(len(row)), h=str(len(self.header))))
                logger.error("ROW: "+str(row))
                square = False
            count += 1
        return square

    def open_file_and_check_for_squareness(self):
        if pathlib.Path(self.file).suffix in [".gz", ".gzip"]:
             with gzip.open(self.file, 'rt') as f:
                 return self.check_file_is_square(f)
        else:
            with open(self.file) as f:
                 return self.check_file_is_square(f)


    def check_leading_trailing_spaces(self, cols, line_number=None):
        '''
        Check if the columns have leading and/or trailing spaces.
        The leading/trailing spaces should raise an error during the validation.
        '''
        leading_trailing_spaces = []
        found_trailing_spaces = False
        for idx, col in enumerate(cols):
            if col.startswith(' ') or col.endswith(' '):
                leading_trailing_spaces.append(self.header[idx]+' => |'+str(col)+'|')
        if len(leading_trailing_spaces):
            if line_number:
                line_name = f'line {line_number} has'
            else:
                line_name = 'following headers have'
            logger.error("The "+line_name+" leading and/or trailing spaces: "+' ; '.join(leading_trailing_spaces))
            found_trailing_spaces = True
        return found_trailing_spaces

    def validate_headers(self):
        self.setup_field_validation()
        required_is_subset = set(STD_COLS_VAR).issubset(self.header)
        if not required_is_subset:
            # check if everything but snp:
            required_is_subset = set(STD_COLS_VAR_POS).issubset(self.header)
            if not required_is_subset:
                required_is_subset = set(STD_COLS_VAR_SNP).issubset(self.header)
            if not required_is_subset:
                logger.error("Required headers: {} are not in the file header: {}".format(STD_COLS_VAR, self.header))

        # Check if at least one of the effect columns is there
        has_effect_col = 0
        for col in STD_COLS_EFFECT:
            if set([col]).issubset(self.header):
                has_effect_col = 1
                break
        if not has_effect_col:
            logger.error("Required headers: at least one of the columns '{}' must be in the file header: {}".format(STD_COLS_EFFECT, self.header))
            required_is_subset = None

        return required_is_subset

def check_ext(filename, ext):
    if filename.endswith(ext):
        return True
    return False

def check_build_is_legit(build):
    build_string = build.lower()
    build_number = build_string.replace('build', '')
    if build_number in BUILD_MAP.keys():
        return True
    return False

def get_seperator(file):
    filename, file_extension = os.path.splitext(file)
    sep = '\t'
    if '.csv' in file_extension:
        sep = ','
    return sep


def run_validator(file, logfile):

    logger.propagate = False

    if not file or not logfile:
        logger.info("Missing file and/or logfile")
        logger.info("Exiting before any further checks")
        sys.exit()
    if not os.path.exists(file):
        logger.info("Error: the file '"+file+"' can't be found")
        logger.info("Exiting before any further checks")
        sys.exit()

    validator = Validator(file=file, logfile=logfile)

    is_ok_to_run_validation = 1
    logger.info("Validating file extension...")
    if not validator.validate_file_extension():
        logger.info("Invalid file extesion: {}".format(file))
        logger.info("Exiting before any further checks")
        is_ok_to_run_validation = 0
        #sys.exit()

    if is_ok_to_run_validation:
        logger.info("Validating headers...")
        if not validator.validate_headers():
            logger.info("Invalid headers...exiting before any further checks")
            is_ok_to_run_validation = 0
            #sys.exit()

    if is_ok_to_run_validation:
        logger.info("Validating data...")
        validator.validate_data()

    # Close log handler
    logger.removeHandler(validator.handler)
    validator.handler.close()


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-f", help='The path to the polygenic scoring file to be validated', metavar='SCORING_FILE_NAME', required=True)
    #argparser.add_argument("--filetype", help='The type of file/stage in the process the file to be validated is in. Recommended to leave as default if unknown.', default='pgs-upload', choices=['gwas-upload','curated','standard','harmonised'])
    argparser.add_argument("--logfile", help='Provide the filename for the logs', default='VALIDATE.log')
    argparser.add_argument("--linelimit", help='Stop when this number of bad rows has been found', default=0)
    argparser.add_argument("--drop-bad-lines", help='Store the good lines from the file in a file named <polygenic-scoring-file>.valid', action='store_true', dest='dropbad')

    args = argparser.parse_args()

    logfile = args.logfile
    linelimit = args.linelimit
    default_filetype = 'pgs-upload'

    validator = Validator(file=args.f, filetype=default_filetype, logfile=args.logfile, error_limit=linelimit)

    print('#-------------------#\n#  File Validation  #\n#-------------------#\n')
    print("Filename: "+args.f+"\n")

    if args.filetype == "curated":
        logger.info("Validating filename...")
        if not validator.validate_filename():
            logger.info("Invalid filename: {}".format(args.f))
            logger.info("Exiting before any further checks")
            sys.exit()
    else:
        logger.info("Validating file extension...")
        if not validator.validate_file_extension():
            logger.info("Invalid file extesion: {}".format(args.f))
            logger.info("Exiting before any further checks")
            sys.exit()

    logger.info("Validating headers...")
    if not validator.validate_headers():
        logger.info("Invalid headers...exiting before any further checks")
        sys.exit()

    logger.info("Validating data...")
    validator.validate_data()
    if args.dropbad:
        logger.info("Writing good lines to {}.valid".format(args.f))
        validator.write_valid_lines_to_file()


if __name__ == '__main__':
    main()
