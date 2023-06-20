import sys
sys.path.append('./src')

import global_variable as glv


def resultFromPIMProf(taskKey, taskName):
    cpucore = 1
    pimCoreCount = 32
    if taskName in glv._get("gapbsList"):
        class1 = glv._get("gapbsGraphName")
    elif taskName in glv._get("specialInputList"):
        class1 = "special"
    else:
        class1 = "default"
    pimprofResultPath = glv._get("resultPath")+class1+"_cpu_"+ str(cpucore)+"_pim_"+ str(pimCoreCount)
    targetFile = pimprofResultPath+"/reusedecision_"+taskName+"_cpu_"+ str(cpucore)+"_pim_"+ str(pimCoreCount)+".out"
    ic(targetFile)
    status = 0 # 1,2,3 record
    bbhashYDict = dict()
    with open(targetFile, 'r') as file:
        for line in file:
            if line.startswith('top10PIMProfBB') or line.startswith('ShowBBTime') or\
               line.startswith('top10SCABB'):
                status += 1
            elif line.startswith('========='):
                continue
            elif status > 3:
                break
            elif status > 0:
                # ic(line)
                fields = line.split()
                # ic(fields[5],fields[6],fields[-2],fields[-1])
                bbhashYDict[fields[-1]] = [int(float(fields[5])),int(float(fields[6]))] # CPU, PIM
    # ic(bbhashYDict)
    return bbhashYDict
        
    
def resultFromSCAFile(targetFile):
    ic(targetFile)
    xgb_train_metrix = glv._get("xgb_train_metrix")
    xgbInputIndex = glv._get("xgb_sca_dataIndex")
    scaIndex = [xgbInputIndex[i] for i in xgb_train_metrix]
    ic(scaIndex)
    bbhashXDict = dict()
    with open(targetFile, 'r') as file:
        for line in file:
            fields = line.split()
            if fields[xgbInputIndex["instrNums"]]!=-1:
                ic(fields[0],fields[1],[fields[i] for i in scaIndex])
                bbhashXDict[fields[1]] = [max(0,float(fields[i])) for i in scaIndex]
    return bbhashXDict
    
def resultFromSCA(taskKey, taskName, curBBhashYDict):
    targetFile = glv._get("logPath") + "assembly/" + taskName + "_bbl.sca"
    ic(targetFile)
    xgb_train_metrix = glv._get("xgb_train_metrix")
    xgbInputIndex = glv._get("xgb_sca_dataIndex")
    scaIndex = [xgbInputIndex[i] for i in xgb_train_metrix]
    ic(scaIndex)
    bbhashXDict = dict()
    with open(targetFile, 'r') as file:
        for line in file:
            fields = line.split()
            if fields[1] in curBBhashYDict and fields[xgbInputIndex["instrNums"]]!=-1:
                ic(fields[0],fields[1],[fields[i] for i in scaIndex])
                bbhashXDict[fields[1]] = [max(0,float(fields[i])) for i in scaIndex]
    return bbhashXDict