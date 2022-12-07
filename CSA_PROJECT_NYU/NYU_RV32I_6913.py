import os
import argparse
from control_functions import *

MemSize = 1000 # memory size, in reality, the memory size should be 2^32, but for this lab, for the space resaon, we keep it as this large number, but the memory is still 32-bit addressable.


class InsMem(object):
    def __init__(self, name, ioDir):
        self.id = name

        with open(ioDir + "/imem.txt") as im:
            self.IMem = [data.replace("\n", "") for data in im.readlines()]

    def readInstr(self, ReadAddress):
        #read instruction memory
        #return 32 bit hex val
        # print(ReadAddress, [i for idx,i in enumerate(self.IMem) if (idx >= ReadAddress) and (idx < ReadAddress + 4)])
        return "".join([i for idx,i in enumerate(self.IMem) if (idx >= ReadAddress) and (idx < ReadAddress + 4)])


class DataMem(object):
    def __init__(self, name, ioDir):
        self.id = name
        self.ioDir = ioDir
        with open(ioDir + "/dmem.txt") as dm:
            self.DMem = [data.replace("\n", "") for data in dm.readlines()]
        

    def readMem(self, ReadAddress):
        #read data memory
        #return 32 bit hex val
        return "".join([i for idx,i in enumerate(self.DMem) if (idx >= ReadAddress) and (idx < ReadAddress + 4)])

    def divideString(self, s, k, fill):
        l=[]
        if len(s) % k != 0:
            s += fill * (k - len(s) % k)
        for i in range(0, len(s), k):
            l.append(s[i:i + k])
        return l

    def writeDataMem(self, Address, WriteData):
        # write data into byte addressable memory

        curr_len = len(self.DMem)
        if int(Address,2) > curr_len:
            to_append = int(Address,2) - curr_len
            self.DMem += ["00000000"]*to_append
        curr_len = len(self.DMem)
        # WriteData is 32 to bit string
        bits_split = 8
        fill_remain = "0"
        array = self.divideString(WriteData, bits_split, fill_remain)

        array_counter = 0
        for i in range(int(Address,2),int(Address,2)+4):
            if i >= curr_len:
                self.DMem.append(array[array_counter])
            else:
                self.DMem[i] = array[array_counter]
            array_counter += 1

    def outputDataMem(self):
        curr_len = len(self.DMem)
        if 1000 > curr_len:
            to_append = 1000 - curr_len
            self.DMem += ["00000000"]*to_append
        resPath = self.ioDir + "/" + self.id + "_DMEMResult.txt"
        with open(resPath, "w") as rp:
            rp.writelines([str(data) + "\n" for data in self.DMem])


class RegisterFile(object):
    def __init__(self, ioDir):
        self.outputFile = ioDir + "RFResult.txt"
        self.Registers = ["00000000000000000000000000000000" for i in range(32)]

    def readRF(self, Reg_addr):
        # Fill in
        return self.Registers[int(Reg_addr,2)]

    def writeRF(self, Reg_addr, Wrt_reg_data):
        # Fill in
        # print(Reg_addr,Wrt_reg_data,self.Registers[int(Reg_addr,2)])
        self.Registers[int(Reg_addr,2)] = Wrt_reg_data


    def outputRF(self, cycle):
        op = ["State of RF after executing cycle:\t" + str(cycle) + "\n"]
        op.extend([str(val) + "\n" for val in self.Registers])
        if(cycle == 0): perm = "w"
        else: perm = "a"
        with open(self.outputFile, perm) as file:
            file.writelines(op)


class State(object):
    def __init__(self):
        self.IF = {"nop": False, "PC": 0, "counter": 0, "halt":False}
        self.ID = {"nop": False, "Instr": 0, "halt":False}
        self.EX = {
            "nop": False, "Operand1": 0, "Operand2": 0, "Imm": 0, "mux_out1": 0,
            "mux_out2": 0, "DestReg": 0, "is_I_type": False, "RdDMem": 0, "WrDMem": 0,
            "AluOperation": 0, "WBEnable": 0, "StData": 0, "AluControlInput": 0, "branch": 0,
            "jump": 0, "halt":False
        }
        self.MEM = {"nop": False, "ALUresult": 0, "Store_data": 0, "Rs": 0, "Rt": 0, "DestReg": 0, "RdDMem": 0,
                   "WrDMem": 0, "WBEnable": 0, "halt":False}
        self.WB = {"nop": False, "Wrt_data": 0, "Rs": 0, "Rt": 0, "DestReg": 0, "wrt_enable": 0, "halt":False}


class Core(object):
    def __init__(self, ioDir, imem, dmem):
        self.myRF = RegisterFile(ioDir)
        self.cycle = 0
        self.halted = False
        self.ioDir = ioDir
        self.state = State()
        self.nextState = State()
        self.ext_imem = imem
        self.ext_dmem = dmem


class SingleStageCore(Core):
    def __init__(self, ioDir, imem, dmem):
        super(SingleStageCore, self).__init__(ioDir + "/SS_", imem, dmem)
        self.opFilePath = ioDir + "/StateResult_SS.txt"

    def step(self):
        # Your implementation
        # --------------------- IF stage ---------------------
        print("IF Stage---------------", self.state.IF["PC"])

        self.state.ID["Instr"] = self.ext_imem.readInstr(int(self.state.IF["PC"]))

        print(self.state.ID["Instr"])

        # --------------------- ID stage --------------------
        print("ID Stage----------------")
        instruction_decode(self.state.ID["Instr"], self.state, self.myRF, self.ext_dmem)

        # --------------------- EX stage ---------------------
        print("EX Stage")
        self.state.MEM["RdDMem"] = self.state.EX["RdDMem"]
        self.state.MEM["WrDMem"] = self.state.EX["WrDMem"]
        self.state.MEM["WBEnable"] = self.state.EX["WBEnable"]
        instruction_exec(
            self.state,
            self.state.EX["AluControlInput"],
            self.state.EX["mux_out1"],
            self.state.EX["mux_out2"],
            self.state.EX["DestReg"],
            self.nextState,
        )

        # --------------------- MEM stage ---------------------
        print("MEM Stage")

        instruction_mem(
            self.state, self.state.MEM["RdDMem"],
            self.state.MEM["WrDMem"],
            self.ext_dmem,
            self.state.MEM["ALUresult"],
            self.state.MEM["DestReg"],
            self.state.MEM["WBEnable"],
        )

        # --------------------- WB stage ---------------------
        print("WB Stage")
        write_nack(self.state.WB["DestReg"], self.state.WB["Wrt_data"], self.state.WB["wrt_enable"], self.myRF)

        # read instruction
        # self.nextState.ID["Instr"] = imem.IMem
        # self.nextState.IF["PC"] = self.state.IF["PC"] + 4

        # self.halted = True
        if self.state.IF["nop"]:
            self.halted = True

        self.myRF.outputRF(self.cycle) # dump RF
        self.printState(self.nextState, self.cycle) # print states after executing cycle 0, cycle 1, cycle 2 ...

        self.state = self.nextState #The end of the cycle and updates the current state with the values calculated in this cycle
        self.nextState = State()
        self.cycle += 1

    def printState(self, state, cycle):
        printstate = ["State after executing cycle:\t" + str(cycle) + "\n"]
        printstate.append("IF.PC:\t" + str(state.IF["PC"]) + "\n")
        printstate.append("IF.nop:\t" + str(int(state.IF["nop"])) + "\n")

    # def printState(self, state, cycle):
    #     printstate = ["State after executing cycle:\t" + str(cycle) + "\n"]
    #     printstate.extend(["IF." + key + ":\t" + str(val) + "\n" for key, val in state.IF.items()])
    #     printstate.extend(["ID." + key + ":\t" + str(val) + "\n" for key, val in state.ID.items()])
    #     printstate.extend(["EX." + key + ":\t" + str(val) + "\n" for key, val in state.EX.items()])
    #     printstate.extend(["MEM." + key + ":\t" + str(val) + "\n" for key, val in state.MEM.items()])
    #     printstate.extend(["WB." + key + ":\t" + str(val) + "\n" for key, val in state.WB.items()])

        if(cycle == 0): perm = "w"
        else: perm = "a"
        with open(self.opFilePath, perm) as wf:
            wf.writelines(printstate)


class FiveStageCore(Core):
    def __init__(self, ioDir, imem, dmem):
        super(FiveStageCore, self).__init__(ioDir + "/FS_", imem, dmem)
        self.opFilePath = ioDir + "/StateResult_FS.txt"

    def step(self):
        # Your implementation

        #------------------------Get Halt and PC status from last state-----
        self.nextState.IF["PC"] = self.state.IF["PC"]
        self.nextState.IF["halt"] = self.state.IF["halt"]
        self.nextState.ID["halt"] = self.state.ID["halt"]
        self.nextState.EX["halt"] = self.state.EX["halt"]
        self.nextState.MEM["halt"] = self.state.MEM["halt"]
        self.nextState.WB["halt"] = self.state.WB["halt"]


        # --------------------- WB stage ---------------------

        print("WB Stage----------------")
        if self.state.WB["halt"] == True:
            print("Last Cycle")
            self.halted = True
        else:
            write_nack(self.state.WB["DestReg"], self.state.WB["Wrt_data"], self.state.WB["wrt_enable"], self.myRF)

        # --------------------- MEM stage --------------------

        print("MEM Stage----------------")

        if self.state.WB["halt"] == True or self.state.MEM["halt"] == True:
            self.nextState.WB["halt"] = True
        else:
            instruction_mem(self.nextState, self.state.MEM["RdDMem"], self.state.MEM["WrDMem"], self.ext_dmem, self.state.MEM["ALUresult"], self.state.MEM["DestReg"], self.state.MEM["WBEnable"], self.myRF)
            if self.state.EX["nop"] == True:
                self.nextState.MEM["nop"] = True

        # --------------------- EX stage ---------------------
        print("EX Stage----------------")
        # halt condition
        if self.state.WB["halt"] == True or self.state.MEM["halt"] == True or self.state.EX["halt"] == True:
            self.nextState.MEM["halt"] = True
        else:
            self.nextState.MEM["RdDMem"] = self.state.EX["RdDMem"]
            self.nextState.MEM["WrDMem"] = self.state.EX["WrDMem"]
            self.nextState.MEM["WBEnable"] = self.state.EX["WBEnable"]
            if self.state.EX["nop"] == True:
                self.nextState.MEM["nop"] = True
            instruction_exec(self.nextState, self.state.EX["AluControlInput"], self.state.EX["mux_out1"], self.state.EX["mux_out2"], self.state.EX["DestReg"], self.nextState)


        # --------------------- ID stage ---------------------
        print("ID Stage----------------")
        if self.state.WB["halt"] == True or self.state.MEM["halt"] == True or self.state.EX["halt"] == True:
            print("Halt")
        else:
            if self.state.ID["Instr"] != 0:
                instruction_decode(self.state.ID["Instr"], self.nextState, self.myRF, self.ext_dmem)
            if self.state.ID["nop"] == True:
                self.nextState.EX["nop"] = True
        

        # --------------------- IF stage ---------------------
        print("IF Stage---------------", self.state.IF["PC"])

        if self.state.WB["halt"] == True or self.state.MEM["halt"] == True or self.state.EX["halt"] == True:
            print("Halt")
        else:
            # Adding stall / nop in case for load
            if self.nextState.EX["nop"] == True:
                self.nextState.ID["Instr"] = self.state.ID["Instr"]
                self.nextState.IF["PC"] = self.state.IF["PC"]
            else:
                self.nextState.ID["Instr"] = self.ext_imem.readInstr(int(self.state.IF["PC"]))
                # self.nextState.IF["PC"] = self.state.IF["PC"] + 4
            if self.state.IF["nop"] == True:
                self.nextState.ID["nop"] == True

        # self.halted = True
        if self.state.IF["nop"] and self.state.ID["nop"] and self.state.EX["nop"] and self.state.MEM["nop"] and self.state.WB["nop"]:
            self.halted = True

        self.myRF.outputRF(self.cycle) # dump RF
        self.printState(self.nextState, self.cycle) # print states after executing cycle 0, cycle 1, cycle 2 ...

        self.state = self.nextState #The end of the cycle and updates the current state with the values calculated in this cycle

        self.nextState = State()
        self.cycle += 1

    def printState(self, state, cycle):
        printstate = ["\n", "State after executing cycle: " + str(cycle) + "\n"]
        printstate.extend(["IF." + key + ": " + str(val) + "\n" for key, val in state.IF.items()])
        printstate.extend(["ID." + key + ": " + str(val) + "\n" for key, val in state.ID.items()])
        printstate.extend(["EX." + key + ": " + str(val) + "\n" for key, val in state.EX.items()])
        printstate.extend(["MEM." + key + ": " + str(val) + "\n" for key, val in state.MEM.items()])
        printstate.extend(["WB." + key + ": " + str(val) + "\n" for key, val in state.WB.items()])

        if(cycle == 0): perm = "w"
        else: perm = "a"
        with open(self.opFilePath, perm) as wf:
            wf.writelines(printstate)


if __name__ == "__main__":

    #parse arguments for input file location
    parser = argparse.ArgumentParser(description='RV32I processor')
    parser.add_argument('--iodir', default="", type=str, help='Directory containing the input files.')
    args = parser.parse_args()

    ioDir = os.path.abspath(args.iodir)
    print("IO Directory:", ioDir)

    imem = InsMem("Imem", ioDir)
    # print("imem",imem.IMem)
    dmem_ss = DataMem("SS", ioDir)
    # print("dmem_ss",dmem_ss.DMem)
    dmem_fs = DataMem("FS", ioDir)
    # print("dmem_fs",dmem_fs.DMem)

    # ssCore = SingleStageCore(ioDir, imem, dmem_ss)
    fsCore = FiveStageCore(ioDir, imem, dmem_fs)

    count = 0
    while True:
        # print('-------------------------------------')
        # if not ssCore.halted:
        #     ssCore.step()
        #     count = 0
            # comment
        # else:
        #     count += 1

        # if count >=3:
        #     print("issue")
        #     break

        if not fsCore.halted:
            fsCore.step()
        if fsCore.halted:
            break
        # if ssCore.halted and fsCore.halted:
        #     break
    # dump SS and FS data mem.
    print(dmem_fs.DMem)
    dmem_ss.outputDataMem()
    dmem_fs.outputDataMem()
