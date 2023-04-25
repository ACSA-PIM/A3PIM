
from excel import *
from terminal_command import *
import math

def analyseResults(taskList, **kwargs):
    if "coreCount" in kwargs:
        pimCoreCount = int(kwargs["coreCount"])
    wb = excelGraphInit()
    totolCount = len(taskList)
    countId = 0
    for taskKey, taskName in taskList.items():
        countId = countId + 1
        write2ExcelList = [taskName] + readDataFromOutputFile(taskName, pimCoreCount)
        excelGraphAdd(wb, write2ExcelList)

def readDataFromOutputFile(taskName, pimCoreCount):
    cpucore = 1
    pimprofResultPath = glv._get("resultPath")+glv._get("gapbsGraphName")+"_cpu_"+ str(cpucore)+"_pim_"+ str(pimCoreCount)
    mkdir(pimprofResultPath)
    targetFile = pimprofResultPath+"/reusedecision_"+taskName+"_cpu_"+ str(cpucore)+"_pim_"+ str(pimCoreCount)+".out"
    excelOutFile = pimprofResultPath+"/Summary_cpu_"+ str(cpucore)+"_pim_"+ str(pimCoreCount)+".xlsx"
    glv._set("excelOutPath",excelOutFile)
    
    if not checkFileExists(targetFile):
        errorPrint("Could not find decision file!!!")
        exit(1)
    else:
        return readListBasedonName(targetFile)

def readListBasedonName(targetFile):
    regexPattern = {
            1:"CPU only time \(ns\): (.*)$",
            2:"PIM only time \(ns\): (.*)$",
            3:"Instruction (.*)$",
            4:"MPKI offloading time \(ns\): (.*) = CPU (.*)$",
            5:"Greedy offloading time \(ns\): (.*) = CPU (.*)$",
            6:"Reuse offloading time \(ns\): (.*) = CPU (.*)$"
        }
    ic(targetFile)
    fread=open(targetFile, 'r') 
    useLineCount=6
    lineNum = 1
    resultList=[]
    while lineNum <= useLineCount:
        line = fread.readline()
        ic(line)
        costTime = string2int(re.search(regexPattern[lineNum],line).group(1))
        resultList.append(costTime)
        lineNum = lineNum + 1
    ic(resultList)
    return resultList

def string2int(S):
    floatGroup = re.search("(.*)e+(.*)$",S)
    if floatGroup:
        return int(float(floatGroup.group(1)) * pow(10, int(floatGroup.group(2))))
    else:
        return int(S)
        