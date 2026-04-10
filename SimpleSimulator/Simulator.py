#Vaibhav's work

# R-TYPE
if opcode == "0110011":

    if funct3 == "000":
        if funct7 == "0000000": # add
            registers[rd] = registers[rs1] + registers[rs2]
        elif funct7 == "0100000": # sub
            registers[rd] = registers[rs1] - registers[rs2]

    pc += 4