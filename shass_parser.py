from shass_instruction import *
from shass_error import *

"""\
This file contains the Parser class used for bulk of the parsing
of the assembly files.
"""

class Parser:
    def __init__(self, entry_file):

        # the input file stream
        self._file_read = open(entry_file, "r")

        # the secondary file stream
        #   from .include pseudo operations
        self._file_read_secondary = 0

        # keeps track of the current location in code space
        self._code_address = 0

        # keeps track of the current location in data space
        self._data_address = 0

        # symbol table for keeping track of labels
        self._code_symbol_table = {}

        # symbol table for keeping track of variables
        self._data_symbol_table = {}

        # indicates whether parsing should be done as .cseg or .dseg
        self._code_segment = True

        # indicates whether the second pass is being done
        self._second_parse = False

        # the output file stream, initially none for first pass
        self._outputFileStream = None

    def setCodeOrigin(self, num):
        """Called by .org pseudo-op"""

        if not self._code_segment:
            raise Exception("\".org\" cannot be set in a data segment!")
        self._code_address = int(num)

    def setCodeSegment(self):
        """Called by .cseg pseudo-op"""

        self._code_segment = True

    def setDataSegment(self):
        """Called by .dseg pseudo-op"""

        self._code_segment = False

    def includeFile(self, filename):
        """Called by .include pseudo-op"""

        # Includes can only be used in the top-level asm file.
        if self._file_read_secondary != 0:
            raise Exception("Cannot include into included files.")
        if filename == self._file_read.name:
            raise Exception("Cannot open file that is already being read.")
        
        # by default, file starts at code segment
        # so need preserving the outer file segment type
        currentSeg = self._code_segment
        self.setCodeSegment()

        # set the secondary file stream
        self._file_read_secondary = open(filename, "r")

        # parse as secondary file
        self._parse(secondary_file=True)

        # after parsing is done, close the filestream
        self._file_read_secondary.close()

        # and indicate that no secondary parsing is being done
        self._file_read_secondary = 0

        # reset outer file segment type
        self._code_segment = currentSeg

    def _parsePseudoOp(self, split_line, line_num, fin):
        """Parses a pseudo-op type statement."""

        # Depending on how many arguments given, call with one or none args
        try:
            if len(split_line) > 1:
                PseudoOp.handlePseudoOp(self, split_line[0], split_line[1])
            else:
                PseudoOp.handlePseudoOp(self, split_line[0])
        except Exception as error:
            ErrorHandler.genericError(fin.name, line_num, error)

    def _codeGen(self, strarr, line_num, fin, rawline):
        """Perform actual line writes to the output object file"""
        try:
            # get operands from Operands class
            operands = Operands(strarr[1:], self._data_symbol_table, self._code_symbol_table, self._code_address)
            # get the actual hex code output from Opcode, and concat with current code address
            code_out = "{:04X}  ".format(self._code_address) + str(Opcode.opcodeFactory(strarr[0], operands))
            # Finally, write to file
            self._outputFileStream.writeLine(code_out + ";     " + rawline.strip())
        except Exception as error:
            ErrorHandler.genericError(fin.name, line_num, error)


    def _parseCodeSeg(self, line, split_line, line_num, fin):
        """Parse code segment section."""

        # line is indented
        if re.match(r'\s', line):

            # if the second parse, means code generation should happen
            if self._second_parse:
                self._codeGen(split_line, line_num, fin, line)

            # line is handled, so code address should increment
            self._code_address += 1

        # if there is something in the first column
        else:

            # if starts with period, matches a pseudoop
            if re.match(r'\.', line):
                self._parsePseudoOp(split_line, line_num, fin)

            # if we are on the first parse, should handle labels
            elif not self._second_parse:

                # check if only contains alphanumeric characters, not only numbers
                if split_line[0].isalnum() and not split_line[0].isnumeric():

                    # check if label not already defined
                    if split_line[0] in self._code_symbol_table:
                        ErrorHandler.genericError(fin.name, line_num, f"Label \"{split_line[0]}\" already defined.")

                    # Save in symbol table
                    self._code_symbol_table[split_line[0]] = self._code_address

                # Invalid statement (contains special characters)
                else:
                    ErrorHandler.genericError(fin.name, line_num, f"\"{split_line[0]}\" is not a valid statement"
                                                                        "on the first column.")
                    
            # We are on the second parse, so output the current address for user-readable
            # object code. All errors should already be caught in the first parse.
            else:
                self._outputFileStream.writeLine("          ; " + split_line[0])

    def _parseDataSeg(self, line, split_line, line_num, fin):
        """Parse data segment section."""

        # Check if there is something in the first column
        if not re.match(r'\s', line):

            # Begins with a period - pseudoop
            if re.match(r'\.', line):
                self._parsePseudoOp(split_line, line_num, fin)

            # Otherwise, if on the first parse, update variable symbol table
            elif not self._second_parse:

                # check for only valid characters, and not only numeric characters
                if split_line[0].isalnum() and not split_line[0].isnumeric():

                    # check not already defined
                    if split_line[0] in self._data_symbol_table:
                        ErrorHandler.genericError(fin.name, line_num, f"Variable \"{split_line[0]}\" already defined.")

                    # Update symbol table
                    self._data_symbol_table[split_line[0]] = self._data_address

                    # check that the length of the variable supplied correctly
                    if len(split_line) < 2 or not split_line[1].isnumeric():
                        ErrorHandler.genericError(fin.name, line_num, "Invalid variable length supplied.")

                    # Increment location in data segment.
                    self._data_address += int(split_line[1])

                # Does not match anything legal - throw an error
                else:
                    ErrorHandler.genericError(fin.name, line_num, f"\"{split_line[0]}\" is not a valid statement"
                                                                        "on the first column.")
                
        # data segment should not have any lines with text starting after first column
        else:
            ErrorHandler.genericError(fin.name, line_num, "All valid statements in data segment "
                                                          "should start on first column.")


    def _parse(self, secondary_file = False):
        """Main parsing entry, for both passes"""

        # If there is a secondary file present (from an include), that should
        # be parsed first. Otherwise parse the main file.
        filestream = self._file_read_secondary if secondary_file else self._file_read

        # Start on line number 1.
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

            # If the line is not empty, parse in either code or data segment.
            if len(split_line) > 0:
                if self._code_segment:
                    self._parseCodeSeg(line, split_line, line_num, filestream)
                else:
                    self._parseDataSeg(line, split_line, line_num, filestream)
                
            # Parsing complete, move on to the next line
            line_num += 1

    def first_parse(self):
        """Perform the first pass. Should be called before second_parse()"""
        self._parse()

    def second_parse(self, f):
        """Perform the second pass. Should be called after first_parse()"""

        # Indicate second pass.
        self._second_parse = True

        # Reinitialize code and address locations.
        self._code_address = 0
        self._data_address = 0

        # By default start at code segment again.
        self._code_segment = True

        # Specify output file stream.
        self._outputFileStream = f

        # Restart reading main file from beginning again.
        self._file_read.seek(0)

        # And parse.
        self._parse()
        self._file_read.close()