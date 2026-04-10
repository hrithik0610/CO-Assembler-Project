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
