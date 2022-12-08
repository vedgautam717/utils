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


def reset_state(state):
    state.IF = {"nop": False, "PC": 0, "counter": 0, 'halt': False}
    state.ID = {"nop": False, "Instr": 0, 'halt': False}
    state.EX = {
        "nop": False, "Operand1": 0, "Operand2": 0, "Imm": 0, "mux_out1": 0,
        "mux_out2": 0, "DestReg": 0, "is_I_type": False, "RdDMem": 0, "WrDMem": 0,
        "AluOperation": 0, "WBEnable": 0, "StData": 0, "AluControlInput": 0, "branch": 0,
        "jump": 0, 'halt': False,
    }


def r_type(s, state, register_file, memory, curr_state):

    rd = s[-12:-7]
    func3 = s[-15:-12]
    rs1 = s[-20:-15]
    rs2 = s[-25:-20]
    func7 = s[:-25]

    #-------------------------------Forwarding logic starts-----------------------------------
    # Forward for all instructions except for load value
    if (rs1 == state.MEM["DestReg"]) and (state.MEM["RdDMem"] != 1 or state.MEM["WBEnable"] != 1):
        state.EX["Operand1"] = state.MEM["ALUresult"]
    elif (rs1 == state.WB["DestReg"]) and state.WB["wrt_enable"] == 1:
        # in case of load value take from write back stage
        state.EX["Operand1"] = state.WB["Wrt_data"]
    elif (rs1 == state.MEM["DestReg"]) and state.MEM["RdDMem"] == 1 and state.MEM["WBEnable"] == 1:
        state.EX["nop"] = 1
        return
    else:
        state.EX["Operand1"] = register_file.readRF(rs1)
    
    if rs2 == state.MEM["DestReg"] and (state.MEM["RdDMem"] != 1 or state.MEM["WBEnable"] != 1):
        state.EX["Operand2"] = state.MEM["ALUresult"]
    elif (rs2 == state.WB["DestReg"]) and state.WB["wrt_enable"] == 1:
        # in case of load value take from write back stage
        state.EX["Operand2"] = state.WB["Wrt_data"]
    elif (rs2 == state.MEM["DestReg"]) and state.MEM["RdDMem"] == 1 and state.MEM["WBEnable"] == 1:
        state.EX["nop"] = 1
        return
    else:
        state.EX["Operand2"] = register_file.readRF(rs2)
    
    #-------------------------------Forwarding logic ends-----------------------------------


    # print(register_file.Registers)
    # print(rs1,rs2)
    # print(state.EX["Operand1"], state.EX["Operand2"])
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

    state.IF["PC"] = curr_state.IF["PC"] + 4


def i_type(s, state, register_file, memory, curr_state):
    opcode = s[-7:]
    rd = s[-12:-7]
    func3 = s[-15:-12]
    rs1 = s[-20:-15]
    imm = s[:-20]

    #-------------------------------Forwarding logic starts-----------------------------------
    # Forward for all instructions except for load value
    if (rs1 == state.MEM["DestReg"]) and (state.MEM["RdDMem"] != 1 or state.MEM["WBEnable"] != 1):
        state.EX["Operand1"] = state.MEM["ALUresult"]
    elif (rs1 == state.WB["DestReg"]) and state.WB["wrt_enable"] == 1:
        # in case of load value take from write back stage
        state.EX["Operand1"] = state.WB["Wrt_data"]
    elif (rs1 == state.MEM["DestReg"]) and state.MEM["RdDMem"] == 1 and state.MEM["WBEnable"] == 1:
        state.EX["nop"] = 1
        return
    else:
        state.EX["Operand1"] = register_file.readRF(rs1)
    
    #-------------------------------Forwarding logic ends-----------------------------------

    # state.EX["Operand1"] = register_file.readRF(rs1)
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
    
    state.IF["PC"] = curr_state.IF["PC"] + 4


def s_type(s, state, register_file, memory, curr_state):

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

    state.IF["PC"] = curr_state.IF["PC"] + 4


def j_type(s, state, register_file, memory, curr_state):

    opcode = s[-7:]
    rd = s[-12:-7]
    imm = s[0] + s[12:20] + s[11:12] + s[1:11]
    state.EX["Imm"] = imm
    state.EX["branch"] = 1
    state.EX["jump"] = 1

    state.EX["DestReg"] = rd
    state.EX["RdDMem"] = 1
    state.EX["WrDMem"] = 0

    # jump Logic
    print("JAL")        
    state.MEM["ALUresult"] = generate_bitstring('{:032b}'.format(curr_state.IF["PC"] + 4))
    imm = [
        (int(state.EX["Imm"], 2) << 1),
        (int(twos_comp_str(state.EX["Imm"]), 2) << 1) * -1
    ][state.EX["Imm"][0] == '1']
    state.IF["PC"] = curr_state.EX["PC"] + imm


def b_type(s, state, register_file, memory, curr_state):

    imm = s[0] + s[-8] + s[1:-25] + s[-12:-8]
    opcode = s[-7:]
    func3 = s[-15:-12]
    rs1 = s[-20:-15]
    rs2 = s[-25:-20]

    #-------------------------------Forwarding logic starts-----------------------------------
    # Forward for all instructions except for load value
    if (rs1 == state.MEM["DestReg"]) and (state.MEM["RdDMem"] != 1 or state.MEM["WBEnable"] != 1):
        state.EX["Operand1"] = state.MEM["ALUresult"]
    elif (rs1 == state.WB["DestReg"]) and state.WB["wrt_enable"] == 1:
        # in case of load value take from write back stage
        state.EX["Operand1"] = state.WB["Wrt_data"]
    elif (rs1 == state.MEM["DestReg"]) and state.MEM["RdDMem"] == 1 and state.MEM["WBEnable"] == 1:
        state.EX["nop"] = 1
        return
    else:
        state.EX["Operand1"] = register_file.readRF(rs1)
    
    if rs2 == state.MEM["DestReg"] and (state.MEM["RdDMem"] != 1 or state.MEM["WBEnable"] != 1):
        state.EX["Operand2"] = state.MEM["ALUresult"]
    elif (rs2 == state.WB["DestReg"]) and state.WB["wrt_enable"] == 1:
        # in case of load value take from write back stage
        state.EX["Operand2"] = state.WB["Wrt_data"]
    elif (rs2 == state.MEM["DestReg"]) and state.MEM["RdDMem"] == 1 and state.MEM["WBEnable"] == 1:
        state.EX["nop"] = 1
        return
    else:
        state.EX["Operand2"] = register_file.readRF(rs2)
    
    #-------------------------------Forwarding logic ends-----------------------------------
    state.EX["branch"] = 1
    state.EX["Imm"] = imm
    state.EX["mux_out1"] = state.EX["Operand1"]
    state.EX["mux_out2"] = state.EX["Operand2"]
    state.EX["AluOperation"] = "00"
    state.EX["AluControlInput"] = s[17:20]


    # Branching Logic
    if state.EX["AluControlInput"] == "000":
        print("BEQ")
        if state.EX["mux_out1"] == state.EX["mux_out2"]:
            imm = [
                (int(state.EX["Imm"], 2) << 1),
                (int(twos_comp_str(state.EX["Imm"]), 2) << 1) * -1
            ][state.EX["Imm"][0] == '1']
            curr_pc = curr_state.ID["PC"] + imm
            reset_state(state)
            state.IF["PC"] = curr_pc
        else:
            state.IF["PC"] = curr_state.IF["PC"] + 4
    elif state.EX["AluControlInput"] == "001":
        print("BNE")
        if state.EX["mux_out1"] != state.EX["mux_out2"]:
            imm = [
                (int(state.EX["Imm"], 2) << 1),
                (int(twos_comp_str(state.EX["Imm"]), 2) << 1) * -1
            ][state.EX["Imm"][0] == '1']
            curr_pc = curr_state.ID["PC"] + imm
            reset_state(state)
            state.IF["PC"] = curr_pc
        else:
            state.IF["PC"] = curr_state.IF["PC"] + 4


def instruction_decode(s, state, register_file, memory, curr_state):
    # R Type 0110011
    if s[-7:] == "0110011":
        print("----------------------------------------do R type")
        r_type(s, state, register_file, memory, curr_state)
        
    # I Type 0010011 (LW 0000011)
    elif (s[-7:] == "0010011") or (s[-7:] == "0000011"):
        print("-----------------------------------------do I type")
        i_type(s, state, register_file, memory, curr_state)
    # S Type 0100011
    elif s[-7:] == "0100011":
        print("------------------------------------------do S type")
        s_type(s, state, register_file, memory, curr_state)
    # J Type 1101111
    elif s[-7:] == "1101111":
        print("do J type")
        j_type(s, state, register_file, memory, curr_state)
    # B Type 1100011
    elif s[-7:] == "1100011":
        print("do B type")
        b_type(s, state, register_file, memory, curr_state)
    # Halt 1111111
    elif s[-7:] == "1111111":
        print("Halt detected")
        state.EX["WrDMem"] = 0
        state.EX["RdDMem"] = 0
        state.EX["halt"] = True
        state.ID["halt"] = True
        state.IF["halt"] = True
        state.IF["PC"] = curr_state.IF["PC"] + 4


def instruction_exec(state, alucontrol, op1, op2, DestReg):
    # print(op1,op2)
    state.MEM["DestReg"] = DestReg
    # if not curr_state.EX['branch']:
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
        # print(res)
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
    
    # else:
        # if alucontrol == "000":
        #     print("BEQ")
        #     if op1 == op2:
        #         imm = [
        #             (int(curr_state.EX["Imm"], 2) << 1),
        #             (int(twos_comp_str(curr_state.EX["Imm"]), 2) << 1) * -1
        #         ][curr_state.EX["Imm"][0] == '1']
        #         curr_pc = curr_state.EX["PC"] + imm
        #         reset_state(state)
        #         state.IF["PC"] = curr_pc
        #     else:
        #         state.IF["PC"] = curr_state.IF["PC"] + 4
        # elif alucontrol == "001":
        #     print("BNE")
        #     if op1 != op2:
        #         imm = [
        #             (int(curr_state.EX["Imm"], 2) << 1),
        #             (int(twos_comp_str(curr_state.EX["Imm"]), 2) << 1) * -1
        #         ][curr_state.EX["Imm"][0] == '1']
        #         curr_pc = curr_state.EX["PC"] + imm
        #         reset_state(state)
        #         state.IF["PC"] = curr_pc
        #     else:
        #         state.IF["PC"] = curr_state.IF["PC"] + 4
        # elif curr_state.EX["jump"]:
        #     print("JAL")
        #     state.MEM["ALUresult"] = generate_bitstring('{:032b}'.format(curr_state.IF["PC"] + 4))
        #     imm = [
        #         (int(curr_state.EX["Imm"], 2) << 1),
        #         (int(twos_comp_str(curr_state.EX["Imm"]), 2) << 1) * -1
        #     ][curr_state.EX["Imm"][0] == '1']
        #     state.IF["PC"] = curr_state.EX["PC"] + imm


def instruction_mem(state, RdDMem, WrDMem, memory, ALUresult, DestReg, WBEnable, register):
    # print(RdDMem, WrDMem, WBEnable)
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
        # write in memory location of ALUresult
        # write data stored in DestReg
        memory.writeDataMem(ALUresult, register.readRF(DestReg))
        state.WB["wrt_enable"] = 0


def write_nack(DestReg, Wrt_data, wrt_enable, register_file):
    if wrt_enable:
        print(DestReg, Wrt_data)
        
        register_file.writeRF(DestReg, Wrt_data)
