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
