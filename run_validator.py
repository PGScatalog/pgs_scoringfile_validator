import validator.validate.validator as main_validator
import os, sys, glob, re
import argparse

data_sum = {'valid': [], 'invalid': [], 'other': []}

def read_last_line(file):
    fileHandle = open ( file,"r" )
    lineList = fileHandle.readlines()
    fileHandle.close()
    return lineList[-1]


def file_validation_state(filename,log_file):
    global data_sum
    if os.path.exists(log_file):
        log_result = read_last_line(log_file)
        if re.search("File is valid", log_result):
            print("> valid\n")
            data_sum['valid'].append(filename)
        elif re.search("File is invalid", log_result):
            print("#### invalid! ####\n")
            data_sum['invalid'].append(filename)
        else:
            print("!! validation process had an issue. Please look at the logs.\n")
            data_sum['other'].append(filename)
    else:
        print("!! validation process had an issue: the log file can't be found")
        data_sum['other'].append(filename)


def main():
    global data_sum

    argparser = argparse.ArgumentParser()
    argparser.add_argument("-f", help='The path to the polygenic scoring file to be validated (no need to use the [--dir] option)', metavar='SCORING_FILE_NAME')
    argparser.add_argument('--dir', help='The name of the directory containing the files that need to processed (no need to use the [-f] option')
    argparser.add_argument('--log_dir', help='The name of the log directory where the log file(s) will be stored', required=True)

    args = argparser.parse_args()

    if not os.path.isdir(args.log_dir):
        print("Error: Log dir '"+args.log_dir+"' can't be found!")
        exit(1)
    if args.f and args.dir:
        print("Error: you can't use both options [-f] - single scoring file and [--dir] - directory of scoring files. Please use only 1 of these 2 options!")
        exit(1)
    if not args.f and not args.dir:
        print("Error: you need to provide a scoring file [-f] or a directory of scoring files [--dir]!")
        exit(1)

    # One file
    if args.f:
        if os.path.isfile(args.f):
            file = os.path.basename(args.f)
            filename = file.split('.')[0]
            log_file = args.log_dir+'/'+filename+'_log.txt'
            main_validator.run_validator(args.f,log_file)
            # Check log
            file_validation_state(file,log_file)
        else:
            print("Error: Scoring file '"+args.f+"' can't be found!")
            exit(1)

    # Content of the directory
    elif args.dir:
        if os.path.isdir(args.dir):
            count_files = 0
            # Browse directory: for each file run validator
            for filepath in sorted(glob.glob(args.dir+"/*.*")):
                file = os.path.basename(filepath)
                filename = file.split('.')[0]
                print("Filename: "+file)
                log_file = args.log_dir+'/'+filename+'_log.txt'
                count_files += 1

                # Run validator
                main_validator.run_validator(filepath,log_file)

                # Check log
                file_validation_state(file,log_file)

            # Print summary  + results
            print("\nSummary:")
            if data_sum['valid']:
                print("- Valid: "+str(len(data_sum['valid']))+"/"+str(count_files))
            if data_sum['invalid']:
                print("- Invalid: "+str(len(data_sum['invalid']))+"/"+str(count_files))
            if data_sum['other']:
                print("- Other issues: "+str(len(data_sum['other']))+"/"+str(count_files))

            if data_sum['invalid']:
                print("Invalid files:")
                print("\n".join(data_sum['invalid']))

        # Directory doesn't exist
        elif not os.path.isdir(args.dir):
            print("Error: the scoring file directory '"+args.dir+"' can't be found!")

if __name__ == '__main__':
    main()
