import global_variable as glv
import sys
import multiprocessing as mp
from data import queueDictInit
from multiprocessing import Pipe,Queue
# from multiBar import *
from collections import defaultdict
# from Bhive import *
# from llvm_mca import *
# from OSACA import *
from collections import defaultdict
# from KendallIndex import calculateKendallIndex
from data import dataDictInit,dataDictClass
from terminal_command import *
from subProcessCommand import *
from tsjPython.tsjCommonFunc import *
import traceback
import time

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
            assert len(list)!=0
        else:
            yellowPrint("[   {}/{}   ] PIM-{} Task {} already finished".format( countId, totolCount,coreNums, taskName))
        passPrint("[   {}/{}   ] PIM-{} Task {} finished successfully".format( countId, totolCount,coreNums, taskName))

    
def singleCpuMode(queueDict, taskKey, taskName, countId, totolCount):
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
    
def parallelSingleCpuMode(taskList):
    
    dataDict = dataDictInit()
    queueDict = queueDictInit(dataDict)
    
    pList=[]
    totolCount = len(taskList)
    countId = 0
    for taskKey, taskName in taskList.items():
        countId = countId + 1
        pList.append(Process(target=singleCpuMode, args=(queueDict, taskKey, taskName, countId, totolCount)))   
        
    for p in pList:
        p.start()
        
    ProcessNum = len(taskList)
    time.sleep(0.5)
    while queueDict.get("finishedSubTask").qsize()<ProcessNum:
        print("QueueNum : {}".format(queueDict.get("finishedSubTask").qsize()))
        sys.stdout.flush()
        time.sleep(5)

    yellowPrint("Reducing parallel processes result...")

