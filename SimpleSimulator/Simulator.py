#Vaibhav's work

# R-TYPE
if opcode == "0110011":

    if funct3 == "000":
        if funct7 == "0000000":
            registers[rd] = registers[rs1] + registers[rs2]
        elif funct7 == "0100000":
            registers[rd] = registers[rs1] - registers[rs2]

    elif funct3 == "010":
        registers[rd] = int(registers[rs1] < registers[rs2])

    elif funct3 == "011":
        registers[rd] = int((registers[rs1] & 0xFFFFFFFF) < (registers[rs2] & 0xFFFFFFFF))

    elif funct3 == "100":
        registers[rd] = registers[rs1] ^ registers[rs2]

    elif funct3 == "110":
        registers[rd] = registers[rs1] | registers[rs2]
    
    elif funct3 == "111":
        registers[rd] = registers[rs1] & registers[rs2]

    elif funct3 == "001":
        registers[rd] = registers[rs1] << (registers[rs2] & 0x1F)
    
    elif funct3 == "101":
        registers[rd] = (registers[rs1] & 0xFFFFFFFF) >> (registers[rs2] & 0x1F)

    pc += 4