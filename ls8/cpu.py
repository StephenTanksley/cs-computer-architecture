"""CPU functionality."""
import os
import sys

instructions = {
    "HLT":  0b00000001,
    "IRET": 0b00010011,  # Needs implementation
    "JMP":  0b01010100,  # Needs implementation
    "JNE":  0b01010110,  # Needs implementation
    "LDI":  0b10000010,
    "POP":  0b01000110,  # Needs implementation
    "PRA":  0b01001000,  # Needs implementation
    "PRN":  0b01000111,
    "PUSH": 0b01000101,  # Needs implementation
    "ST":   0b10000100,  # Needs implementation
}

# Third bit from the left indicates an ALU operation. We can determine if
math = {
    "ADD":  0b10100000,
    "AND":  0b10101000,
    "CMP":  0b10100111,  # Needs implementation
    "DEC":  0b01100110,
    "DIV":  0b10100011,
    "INC":  0b01100101,
    "MOD":  0b10100100,
    "MUL":  0b10100010,
    "NOT":  0b01101001,
    "SHL":  0b10101100,
    "SHR":  0b10101101,
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

        # This sets the register at self.reg[7] to 243. We can now say self.reg[]
        self.reg[self.stack_pointer] = 243

        self.running = False

        self.branch_table = {
            "HLT": self.halt
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
                print(program)

            for instruction in program:
                self.ram[address] = instruction
                address += 1

        except FileNotFoundError:
            print(f"{sys.argv[1]} file not found!")
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):

        if op == math["ADD"]:
            self.reg[reg_a] += self.reg[reg_b]

        elif op == math["AND"]:
            self.reg[reg_a] &= self.reg[reg_b]

        elif op == math["DEC"]:
            self.reg[reg_a] -= 1

        elif op == math["DIV"]:
            if reg_b == 0:
                print("Cannot divide by zero!")
                self.running = False
                sys.exit(1)

            else:
                self.reg[reg_a] /= self.reg[reg_b]

        elif op == math["INC"]:
            self.reg[reg_a] += 1

        elif op == math["MOD"]:
            self.reg[reg_a] %= self.reg[reg_b]

        elif op == math["MUL"]:
            self.reg[reg_a] *= self.reg[reg_b]

        elif op == math["NOT"]:
            self.reg[reg_a] != self.reg[reg_b]

        elif op == math["SHL"]:
            self.reg[reg_a] <<= self.reg[reg_b]

        elif op == math["SHR"]:
            self.reg[reg_a] >>= self.reg[reg_b]

        elif op == math["SUB"]:
            self.reg[reg_a] -= self.reg[reg_b]

        elif op == math["XOR"]:
            self.reg[reg_a] ^= self.reg[reg_b]

        else:
            raise Exception("Unsupported ALU operation")

    # To read from our ram, we'll need to know where to look first.

    def ram_read(self, mar):
        # The mar holds the memory address we're reading from or writing to.
        print(self.ram[mar])
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

    def halt(self, operand_a, operand_b):
        # Exits execution immediately.
        self.running = False

    def print(self, operand_a, operand_b):
        print(self.reg[operand_a])

    def load_data(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b

    # Here's the run function which basically powers the whole shebang. The Run method is the master controller. It decides what needs to happen and in which method.

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

            # I can determine if my operation is something for the ALU by masking it.
            arithmetic_operation = (instruction_register >> 5) & 0b00000001

            # Basically I want it separated into two areas. If there's an arithmetic function, the ALU handles it.
            if arithmetic_operation:
                self.alu(instruction_register, operand_a, operand_b)

            # If it isn't an arithmetic operation, I want the run function to handle it.
            else:

                # I can just define the functions themselves and then pass along a reference to the function from the branch table.
                if instruction_register in self.branch_table:
                    self.branch_table[instruction_register](
                        operand_a, operand_b)

                # # All of these operations need to be moved to the branch table.
                # if instruction_register == instructions["LDI"]:
                #     self.reg[operand_a] = operand_b
                #     self.pc += 3

                # elif instruction_register == instructions["PRN"]:
                #     print(self.reg[operand_a])
                #     self.pc += 2

                # elif instruction_register == instructions["HLT"]:
                #     self.running = False
                #     self.pc += 1

                elif instruction_register == instructions["PUSH"]:
                    # If we're storing an item in the stack, we want to decrease the stack pointer because we're moving DOWN in memory towards the bottom.
                    # This is the stack pointer.
                    self.reg[self.stack_pointer] -= 1
                    self.ram_write(self.reg[operand_a], self.stack_pointer)

                elif instruction_register == instructions["POP"]:
                    # If we're removing an item FROM the stack, we want to INCREASE the stack pointer because we are moving UP towards the top of memory again.

                    # We're retrieving an item from the stack and putting it into a register.

                    # This is the stack pointer.
                    item = self.ram_read(self.stack_pointer)
                    self.reg[operand_a] = item
                    self.reg[self.stack_pointer] += 1

                else:
                    raise Exception(
                        f"Unsupported instruction: {instruction_register}")

                # If a program sets the program counter, we want to have a mask set up for that.
                set_pc = (instruction_register >> 4) & 0b00000001

                if set_pc == 0:
                    num_args = instruction_register >> 6
                    self.pc += num_args + 1
