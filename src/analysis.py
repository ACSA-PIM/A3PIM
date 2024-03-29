
from excel import *
from terminal_command import *
import math

def analyseResults(taskList, **kwargs):
    if "coreCount" in kwargs:
        pimCoreCount = int(kwargs["coreCount"])
    wb = excelGraphInit()
    totolCount = len(taskList)
    countId = 0
    
    cpucore = 1
    class1 = glv._get("gapbsGraphName")
    pimprofResultPath = glv._get("resultPath")+class1+"_cpu_"+ str(cpucore)+"_pim_"+ str(pimCoreCount)
    mkdir(pimprofResultPath)
    excelOutFile = pimprofResultPath+"/Summary_cpu_"+ str(cpucore)+"_pim_"+ str(pimCoreCount)+".xlsx"
    graphOutFile = pimprofResultPath+"/ExeTime_cpu_"+ str(cpucore)+"_pim_"+ str(pimCoreCount)+".png"
    graphOutFileTest1 = pimprofResultPath+"/speedup_ExeTime_cpu_"+ str(cpucore)+"_pim_"+ str(pimCoreCount)+".png"
    graphOutFileTest2 = pimprofResultPath+"/stackedBar_ExeTime_cpu_"+ str(cpucore)+"_pim_"+ str(pimCoreCount)+".png" 
    glv._set("graphlOutPath",graphOutFile)
    glv._set("graphlOutPathTest1",graphOutFileTest1)
    glv._set("graphlOutPathTest2",graphOutFileTest2)
    glv._set("excelOutPath",excelOutFile)
    
    for taskKey, taskName in taskList.items():
        countId = countId + 1
        
        # func
        [Instructions, resultList] = readDataFromOutputFile(taskName, pimCoreCount, "func")
        glvGraphDict = glv._get("graphAppDict_func")
        glvGraphDict[taskName] = resultList
        # ic(glvGraphDict)
        glv._set("graphAppDict_func",glvGraphDict)
        
        # bbls
        [Instructions, resultList] = readDataFromOutputFile(taskName, pimCoreCount)
        glvGraphDict = glv._get("graphAppDict")
        glvGraphDict[taskName] = resultList
        # ic(glvGraphDict)
        glv._set("graphAppDict",glvGraphDict)
        
        # set excel
        write2ExcelList = [taskName]
        write2ExcelList.append(Instructions) 
        write2ExcelList += resultList
        excelGraphAdd(wb, write2ExcelList)
    
    return pimprofResultPath

def readDataFromOutputFile(taskName, pimCoreCount, bbls_func="bbls"):
    cpucore = 1
    if taskName in glv._get("gapbsList"):
        class1 = glv._get("gapbsGraphName")
    elif taskName in glv._get("specialInputList"):
        class1 = "special"
    else:
        class1 = "default"
        
    class1 += f"{'_func' if bbls_func=='func' else ''}"
    pimprofResultPath = glv._get("resultPath")+class1+"_cpu_"+ str(cpucore)+"_pim_"+ str(pimCoreCount)
    mkdir(pimprofResultPath)
    targetFile = pimprofResultPath+"/reusedecision_"+taskName+"_cpu_"+ str(cpucore)+"_pim_"+ str(pimCoreCount)+".out"
    
    
    if not checkFileExists(targetFile):
        errorPrint("Could not find pimprof result file!!!")
        exit(1)
    else:
        glvGraphDict = glv._get("graphAppDetailDict"+f"{'_func' if bbls_func=='func' else ''}")
        glvGraphDict[taskName] = readListDetail(targetFile)
        # ic(glvGraphDict)
        glv._set("graphAppDetailDict"+f"{'_func' if bbls_func=='func' else ''}",glvGraphDict)
        return readListBasedonName(targetFile)
    
def readListDetail(targetFile):
    regexPattern = {
        1:"CPU only time \(ns\): (.*)$",
        2:"PIM only time \(ns\): (.*)$",
        3:"Instruction (.*)$",
        4:"MPKI offloading time \(ns\): (.*) = CPU (.*) \+ PIM (.*) \+ REUSE (.*) \+ SWITCH (.*)$",
        5:"Greedy offloading time \(ns\): (.*) = CPU (.*) \+ PIM (.*) \+ REUSE (.*) \+ SWITCH (.*)$",
        6:"Reuse offloading time \(ns\): (.*) = CPU (.*) \+ PIM (.*) \+ REUSE (.*) \+ SWITCH (.*)$",
        7:"CTS offloading time \(ns\): (.*) = CPU (.*) \+ PIM (.*) \+ REUSE (.*) \+ SWITCH (.*)$",
        8:"SCAFromfile offloading time \(ns\): (.*) = CPU (.*) \+ PIM (.*) \+ REUSE (.*) \+ SWITCH (.*)$",
        9:"SCA offloading time \(ns\): (.*) = CPU (.*) \+ PIM (.*) \+ REUSE (.*) \+ SWITCH (.*)$"
        }
    ic(targetFile)
    fread=open(targetFile, 'r') 
    useLineCount=8
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
            6:"Reuse offloading time \(ns\): (.*) = CPU (.*)$",
            7:"CTS offloading time \(ns\): (.*) = CPU (.*)$",
            8:"SCAFromfile offloading time \(ns\): (.*) = CPU (.*)$",
            9:"SCA offloading time \(ns\): (.*) = CPU (.*)$"
        }
    ic(targetFile)
    fread=open(targetFile, 'r') 
    useLineCount=8
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
        