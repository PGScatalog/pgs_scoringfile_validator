import glob
import sys
import os
import gzip
import argparse
from tqdm import tqdm
import pandas as pd
#from format import peek
from . import peek
#from format.utils import *
from .utils import *

extra_formatted_dir = '/formatted/'

def multi_delimiters_to_single(row):
    return "\t".join(row.split())


def process_file(file):
    dirname = os.path.dirname(file)
    filename, file_extension = os.path.splitext(file)
    print("FILE: "+file)
    print("DIRNAME: "+dirname)
    create_formatted_directory(dirname)
    new_filename = dirname + extra_formatted_dir + '/formatted_' + os.path.basename(filename) + '.txt'
    temp_file  = filename + '.tmp'
    unnamed_col = 'Unnamed: 0'
    main_sep = '\t'
    sep = main_sep
    if file_extension == '.csv':
        sep = ','


    df = pd.read_csv(file, comment='#', sep=sep, dtype=str, error_bad_lines=False, warn_bad_lines=True, chunksize=1000000)

    header = None
    new_header = None
    what_changed = None

    first = True
    for chunk in df:

        # map headers
        header = chunk.columns.values
        chunk.rename(columns=known_header_transformations, inplace=True)
        new_header = chunk.columns.values
        what_changed = dict(zip(header, new_header))
        #print("PARSED HEADER: "+str(new_header))


        if first:
            chunk.to_csv(temp_file, mode='w', header=True, sep=main_sep, na_rep="NA")
            first = False
        else:
            chunk.to_csv(temp_file, mode='a', header=False, sep=main_sep, na_rep="NA")


    if CHR_BP in new_header:
        # split the chr_bp field
        df = pd.read_csv(temp_file, usecols=[CHR_BP], comment='#', sep=main_sep, dtype=str, error_bad_lines=False, warn_bad_lines=True)
        df = df.join(df[CHR_BP].str.split('_|:', expand=True).add_prefix(CHR_BP).fillna('NA'))

        if CHR_BP + '1' in df:
            df[CHR] = df[CHR_BP + '0'].str.replace('CHR|chr|_|-', '')
            df[CHR] = df[CHR].apply(lambda i: i if i in VALID_CHROMS else 'NA')
            df[BP] = df[CHR_BP + '1']
            df = df.drop(CHR_BP + '1', axis=1)
        else:
            df[BP] = df[CHR_BP + '0']
        df = df.drop(CHR_BP, axis=1)
        df = df.drop(CHR_BP + '0', axis=1)

        chunks = pd.read_csv(temp_file, comment='#', sep=main_sep, dtype=str, error_bad_lines=False, warn_bad_lines=True, chunksize=1000000)
        first = True
        for chunk in chunks:
            result = pd.merge(chunk, df, left_index=True, right_index=True).drop([unnamed_col,CHR_BP],axis=1)
            result = ordered_columns(result)
            if first:
                result.to_csv(new_filename, mode='w', header=True, sep=main_sep, na_rep="NA", index=False)
                first = False
            else:
                result.to_csv(new_filename, mode='a', header=False, sep=main_sep, na_rep="NA", index=False)

    elif CHR in new_header:
        # clean the chr field
        chunks = pd.read_csv(temp_file, comment='#', sep=main_sep, dtype=str, error_bad_lines=False, warn_bad_lines=True, chunksize=1000000)
        first = True
        for chunk in chunks:
            if unnamed_col in chunk:
                chunk = chunk.drop(unnamed_col,axis=1)
            chunk = ordered_columns(chunk)
            if first:
                chunk.to_csv(new_filename, mode='w', header=True, sep=main_sep, na_rep="NA", index=False)
                first = False
            else:
                chunk.to_csv(new_filename, mode='a', header=False, sep=main_sep, na_rep="NA", index=False)

    elif CHR not in new_header and BP not in new_header and VARIANT in new_header:

        if VARIANT != 'rsID':
            # split the snp field
            df = pd.read_csv(temp_file, usecols=[VARIANT], comment='#', sep=main_sep, dtype=str, error_bad_lines=False, warn_bad_lines=True)

            df = df.join(df[VARIANT].str.split('_|:', expand=True).add_prefix(VARIANT).fillna('NA'))
            df[CHR] = df[VARIANT + '0'].str.replace('CHR|chr|_|-', '')
            df[CHR] = df[CHR].apply(lambda i: i if i in VALID_CHROMS else 'NA')
            if VARIANT + '1' in df.columns:
                df[BP] = df[VARIANT + '1']
                df = df.drop(VARIANT + '1', axis=1)
            df = df.drop(VARIANT + '0', axis=1)
            df = df.drop(VARIANT, axis=1)

        chunks = pd.read_csv(temp_file, comment='#', sep=main_sep, dtype=str, error_bad_lines=False, warn_bad_lines=True, chunksize=1000000)
        first = True
        for chunk in chunks:
            if VARIANT == 'rsID':
                result = chunk
            else:
                result = pd.merge(chunk, df, left_index=True, right_index=True).drop(VARIANT,axis=1)

            # Cleanup/order the columns
            if unnamed_col in result:
                result = result.drop(unnamed_col,axis=1)
            result = ordered_columns(result)

            if first:
                result.to_csv(new_filename, mode='w', header=True, sep=main_sep, na_rep="NA", index=False)
                first = False
            else:
                result.to_csv(new_filename, mode='a', header=False, sep=main_sep, na_rep="NA", index=False)

    else:
        print("Exiting because, couldn't map the headers")
        os.remove(new_filename)
        sys.exit()

    if os.path.isfile(temp_file):
        os.remove(temp_file)

    if os.path.exists(new_filename):
        new_gzip_filename = new_filename+'.gz'
        input = open(new_filename, 'rb')
        file_content = input.read()
        input.close()

        compressed_file = gzip.open(new_gzip_filename, 'wb')
        compressed_file.write(file_content)
        compressed_file.close()

        print("\n------> Output saved in file:", new_gzip_filename, "<------\n")
        print("Please use this file for any further formatting.\n")
        print("Showing how the headers where mapped below...\n")
        for key, value in what_changed.items():
            print(key, " -> ", value)
        print("\nPeeking into the new file...")
        print("\n")
        peek.peek(new_gzip_filename)

    return new_gzip_filename


def ordered_columns(dataframe):
    new_header = []
    df_header = dataframe.columns.values
    # Order of expected columns
    for col in TO_DISPLAY_ORDER:
        if col in df_header:
            new_header.append(col)
    # Order of other columns
    for hcol in df_header:
        if not hcol in new_header:
            new_header.append(hcol)
    #print("PROCESSED HEADER: "+str(new_header))
    return dataframe[new_header]


def create_formatted_directory(path):
    """ Creates directory for a given file """
    path += extra_formatted_dir
    if not os.path.isdir(path):
        try:
            os.mkdir(path, 0o755)
        except OSError:
            print ("Creation of the directory %s failed" % path)
            exit()

def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-f', help='The name of the file to be processed', metavar='SCORING_FILE_NAME')
    argparser.add_argument('--dir', help='The name of the directory containing the files that need to processed')
    args = argparser.parse_args()

    new_file = None

    print('\n#-------------------#\n#  File Formatting  #\n#-------------------#')
    if args.f and args.dir is None:
        file = args.f
        new_file = process_file(file)
    elif args.dir and args.f is None:
        dir = args.dir
        print("Processing the following files:")
        for f in glob.glob("{}/*.*".format(dir)):
            print(f)
            new_file = process_file(f)
    else:
        print("You must specify either -f <file> OR --dir <directory containing files>")

    return new_file

if __name__ == "__main__":
    main()
