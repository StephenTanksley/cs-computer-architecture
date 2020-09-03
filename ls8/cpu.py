"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""

        # general purpose registers: They store information we're currently working with.
        self.reg = [0] * 8

        # IR - Instruction Register: Holds a copy of the currently executing instruction.
        self.ir = None

        # MAR - Memory Address Register: Holds the memory address we're reading or writing.
        self.mar = None

        # MDR - Memory Data Register: Holds the value to write or the value just read.
        self.mdr = None

        # This is the program counter. We use this to keep track of where we are in our execution order.
        self.pc = 0

        # RAM will be used to store a list of programs.
        self.ram = [0] * 256

        # # Reserved as the interrupt mask (IM)
        # self.reg[5]

        # # Reserved as interrupt status (IS)
        # self.reg[6]

        # # Reserved as stack pointer (SP)
        # self.reg[7]

    """Load will parse through a program that we've written and will add those instructions line by line in to the RAM at an address indicated by our address variable."""

    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        program = [
            # From print8.ls8
            # This top instruction tells our CPU to do an operation (loading data). It then gives it the register to load that information into (R0). It then provides the information to load (the number 8).
            0b10000010,  # LDI R0,8
            0b00000000,
            0b00001000,

            # This next instruction will print whatever is located at the next provided register number (in this case reg[0]).
            0b01000111,  # PRN R0
            0b00000000,

            # At this point, we should have the number 8 printed to the screen. Once we advance the pc, we'll hit the HLT OP Code and terminate the program.
            0b00000001,  # HLT
        ]

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    """The arithmetic logic unit will perform mathematic operations on the registers. Should implement addition, subtraction, multiplication, division."""

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]

        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]

        elif op == "MULT":
            self.reg[reg_a] *= self.reg[reg_b]

        elif op == "DIV":
            self.reg[reg_a] //= self.reg[reg_b]

        else:
            raise Exception("Unsupported ALU operation")

    # To read from our ram, we'll need to know where to look first.

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, address, instruction):
        self.ram[address] = instruction
        print(f'{self.ram[address]} : {instruction}')

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

        running = True

        while running:
            instruction = self.ram[self.pc]

        # running = False
        """Run the CPU."""
        pass
