import global_variable as glv
import sys
import multiprocessing as mp
from data import queueDictInit
from multiprocessing import Pipe,Queue
from multiBar import *
from collections import defaultdict
# from Bhive import *
# from llvm_mca import *
# from OSACA import *
from collections import defaultdict
# from KendallIndex import calculateKendallIndex
from data import dataDictInit,dataDictClass,bblDictInit
from terminal_command import *
from subProcessCommand import *
from tsjPython.tsjCommonFunc import *
from disassembly import abstractBBLfromAssembly
import traceback
import time
import json
import pickle
from xgboost import XGBClassifier
from logPrint import *
from tqdm import tqdm

FollowStatus = -1

class Process(mp.Process):
    def __init__(self, *args, **kwargs):
        mp.Process.__init__(self, *args, **kwargs)
        self._pconn, self._cconn = mp.Pipe()
        self._exception = None

    def run(self):
        try:
            mp.Process.run(self)
            self._cconn.send(None)
        except Exception as e:
            tb = traceback.format_exc()
            self._cconn.send((e, tb))
            # raise e  # You can still rise this exception if you need to

    @property
    def exception(self):
        if self._pconn.poll():
            self._exception = self._pconn.recv()
        return self._exception

def fileLineNum(filename):
    fread=open(filename, 'r')
    num_file = sum([1 for i in open(filename, "r")])
    glv._set("num_file",num_file)
    fread.close() 
    return num_file

def multiCorePIMMode(taskList, coreNums):
    totolCount = len(taskList)
    countId = 0
    for taskKey, taskName in taskList.items():
        countId = countId + 1
        yellowPrint("[   {:2}/{:2}   ] PIM-{:<10} Task {} is running……".format( countId, totolCount,coreNums, taskName))
        if taskName in glv._get("gapbsList"):
            [core, command,targetFile] = gapbsInput(taskKey, taskName, "pim", coreNums)
        elif taskName in glv._get("specialInputList"):
            [core, command,targetFile] = specialInput(taskKey, taskName, "pim", coreNums)
        else:
            [core, command,targetFile] = defaultInput(taskKey, taskName, "pim", coreNums)
        if not checkFileExists(targetFile):
            list=TIMEOUT_COMMAND(core, command,glv._get("timeout"))
            ic(list)
            if not checkFileExists(targetFile):
                errorPrint("{}-PIM falied for targetFile {} not found".format(taskName,targetFile))
                yellowPrint("Falied command {}".format(command))
                exit(1)
        else:
            yellowPrint("[   {}/{}   ] PIM-{:<10} Task {} already finished".format( countId, totolCount,coreNums, taskName))
        passPrint("[   {}/{}   ] PIM-{:<10} Task {} finished successfully".format( countId, totolCount,coreNums, taskName))

def pimprof(queueDict, app_info, countId, totolCount, coreCount):
    yellowPrint("[   {:2}/{:2}   ] PIMProf {:<10} is running……".format( countId, totolCount, app_info.name))
    [command,targetFile, redirect2log] = app_info.pimprof_command(coreCount, "bbls")
    print(command)
    if not checkFileExists(targetFile):
        list=TIMEOUT_COMMAND_2FILE(1, command, redirect2log, glv._get("timeout"))
        ic(list)
        assert len(list)!=0
    else:
        yellowPrint("[   {:2}/{:2}   ] PIMProf {:<10} already finished".format( countId, totolCount, app_info.name))
    passPrint("[   {:2}/{:2}   ] PIMProf {:<10} finished successfully".format( countId, totolCount, app_info.name))
    queueDict.get("finishedSubTask").put(app_info.name)
    
def singleCpuMode(queueDict, taskKey, taskName, countId, totolCount, **kwargs):
    sys.stdout.flush()
    yellowPrint("[   {}/{}   ] CPU-1 Task {:<10} is running……".format( countId, totolCount, taskName))
    if taskName in glv._get("gapbsList"):
        [core, command,targetFile] = gapbsInput(taskKey, taskName, "cpu", 1)
    elif taskName in glv._get("specialInputList"):
        [core, command,targetFile] = specialInput(taskKey, taskName, "cpu", 1)
    else:
        [core, command,targetFile] = defaultInput(taskKey, taskName, "cpu", 1)
    if not checkFileExists(targetFile):
        list=TIMEOUT_COMMAND(core, command,glv._get("timeout"))
        ic(list)
        assert len(list)!=0
    else:
        yellowPrint("[   {}/{}   ] CPU-1 Task {:<10} already finished".format( countId, totolCount, taskName))
    passPrint("[   {}/{}   ] CPU-1 Task {:<10} finished successfully".format( countId, totolCount, taskName))
    queueDict.get("finishedSubTask").put(taskName)
    
def singlePIMMode(queueDict, taskKey, taskName, countId, totolCount, coreNums):
    yellowPrint("[   {}/{}   ] PIM-{:<10} Task {} is running……".format( countId, totolCount,coreNums, taskName))
    if taskName in glv._get("gapbsList"):
        [core, command,targetFile] = gapbsInput(taskKey, taskName, "pim", coreNums)
    elif taskName in glv._get("specialInputList"):
        [core, command,targetFile] = specialInput(taskKey, taskName, "pim", coreNums)
    else:
        [core, command,targetFile] = defaultInput(taskKey, taskName, "pim", coreNums)
    if not checkFileExists(targetFile):
        list=TIMEOUT_COMMAND(core, command,glv._get("timeout"))
        ic(list)
        if not checkFileExists(targetFile):
            errorPrint("{}-PIM falied for targetFile {} not found".format(taskName,targetFile))
            yellowPrint("Falied command {}".format(command))
            exit(1)
    else:
        yellowPrint("[   {}/{}   ] PIM-{:<10} Task {} already finished".format( countId, totolCount,coreNums, taskName))
    passPrint("[   {}/{}   ] PIM-{:<10} Task {} finished successfully".format( countId, totolCount,coreNums, taskName))
    queueDict.get("finishedSubTask").put(taskName)


def singleDisassembly(queueDict, app_info, countId, totolCount, **kwargs):
    taskName = app_info.name
    taskKey = app_info.inj
    sys.stdout.flush()
    yellowPrint("[   {:2}/{:2}   ] Disassembly-1 Task {:<10} is running……".format( countId, totolCount, taskName))
    # if taskName in glv._get("gapbsList"):
    [command,targetFile] = disassemblyInput(taskKey, taskName)
    if not checkFileExists(targetFile):
        # list=TIMEOUT_COMMAND(1, command,glv._get("timeout")) weird, can not parallel objdump > Difffile
        list=TIMEOUT_COMMAND_2FILE(1, command, targetFile, glv._get("timeout"))
        ic(list)
        assert len(list)!=0
    else:
        yellowPrint("[   {:2}/{:2}   ] Disassembly-1 Task {:<10} already finished".format( countId, totolCount, taskName))
    bblFile = targetFile[:-2] + ".bbl"
    bblJsonFile = targetFile[:-2] + "_bbl.json"
    tmpbblFile = targetFile[:-2] + ".tmp"
    bblHashDict = abstractBBLfromAssembly(targetFile,bblFile,bblJsonFile,tmpbblFile)
    # loadStoreDataMove(bblHashDict, targetFile[:-2] + "_bbl.sl_data")
    passPrint("[   {:2}/{:2}   ] Disassembly-1 Task {:<10} finished successfully".format( countId, totolCount, taskName))
    queueDict.get("finishedSubTask").put(taskName)
    
    
def parallelTask(all_for_one, SubFunc,  **kwargs):
    
    dataDict = dataDictInit()
    queueDict = queueDictInit(dataDict)
    
    pList=[]
    totolCount = len(all_for_one.app_info_list)
    countId = 0
    for _, app_info in all_for_one.app_info_list.items():
        countId = countId + 1
        if "coreCount" in kwargs:
            ic(kwargs)
            pList.append(Process(target=SubFunc, args=(queueDict, app_info, countId, totolCount, int(kwargs["coreCount"]))))
        else:
            pList.append(Process(target=SubFunc, args=(queueDict, app_info, countId, totolCount)))
            
        
    for p in pList:
        p.start()
        
    ProcessNum = len(all_for_one.app_info_list)
    time.sleep(0.5)
    while queueDict.get("finishedSubTask").qsize()<ProcessNum:
        print("QueueNum : {}".format(queueDict.get("finishedSubTask").qsize()))
        sys.stdout.flush()
        time.sleep(5)

    yellowPrint("Reducing parallel processes result...")

        
def llvmCommand(to_filtered_list):
    bblList = [item for item in to_filtered_list if not item.startswith('callq')]
    # ic(bblList)
    bbl = '\n'.join(bblList)
    bbl = bbl.replace('$', '\\$')
    command = 'echo "'+ bbl + '" |'+" llvm-mca -march=x86 -mcpu=x86-64 -timeline --bottleneck-analysis --resource-pressure --iterations=100"
    # ic(command)
    return command

def mergeQueue2dataDict(queueDict,dataDict):
    for key, value in dataDict.dataDict.items():
        # ic(key,type(value))
        if isinstance(value,set):
            # ic("set")
            dataDict.dataDict[key]=dataDict.dataDict[key].union(queueDict.dataDict[key].get())
        elif isinstance(value,defaultdict):
            # ic("defaultdict(int)")
            ic(key)
            if key == "frequencyRevBiBlock":
                a=dataDict.dataDict[key]
                b=queueDict.dataDict[key].get()
                for key2 in b:
                    dataDict.dataDict[key][key2]=a[key2]+b[key2]
            else:
                dataDict.dataDict[key].update(queueDict.dataDict[key].get())
    return dataDict

def getBBLFunc(bblHashDict, sendPipe,rank,queueDict):
    llvmCycles = defaultdict(int)
    llvmInstrNums = defaultdict(int)
    llvmMayLoad = defaultdict(int)
    llvmMayStore = defaultdict(int)
    llvmLoadPressure = defaultdict(float)
    llvmStorePressure = defaultdict(float)
    llvmPressure = defaultdict(float)
    llvmPortUsage = defaultdict(float)
    llvmSBPort23Pressure = defaultdict(float)
    llvmResourcePressure = defaultdict(float)
    llvmRegisterPressure = defaultdict(float)
    llvmMemoryPressure = defaultdict(float)
    finishedSubTask = set()
    
    i=1
    sendSkipNum=int(len(bblHashDict)/50)+1
    ic(sendSkipNum)
    try:
        for bblHashStr, bblList in bblHashDict.items():
            if i%sendSkipNum==0:
                sendPipe.send(i)
            i+=1
            command = llvmCommand(bblList)
            [list, errList]=TIMEOUT_severalCOMMAND(command, 5)
            # ic(errList)
            MayLoad = 0
            MayStore = 0
            MayLoadPostition = 3*7+1
            MayStorePostition = 4*7+1
            if errList and errList[-1]=="error: no assembly instructions found.\n":
                cycles = FollowStatus
                instrNums = FollowStatus
                pressure = FollowStatus
                loadPortUsage = FollowStatus
                SBPort23Pressure = FollowStatus
                resourcePressure = FollowStatus
                registerPressure = FollowStatus
                memoryPressure = FollowStatus
            else:
                # ic(list[2])
                # ic(list[11])
                instrNums = int(re.match(r"Instructions:(\s*)([0-9]*)(\s*)",list[1]).group(2))/100
                cycles = int(re.match(r"Total Cycles:(\s*)([0-9]*)(\s*)",list[2]).group(2))
                if list[11]=="No resource or data dependency bottlenecks discovered.\n":
                    pressure = 0
                else:
                    pressure = float(re.match(r"Cycles with backend pressure increase(\s*)\[ ([0-9\.]*)% \](\s*)",list[11]).group(2))              
                loadPortUsage = 0.0
                SBPort23Pressure = 0.0
                resourcePressure = 0.0
                registerPressure = 0.0
                memoryPressure = 0.0
                for i in range(len(list)):
                    # ic(list[i])
                    if re.match(r".{"+str(MayLoadPostition)+r"}\*.*$",list[i]):
                        MayLoad += 1
                    if re.match(r".{"+str(MayStorePostition)+r"}\*.*$",list[i]):
                        MayStore += 1
                    if list[i].startswith('  - SBPort23 '):
                        matchPressure = re.match(r".*\[ ([0-9\.]*)% \](\s*)$",list[i])
                        if not matchPressure:
                            SBPort23Pressure = -2
                        else:
                            SBPort23Pressure = float(matchPressure.group(1))
                    if list[i].startswith('  Resource Pressure       '):
                        matchPressure = re.match(r".*\[ ([0-9\.]*)% \](\s*)$",list[i])
                        if not matchPressure:
                            resourcePressure = -2
                        else:
                            resourcePressure = float(matchPressure.group(1))
                    elif list[i].startswith('  - Register Dependencies ['):
                        matchPressure = re.match(r".*\[ ([0-9\.]*)% \](\s*)$",list[i])
                        if not matchPressure:
                            registerPressure = -2
                        else:
                            registerPressure = float(matchPressure.group(1))
                    elif list[i].startswith('  - Memory Dependencies   ['):
                        matchPressure = re.match(r".*\[ ([0-9\.]*)% \](\s*)$",list[i])
                        if not matchPressure:
                            memoryPressure = -2
                        else:
                            memoryPressure = float(matchPressure.group(1))
                    elif list[i].startswith('Resource pressure per iteration'):     
                        matchPort = re.match(r".*(\s+)([0-9\.]+)(\s*)\n$",list[i+2])
                        if not matchPort:
                            loadPortUsage = -2
                        else:
                            loadPortUsage = float(matchPort.group(2))
            llvmCycles[bblHashStr]=cycles
            llvmInstrNums[bblHashStr]=instrNums
            llvmMayLoad[bblHashStr]=MayLoad
            llvmMayStore[bblHashStr]=MayStore
            llvmLoadPressure[bblHashStr]=max(0, MayLoad/instrNums)
            llvmStorePressure[bblHashStr]=max(0, MayStore/instrNums)
            llvmPressure[bblHashStr]=pressure      
            llvmPortUsage[bblHashStr]=loadPortUsage   
            llvmSBPort23Pressure[bblHashStr] = SBPort23Pressure
            llvmResourcePressure[bblHashStr] = resourcePressure
            llvmRegisterPressure[bblHashStr] = registerPressure
            llvmMemoryPressure[bblHashStr] = memoryPressure         
    except Exception as e:
        sendPipe.send(e)
        errorPrint("error = {}".format(e))
        print(command)
        # raise TypeError("paralleReadProcess = {}".format(e))
    queueDict.get("llvmCycles").put(llvmCycles)
    queueDict.get("llvmInstrNums").put(llvmInstrNums)
    queueDict.get("llvmMayLoad").put(llvmMayLoad)
    queueDict.get("llvmMayStore").put(llvmMayStore)
    queueDict.get("llvmLoadPressure").put(llvmLoadPressure)
    queueDict.get("llvmStorePressure").put(llvmStorePressure)
    queueDict.get("llvmPressure").put(llvmPressure)
    queueDict.get("llvmPortUsage").put(llvmPortUsage)
    queueDict.get("llvmSBPort23Pressure").put(llvmSBPort23Pressure)
    queueDict.get("llvmResourcePressure").put(llvmResourcePressure)
    queueDict.get("llvmRegisterPressure").put(llvmRegisterPressure)
    queueDict.get("llvmMemoryPressure").put(llvmMemoryPressure)
    queueDict.get("finishedSubTask").put(finishedSubTask)
    ic(str(rank) + "end")
    sendPipe.send(i+sendSkipNum)
    sendPipe.close()
    
def parallelGetSCAResult(taskName, bblSCAFile ,bblSCAPickleFile , bblHashDict):
    
    # taskName = app_info.name
    # bblSCAFile = app_info.bblSCAFile
    # bblSCAPickleFile = app_info.bblSCAPickleFile
    
    bblDict = bblDictInit()
    ProcessNum=glv._get("ProcessNum")
    DivideNum = ProcessNum-1
    
    queueDict = queueDictInit(bblDict)

    sendPipe=dict()
    receivePipe=dict()
    total=dict()
    
    # 用 items() 方法将所有的键值对转成元组
    items = list(bblHashDict.items())

    # 我们需要计算每个变量存储的键值对数量
    count = len(items) // DivideNum
    
    # 循环30次，每次取出 count 个键值对存入变量
    for i in range(DivideNum):
        ic(i)
        vars()["var_" + str(i+1)] = dict(items[i*count:(i+1)*count])
        # ic(vars()["var_" + str(i+1)])
    
    # 最后如果键值对数量不能整除30，将剩余的键值对存入一个变量
    # if len(items) % DivideNum != 0:
    vars()["var_" + str(DivideNum+1)] = dict(items[DivideNum*count:])
    # ic(vars()["var_" + str(DivideNum+1)])
    
    pList=[]
    for i in range(ProcessNum):
        receivePipe[i], sendPipe[i] = Pipe(False)
        total[i]=len(vars()["var_" + str(i+1)])
        pList.append(Process(target=getBBLFunc, args=(vars()["var_" + str(i+1)],sendPipe[i],i,queueDict)))

    for p in pList:
        p.start()
    
    if glv._get("debug")=='no':
        stdscr = curses.initscr()
        multBar(taskName,ProcessNum,total,sendPipe,receivePipe,pList,stdscr)
    
    while queueDict.get("finishedSubTask").qsize()<ProcessNum:
        print("QueueNum : {}".format(queueDict.get("finishedSubTask").qsize()))
        sys.stdout.flush()
        time.sleep(5)

    yellowPrint("Reducing parallel processes result...")
    
    for i in range(ProcessNum):
        bblDict=mergeQueue2dataDict(queueDict,bblDict)
               
    save2File(bblDict, bblSCAFile, bblSCAPickleFile)
    # decisionByLogisticRegression(bblDict, bblSCAFile, bblDecisionFile)
    # decisionByXGB(bblDict, bblSCAFile, bblDecisionFile)
    
    return bblDict

def save2File(bblDict, bblSCAFile, bblSCAPickleFile):
    with open(bblSCAPickleFile, 'wb') as f:
        pickle.dump(bblDict, f)
    
    for key, value in bblDict.dataDict.items():
        globals()[key]=value

    with open(bblSCAFile, 'w') as fsca:
        for [bblHashStr, cycles] in  llvmCycles.items():
            pressure = llvmPressure[bblHashStr]
            portUsage = llvmPortUsage[bblHashStr]
            resourcePressure = llvmResourcePressure[bblHashStr] 
            registerPressure = llvmRegisterPressure[bblHashStr] 
            memoryPressure = llvmMemoryPressure[bblHashStr] 
            fsca.write("{:36} instrNums: {:5} MayLoad: {:5} MayStore: {:5} "
                        "loadPressure: {:5} storePressure: {:5} "
                        "SBPort23Pressure: {:5} "
                        "portUsage: {:5} cycles: {:5} pressure: {:5} "
                       "resourcePressure: {:5} registerPressure: {:5} memoryPressure: {:5}\n".format(
                    bblHashStr, str(llvmInstrNums[bblHashStr]), str(llvmMayLoad[bblHashStr]), str(llvmMayStore[bblHashStr]), 
                    str(round(llvmLoadPressure[bblHashStr],3)), str(round(llvmStorePressure[bblHashStr],3)), 
                    str(round(llvmSBPort23Pressure[bblHashStr],3)), 
                    str(portUsage), str(cycles),str(pressure), 
                    str(resourcePressure), str(registerPressure), str(memoryPressure)
                )) 
            
def decisionByManual(bblDict, bblDecisionFile,prioriKnowDecision):
    for key, value in bblDict.dataDict.items():
        globals()[key]=value
     
     # bblDecisionFile save to file
    with open(bblDecisionFile, 'w') as f:
        for [bblHashStr, cycles] in  tqdm(llvmCycles.items()) :
            instrNums = llvmInstrNums[bblHashStr]
            pressure = llvmPressure[bblHashStr]   
            # reverse of Arithmetic Intensity (AI) 
            reAI = max(0,llvmLoadPressure[bblHashStr]) + max(0,llvmStorePressure[bblHashStr])   
            portPressure = max(0,llvmSBPort23Pressure[bblHashStr])
            portUsage = max(0,llvmPortUsage[bblHashStr])
            if pressure == FollowStatus:
                decision = "Follower"
            else:
                # priori knowledge
                if prioriKnowDecision == "Full-CPU":
                    decision = "CPU"
                elif portPressure > glv._get("tuning_lspressure") or reAI > glv._get("tuning_reAI")\
                    or instrNums >= glv._get("tuning_bblNum"):
                    decision = "PIM"
                else:
                    decision = "CPU"

            f.write(bblHashStr + " " + decision + \
                    " " + str(cycles) + '\n')   
            
def decisionByXGB(bblDict, bbhashXDict, bblDecisionFile):
    for key, value in bblDict.dataDict.items():
        globals()[key]=value
    
    n_estimators = glv._get("xgb_n_estimators")
    trained_model = XGBClassifier() 
    trained_model.load_model(f"./src/trainning/xgb_model_{n_estimators}.bin")
    

    # 创建新的XGBClassifier模型，并设置加载的参数
   
    # bblDecisionFile save to file
    with open(bblDecisionFile, 'w') as f:
        for [bblHashStr, cycles] in  tqdm(llvmCycles.items()) :
            pressure = llvmPressure[bblHashStr]       
            if pressure == FollowStatus:
                decision = "Follower"
            else:
                value = bbhashXDict[bblHashStr.split(" ")[-1]]
                y_pred = trained_model.predict([value])
                if y_pred == 1:
                    decision = "PIM"
                else:
                    decision = "CPU"

            f.write(bblHashStr + " " + decision + \
                    " " + str(cycles) + '\n')   
    
# discarded function
def decisionByLogisticRegression(bblDict, bblSCAFile, bblDecisionFile):
    for key, value in bblDict.dataDict.items():
        globals()[key]=value
    with open('./src/trainning/Coefficients.txt','r') as f:
        data = json.load(f)
    coefficients = data["coefficients"]
    intercept = data["intercept"]
    # 打印模型参数
    ic(intercept, coefficients)
    
    # bblDecisionFile, bblSCAFile save to file
    with open(bblSCAFile, 'w') as fsca:
            with open(bblDecisionFile, 'w') as f:
                for [bblHashStr, cycles] in llvmCycles.items() :
                    pressure = llvmPressure[bblHashStr]
                    portUsage = llvmPortUsage[bblHashStr]
                    resourcePressure = llvmResourcePressure[bblHashStr] 
                    registerPressure = llvmRegisterPressure[bblHashStr] 
                    memoryPressure = llvmMemoryPressure[bblHashStr]   
                    
                    Affinity = coefficients[0]*portUsage + coefficients[1]*cycles +\
                                coefficients[2]*resourcePressure + coefficients[3]*registerPressure +\
                                coefficients[4]*memoryPressure + intercept
                    if pressure == FollowStatus:
                        decision = "Follower"
                    elif Affinity > 0: # log(CPU/PIM) > 0
                        decision = "PIM"
                    else:
                        decision = "CPU"
                    
                    # elif portUsage > 0 and pressure*6 + cycles > 306: #enough big 2 PIM
                    #     decision = "PIM"
                    # elif pressure >= 50:
                    #     decision = "PIM"
                    # else:
                    #     decision = "CPU"
                    f.write(bblHashStr + " " + decision + \
                            " " + str(cycles) + '\n')   
                    fsca.write("{:36} {:10} portUsage: {:5} cycles: {:5} pressure: {:5} resourcePressure: {:5} registerPressure: {:5} memoryPressure: {:5}\n".format(
                                bblHashStr, decision,
                                str(portUsage),
                                str(cycles),
                                str(pressure), str(resourcePressure), str(registerPressure), str(memoryPressure)
                            )) 