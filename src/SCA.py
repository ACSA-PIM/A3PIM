# satic code analyzer for offload decision algorithms
import json
import global_variable as glv

def OffloadBySCA(taskList):
    for taskKey, taskName in taskList.items():
        ic(taskKey, taskName)
        assemblyPath = glv._get("logPath")+ "assembly/"
        targetAssembly = assemblyPath + taskName + ".s"
        bblJsonFile = targetAssembly[:-2] + "_bbl.json"
        bblDecisionFile = targetAssembly[:-2] + "_bbl.decision"
        bblHashDict = dict()
        with open(bblJsonFile, 'r') as f:
            bblHashDict = json.load(f)
        with open(bblDecisionFile, 'w') as f:
            for bblHashStr, bblList in bblHashDict.items():
                f.write(bblHashStr + " " + llvmResult(bblList)[0] + '\n')          

def llvmResult(bblList):
    cycles = 0
    pressure = 0.9
    decision = "PIM"
    return [decision, cycles, pressure]
        