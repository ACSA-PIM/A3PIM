# satic code analyzer for offload decision algorithms
import pickle
import json
import global_variable as glv
from terminal_command import *
import re
from tqdm import tqdm
from multiProcess import parallelGetSCAResult, llvmCommand, decisionByXGB
from tsjPython.tsjCommonFunc import *

def loadStoreDataMove(bblHashDict, targetFile):
    with open(targetFile, 'w') as f:
        for bblHash, bbl in bblHashDict.items():
            loadSet = set()
            storeSet = set()
            f.write(bblHash+'\n')
            for command in bbl:
                ic(command)
                if re.match(r".*(\(.*\)).*$",command):
                    ic("Get load store")
                    if re.match(r".*(,.*\(.*\)).*$",command):
                        ic("Get store")
                        ic(re.match(r".*(,.*\(.*\)).*$",command).group(1))
                    elif re.match(r".*(\(.*\).*,).*$",command):
                        ic("Get load")
                        ic(re.match(r".*(\(.*\).*,).*$",command).group(1))
                    else:
                        assert("Not match load store command")
                    
    
def regDataMovement(taskList):
    for taskKey, taskName in taskList.items():
        ic(taskKey, taskName)
        assemblyPath = glv._get("logPath")+ "assembly/"
        targetAssembly = assemblyPath + taskName + ".s"
        bblJsonFile = targetAssembly[:-2] + "_bbl.json"
        bblRegInfo
        if not checkFileExists(bblDecisionFile):
            bblHashDict = dict()
            with open(bblJsonFile, 'r') as f:
                bblHashDict = json.load(f)
            for bblHashStr, bblList in bblHashDict.items():
                ic(bblHashStr)
                # No need to collect for now
        else:
            yellowPrint("{} bblDecisionFile already existed".format(taskName))

def llvmAnalysis(taskList):
    for taskKey, taskName in taskList.items():
        ic(taskKey, taskName)
        assemblyPath = glv._get("logPath")+ "assembly/"
        targetAssembly = assemblyPath + taskName + ".s"
        bblJsonFile = targetAssembly[:-2] + "_bbl.json"
        bblSCAFile = targetAssembly[:-2] + "_bbl.sca"
        bblSCAPickleFile = targetAssembly[:-2] + "_bbl_sca.pickle"
        if not checkFileExists(bblSCAPickleFile):
            bblHashDict = dict()
            with open(bblJsonFile, 'r') as f:
                bblHashDict = json.load(f)
            parallelGetSCAResult(taskName, bblHashDict, bblSCAFile, bblSCAPickleFile)
        else:
            yellowPrint("{} bblSCAPickleFile already existed".format(taskName))
        
def OffloadBySCA(taskList):
    for taskKey, taskName in taskList.items():
        ic(taskKey, taskName)
        assemblyPath = glv._get("logPath")+ "assembly/"
        targetAssembly = assemblyPath + taskName + ".s"
        bblDecisionFile = targetAssembly[:-2] + "_bbl.decision"
        bblSCAPickleFile = targetAssembly[:-2] + "_bbl_sca.pickle"
        with open(bblSCAPickleFile, 'rb') as f:
            bblDict = pickle.load(f)
        decisionByXGB(bblDict,bblDecisionFile)
            
def llvmResult(bblList):
    command = llvmCommand(bblList)
    [list, errList]=TIMEOUT_severalCOMMAND(command, glv._get("timeout"))
    # ic(errList)
    if errList and errList[-1]=="error: no assembly instructions found.\n":
        cycles = 0
        pressure = 0
        decision = "None"
        return [decision, cycles, pressure]
    loadPortUsage = 0.0
    resourcePressure = 0.0
    registerPressure = 0.0
    memoryPressure = 0.0
    for i in range(len(list)):
        # ic(list[i])
        if list[i].startswith('  Resource Pressure       '):
            ic(list[i])
            matchPressure = re.match(r".*\[ ([0-9\.]*)% \](\s*)$",list[i])
            if not matchPressure:
                resourcePressure = -2
            else:
                resourcePressure = float(matchPressure.group(1))
            ic(resourcePressure)
        if list[i].startswith('  - Register Dependencies ['):
            ic(list[i])
            registerPressure = float(re.match(r".*\[ ([0-9\.]*)% \](\s*)$",list[i]).group(1))
            ic(registerPressure)
        if list[i].startswith('  - Memory Dependencies   ['):
            ic(list[i])
            memoryPressure = float(re.match(r".*\[ ([0-9\.]*)% \](\s*)$",list[i]).group(1))
            ic(memoryPressure)
        # if list[i].startswith('Resource pressure per iteration'):
        #     ic(list[i])
        #     ic(list[i+1])
        #     ic(list[i+2])       
        #     matchPort = re.match(r".*(\s+)([0-9\.]+)(\s*)\n$",list[i+2])
        #     if not matchPort:
        #         loadPortUsage = -2
        #     else:
        #         ic(matchPort)
        #         ic(matchPort.group(0))
        #         ic(matchPort.group(1))
        #         ic(matchPort.group(2))
        #         loadPortUsage = float(matchPort.group(2))
        #     ic(loadPortUsage)
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
