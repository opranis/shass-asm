import sys
import os.path
import re

class CommandLineInputParser:
    def __init__(self):
        # get the argument for the main file
        self._main_file = ErrorHandler.getCommandLineArgument()
        # check that it exists
        ErrorHandler.checkFileExists(self._main_file)
    
    def getEntryFile(self):
        return self._main_file

class FirstPassParser:
    def __init__(self, entry_file):
        self._file_read = open(entry_file, "r")
        self._file_read_secondary = 0
        self._code_address = 0
        self._data_address = 0
        self._code_symbol_table = {}
        self._data_symbol_table = {}
        self._code_segment = True

    def setCodeOrigin(self, num):
        self._code_address = int(num)

    def setCodeSegment(self):
        self._code_segment = True

    def setDataSegment(self):
        self._code_segment = False

    def includeFile(self, filename):
        if self._file_read_secondary != 0:
            raise Exception("Cannot include into included files.")
        if filename == self._file_read.name:
            raise Exception("Cannot open file that is already being read.")
        self._file_read_secondary = open(filename, "r")
        self.parse(True)

    def parse(self, secondary_file = False):
        filestream = self._file_read_secondary if secondary_file else self._file_read
        line_num = 1
        while True:
            # read in lines until end of file is reached
            line = filestream.readline()
            if not line:
                break

            # Remove comments from parsing
            line += " "
            line = line[:line.find(';')]

            # Split the line on whitespace
            split_line = line.split()

            # check if line is empty
            if len(split_line) == 0:
                # if it is empty, don't increment code address
                self._code_address -= 1

            # Check if there is something in the first column
            elif not re.match(r'\s', line):
                if re.match(r'\.', line): # matches a pseudoop
                    try:
                        if len(split_line) > 1:
                            PseudoOp.handlePseudoOp(self, split_line[0], split_line[1])
                        else:
                            PseudoOp.handlePseudoOp(self, split_line[0])
                    except Exception as error:
                        ErrorHandler.genericError(filestream.name, line_num, error)

                elif split_line[0].isalnum():
                    if split_line[0] in self._code_symbol_table:
                        ErrorHandler.genericError(filestream.name, line_num, f"Label \"{split_line[0]}\" already exists.")
                    self._code_symbol_table[split_line[0]] = self._code_address
                else:
                    ErrorHandler.genericError(filestream.name, line_num, f"\"{split_line[0]}\" is not a valid statement"
                                                                          "on the first column.")
                self._code_address -= 1 # nothing in the first line increments code address
                    
            self._code_address += 1
            line_num += 1

class PseudoOp:
    def handlePseudoOp(parser, op, arg=""):
        if op == ".org":
            if not arg.isnumeric():
                raise Exception(f"Pseudo op \"{op}\" passed non-numeric argument: \"{arg}\"")
            parser.setCodeOrigin(arg)
        elif op == ".cseg":
            parser.setCodeSegment()
        elif op == ".dseg":
            parser.setDataSegment()
        elif op == ".include":
            if not os.path.isfile(arg):
                raise Exception(f"File \"{arg}\" does not exist.")
            parser.includeFile(arg)
        else:
            raise Exception(f"Pseudo op \"{op}\" does not exist.")


class ErrorHandler:
    def genericError(file, line_num, message):
        print(f"Error in file \"{file}\" on line {line_num}:")
        print("    ", message)
        quit()

    def getCommandLineArgument():
        try:
            return sys.argv[1]
        except:
            return "main.asm"

    def checkFileExists(file):
        if not os.path.isfile(file):
            print(f"File \"{file}\" does not exist.")
            quit()

# Start execution of the assembler
entry_file = CommandLineInputParser().getEntryFile()
first_parser = FirstPassParser(entry_file)
first_parser.parse()
print(first_parser._code_symbol_table)