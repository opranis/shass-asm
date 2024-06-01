import os.path
import sys

class ErrorHandler:
    """Class used for handling errors during parsing."""

    def genericError(file, line_num, message):
        """Throw a generic error in file, on line number."""

        print(f"Error in file \"{file}\" on line {line_num}:")
        print("    ", message)

        # After an error is found, stop execution.
        quit()

    def getCommandLineArgument():
        """Get user supplied command line argument."""

        try:
            return sys.argv[1]
        except:
            # If no arg supplied, go to main.asm by default.
            return "main.asm"

    def checkFileExists(file, doExcept = False):
        """Check for existence of a file"""

        if not os.path.isfile(file):
            # Depending on the passed arg, either just except, or also quit immediately.
            if not doExcept:
                print(f"File \"{file}\" does not exist.")
                quit()
            else:
                raise Exception(f"File \"{file}\" does not exist.")