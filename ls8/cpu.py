"""CPU functionality."""
import os
import sys

# Run method operations. Third bit from the left is a 0, so this is handled by the main run method.
CALL = 0b01010000
HLT = 0b00000001
IRET = 0b00010011   # Needs implementation
JEQ = 0b01010101   # 85
JMP = 0b01010100
JNE = 0b01010110   # Needs implementation
LDI = 0b10000010   # 130
POP = 0b01000110
PRA = 0b01001000   # Needs implementation
PRN = 0b01000111
PUSH = 0b01000101
RET = 0b00010001
ST = 0b10000100   # Needs implementation


# ALU operations. If the third bit from the left is a 1, we know we have an ALU operation.
ADD = 0b10100000
AND = 0b10101000
CMP = 0b10100111
DEC = 0b01100110
DIV = 0b10100011
INC = 0b01100101
MOD = 0b10100100
MUL = 0b10100010
NOT = 0b01101001
SHL = 0b10101100
SHR = 0b10101101
SUB = 0b10100001
XOR = 0b10101011


class CPU:

    """Main CPU class."""

    def __init__(self):

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

        self.fl = 0b00000000

        # This sets the register at self.reg[7] to 243. We can now say self.reg[]
        self.reg[self.stack_pointer] = 243

        self.running = False

        self.branch_table = {
            CALL: self.call_op,
            HLT:  self.halt_op,
            # IRET: self.interrupt_return_op,  # Needs implementation
            JEQ:  self.jeq_op,
            JMP:  self.jump_op,
            JNE:  self.jne_op,
            LDI:  self.ldi_op,
            POP:  self.pop_op,  # Needs implementation
            # PRA:  self.pra_op,  # Needs implementation
            PRN:  self.print_op,
            PUSH: self.push_op,  # Needs implementation
            # ST:   self.store_op,  # Needs implementation
        }

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
                # print(program)

            for instruction in program:
                self.ram[address] = instruction
                address += 1

        except FileNotFoundError:
            print(f"{sys.argv[1]} file not found!")
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):

        if op == ADD:
            self.reg[reg_a] += self.reg[reg_b]

        elif op == AND:
            self.reg[reg_a] &= self.reg[reg_b]

        elif op == CMP:
            if self.reg[reg_a] > self.reg[reg_b]:
                self.fl = 0b00000010
                # print("current flag: ", self.fl)

            elif self.reg[reg_a] < self.reg[reg_b]:
                self.fl = 0b00000100
                # print("current flag: ", self.fl)

            else:
                self.fl = 0b00000001
                # print("current flag: ", self.fl)

        elif op == DEC:
            self.reg[reg_a] -= 1

        elif op == DIV:
            if reg_b == 0:
                print("Cannot divide by zero!")
                self.running = False
                sys.exit(1)

            else:
                self.reg[reg_a] /= self.reg[reg_b]

        elif op == INC:
            self.reg[reg_a] += 1

        elif op == MOD:
            self.reg[reg_a] %= self.reg[reg_b]

        elif op == MUL:
            self.reg[reg_a] *= self.reg[reg_b]

        elif op == NOT:
            self.reg[reg_a] != self.reg[reg_b]

        elif op == SHL:
            self.reg[reg_a] <<= self.reg[reg_b]

        elif op == SHL:
            self.reg[reg_a] >>= self.reg[reg_b]

        elif op == SUB:
            self.reg[reg_a] -= self.reg[reg_b]

        elif op == XOR:
            self.reg[reg_a] ^= self.reg[reg_b]

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

    # Operation methods - Basically the op code will look up a value from the branch table and will be returned a function.

    def call_op(self, operand_a, operand_b):
        self.reg[self.stack_pointer] -= 1

        # Writing the return address at the location in memory of the stack pointer.
        self.ram_write(operand_b, self.reg[self.stack_pointer])

        # change the PC to the address in the provided register.
        self.pc = self.reg[operand_a]

    def jeq_op(self, operand_a, operand_b):
        # We're bringing in the next location in the

        # We use bitwise masking to grab only the bit we want - the Equals flag.
        equals = self.fl & 0b00000001
        # print("JEQ Equals value: ", equals)

        # If that flag is active, it means we want to jump to the location indicated on that register.
        if equals == 1:
            # We use our self.jump_op method to do that.
            self.jump_op(operand_a, operand_b)
        else:
            self.pc += 2

    def jne_op(self, operand_a, operand_b):
        # We use bitwise masking to grab only the bit we want - the Equals flag.
        equals = self.fl & 0b00000001
        # print("JNE Equals value: ", equals)

        # If that flag is inactive, it means we want to jump to the location indicated on the next register.
        if equals == 0:
            # We use our self.jump_op method to do that.
            self.jump_op(operand_a, operand_b)
        else:
            self.pc += 2

    # change the program counter to move to a different instruction.
    def jump_op(self, operand_a, operand_b):
        self.pc = self.reg[operand_a]
        # print("current program counter: ", self.pc)

    # Grab value from the top of the stack and use that to set the PC.
    def ret_op(self, operand_a, operand_b):
        self.pc = self.ram_read(self.reg[self.stack_pointer])
        self.reg[self.stack_pointer] += 1

    # Exits execution immediately.
    def halt_op(self, operand_a, operand_b):
        self.running = False

    # Print the value at the provided register.
    def print_op(self, operand_a, operand_b):
        print(f"Value at register location {operand_a}: {self.reg[operand_a]}")

    # Load data
    def ldi_op(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b

    def push_op(self, operand_a, operand_b):
        self.reg[self.stack_pointer] -= 1
        self.ram_write(self.reg[operand_a], self.stack_pointer)

    def pop_op(self, operand_a, operand_b):
        item = self.ram_read(self.stack_pointer)
        self.reg[operand_a] = item
        self.reg[self.stack_pointer] += 1

    # Here's the run function which basically powers the whole shebang. The Run method is the master controller. It decides what needs to happen and in which method.

    # Comparison flag setting

    def run(self):
        self.running = True
        self.pc = 0

        while self.running == True:

            instruction_register = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            # I can determine if my operation is something for the ALU by masking it.
            arithmetic_operation = (instruction_register >> 5) & 0b00000001

            # Basically I want it separated into two areas. If there's an arithmetic function, the ALU handles it.
            if arithmetic_operation == 1:
                self.alu(instruction_register, operand_a, operand_b)

            # If it isn't an arithmetic operation, I want the run function to handle it.

            elif instruction_register in self.branch_table:
                self.branch_table[instruction_register](
                    operand_a, operand_b)

            else:
                raise Exception(
                    f"Unsupported instruction: {instruction_register}")

            # If a program sets the program counter, we want to have a mask set up for that.
            increment_pc = (instruction_register >> 4) & 0b00000001

            if increment_pc == 0:
                num_args = instruction_register >> 6
                self.pc += (num_args + 1)
                # print("Current program counter: ", self.pc)
            print(self.reg)
