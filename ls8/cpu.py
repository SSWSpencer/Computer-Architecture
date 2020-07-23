"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.pc = 0
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.SP = 7
        self.reg[self.SP] = 0xf4

    def load(self):
        """Load a program into memory."""

        try:
            with open(f"{sys.argv[-1]}") as f:
                address = 0
                for line in f:
                    try:
                        line = line.split("#",1)[0]
                        line = int(line, 2)
                        self.ram[address] = line
                        address+= 1
                    except ValueError:
                        pass
        except FileNotFoundError:
            print(f"Could not find file: {sys.argv[-1]}")
            sys.exit(1)


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()
    
    def ram_read(self, address):
        if address >= len(self.ram) or address < 0:
            print(f"Address out of range of ram")
        else:
            if self.ram[address]:
                return self.ram[address]
            else:
                return f"Nothing found at ram[{address}]"

    def ram_write(self, address, value):
        if address >= len(self.ram) or address < 0:
            return f"Address out of range of ram"
        else:
            self.ram[address] = value
    
    def increment_pc(self, inst):
        inst = inst & 0b11000000
        inst = inst >> 6
        return inst + 1

    def run(self):
        """Run the CPU."""
        running = True
        while running:
            if self.pc < len(self.ram):
                inst = self.ram[self.pc]
                if inst == 0b00000001: # HLT
                    print("HALT")
                    break
                elif inst == 0b10000010: # LDI
                    #print(f"executing ldi with {self.ram[self.pc + 1]}, {self.ram[self.pc + 2]}")
                    reg_num = self.ram[self.pc + 1]
                    value = self.ram[self.pc + 2]
                    self.reg[reg_num] = value
                    #Original way (less clean): self.reg[self.ram[self.pc + 1]] = self.ram[self.pc+2]
                
                elif inst == 0b01000111: #PRN
                    #print(f"executing print")
                    reg_val = self.ram[self.pc + 1]
                    print(self.reg[reg_val])

                elif inst == 0b10100010: # MULT
                    #print(f"executing mult with {self.ram[self.pc + 1]}, {self.ram[self.pc + 2]}")
                    reg1 = self.ram[self.pc + 1]
                    reg2 = self.ram[self.pc + 2]
                    val_1 = self.reg[reg1]
                    val_2 = self.reg[reg2]
                    prod = val_1 * val_2
                    self.reg[reg1] = prod
                
                elif inst == 0b01000101: # PUSH
                    self.reg[self.SP] -= 1

                    # get register value
                    reg_num = self.ram[self.pc + 1]
                    value = self.reg[reg_num]

                    # Store in memory
                    push_address = self.reg[self.SP]
                    self.ram[push_address] = value

                elif inst == 0b01000110: # POP
                    # Get the value
                    pop_address = self.reg[self.SP]
                    value = self.ram[pop_address]

                    # Store in the given register
                    reg_num = self.ram[self.pc + 1]
                    self.reg[reg_num] = value

                    # Increment SP
                    self.reg[self.SP] += 1
                
                else:
                    print(f"Unknown inst: {inst}")

                self.pc += self.increment_pc(inst)
            else:
                break
            

