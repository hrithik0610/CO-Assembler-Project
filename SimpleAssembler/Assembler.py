import sys 

# 1. DICTIONARIES (ISA Definitions)

registers = {
    "x0": "00000", "zero": "00000",
    "x1": "00001", "ra": "00001",
    "x2": "00010", "sp": "00010",
    "x3": "00011", "gp": "00011",
    "x4": "00100", "tp": "00100",
    "x5": "00101", "t0": "00101",
    "x6": "00110", "t1": "00110",
    "x7": "00111", "t2": "00111",
    "x8": "01000", "s0": "01000", "fp": "01000",
    "x9": "01001", "s1": "01001",
    "x10": "01010", "a0": "01010",
    "x11": "01011", "a1": "01011",
    "x12": "01100", "a2": "01100",
    "x13": "01101", "a3": "01101",
    "x14": "01110", "a4": "01110",
    "x15": "01111", "a5": "01111",
    "x16": "10000", "a6": "10000",
    "x17": "10001", "a7": "10001",
    "x18": "10010", "s2": "10010",
    "x19": "10011", "s3": "10011",
    "x20": "10100", "s4": "10100",
    "x21": "10101", "s5": "10101",
    "x22": "10110", "s6": "10110",
    "x23": "10111", "s7": "10111",
    "x24": "11000", "s8": "11000",
    "x25": "11001", "s9": "11001",
    "x26": "11010", "s10": "11010",
    "x27": "11011", "s11": "11011",
    "x28": "11100", "t3": "11100",
    "x29": "11101", "t4": "11101",
    "x30": "11110", "t5": "11110",
    "x31": "11111", "t6": "11111"
}

opcode_dict = {
    "add": "0110011", "sub": "0110011", "sll": "0110011", "slt": "0110011",
    "sltu": "0110011", "xor": "0110011", "srl": "0110011", "or": "0110011", "and": "0110011",
    "lw": "0000011", "addi": "0010011", "sltiu": "0010011", "jalr": "1100111",
    "sw": "0100011",
    "beq": "1100011", "bne": "1100011", "blt": "1100011", "bge": "1100011", "bltu": "1100011", "bgeu": "1100011",
    "lui": "0110111", "auipc": "0010111",
    "jal": "1101111"
}

funct3_dict = {
    "add": "000", "sub": "000", "sll": "001", "slt": "010", "sltu": "011",
    "xor": "100", "srl": "101", "or": "110", "and": "111",
    "lw": "010", "addi": "000", "sltiu": "011", "jalr": "000",
    "sw": "010",
    "beq": "000", "bne": "001", "blt": "100", "bge": "101", "bltu": "110", "bgeu": "111"
}

funct7_dict = {
    "add": "0000000", "sub": "0100000", "sll": "0000000", "slt": "0000000",
    "sltu": "0000000", "xor": "0000000", "srl": "0000000", "or": "0000000", "and": "0000000"
}

# 2. FILE I/O AND CLEANING

def read_file(path):
    with open(path, "r") as f:
        return f.readlines()

def clean_lines(lines):
    cleaned = []
    for line in lines:
        line = line.strip()
        if line == "":
            continue
        cleaned.append(line)
    return cleaned

def write_output(path, binary_lines):
    with open(path, "w") as f:
        for line in binary_lines:
            f.write(line + "\n")

# 3. ERROR CHECKING

def is_valid_immediate(imm_string, bit_size):
    try:
        if "0x" in imm_string or "0X" in imm_string:
            val = int(imm_string, 16)
        else:
            val = int(imm_string)
        if bit_size == 12:
            if val < -2048 or val > 2047: return False
        elif bit_size == 20:
            if val < -1048576 or val > 1048575: return False
        return True
    except ValueError:
        return True 

def check_program_errors(lines):
    R_type = ["add", "sub", "slt", "sltu", "xor", "sll", "srl", "or", "and"]
    I_type = ["addi", "sltiu", "jalr"]
    I_type_load = ["lw"]
    S_type = ["sw"]
    B_type = ["beq", "bne", "blt", "bge", "bltu", "bgeu"]
    U_type = ["lui", "auipc"]
    J_type = ["jal"]
    
    valid_opcodes = R_type + I_type + I_type_load + S_type + B_type + U_type + J_type

    clean_lines = []
    original_line_numbers = []
    
    line_num = 1
    for line in lines:
        stripped_line = line.strip()
        if stripped_line != "": 
            clean_lines.append(stripped_line)
            original_line_numbers.append(line_num)
        line_num += 1

    if len(clean_lines) > 64:
        print("Error: Program memory overflow. Maximum 64 instructions allowed.")
        return False

    if len(clean_lines) == 0:
        print("Error: The input file is empty.")
        return False
    
    last_line = clean_lines[-1]
    if ":" in last_line:
        last_line = last_line.split(":")[1].strip()
        
    last_instr = last_line.replace(" ", "")
    if last_instr != "beqzero,zero,0x00000000" and last_instr != "beqzero,zero,0":
        print("Error: Virtual halt is not at the last instruction.")
        return False
    count = 0
    for i in range(len(clean_lines)):
        temp_line = clean_lines[i]
        if ":" in temp_line:
            temp_line = temp_line.split(":")[1].strip()
            
        temp_instr = temp_line.replace(" ", "")
        if temp_instr != "beqzero,zero,0x00000000" or temp_instr != "beqzero,zero,0":
            count += 1
            
    if count == 0:
        print(f"Error: Virtual halt is missing.")
        return False

    for i in range(len(clean_lines)):
        line = clean_lines[i]
        orig_num = original_line_numbers[i]

        if ":" in line:
            parts = line.split(":")
            line = parts[1].strip()

        clean_line = line.replace(",", " ").replace("(", " ").replace(")", " ")
        words = clean_line.split()

        if len(words) == 0:
            continue
            
        opcode = words[0]

        if opcode not in valid_opcodes:
            print(f"Error at line {orig_num}: Invalid instruction or typo '{opcode}'")
            return False

        args = words[1:]
        
        if opcode in R_type:
            if len(args) != 3:
                print(f"Error at line {orig_num}: {opcode} needs 3 operands.")
                return False
            for reg in args:
                if reg not in registers:
                    print(f"Error at line {orig_num}: Invalid register '{reg}'")
                    return False

        elif opcode in I_type:
            if len(args) != 3:
                print(f"Error at line {orig_num}: {opcode} needs 3 operands")
                return False
            if args[0] not in registers or args[1] not in registers:
                print(f"Error at line {orig_num}: Invalid register name")
                return False
            if not is_valid_immediate(args[2], 12):
                print(f"Error at line {orig_num}: Immediate number goes out of bounds")
                return False

        elif opcode in I_type_load or opcode in S_type:
            if len(args) != 3:
                print(f"Error at line {orig_num}: {opcode} needs 3 operands")
                return False
            if args[0] not in registers or args[2] not in registers:
                print(f"Error at line {orig_num}: Invalid register name")
                return False
            if not is_valid_immediate(args[1], 12):
                print(f"Error at line {orig_num}: Immediate number goes out of bounds")
                return False

        elif opcode in B_type:
            if len(args) != 3:
                print(f"Error at line {orig_num}: {opcode} needs 3 operands")
                return False
            if args[0] not in registers or args[1] not in registers:
                print(f"Error at line {orig_num}: Invalid register name")
                return False
            if not is_valid_immediate(args[2], 12):
                print(f"Error at line {orig_num}: Immediate number goes out of bounds")
                return False

        elif opcode in U_type or opcode in J_type:
            if len(args) != 2:
                print(f"Error at line {orig_num}: {opcode} needs 2 operands")
                return False
            if args[0] not in registers:
                print(f"Error at line {orig_num}: Invalid register name")
                return False
            if not is_valid_immediate(args[1], 20):
                print(f"Error at line {orig_num}: Immediate number goes out of bounds")
                return False

    return True



def dec_to_bin(num, bits):
    if num < 0: num = (1 << bits) + num
    return format(num, '0' + str(bits) + 'b')

def calc_offset(current_pc, label_address):
    return label_address - current_pc

def parse_imm(x):
    s = str(x).lower()
    if '0x' in s: return int(s, 16)
    return int(s)

def translate_S_type(parts):
    opc = parts[0]
    r2 = registers[parts[1]]
    imm_val = parse_imm(parts[2])
    r1 = registers[parts[3]]
    
    b_str = dec_to_bin(imm_val, 12)
    return str(b_str[:7]) + r2 + r1 + funct3_dict[opc] + str(b_str[7:12]) + opcode_dict[opc]

def translate_B_type(parts, labels, pc):
    op = parts[0]
    s1 = registers[parts[1]]
    s2 = registers[parts[2]]
    
    t = parts[3]
    if t in labels:
        v = calc_offset(pc, labels[t])
    else:
        v = parse_imm(t)
        
    b = dec_to_bin(v, 13)
    return b[0] + b[2:8] + s2 + s1 + funct3_dict[op] + b[8:12] + b[1] + opcode_dict[op]

def translate_U_type(parts):
    r_dest = registers[parts[1]]
    val = parse_imm(parts[2])
    return dec_to_bin(val, 20) + r_dest + opcode_dict[parts[0]]

def translate_J_type(parts, labels, pc):
    cmd = parts[0]
    dest = registers[parts[1]]
    targ = parts[2]
    
    v = calc_offset(pc, labels[targ]) if targ in labels else parse_imm(targ)
        
    bin_v = dec_to_bin(v, 21)
    res = bin_v[0] + bin_v[10:20] + bin_v[9] + bin_v[1:9] + dest + opcode_dict[cmd]
    return res
