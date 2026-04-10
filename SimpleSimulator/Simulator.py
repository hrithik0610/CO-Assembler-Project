import sys

# PERSON 2 — Instruction Decoding

def sign_extend(val, src_bits):
    if val & (1 << (src_bits - 1)):
        val -= (1 << src_bits)
    return val


def decode_instruction(instr_bin):

    opcode = instr_bin[25:32]
    rd = int(instr_bin[20:25], 2)
    funct3 = instr_bin[17:20]
    rs1 = int(instr_bin[12:17], 2)
    rs2 = int(instr_bin[7:12],  2)
    funct7 = instr_bin[0:7]

    # I-type immediate
    imm_i = sign_extend(int(instr_bin[0:12], 2), 12)

    # S-type immediate
    imm_s = sign_extend(int(instr_bin[0:7] + instr_bin[20:25], 2), 12)

    # B-type immediate
    b12   = instr_bin[0]
    b11   = instr_bin[24]
    b10_5 = instr_bin[1:7]
    b4_1  = instr_bin[20:24]
    imm_b = sign_extend(int(b12 + b11 + b10_5 + b4_1 + '0', 2), 13)

    # U-type immediate
    imm_u = sign_extend(int(instr_bin[0:20], 2) << 12, 32)

    # J-type immediate
    j20    = instr_bin[0]
    j10_1  = instr_bin[1:11]
    j11    = instr_bin[11]
    j19_12 = instr_bin[12:20]
    imm_j  = sign_extend(int(j20 + j19_12 + j11 + j10_1 + '0', 2), 21)

    result = {
        "rd": rd, "rs1": rs1, "rs2": rs2,
        "funct3": funct3, "funct7": funct7,
        "imm": 0, "type": "", "instr": ""
    }

    # R-type
    if opcode == "0110011":
        result["type"] = "R"
        result["imm"]  = 0
        mapping = {
            ("000", "0000000"): "add",
            ("000", "0100000"): "sub",
            ("001", "0000000"): "sll",
            ("010", "0000000"): "slt",
            ("011", "0000000"): "sltu",
            ("100", "0000000"): "xor",
            ("101", "0000000"): "srl",
            ("110", "0000000"): "or",
            ("111", "0000000"): "and",
        }
        result["instr"] = mapping.get((funct3, funct7), "unknown_R")

    # I-type: loads
    elif opcode == "0000011":
        result["type"]  = "I"
        result["imm"]   = imm_i
        result["instr"] = "lw" if funct3 == "010" else "unknown_load"

    # I-type: arithmetic
    elif opcode == "0010011":
        result["type"] = "I"
        result["imm"]  = imm_i
        mapping = {"000": "addi", "011": "sltiu"}
        result["instr"] = mapping.get(funct3, "unknown_I")

    # I-type: jalr
    elif opcode == "1100111":
        result["type"]  = "I"
        result["imm"]   = imm_i
        result["instr"] = "jalr"

    # S-type
    elif opcode == "0100011":
        result["type"]  = "S"
        result["imm"]   = imm_s
        result["instr"] = "sw" if funct3 == "010" else "unknown_S"

    # B-type
    elif opcode == "1100011":
        result["type"] = "B"
        result["imm"]  = imm_b
        mapping = {
            "000": "beq", "001": "bne", "100": "blt",
            "101": "bge", "110": "bltu", "111": "bgeu"
        }
        result["instr"] = mapping.get(funct3, "unknown_B")

    # U-type: lui
    elif opcode == "0110111":
        result["type"]  = "U"
        result["imm"]   = imm_u
        result["instr"] = "lui"

    # U-type: auipc
    elif opcode == "0010111":
        result["type"]  = "U"
        result["imm"]   = imm_u
        result["instr"] = "auipc"

    # J-type: jal
    elif opcode == "1101111":
        result["type"]  = "J"
        result["imm"]   = imm_j
        result["instr"] = "jal"

    else:
        result["type"]  = "UNKNOWN"
        result["instr"] = "unknown"

    return result


# PERSON 3 — R, I, S Type Execution


DATA_MEM_BASE = 0x00010000
DATA_MEM_END  = 0x0001007F
STACK_BASE    = 0x00000100
STACK_END     = 0x0000017F


def to_signed32(val):
    val = val & 0xFFFFFFFF
    if val >= (1 << 31):
        val -= (1 << 32)
    return val


def to_unsigned32(val):
    return val & 0xFFFFFFFF


def mem_read(data_mem, address):
    address = to_unsigned32(address)
    if DATA_MEM_BASE <= address <= DATA_MEM_END:
        idx = (address - DATA_MEM_BASE) // 4
        return data_mem[idx]
    elif STACK_BASE <= address <= STACK_END:
        idx = (address - STACK_BASE) // 4 + 32
        return data_mem[idx] if idx < len(data_mem) else 0
    else:
        print(f"Error: Memory read out of range at address 0x{address:08X}")
        sys.exit(1)


def mem_write(data_mem, address, value):
    address = to_unsigned32(address)
    value   = to_unsigned32(value)
    if DATA_MEM_BASE <= address <= DATA_MEM_END:
        idx = (address - DATA_MEM_BASE) // 4
        data_mem[idx] = value
    elif STACK_BASE <= address <= STACK_END:
        idx = (address - STACK_BASE) // 4 + 32
        while len(data_mem) <= idx:
            data_mem.append(0)
        data_mem[idx] = value
    else:
        print(f"Error: Memory write out of range at address 0x{address:08X}")
        sys.exit(1)


def execute_RIS(decoded, regs, data_mem, pc):
 
    instr = decoded["instr"]
    rd    = decoded["rd"]
    rs1   = decoded["rs1"]
    rs2   = decoded["rs2"]
    imm   = decoded["imm"]

    next_pc = pc + 4

    # R-type
    if instr == "add":
        regs[rd] = to_unsigned32(regs[rs1] + regs[rs2])

    elif instr == "sub":
        regs[rd] = to_unsigned32(regs[rs1] - regs[rs2])

    elif instr == "sll":
        shamt    = regs[rs2] & 0x1F
        regs[rd] = to_unsigned32(regs[rs1] << shamt)

    elif instr == "slt":
        regs[rd] = 1 if to_signed32(regs[rs1]) < to_signed32(regs[rs2]) else 0

    elif instr == "sltu":
        regs[rd] = 1 if to_unsigned32(regs[rs1]) < to_unsigned32(regs[rs2]) else 0

    elif instr == "xor":
        regs[rd] = to_unsigned32(regs[rs1] ^ regs[rs2])

    elif instr == "srl":
        shamt    = regs[rs2] & 0x1F
        regs[rd] = to_unsigned32(regs[rs1]) >> shamt

    elif instr == "or":
        regs[rd] = to_unsigned32(regs[rs1] | regs[rs2])

    elif instr == "and":
        regs[rd] = to_unsigned32(regs[rs1] & regs[rs2])

    # I-type
    elif instr == "addi":
        regs[rd] = to_unsigned32(regs[rs1] + imm)

    elif instr == "sltiu":
        regs[rd] = 1 if to_unsigned32(regs[rs1]) < to_unsigned32(imm) else 0

    elif instr == "lw":
        address  = to_unsigned32(regs[rs1] + imm)
        regs[rd] = mem_read(data_mem, address)

    elif instr == "jalr":
        ret_addr = to_unsigned32(pc + 4)
        target   = to_unsigned32(regs[rs1] + imm) & 0xFFFFFFFE
        regs[rd] = ret_addr
        next_pc  = target

    # S-type
    elif instr == "sw":
        address = to_unsigned32(regs[rs1] + imm)
        mem_write(data_mem, address, regs[rs2])

    else:
        print(f"Error: Unknown R/I/S instruction '{instr}'")
        sys.exit(1)

    regs[0] = 0
    return next_pc


# PERSON 4 

def execute_BJ(decoded, regs, data_mem, pc):
    instr = decoded["instr"]
    rd    = decoded["rd"]
    rs1   = decoded["rs1"]
    rs2   = decoded["rs2"]
    imm   = decoded["imm"]

    next_pc = pc + 4

    # B-type
    if instr == "beq":
        if to_signed32(regs[rs1]) == to_signed32(regs[rs2]):
            next_pc = to_unsigned32(pc + imm)

    elif instr == "bne":
        if to_signed32(regs[rs1]) != to_signed32(regs[rs2]):
            next_pc = to_unsigned32(pc + imm)

    elif instr == "blt":
        if to_signed32(regs[rs1]) < to_signed32(regs[rs2]):
            next_pc = to_unsigned32(pc + imm)

    elif instr == "bge":
        if to_signed32(regs[rs1]) >= to_signed32(regs[rs2]):
            next_pc = to_unsigned32(pc + imm)

    elif instr == "bltu":
        if to_unsigned32(regs[rs1]) < to_unsigned32(regs[rs2]):
            next_pc = to_unsigned32(pc + imm)

    elif instr == "bgeu":
        if to_unsigned32(regs[rs1]) >= to_unsigned32(regs[rs2]):
            next_pc = to_unsigned32(pc + imm)

    # J-type
    elif instr == "jal":
        regs[rd] = to_unsigned32(pc + 4)
        next_pc  = to_unsigned32(pc + imm) & 0xFFFFFFFE

    # U-type
    elif instr == "lui":
        regs[rd] = to_unsigned32(imm)

    elif instr == "auipc":
        regs[rd] = to_unsigned32(pc + imm)

    else:
        print(f"Error: Unknown B/J/U instruction '{instr}'")
        sys.exit(1)

    regs[0] = 0
    return next_pc


def dump_memory(data_mem):
    lines = []  
    for i in range(32):
        address = DATA_MEM_BASE + i * 4
        value   = data_mem[i] if i < len(data_mem) else 0
        bin_val = "0b" + format(value & 0xFFFFFFFF, '032b')
        lines.append(f"0x{address:08X}:{bin_val}")
    return lines


# PERSON 1 — File Input, Main Loop, Printing Trace


NUM_REGS      = 32
SP_INIT       = 0x0000017C
DATA_MEM_SIZE = 64 

def init_registers():
    regs = [0] * NUM_REGS
    regs[2] = SP_INIT 
    return regs


def init_memory():
    return [0] * DATA_MEM_SIZE


def read_binary_file(path):
    instructions = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                instructions.append(line)
    return instructions


def format_trace(pc, regs):
    pc_bin   = "0b" + format(pc & 0xFFFFFFFF, '032b')
    reg_bins = ["0b" + format(r & 0xFFFFFFFF, '032b') for r in regs]
    return pc_bin + " " + " ".join(reg_bins)


def write_output(path, trace_lines, memory_lines):
    with open(path, "w") as f:
        for line in trace_lines:
            f.write(line + "\n")
        for line in memory_lines:
            f.write(line + "\n")


def is_virtual_halt(instr_bin):
    return instr_bin == "00000000000000000000000001100011"


def main():
    if len(sys.argv) < 3:
        print("Usage: python Simulator.py <input_binary_file> <output_trace_file>")
        sys.exit(1)

    input_file  = sys.argv[1]
    output_file = sys.argv[2]

    instructions = read_binary_file(input_file)
    regs         = init_registers()
    data_mem     = init_memory()
    pc           = 0x00000000
    trace_lines  = []

    while True:
        instr_index = pc // 4
        if instr_index < 0 or instr_index >= len(instructions):
            print(f"Error: PC 0x{pc:08X} out of program memory bounds.")
            sys.exit(1)

        instr_bin = instructions[instr_index]

        
        if is_virtual_halt(instr_bin):
            trace_lines.append(format_trace(pc, regs))
            break

        # Decode (Person 2)
        decoded = decode_instruction(instr_bin)

        instr_type = decoded["type"]
        if instr_type in ("R", "I", "S"):
            next_pc = execute_RIS(decoded, regs, data_mem, pc)
        else:
            next_pc = execute_BJ(decoded, regs, data_mem, pc)

        # x0 is always hard-wired to zero
        regs[0] = 0

        trace_lines.append(format_trace(next_pc, regs))
        pc = next_pc

    memory_lines = dump_memory(data_mem)
    write_output(output_file, trace_lines, memory_lines)


if __name__ == "__main__":
    main()
