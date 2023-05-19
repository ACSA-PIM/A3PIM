
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
        [Instructions, resultList] = readDataFromOutputFile(taskName, pimCoreCount)
        glvGraphDict = glv._get("graphAppDict")
        glvGraphDict[taskName] = resultList
        # ic(glvGraphDict)
        glv._set("graphAppDict",glvGraphDict)
        write2ExcelList = [taskName]
        write2ExcelList.append(Instructions) 
        write2ExcelList += resultList
        excelGraphAdd(wb, write2ExcelList)

def readDataFromOutputFile(taskName, pimCoreCount):
    cpucore = 1
    pimprofResultPath = glv._get("resultPath")+glv._get("gapbsGraphName")+"_cpu_"+ str(cpucore)+"_pim_"+ str(pimCoreCount)
    mkdir(pimprofResultPath)
    targetFile = pimprofResultPath+"/reusedecision_"+taskName+"_cpu_"+ str(cpucore)+"_pim_"+ str(pimCoreCount)+".out"
    excelOutFile = pimprofResultPath+"/Summary_cpu_"+ str(cpucore)+"_pim_"+ str(pimCoreCount)+".xlsx"
    graphOutFile = pimprofResultPath+"/ExeTime_cpu_"+ str(cpucore)+"_pim_"+ str(pimCoreCount)+".png"
    graphOutFileTest1 = pimprofResultPath+"/test1_ExeTime_cpu_"+ str(cpucore)+"_pim_"+ str(pimCoreCount)+".png"
    graphOutFileTest2 = pimprofResultPath+"/test2_ExeTime_cpu_"+ str(cpucore)+"_pim_"+ str(pimCoreCount)+".png"
    
    glv._set("graphlOutPath",graphOutFile)
    glv._set("graphlOutPathTest1",graphOutFileTest1)
    glv._set("graphlOutPathTest2",graphOutFileTest2)
    glv._set("excelOutPath",excelOutFile)
    
    if not checkFileExists(targetFile):
        errorPrint("Could not find decision file!!!")
        exit(1)
    else:
        glvGraphDict = glv._get("graphAppDetailDict")
        glvGraphDict[taskName] = readListDetail(targetFile)
        # ic(glvGraphDict)
        glv._set("graphAppDetailDict",glvGraphDict)
        return readListBasedonName(targetFile)
    
def readListDetail(targetFile):
    regexPattern = {
        1:"CPU only time \(ns\): (.*)$",
        2:"PIM only time \(ns\): (.*)$",
        3:"Instruction (.*)$",
        4:"MPKI offloading time \(ns\): (.*) = CPU (.*) \+ PIM (.*) \+ REUSE (.*) \+ SWITCH (.*)$",
        5:"Greedy offloading time \(ns\): (.*) = CPU (.*) \+ PIM (.*) \+ REUSE (.*) \+ SWITCH (.*)$",
        6:"Reuse offloading time \(ns\): (.*) = CPU (.*) \+ PIM (.*) \+ REUSE (.*) \+ SWITCH (.*)$",
        7:"SCA offloading time \(ns\): (.*) = CPU (.*) \+ PIM (.*) \+ REUSE (.*) \+ SWITCH (.*)$"
        }
    ic(targetFile)
    fread=open(targetFile, 'r') 
    useLineCount=7
    lineNum = 1
    resultList=[]
    while lineNum <= useLineCount:
        line = fread.readline()
        ic(line)

        if lineNum == 1:
            costTime = [] 
            costTime.append(string2int(re.search(regexPattern[lineNum],line).group(1)))
            costTime += [0,0,0]
            resultList.append(costTime)
        elif lineNum == 2:
            costTime = [] 
            costTime += [0]
            costTime.append(string2int(re.search(regexPattern[lineNum],line).group(1)))
            costTime += [0,0]
            resultList.append(costTime)
        elif lineNum == 3:
            lineNum = lineNum + 1
            continue
        else:
            costTime = [] 
            costTime.append(string2int(re.search(regexPattern[lineNum],line).group(2)))
            costTime.append(string2int(re.search(regexPattern[lineNum],line).group(3)))
            costTime.append(string2int(re.search(regexPattern[lineNum],line).group(4)))
            costTime.append(string2int(re.search(regexPattern[lineNum],line).group(5)))
            resultList.append(costTime) 
        lineNum = lineNum + 1
    ic(resultList)
    return resultList

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
        if lineNum == 3:
            Instructions = string2int(re.search(regexPattern[lineNum],line).group(1))
        else:
            costTime = string2int(re.search(regexPattern[lineNum],line).group(1))
            resultList.append(costTime)
        lineNum = lineNum + 1
    ic(resultList)
    return [Instructions, resultList]

def string2int(S):
    floatExp = re.search("(.*)e+(.*)$",S)
    if floatExp:
        return int(float(floatExp.group(1)) * pow(10, int(floatExp.group(2))))
    else:
        floatGroup = re.search("([0-9]*)\.(.*)$",S)
        if floatGroup:
            return int(floatGroup.group(1))
        else:
            return int(S)
        