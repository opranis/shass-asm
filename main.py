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

class Parser:
    def __init__(self, entry_file):
        self._file_read = open(entry_file, "r")
        self._file_read_secondary = 0
        self._code_address = 0
        self._data_address = 0
        self._code_symbol_table = {}
        self._data_symbol_table = {}
        self._code_segment = True
        self._second_parse = False
        self._outputFileStream = None

    def setCodeOrigin(self, num):
        if not self._code_segment:
            raise Exception("\".org\" cannot be set in a data segment!")
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
        
        currentSeg = self._code_segment
        self.setCodeSegment()
        self._file_read_secondary = open(filename, "r")
        self._parse(True)
        self._file_read_secondary.close()
        self._file_read_secondary = 0
        self._code_segment = currentSeg

    def _parsePseudoOp(self, split_line, line_num, fin):
        try:
            if len(split_line) > 1:
                PseudoOp.handlePseudoOp(self, split_line[0], split_line[1])
            else:
                PseudoOp.handlePseudoOp(self, split_line[0])
        except Exception as error:
            ErrorHandler.genericError(fin.name, line_num, error)

    def _codeGen(self, strarr, line_num, fin):
        try:
            operands = Operands(strarr[1:], self._data_symbol_table, self._code_symbol_table, self._code_address)
            self._outputFileStream.writeLine("{:04X}  ".format(self._code_address) + str(Opcode.opcodeFactory(strarr[0], operands)))
        except Exception as error:
            ErrorHandler.genericError(fin.name, line_num, error)


    def _parseCodeSeg(self, line, split_line, line_num, fin):

        # line is indented
        if re.match(r'\s', line):
            if self._second_parse:
                self._codeGen(split_line, line_num, fin)

            self._code_address += 1

        # if there is something in the first column
        else:
            if re.match(r'\.', line): # matches a pseudoop
                self._parsePseudoOp(split_line, line_num, fin)
            elif not self._second_parse:
                if split_line[0].isalnum():
                    if split_line[0] in self._code_symbol_table:
                        ErrorHandler.genericError(fin.name, line_num, f"Label \"{split_line[0]}\" already defined.")
                    self._code_symbol_table[split_line[0]] = self._code_address
                else:
                    ErrorHandler.genericError(fin.name, line_num, f"\"{split_line[0]}\" is not a valid statement"
                                                                        "on the first column.")
        
            

    def _parseDataSeg(self, line, split_line, line_num, fin):

        # Check if there is something in the first column
        if not re.match(r'\s', line):
            if re.match(r'\.', line): # matches a pseudoop
                self._parsePseudoOp(split_line, line_num, fin)
            elif not self._second_parse:
                if split_line[0].isalnum():
                    if split_line[0] in self._data_symbol_table:
                        ErrorHandler.genericError(fin.name, line_num, f"Variable \"{split_line[0]}\" already defined.")
                    self._data_symbol_table[split_line[0]] = self._data_address
                    if len(split_line) < 2 or not split_line[1].isnumeric():
                        ErrorHandler.genericError(fin.name, line_num, "Invalid variable length supplied.")
                    self._data_address += int(split_line[1])
                else:
                    ErrorHandler.genericError(fin.name, line_num, f"\"{split_line[0]}\" is not a valid statement"
                                                                        "on the first column.")
                
        # data segment should not have any lines with text starting after first column
        else:
            ErrorHandler.genericError(fin.name, line_num, "All valid statements in data segment "
                                                          "should start on first column.")


    def _parse(self, secondary_file = False):
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

            if len(split_line) > 0:
                if self._code_segment:
                    self._parseCodeSeg(line, split_line, line_num, filestream)
                else:
                    self._parseDataSeg(line, split_line, line_num, filestream)
                
            line_num += 1

    def first_parse(self):
        self._parse()

    def second_parse(self, f):
        self._second_parse = True
        self._code_address = 0
        self._data_address = 0
        self._code_segment = True
        self._outputFileStream = f
        self._file_read.seek(0)
        self._parse()
        self._file_read.close()

class Opcode:
    no_operand_codes = {
        "ASR": 0b0111000100000001,
        "DEC": 0b0111101100000000,
        "INC": 0b0000000000000000,
        "LSL": 0b0101100000000000,
        "LSR": 0b0111000100000000,
        "NEG": 0b0010011100000000,
        "NOT": 0b0010110100000000,
        "RLC": 0b0101000000000000,
        "ROL": 0b0101001000000000,
        "ROR": 0b0111000100000010,
        "RRC": 0b0111000100000011,
        "STI": 0b0111111110000001,
        "CLI": 0b0000011101101001,
        "STU": 0b0111111100100010,
        "CLU": 0b0000011111001010,
        "STC": 0b0111111100001100,
        "CLC": 0b0000011111100100,
        "TAX": 0b0000011110000000,
        "TXA": 0b0110011100000001,
        "INX": 0b0000010110000000,
        "DEX": 0b0000110110000000,
        "TAS": 0b0000011101010000,
        "TSA": 0b0110011100000000,
        "INS": 0b0000011001000000,
        "DES": 0b0000111001000000,
        "RTS": 0b0001111100000000,
        "POPF": 0b0000001000000000,
        "PUSHF": 0b0000111000000000,
        "NOP": 0b0001111110000000
    }
    one_operand_codes = {
        "ADCI": 0b01100011,
        "ADDI": 0b01101011,
        "ANDI": 0b01000111,
        "CMPI": 0b00110011,
        "ORI": 0b01110111,
        "SBBI": 0b00011011,
        "SUBI": 0b00010011,
        "TSTI": 0b01001111,
        "XORI": 0b00110111,
        "LDI": 0b10001001,
        "LDD": 0b10000000,
        "STD": 0b10100000,
        "JA": 0b10001000,
        "JNC": 0b10001100,
        "JAE": 0b10001100,
        "JC": 0b10001111,
        "JB": 0b10001111,
        "JBE": 0b10001011,
        "JE": 0b10011111,
        "JZ": 0b10011111,
        "JG": 0b10101111,
        "JGE": 0b10111011,
        "JL": 0b10111000,
        "JLE": 0b10101100,
        "JNZ": 0b10011100,
        "JNE": 0b10011100,
        "JNS": 0b10011000,
        "JNU": 0b10111100,
        "JNV": 0b10101000,
        "JS": 0b10011011,
        "JU": 0b10111111,
        "JV": 0b10101011,
        "IN": 0b10010000,
        "OUT": 0b10110000,
        
    }
    long_operand_codes = {
        "JMP": 0b110,
        "CALL": 0b111
    }
    st_ld_codes = {
        "ST": 0b101,
        "LD": 0b100
    }
    alu_codes = {
        "ADC": 0b011000,
        "ADD": 0b011010,
        "AND": 0b010001,
        "CMP": 0b001100,
        "OR": 0b011101,
        "SBB": 0b000110,
        "SUB": 0b000100,
        "TST": 0b010011,
        "XOR": 0b001101
    }

    def __init__(self, opcode):
        self._opcode = opcode

    def opcodeFactory(opcode, operand):
        if opcode in Opcode.no_operand_codes:
            return NoOperandOpcode(opcode, operand)
        elif opcode in Opcode.one_operand_codes:
            return OneOperandOpcode(opcode, operand)
        elif opcode in Opcode.long_operand_codes:
            return LongOperandOpcode(opcode, operand)
        elif opcode in Opcode.st_ld_codes:
            return StLdOpcode(opcode, operand)
        elif opcode in Opcode.alu_codes:
            return AluOpcode(opcode, operand)
        else:
            raise Exception(f"Opcode {opcode} is not defined.")

class NoOperandOpcode(Opcode):
    def __init__(self, opcode, operand):
        super().__init__(opcode)
        if operand.getCount() != 0:
            raise Exception(f"Opcode {opcode} should have no arguments.")

    def __str__(self):
        return "{:04X}".format(Opcode.no_operand_codes[self._opcode])

class OneOperandOpcode(Opcode):
    def __init__(self, opcode, operand):
        super().__init__(opcode)
        if operand.getCount() != 1:
            raise Exception(f"Opcode {opcode} should have 1 argument.")
        self._operand = operand

    def __str__(self):
        opcode_str = "{:02X}".format(Opcode.one_operand_codes[self._opcode])
        operand_str = "{:02X}".format(self._operand.evaluateOneOperand())
        return opcode_str + operand_str

class LongOperandOpcode(Opcode):
    def __init__(self, opcode, operand):
        super().__init__(opcode)
        if operand.getCount() != 1:
            raise Exception(f"Opcode {opcode} should have 1 argument.")
        self._operand = operand

    def __str__(self):
        opcode_str = "{:03b}".format(Opcode.long_operand_codes[self._opcode])
        operand_str = "{:013b}".format(self._operand.evaluateOneOperand(absolute = True))
        return "{:04X}".format(int(opcode_str + operand_str, 2))

class StLdOpcode(Opcode):
    def __init__(self, opcode, operand):
        super().__init__(opcode)
        if operand.getCount() != 2:
            raise Exception(f"Opcode {opcode} should have 2 arguments.")
        self._operand = operand

    def __str__(self):
        opcode_str = "{:03b}".format(Opcode.st_ld_codes[self._opcode])
        opcode_str += self._operand.sxPattern()
        operand_str = "{:08b}".format(self._operand.evaluateOneOperand(swap = True))
        return "{:04X}".format(int(opcode_str + operand_str, 2))

class AluOpcode(Opcode):
    def __init__(self, opcode, operand):
        super().__init__(opcode)
        self._operand = operand

    def __str__(self):
        opcode_str = "{:06b}".format(Opcode.alu_codes[self._opcode])
        if self._operand.getCount() == 1:
            opcode_str += "00"
            operand_str = "{:08b}".format(self._operand.evaluateOneOperand())
        elif self._operand.aluX():
            opcode_str += "01"
            operand_str = "{:08b}".format(self._operand.evaluateOneOperand(swap = True))
        else:
            opcode_str += "10"
            operand_str = "{:08b}".format(self._operand.evaluateOneOperand(swap = True))
        return "{:04X}".format(int(opcode_str + operand_str, 2))


class Operands:
    def __init__(self, operand_arr, dsym, csym, ip):
        if len(operand_arr) > 2:
            raise Exception("An instruction can have no more than 2 operands.")
        
        self._op_count = len(operand_arr)
        self._op1 = None if self._op_count == 0 else operand_arr[0]
        self._op2 = None if self._op_count < 2 else operand_arr[1]
        self._dsym = dsym
        self._csym = csym
        self._ip = ip

    def getCount(self):
        return self._op_count
    
    def aluX(self):
        if self._op1 == "X":
            return True
        elif self._op1 == "S":
            return False
        else:
            raise Exception("First operand needs to be either \"S\" or \"X\".")

    def sxPattern(self):
        pat = re.search(r"[+-][SX]|[SX][+-]|[SX]", self._op1)
        pat = pat.group()

        if len(pat) != len(self._op1):
            raise Exception(f"Invalid argument: {self._op1}")
        
        prepost = "1" if len(pat) == 1 or pat[1] == "+" or pat[1] == "-" else "0"
        incdec = "0" if len(pat) == 1 or pat[0] == "+" or pat[1] == "+" else "1"
        sx = "0" if "S" in pat else "1" 
        addrmode = "11" if len(pat) == 1 else "10"

        return prepost+incdec+sx+addrmode
    
    def evaluateOneOperand(self, absolute = False, swap = False):
        num = 0
        op = self._op1 if not swap else self._op2
        if op.isnumeric():
            # immediate value - just copy in
            num = int(op)
        elif op in self._csym:
            num = self._csym[op]
            
            # relative jump - calculate offset
            if not absolute:
                num = num - self._ip - 1
                if num < 0:
                    num = (1<<8) + num

        elif op in self._dsym:
            # variable - look up and copy in
            num = self._dsym[op]
        elif op == ".IP":
            # instruction pointer - just copy in
            num = self._ip
        else:
            raise Exception("Invalid argument given.")
        
        if not (0 <= num <= 8191 if absolute else 255):
            raise Exception("Argument outside range.")

        return num

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

class FileWriter:
    def __init__(self):
        self.filewrite = open("a.obj", "w")

    def writeLine(self, str):
        self.filewrite.write(str + "\n")

    def close(self):
        self.writeLine("")
        self.filewrite.close()

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
parser = Parser(entry_file)

f = FileWriter()

parser.first_parse()
parser.second_parse(f)

f.close()

print("Assembler finished successfully!")