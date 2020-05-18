import sys
import curator_formatter.format.automatic_formatting as main_formatting
import validator.validate.validator as main_validator

# File formatting
formatted_file = main_formatting.main()

# File validation
if formatted_file:
    sys.argv.extend(['-f', formatted_file])
    sys.argv.extend(['--logfile', 'log.txt'])
    main_validator.main()
else:
    print("The formatting failed, therefore we can't validate the file")
