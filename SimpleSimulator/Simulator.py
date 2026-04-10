import sys


# READ INPUT FILE

def read_file(path):
    with open(path, "r") as f:
        return [line.strip() for line in f if line.strip() != ""]

# SIGN EXTENSION

def sign_extend(value, bits):
    if value & (1 << (bits - 1)):
        value = value - (1 << bits)
    return value

# PRINT STATE

def print_state(pc, registers, outfile):
    line = format(pc, '032b')
    for reg in registers:
        line += " " + format(reg & 0xFFFFFFFF, '032b')
    outfile.write(line + "\n")


# PRINT MEMORY

def print_memory(memory, outfile):
    base = 0x00010000
    for i in range(32):
        addr = base + i * 4
        val = format(memory[i] & 0xFFFFFFFF, '032b')
        outfile.write(f"{hex(addr)}: {val}\n")

# HALT CHECK

def is_halt(instr):
    opcode = instr[25:32]
    if opcode != "1100011":
        return False

    rs1 = int(instr[12:17], 2)
    rs2 = int(instr[7:12], 2)

    imm = instr[0:7] + instr[20:25]

    return rs1 == 0 and rs2 == 0 and int(imm, 2) == 0


def execute_instruction(instr, pc, registers, memory):

    opcode = instr[25:32]
    rd = int(instr[20:25], 2)
    funct3 = instr[17:20]
    rs1 = int(instr[12:17], 2)
    rs2 = int(instr[7:12], 2)
    funct7 = instr[0:7]

    # R-TYPE
    if opcode == "0110011":

        if funct3 == "000":
            if funct7 == "0000000": # add
                registers[rd] = registers[rs1] + registers[rs2]
            elif funct7 == "0100000": # sub
                registers[rd] = registers[rs1] - registers[rs2]

        elif funct3 == "010": # slt
            registers[rd] = int(registers[rs1] < registers[rs2])

        elif funct3 == "011": # sltu
            registers[rd] = int((registers[rs1] & 0xFFFFFFFF) < (registers[rs2] & 0xFFFFFFFF))

        elif funct3 == "100": #xor
            registers[rd] = registers[rs1] ^ registers[rs2]

        elif funct3 == "110": #or
            registers[rd] = registers[rs1] | registers[rs2]

        elif funct3 == "111": #and
            registers[rd] = registers[rs1] & registers[rs2]

        elif funct3 == "001": #sll
            registers[rd] = registers[rs1] << (registers[rs2] & 0x1F)

        elif funct3 == "101": #srl
            registers[rd] = (registers[rs1] & 0xFFFFFFFF) >> (registers[rs2] & 0x1F)

        pc += 4

    # I-TYPE 
    elif opcode == "0010011":  # addi, sltiu

        imm = sign_extend(int(instr[0:12], 2), 12)

        if funct3 == "000":  # addi
            registers[rd] = registers[rs1] + imm

        elif funct3 == "011":  # sltiu
            registers[rd] = int((registers[rs1] & 0xFFFFFFFF) < (imm & 0xFFFFFFFF))

        pc += 4

    # LOAD
    elif opcode == "0000011":  # lw

        imm = sign_extend(int(instr[0:12], 2), 12)
        addr = registers[rs1] + imm
        registers[rd] = memory[addr // 4]

        pc += 4

    # STORE
    elif opcode == "0100011":  # sw

        imm = int(instr[0:7] + instr[20:25], 2)
        imm = sign_extend(imm, 12)

        addr = registers[rs1] + imm
        memory[addr // 4] = registers[rs2]

        pc += 4