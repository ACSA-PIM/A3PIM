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
        yellowPrint("[   {}/{}   ] PIM-{} Task {} is running……".format( countId, totolCount,coreNums, taskName))
        if taskName in glv._get("gapbsList"):
            [core, command,targetFile] = gapbsInput(taskKey, taskName, "pim", coreNums)
        if not checkFileExists(targetFile):
            list=TIMEOUT_COMMAND(core, command,glv._get("timeout"))
            ic(list)
            if not checkFileExists(targetFile):
                errorPrint("{}-PIM falied for targetFile {} not found".format(taskName,targetFile))
                yellowPrint("Falied command {}".format(command))
                exit(1)
        else:
            yellowPrint("[   {}/{}   ] PIM-{} Task {} already finished".format( countId, totolCount,coreNums, taskName))
        passPrint("[   {}/{}   ] PIM-{} Task {} finished successfully".format( countId, totolCount,coreNums, taskName))

def pimprof(queueDict, taskKey, taskName, countId, totolCount, coreCount):
    yellowPrint("[   {}/{}   ] PIMProf {} is running……".format( countId, totolCount, taskName))
    [command,targetFile, redirect2log] = pimprofInput(taskKey, taskName, coreCount)
    print(command)
    if not checkFileExists(targetFile):
        list=TIMEOUT_COMMAND_2FILE(1, command, redirect2log, glv._get("timeout"))
        ic(list)
        assert len(list)!=0
    else:
        yellowPrint("[   {}/{}   ] PIMProf {} already finished".format( countId, totolCount, taskName))
    passPrint("[   {}/{}   ] PIMProf {} finished successfully".format( countId, totolCount, taskName))
    queueDict.get("finishedSubTask").put(taskName)
    
def singleCpuMode(queueDict, taskKey, taskName, countId, totolCount, **kwargs):
    sys.stdout.flush()
    yellowPrint("[   {}/{}   ] CPU-1 Task {} is running……".format( countId, totolCount, taskName))
    if taskName in glv._get("gapbsList"):
        [core, command,targetFile] = gapbsInput(taskKey, taskName, "cpu", 1)
    if not checkFileExists(targetFile):
        list=TIMEOUT_COMMAND(core, command,glv._get("timeout"))
        ic(list)
        assert len(list)!=0
    else:
        yellowPrint("[   {}/{}   ] CPU-1 Task {} already finished".format( countId, totolCount, taskName))
    passPrint("[   {}/{}   ] CPU-1 Task {} finished successfully".format( countId, totolCount, taskName))
    queueDict.get("finishedSubTask").put(taskName)
    

def singleDisassembly(queueDict, taskKey, taskName, countId, totolCount, **kwargs):
    sys.stdout.flush()
    yellowPrint("[   {}/{}   ] Disassembly-1 Task {} is running……".format( countId, totolCount, taskName))
    if taskName in glv._get("gapbsList"):
        [command,targetFile] = disassemblyInput(taskKey, taskName)
    if not checkFileExists(targetFile):
        # list=TIMEOUT_COMMAND(1, command,glv._get("timeout")) weird, can not parallel objdump > Difffile
        list=TIMEOUT_COMMAND_2FILE(1, command, targetFile, glv._get("timeout"))
        ic(list)
        assert len(list)!=0
    else:
        yellowPrint("[   {}/{}   ] Disassembly-1 Task {} already finished".format( countId, totolCount, taskName))
    abstractBBLfromAssembly(targetFile)
    passPrint("[   {}/{}   ] Disassembly-1 Task {} finished successfully".format( countId, totolCount, taskName))
    queueDict.get("finishedSubTask").put(taskName)
    
    
def parallelTask(taskList, SubFunc,  **kwargs):
    
    dataDict = dataDictInit()
    queueDict = queueDictInit(dataDict)
    
    pList=[]
    totolCount = len(taskList)
    countId = 0
    for taskKey, taskName in taskList.items():
        countId = countId + 1
        if "coreCount" in kwargs:
            ic(kwargs)
            pList.append(Process(target=SubFunc, args=(queueDict, taskKey, taskName, countId, totolCount, int(kwargs["coreCount"]))))
        else:
            pList.append(Process(target=SubFunc, args=(queueDict, taskKey, taskName, countId, totolCount)))
            
        
    for p in pList:
        p.start()
        
    ProcessNum = len(taskList)
    time.sleep(0.5)
    while queueDict.get("finishedSubTask").qsize()<ProcessNum:
        print("QueueNum : {}".format(queueDict.get("finishedSubTask").qsize()))
        sys.stdout.flush()
        time.sleep(5)

    yellowPrint("Reducing parallel processes result...")

        
def llvmCommand(bblList):
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
    llvmPressure = defaultdict(float)
    llvmPortUsage = defaultdict(float)
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
            [list, errList]=TIMEOUT_severalCOMMAND(command, glv._get("timeout"))
            # ic(errList)
            if errList and errList[-1]=="error: no assembly instructions found.\n":
                cycles = FollowStatus
                pressure = FollowStatus
                loadPortUsage = FollowStatus
            else:
                # ic(list[2])
                # ic(list[11])
                cycles = int(re.match(r"Total Cycles:(\s*)([0-9]*)(\s*)",list[2]).group(2))
                if list[11]=="No resource or data dependency bottlenecks discovered.\n":
                    pressure = 0
                else:
                    pressure = float(re.match(r"Cycles with backend pressure increase(\s*)\[ ([0-9\.]*)% \](\s*)",list[11]).group(2))              
                loadPortUsage = 0.0
                for i in range(len(list)):
                    # ic(list[i])
                    if list[i].startswith('Resource pressure per iteration'):     
                        matchPort = re.match(r".*(\s+)([0-9\.]+)(\s*)\n$",list[i+2])
                        if not matchPort:
                            loadPortUsage = -2
                        else:
                            loadPortUsage = float(matchPort.group(2))
            llvmCycles[bblHashStr]=cycles
            llvmPressure[bblHashStr]=pressure      
            llvmPortUsage[bblHashStr]=loadPortUsage             
    except Exception as e:
        sendPipe.send(e)
        errorPrint("error = {}".format(e))
        raise TypeError("paralleReadProcess = {}".format(e))
    queueDict.get("llvmCycles").put(llvmCycles)
    queueDict.get("llvmPressure").put(llvmPressure)
    queueDict.get("llvmPortUsage").put(llvmPortUsage)
    queueDict.get("finishedSubTask").put(finishedSubTask)
    ic(str(rank) + "end")
    sendPipe.send(i+sendSkipNum)
    sendPipe.close()
    
def parallelGetBBL(taskName, bblHashDict, bblDecisionFile, bblSCAFile):
    bblDict = bblDictInit()
    ProcessNum=glv._get("ProcessNum")
    
    queueDict = queueDictInit(bblDict)

    sendPipe=dict()
    receivePipe=dict()
    total=dict()
    
    # 用 items() 方法将所有的键值对转成元组
    items = list(bblHashDict.items())

    # 我们需要计算每个变量存储的键值对数量
    count = len(items) // ProcessNum
    
    # 循环30次，每次取出 count 个键值对存入变量
    for i in range(ProcessNum):
        ic(i)
        vars()["var_" + str(i+1)] = dict(items[i*count:(i+1)*count])
        # ic(vars()["var_" + str(i+1)])
    
    # 最后如果键值对数量不能整除30，将剩余的键值对存入一个变量
    # if len(items) % ProcessNum != 0:
    vars()["var_" + str(ProcessNum+1)] = dict(items[ProcessNum*count:])
    # ic(vars()["var_" + str(ProcessNum+1)])
    
    pList=[]
    for i in range(ProcessNum+1):
        receivePipe[i], sendPipe[i] = Pipe(False)
        total[i]=len(vars()["var_" + str(i+1)])
        pList.append(Process(target=getBBLFunc, args=(vars()["var_" + str(i+1)],sendPipe[i],i,queueDict)))

    for p in pList:
        p.start()
    
    if glv._get("debug")=='no':
        stdscr = curses.initscr()
        multBar(taskName,ProcessNum+1,total,sendPipe,receivePipe,pList,stdscr)
    
    while queueDict.get("finishedSubTask").qsize()<ProcessNum:
        print("QueueNum : {}".format(queueDict.get("finishedSubTask").qsize()))
        sys.stdout.flush()
        time.sleep(5)

    yellowPrint("Reducing parallel processes result...")
    
    for i in range(ProcessNum):
        bblDict=mergeQueue2dataDict(queueDict,bblDict)
        
    for key, value in bblDict.dataDict.items():
        globals()[key]=value
        
    # bblDecisionFile, bblSCAFile save to file
    with open(bblSCAFile, 'w') as fsca:
            with open(bblDecisionFile, 'w') as f:
                for [bblHashStr, cycles] in llvmCycles.items() :
                    pressure = llvmPressure[bblHashStr]
                    portUsage = llvmPortUsage[bblHashStr]
                    if pressure == FollowStatus:
                        decision = "Follower"
                    elif portUsage > 0 and cycles > 200: #enough big 2 PIM
                        decision = "PIM"
                    elif pressure >= 40:
                        decision = "PIM"
                    else:
                        decision = "CPU"
                    f.write(bblHashStr + " " + decision + \
                            " " + str(cycles) + '\n')   
                    fsca.write(bblHashStr + "\t" + decision + \
                                " portUsage: " + str(portUsage) + \
                                "\t pressure: " + str(pressure) + \
                                "\t cycles: " + str(cycles) + '\n')    
    return bblDict