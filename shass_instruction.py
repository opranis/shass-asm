import re
from shass_error import *

class Opcode:
    """Generic parent class for handling an instruction by a given opcode."""

    # Constants for translating opcodes into bytecode
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
        """Returns the correct child class for a given opcode."""

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
    """Child opcode class for instructions with no operands."""

    def __init__(self, opcode, operand):
        super().__init__(opcode)
        if operand.getCount() != 0:
            raise Exception(f"Opcode {opcode} should have no arguments.")

    def __str__(self):
        return "{:04X}".format(Opcode.no_operand_codes[self._opcode])

class OneOperandOpcode(Opcode):
    """Child opcode class for instructions with a single operand."""

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
    """Child opcode class for instructions with a long (13-bit) single operand."""

    def __init__(self, opcode, operand):
        super().__init__(opcode)
        if operand.getCount() != 1:
            raise Exception(f"Opcode {opcode} should have 1 argument.")
        self._operand = operand

    def __str__(self):
        opcode_str = "{:03b}".format(Opcode.long_operand_codes[self._opcode])

        # Long operands correspond to absolute addresses, so pass with corresponding arg.
        operand_str = "{:013b}".format(self._operand.evaluateOneOperand(absolute = True))
        return "{:04X}".format(int(opcode_str + operand_str, 2))

class StLdOpcode(Opcode):
    """Child opcode class for store and load instructions."""

    def __init__(self, opcode, operand):
        super().__init__(opcode)
        if operand.getCount() != 2:
            raise Exception(f"Opcode {opcode} should have 2 arguments.")
        self._operand = operand

    def __str__(self):
        opcode_str = "{:03b}".format(Opcode.st_ld_codes[self._opcode])

        # Get the correct pattern for +X, -X, X+, X- etc.
        opcode_str += self._operand.sxPattern()

        # Evaluate other operand, but swap order, since it is the second one
        operand_str = "{:08b}".format(self._operand.evaluateOneOperand(swap = True))

        return "{:04X}".format(int(opcode_str + operand_str, 2))

class AluOpcode(Opcode):
    """Child opcode class for ALU instructions."""

    def __init__(self, opcode, operand):
        super().__init__(opcode)
        self._operand = operand

    def __str__(self):
        opcode_str = "{:06b}".format(Opcode.alu_codes[self._opcode])

        # If only a single operand given, it is absolute addressing
        if self._operand.getCount() == 1:
            opcode_str += "00"
            operand_str = "{:08b}".format(self._operand.evaluateOneOperand())

        # If X is passed as the first argument
        elif self._operand.aluX():
            opcode_str += "01"
            operand_str = "{:08b}".format(self._operand.evaluateOneOperand(swap = True))

        # If S is passed as the first argument
        else:
            opcode_str += "10"
            operand_str = "{:08b}".format(self._operand.evaluateOneOperand(swap = True))


        return "{:04X}".format(int(opcode_str + operand_str, 2))

class Operands:
    """Class handling the various types of operands passed to an instruction."""

    def __init__(self, operand_arr, dsym, csym, ip):
        if len(operand_arr) > 2:
            raise Exception("An instruction can have no more than 2 operands.")
        
        # Set number of operands passed
        self._op_count = len(operand_arr)

        # Set the operands themselves
        self._op1 = None if self._op_count == 0 else operand_arr[0]
        self._op2 = None if self._op_count < 2 else operand_arr[1]

        # Store data and code symbol tables
        self._dsym = dsym
        self._csym = csym

        # Store current instruction pointer
        self._ip = ip

    def getCount(self):
        """Return amount of operands given."""

        return self._op_count
    
    def aluX(self):
        """Return whether X or S is passed to an ALU instruction."""

        if self._op1 == "X":
            return True
        elif self._op1 == "S":
            return False
        else:
            raise Exception("First operand needs to be either \"S\" or \"X\".")

    def sxPattern(self):
        """Get store/load instruction pattern."""

        pat = re.search(r"[+-][SX]|[SX][+-]|[SX]", self._op1)
        pat = pat.group()

        # Check that the argument contains ONLY S/X and +/-
        if len(pat) != len(self._op1):
            raise Exception(f"Invalid argument: {self._op1}")
        
        # Set the correct pattern according to datasheet.
        prepost = "1" if len(pat) == 1 or pat[1] == "+" or pat[1] == "-" else "0"
        incdec = "0" if len(pat) == 1 or pat[0] == "+" or pat[1] == "+" else "1"
        sx = "0" if "S" in pat else "1" 
        addrmode = "11" if len(pat) == 1 else "10"

        return prepost+incdec+sx+addrmode
    
    def evaluateOneOperand(self, absolute = False, swap = False):
        """Evaluate a single generic operand"""

        # Absolute: no difference between label and IP should be calculated
        # Swap: the argument is given as the second one

        # Return value initially zero.
        num = 0

        op = self._op1 if not swap else self._op2

        # immediate value - just copy in
        if op.isnumeric():
            num = int(op)

        # If in the code symbol table
        elif op in self._csym:
            num = self._csym[op]
            
            # relative jump - calculate offset
            if not absolute:
                num = num - self._ip - 1

                # If negative, two's complement
                if num < 0:
                    num = (1<<8) + num

        # variable - look up and copy in
        elif op in self._dsym:
            num = self._dsym[op]

        # instruction pointer - just copy in
        elif op == ".IP":
            num = self._ip

            # relative jump - calculate offset
            if not absolute:
                num = num - self._ip - 1

                # If negative, two's complement
                if num < 0:
                    num = (1<<8) + num
        else:
            raise Exception("Invalid argument given.")
        
        # Check for a valid range for 13 or 8 bit number
        if not (0 <= num <= 8191 if absolute else 255):
            raise Exception("Argument outside range.")

        return num
    
class PseudoOp:
    """Handles a pseudo-op operation."""

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
            ErrorHandler.checkFileExists(arg, True)
            parser.includeFile(arg)
        else:
            raise Exception(f"Pseudo op \"{op}\" does not exist.")