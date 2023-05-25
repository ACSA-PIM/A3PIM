# satic code analyzer for offload decision algorithms
import json
import global_variable as glv
from terminal_command import *
import re
from tqdm import tqdm

def OffloadBySCA(taskList):
    for taskKey, taskName in taskList.items():
        ic(taskKey, taskName)
        assemblyPath = glv._get("logPath")+ "assembly/"
        targetAssembly = assemblyPath + taskName + ".s"
        bblJsonFile = targetAssembly[:-2] + "_bbl.json"
        bblDecisionFile = targetAssembly[:-2] + "_bbl.decision"
        bblSCAFile = targetAssembly[:-2] + "_bbl.sca"
        bblHashDict = dict()
        with open(bblJsonFile, 'r') as f:
            bblHashDict = json.load(f)
        with open(bblSCAFile, 'w') as fsca:
            with open(bblDecisionFile, 'w') as f:
                for bblHashStr, bblList in tqdm(bblHashDict.items()):
                    [decision, cycles, pressure] = llvmResult(bblList)
                    f.write(bblHashStr + " " + decision + '\n')   
                    fsca.write(bblHashStr + "\t" + decision + " pressure: " + str(pressure) + "\t cycles: " + str(cycles) + '\n')        

def llvmResult(bblList):
    command = llvmCommand(bblList)
    [list, errList]=TIMEOUT_severalCOMMAND(command, glv._get("timeout"))
    # ic(errList)
    if errList and errList[-1]=="error: no assembly instructions found.\n":
        cycles = 0
        pressure = 0
        decision = "None"
        return [decision, cycles, pressure]
    # ic(list[2])
    # ic(list[11])
    cycles = int(re.match(r"Total Cycles:(\s*)([0-9]*)(\s*)",list[2]).group(2))
    if list[11]=="No resource or data dependency bottlenecks discovered.\n":
        pressure = 0
    else:
        pressure = float(re.match(r"Cycles with backend pressure increase(\s*)\[ ([0-9\.]*)% \](\s*)",list[11]).group(2))
    if pressure < 70:
        decision = "CPU"
    else:
        decision = "PIM"
    # ic(decision, cycles, pressure)
    return [decision, cycles, pressure]
        
def llvmCommand(bblList):
    bbl = '\n'.join(bblList)
    bbl = bbl.replace('$', '\\$')
    command = 'echo "'+ bbl + '" |'+" llvm-mca -march=x86 -mcpu=x86-64 -timeline --bottleneck-analysis --resource-pressure --iterations=1000 |head -n 30"
    # ic(command)
    return command