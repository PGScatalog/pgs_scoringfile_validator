import validator.validate.validator as main_validator
import os, sys, glob, re
import argparse

# Browse directory

def read_last_line(file):
    fileHandle = open ( file,"r" )
    lineList = fileHandle.readlines()
    fileHandle.close()
    return lineList[-1]


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-dir', help='The name of the directory containing the files that need to processed', required=True)
    argparser.add_argument('-log_dir', help='The name of the log directory where the log files will be stored', required=True)

    args = argparser.parse_args()

    if os.path.isdir(args.dir) and os.path.isdir(args.log_dir):
        data_sum = {'valid': [], 'invalid': [], 'other': []}
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

    # Print summary  + results
    elif not os.path.isdir(args.dir):
        print("Error: the scoring file directory '"+args.dir+"' can't be found!")
    elif not os.path.isdir(args.log_dir):
        print("Error: the log directory '"+args.log_dir+"' can't be found!")

if __name__ == '__main__':
    main()
