import os, sys, glob, re
import argparse
import curator_formatter.format.automatic_formatting as main_formatting
import validator.validate.validator as main_validator


def read_last_line(file):
    fileHandle = open ( file,"r" )
    lineList = fileHandle.readlines()
    fileHandle.close()
    return lineList[-1]


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-f", help='The path to the polygenic scoring file to be formatted and validated (no need to use the [--dir] option)', metavar='SCORING_FILE_NAME')
    argparser.add_argument('--dir', help='The name of the directory containing the mutiple files that need to processed (no need to use the [-f] option)')
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
            # File formatting
            formatted_file = main_formatting.main()

            # File validation
            if formatted_file:
                file = os.path.basename(formatted_file)
                filename = file.split('.')[0]

                sys.argv.extend(['-f', formatted_file])
                sys.argv.extend(['--logfile', argv.log_dir+"/"+filename+'_log.txt'])
                main_validator.main()
            else:
                print("The formatting of '"+formatted_file+"' failed, therefore we can't validate the file")
        else:
            print("Error: Scoring file '"+args.f+"' can't be found!")
            exit(1)

    # Content of the directory
    elif args.dir:
        if os.path.isdir(args.dir):
            data_sum = {'valid': [], 'invalid': [], 'other': []}
            count_files = 0
            count_files_formatted = 0
            files_not_formatted = []
            files_validated = 0
            # Browse directory: for each file run validator
            for filepath in sorted(glob.glob(args.dir+"/*.*")):
                file = os.path.basename(filepath)
                filename = file.split('.')[0]
                print("Filename: "+file)
                log_file = args.log_dir+'/'+filename+'_log.txt'
                count_files += 1

                # Run formatter
                formatted_file = main_formatting.process_file(filepath)
                if os.path.exists(formatted_file):
                    count_files_formatted += 1
                else:
                    files_not_formatted.append(file)
                    continue

                # Run validator
                main_validator.run_validator(formatted_file,log_file)

                # Check log

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

            print("\n# Summary:")
            print("  - Formatted: "+str(count_files_formatted)+"/"+str(count_files))
            if data_sum['valid']:
                print("  - Valid: "+str(len(data_sum['valid']))+"/"+str(count_files))
            if data_sum['invalid']:
                print("  - Invalid: "+str(len(data_sum['invalid']))+"/"+str(count_files))
            if data_sum['other']:
                print("  - Other issues: "+str(len(data_sum['other']))+"/"+str(count_files))

            if (len(files_not_formatted)):
                print("\n# Files not formatted:")
                print("  - "+"\n  - ".join(files_not_formatted))
            if data_sum['invalid']:
                print("\n# Invalid file(s):")
                print("  - "+"\n  - ".join(data_sum['invalid']))
            if data_sum['other']:
                print("\n# File(s) with other validation issues:")
                print("  - "+"\n  - ".join(data_sum['other']))

        # Print summary  + results
        elif not os.path.isdir(args.dir):
            print("Error: the scoring file directory '"+args.dir+"' can't be found!")

if __name__ == '__main__':
    main()
