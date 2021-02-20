"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.pc = 0
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.fl =0b00000000 # 00000LGE
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
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "DIV":
            if self.reg[reg_b] != 0:
                self.reg[reg_a] /= self.reg[reg_b]
            else:
                print("Error: Cannot divide by 0")
                self.pc = [0b00000001] * len(self.pc)
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.fl = 0b00000001
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.fl = 0b00000100
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl = 0b00000010

            
        # Stretch
        elif op == "AND":
            self.reg[reg_a] = self.reg[reg_a] & self.reg[reg_b]
        elif op == "OR":
            self.reg[reg_a] = self.reg[reg_a] | self.reg[reg_b]
        elif op == "XOR":
            self.reg[reg_a] = self.reg[reg_a] ^ self.reg[reg_b]
        # elif op == "NOT":
        #     self.reg[reg_a] = self.reg[reg_a] ~ self.reg[reg_b]
        elif op == "SHL":
            self.reg[reg_a] = self.reg[reg_a] << self.reg[reg_b]
        elif op == "SHR":
            self.reg[reg_a] = self.reg[reg_a] >> self.reg[reg_b]
        elif op == "MOD":
            if self.reg[reg_b] != 0:
                self.reg[reg_a] = self.reg[reg_a] % self.reg[reg_b]
            else:
                print("Error: Cannot divide by 0")
                self.pc = [0b00000001] * len(self.pc)

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
        cInst = inst
        cInst = cInst & 0b00010000
        cInst = cInst >> 4
        if cInst != 0b0001:
            inst = inst & 0b11000000
            inst = inst >> 6
            return inst + 1
        else:
            return 0

    def run(self):
        HLT = 0b00000001
        LDI = 0b10000010 
        PRN = 0b01000111
        ALU = 0b001
        MUL = 0b10100010
        ADD = 0b10100000
        DIV = 0b10100011
        SUB = 0b10100000
        PUSH = 0b01000101
        POP = 0b01000110
        CALL = 0b01010000
        RET = 0b00010001
        CMP = 0b10100111
        JMP = 0b01010100
        JEQ = 0b01010101
        JNE = 0b01010110

        #STRETCH
        AND = 0b10101000
        OR = 0b10101010
        XOR = 0b10101011
        NOT = 0b01101001
        SHL = 0b10101100
        SHR = 0b10101101
        MOD = 0b10100100

        """Run the CPU."""
        running = True
        while running:
            if self.pc < len(self.ram):
                inst = self.ram[self.pc]

                if inst == HLT: 
                    print("HALT")
                    break

                elif inst == LDI:
                    # print('executing ldi')
                    reg_num = self.ram[self.pc + 1]
                    value = self.ram[self.pc + 2]
                    self.reg[reg_num] = value
                    #Original way (less clean): self.reg[self.ram[self.pc + 1]] = self.ram[self.pc+2]
                
                elif inst == PRN:
                    # print('executing prn')
                    reg_val = self.ram[self.pc + 1]
                    print(self.reg[reg_val])

                elif ((inst & 0b00100000) >> 5) == ALU:
                    # print('executing alu')
                    reg1 = self.ram[self.pc + 1]
                    reg2 = self.ram[self.pc + 2]
                    if inst == MUL:
                        # print('executing mul')
                        self.alu("MUL", reg1, reg2)
                    elif inst == ADD:
                        # print('executing add')
                        self.alu("ADD", reg1, reg2)
                    elif inst == DIV:
                        # print('executing div') 
                        self.alu("DIV", reg1, reg2)
                    elif inst == SUB: 
                        # print('executing sub')
                        self.alu("SUB", reg1, reg2)
                    elif inst == CMP:
                        # print('executing cmp')
                        self.alu("CMP", reg1, reg2)

                    # Stretch
                    elif inst == AND:
                        self.alu("AND", reg1, reg2)
                    elif inst == OR:
                        self.alu("OR", reg1, reg2)
                    elif inst == XOR:
                        self.alu("XOR", reg1, reg2)
                    elif inst == NOT:
                        self.alu("NOT", reg1, reg2)
                    elif inst == SHL:
                        self.alu("SHL", reg1, reg2)
                    elif inst == SHR:
                        self.alu("SHR", reg1, reg2)
                    elif inst == MOD:
                        self.alu("MOD", reg1, reg2)
                    

                
                elif inst == PUSH:
                    # print('executing push')
                    self.reg[self.SP] -= 1

                    reg_num = self.ram[self.pc + 1]
                    value = self.reg[reg_num]

                    push_address = self.reg[self.SP]
                    self.ram[push_address] = value

                elif inst == POP: 
                    # print('executing pop')
                    pop_address = self.reg[self.SP]
                    value = self.ram[pop_address]

                    reg_num = self.ram[self.pc + 1]
                    self.reg[reg_num] = value

                    self.reg[self.SP] += 1
                
                elif inst == CALL: 
                    # print('executing call')
                    ret_address = self.pc + 2

                    self.reg[self.SP] -= 1
                    address_to_push_to = self.reg[self.SP]
                    self.ram[address_to_push_to] = ret_address

                    reg_num = self.ram[self.pc+1]
                    subroutine_address = self.reg[reg_num]

                    self.pc = subroutine_address
                
                elif inst == RET:
                    # print('executing ret')
                    address_to_pop_from = self.reg[self.SP]
                    ret_address = self.ram[address_to_pop_from]
                    self.reg[self.SP] += 1

                    self.pc = ret_address
                
                elif inst == JMP:
                    # print('executing jmp')
                    jmp_address = self.ram[self.pc + 1]
                    self.pc = jmp_address
                
                elif inst == JEQ:
                    # print('executing jeq')
                    if self.fl & 0b00000001 == 0b00000001:
                        reg_num = self.ram[self.pc + 1]
                        jmp_address = self.reg[reg_num]
                        self.pc = jmp_address
                    else:
                        self.pc += 2

                elif inst == JNE:
                    # print('executing jne')
                    if self.fl & 0b00000001 == 0b00000000:
                        reg_num = self.ram[self.pc + 1]
                        jmp_address = self.reg[reg_num]
                        self.pc = jmp_address
                    else:
                        self.pc += 2


                else:
                    break
                    print(f"Unknown inst: {inst}")


                self.pc += self.increment_pc(inst)
            else:
                break
            

