def twos_comp(val, bits):
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0:
        val = val - (1 << bits)
    return val


def generate_bitstring(s):
    #TODO: rm, this is for debugging the error
    if '-' in s:
        return s
    return s[-1: -33: -1][::-1]


def twos_comp_str(s):
    s = list(s)
    for i in range(len(s)):
        if s[i] == '0':
            s[i] = '1'
        else:
            s[i] = '0'
    return '{:032b}'.format(int(''.join(s), 2) + 1)


def r_type(s, state, register_file, memory):

    rd = s[-12:-7]
    func3 = s[-15:-12]
    rs1 = s[-20:-15]
    rs2 = s[-25:-20]
    func7 = s[:-25]

    #-------------------------------Forwarding logic starts-----------------------------------
    # Forward for all instructions except for load value
    if (rs1 == state.MEM["DestReg"]) and (state.MEM["RdDMem"] != 1 or state.MEM["WBEnable"] != 1):
        state.EX["Operand1"] = state.MEM["ALUresult"]
    elif (rs1 == state.WB["DestReg"]) and (state.WB["RdDMem"] == 1 or state.WB["WBEnable"] == 1):
        # in case of load value take from write back stage
        state.EX["Operand1"] = state.WB["Wrt_data"]
    elif (rs1 == state.MEM["DestReg"]) and state.MEM["RdDMem"] == 1 and state.MEM["WBEnable"] == 1:
        state.EX["nop"] = 1
        return
    else:
        state.EX["Operand1"] = register_file.readRF(rs1)
    
    if rs2 == state.MEM["DestReg"] and (state.MEM["RdDMem"] != 1 or state.MEM["WBEnable"] != 1):
        state.EX["Operand2"] = state.MEM["ALUresult"]
    elif (rs1 == state.WB["DestReg"]) and (state.WB["RdDMem"] == 1 or state.WB["WBEnable"] == 1):
        # in case of load value take from write back stage
        state.EX["Operand2"] = state.WB["Wrt_data"]
    elif (rs1 == state.MEM["DestReg"]) and state.MEM["RdDMem"] == 1 and state.MEM["WBEnable"] == 1:
        state.EX["nop"] = 1
        return
    else:
        state.EX["Operand2"] = register_file.readRF(rs2)
    
    #-------------------------------Forwarding logic ends-----------------------------------


    print(register_file.Registers)
    print(rs1,rs2)
    print(state.EX["Operand1"], state.EX["Operand2"])
    state.EX["DestReg"] = rd

    if func3 == "000" and func7 == "0100000":
        print("SUB")
        state.EX["AluControlInput"] = "0110"

    elif func3 == "000" and func7 == "0000000":
        print("Add")
        state.EX["AluControlInput"] = "0010"

    elif func3 == "100" and func7 == "0000000":
        print("XOR")
        state.EX["AluControlInput"] = "0011"

    elif func3 == "110" and func7 == "0000000":
        print("OR")
        state.EX["AluControlInput"] = "0001"

    elif func3 == "111" and func7 == "0000000":
        print("AND")
        state.EX["AluControlInput"] = "0000"
    
    state.EX["mux_out1"] = state.EX["Operand1"]
    state.EX["mux_out2"] = state.EX["Operand2"]
    state.EX["RdDMem"] = 1
    state.EX["WrDMem"] = 0


def i_type(s, state, register_file, memory):
    opcode = s[-7:]
    rd = s[-12:-7]
    func3 = s[-15:-12]
    rs1 = s[-20:-15]
    imm = s[:-20]

    state.EX["Operand1"] = register_file.readRF(rs1)
    state.EX["Imm"] = twos_comp(int(imm,2), 12)
    state.EX["DestReg"] = rd
    state.EX["is_I_type"] = 1
    state.EX["AluOperation"] = "00"
    state.EX["mux_out1"] = state.EX["Operand1"]
    state.EX["RdDMem"] = 1
    state.EX["WrDMem"] = 0

    if opcode == "0000011":
        state.EX["WBEnable"] = 1

    diff_len = 32 - len(imm)
    state.EX["mux_out2"] = imm[0]*diff_len + imm

    if opcode == "0000011":
        print("Load")
        state.EX["AluControlInput"] = "0010"
        

    elif func3 == "000":
        print("ADDI")
        state.EX["AluControlInput"] = "0010"

    elif func3 == "100":
        print("XORI")
        state.EX["AluControlInput"] = "0011"

    elif func3 == "110":
        print("ORI")
        state.EX["AluControlInput"] = "0001"

    elif func3 == "111":
        print("ANDI")
        state.EX["AluControlInput"] = "0000"


def s_type(s, state, register_file, memory):

    imm1 = s[-12:-7]
    rs1 = s[-20:-15]
    rs2 = s[-25:-20]
    imm2 = s[:-25]
    imm = imm2 + imm1

    
    state.EX["Operand1"] = register_file.readRF(rs1)
    state.EX["DestReg"] = rs2
    state.EX["is_I_type"] = 1
    # state.EX["WBEnable"] = 1
    state.EX["RdDMem"] = 0
    state.EX["WrDMem"] = 1
    
    state.EX["AluControlInput"] = "0010"

    state.EX["mux_out1"] = state.EX["Operand1"]

    diff_len = 32 - len(imm)
    state.EX["mux_out2"] = imm[0]*diff_len + imm
    state.EX["Imm"] = state.EX["mux_out2"]

def j_type(s, state, register_file, memory):

    opcode = s[-7:]
    rd = s[-12:-7]
    imm = s[:-12]

def b_type(s, state, register_file, memory):

    opcode = s[-7:]
    imm1 = s[-12:-7]
    func3 = s[-15:-12]
    rs1 = s[-20:-15]
    rs2 = s[-25:-20]
    imm2 = s[:-25]


def instruction_decode(s, state, register_file, memory):
    # R Type 0110011
    if s[-7:] == "0110011":
        print("----------------------------------------do R type")
        r_type(s, state, register_file, memory)
    # I Type 0010011 (LW 0000011)
    elif (s[-7:] == "0010011") or (s[-7:] == "0000011"):
        print("-----------------------------------------do I type")
        i_type(s, state, register_file, memory)
    # S Type 0100011
    elif s[-7:] == "0100011":
        print("------------------------------------------do S type")
        s_type(s, state, register_file, memory)
    # J Type 1101111
    elif s[-7:] == "1101111":
        print("do J type")
        j_type(s, state, register_file, memory)
    # B Type 1100011
    elif s[-7:] == "1100011":
        print("do B type")
        b_type(s, state, register_file, memory)
    # Halt 1111111
    elif s[-7:] == "1111111":
        print("do H type")
        state.EX["WrDMem"] = 0
        state.EX["RdDMem"] = 0
        state.IF["nop"] = True


def instruction_exec(state, alucontrol, op1, op2, DestReg):
    print(op1,op2)
    state.MEM["DestReg"] = DestReg
    if alucontrol == "0110":
        print("SUB")
        state.MEM["ALUresult"] = generate_bitstring('{:032b}'.format(int(op1,2) + int(twos_comp_str(op2), 2)))

    elif alucontrol == "0010":
        print("ADD..............")
        # print(int(op1,2) + int(op2,2), '{0:032b}'.format(int(op1,2) + int(op2,2)))
        state.MEM["ALUresult"] = generate_bitstring('{:032b}'.format(int(op1,2) + int(op2,2)))

    elif alucontrol == "0000":
        print("AND")
        # Initialize res as NULL string
        res = ""
        for i in range(len(op1)):
            res = res + str(int(op1[i]) & int(op2[i]))
        print(res)
        state.MEM["ALUresult"] = generate_bitstring('{:032b}'.format(int(res,2)))

    elif alucontrol == "0001":
        print("OR")
        res = ""
        for i in range(len(op1)):
            res = res + str(int(op1[i]) or int(op2[i]))

        state.MEM["ALUresult"] = generate_bitstring('{:032b}'.format(int(res,2)))

    elif alucontrol == "0011":
        print("XOR")
        state.MEM["ALUresult"] = generate_bitstring('{:032b}'.format(int(op1,2) ^ int(op2,2)))


def instruction_mem(state, RdDMem, WrDMem, memory, ALUresult, DestReg, WBEnable):
    print(RdDMem, WrDMem, WBEnable)
    if RdDMem == 1 and WBEnable == 1:
        print("Read From memory")
        state.WB["Wrt_data"] = memory.readMem(int(ALUresult, 2))
        state.WB["wrt_enable"] = 1
        state.WB["DestReg"] = DestReg
    
    if RdDMem == 1 and WBEnable == 0:
        print("write back")
        state.WB["Wrt_data"] = ALUresult
        state.WB["wrt_enable"] = 1
        state.WB["DestReg"] = DestReg

    if WrDMem == 1:
        print("Write to memory", ALUresult, DestReg)
        memory.writeDataMem(DestReg, ALUresult)
        state.WB["wrt_enable"] = 0


def write_nack(DestReg, Wrt_data, wrt_enable, register_file):
    if wrt_enable:
        print(DestReg, Wrt_data)
        
        register_file.writeRF(DestReg, Wrt_data)
