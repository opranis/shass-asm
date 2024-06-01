#!/usr/bin/env python3

"""\
This is the entry file of the shass-asm assembler for the Caltech10 CPU.

To run the assembler, this program should be run with one argument - 
the main (entry) assembly file. By default, main.asm will be assembled.
"""

from shass_parser import *

class CommandLineInputParser:
    """Class for getting the entry file as specified by user."""
    def __init__(self):
        # get the argument for the main file
        self._main_file = ErrorHandler.getCommandLineArgument()
        # check that it exists
        ErrorHandler.checkFileExists(self._main_file)
    
    def getEntryFile(self):
        return self._main_file

class FileWriter:
    """Class through which all file writes are done."""
    def __init__(self):
        # The object file output is always going to be "a.obj"
        self.filewrite = open("a.obj", "w")

    def writeLine(self, str):
        self.filewrite.write(str + "\n")

    def close(self):
        # Add a trailing blank line to the file.
        self.writeLine("")
        self.filewrite.close()

# Start execution of the assembler
entry_file = CommandLineInputParser().getEntryFile()

parser = Parser(entry_file)

parser.first_parse()

f = FileWriter()
parser.second_parse(f)

f.close()

print("Assembler finished successfully!")