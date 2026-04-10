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
