def dec_to_bin(num, bits):
    if num < 0: num = (1 << bits) + num
    return format(num, '0' + str(bits) + 'b')

def calc_offset(current_pc, label_address):
    return label_address - current_pc

def parse_imm(x):
    s = str(x).lower()
    if '0x' in s: return int(s, 16)
    return int(s)

def translate_R_type(parts):
    c = parts[0]
    d = registers[parts[1]]
    s1 = registers[parts[2]]
    s2 = registers[parts[3]]
    return funct7_dict[c] + s2 + s1 + funct3_dict[c] + d + opcode_dict[c]

def translate_I_type(parts):
    o = parts[0]
    if o == "lw":
        rd = registers[parts[1]]
        i = parse_imm(parts[2])
        rs1 = registers[parts[3]]
    else:
        rd = registers[parts[1]]
        rs1 = registers[parts[2]]
        i = parse_imm(parts[3])
        
    b = dec_to_bin(i, 12)
    return b + rs1 + funct3_dict[o] + rd + opcode_dict[o]

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

