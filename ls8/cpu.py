"""CPU functionality."""
import os
import sys

instructions = {
    "HLT":  0b00000001,
    "LDI":  0b10000010,
    "PRN":  0b01000111,
    "PUSH": 0b01000101,  # Needs implementation
    "POP":  0b01000110,  # Needs implementation
    "JMP":  0b01010100,  # Needs implementation
    "JNE":  0b01010110,  # Needs implementation
    "ST":   0b10000100,  # Needs implementation
    "PRA":  0b01001000,  # Needs implementation
    "IRET": 0b00010011,  # Needs implementation
}

math = {
    "ADD":  0b10100000,
    "AND":  0b10101000,  # Needs implementation
    "CMP":  0b10100111,  # Needs implementation
    "DEC":  0b01100110,  # Needs implementation
    "DIV":  0b10100011,
    "INC":  0b01100101,  # Needs implementation
    "MOD":  0b10100100,  # Needs implementation
    "MUL":  0b10100010,
    "SHL":  0b10101100,  # Needs implementation
    "SHR":  0b10101101,  # Needs implementation
    "SUB":  0b10100001,
    "XOR":  0b10101011,  # Needs implementation
}


class CPU:

    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""

        # general purpose registers: They store information we're currently working with.
        self.reg = [0] * 8

        # This is the program counter. We use this to keep track of where we are in our execution order.
        self.pc = 0

        # RAM will be used to store a list of programs.
        self.ram = [0] * 256

        # # Reserved as the interrupt mask (IM)
        # self.reg[5]

        # # Reserved as interrupt status (IS)
        # self.reg[6]

        # # Reserved as stack pointer (SP). This pointer will keep track of the place in the stack where our last item is living.
        # self.reg[stack_pointer]
        self.stack_pointer = 7

        self.running = False

    """Load will parse through a program that we've written and will add those instructions line by line in to the RAM at an address indicated by our address variable."""

    def load(self):
        """Load a program into memory."""

        address = 0

        try:
            if len(sys.argv) != 2:
                print("Usage: cpu.py filename")
                sys.exit(1)

            filename = sys.argv[1]

            with open(f'{filename}.ls8', 'r') as file:
                program = []

                for i in file:
                    if i[0] != "#" and i[0] != "\n":
                        # When we cast to int, we can specify a number base. In this case, we're specifying binary.
                        i = int(i[:8], 2)
                        program.append(i)
                print(program)

            for instruction in program:
                self.ram[address] = instruction
                address += 1

        except FileNotFoundError:
            print(f"{sys.argv[1]} file not found!")
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == math["ADD"]:
            self.reg[reg_a] += self.reg[reg_b]
            self.pc += 3

        elif op == math["SUB"]:
            self.reg[reg_a] -= self.reg[reg_b]
            self.pc += 3

        elif op == math["MUL"]:
            self.reg[reg_a] *= self.reg[reg_b]
            self.pc += 3

        elif op == math["DIV"]:
            if (self.reg[reg_b] == 0):
                print("Cannot divide by zero!")
                self.running = False
            else:
                self.reg[reg_a] //= self.reg[reg_b]
                self.pc += 3

        else:
            raise Exception("Unsupported ALU operation")

    # To read from our ram, we'll need to know where to look first.

    def ram_read(self, mar):
        # The mar holds the memory address we're reading from or writing to.
        return self.ram[mar]

    def ram_write(self, mar, mdr):
        # write the data (mdr) to the address (mar) in ram.
        self.ram[mar] = mdr

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        # self.trace()
        self.running = True
        self.pc = 0

        # Determine # of operands based on the first two digits of OP Code.
        # Number should be 1 plus the number of operands.

        while self.running == True:

            # This instruction register is where the actual instruction is located. When we do operations, we're essentially skipping from instruction register to instruction register.
            instruction_register = self.ram_read(self.pc)
            operand_a = self.ram[self.pc+1]
            operand_b = self.ram[self.pc+2]

            if instruction_register in math.values():
                self.alu(instruction_register, operand_a, operand_b)

            else:
                if instruction_register == instructions["LDI"]:
                    self.reg[operand_a] = operand_b
                    self.pc += 3

                elif instruction_register == instructions["PRN"]:
                    print(self.reg[operand_a])
                    self.pc += 2

                elif instruction_register == instructions["HLT"]:
                    self.running = False
                    self.pc += 1

                elif instruction_register == instructions["PUSH"]:
                    # If we're storing an item in the stack, we want to decrease the stack pointer because we're moving DOWN in memory towards the bottom.
                    # This is the stack pointer.
                    self.ram_write(self.reg[operand_a], self.stack_pointer)
                    self.stack_pointer -= 1

                elif instruction_register == instructions["POP"]:
                    # If we're removing an item FROM the stack, we want to INCREASE the stack pointer because we are moving UP towards the top of memory again.

                    # We're retrieving an item from the stack and putting it into a register.

                    # This is the stack pointer.
                    item = self.ram_read(self.stack_pointer)
                    self.reg[operand_a] = item
                    self.stack_pointer += 1

                else:
                    raise Exception(
                        f"Unsupported instruction: {instruction_register}")
