

import config  # 加载配置
from config import pasteFullFileName
import global_variable as glv
from input_process import inputParameters, isIceEnable
# from excel import *
from multiProcess import *
from logPrint import *

def main():
    ## icecream & input
    args=inputParameters()
    isIceEnable(args.debug)
    # checkFile(glv._get("taskfilePath"))
    # wb = excelGraphInit()
    
    isFirstSheet=1
    taskList = glv._get("taskList")
    processBeginTime=timeBeginPrint("multiple taskList")

    # Step1: manual compile all exe before run-sniper phase
    
    # Step2: run-sniper phase
    # Step2.1: parallel run single cpu mode
    parallelTask( taskList, singleCpuMode)
    # Step2.2: consecutive run multi pim-cores mode
    multiCorePIMMode(taskList, 32)

    # Step3: run modified PIMProf result
    parallelTask(taskList, pimprof, coreCount=32 ) # 
    # for taskKey, taskName in taskList.items():
    #     errorPrint("-----------------------------------Task cut line----------------------------------------")
    #     # filename=pasteFullFileName(taskKey)
    #     ic(taskKey)
    #     dataDict = dataDictInit()
    #     glv._set("historyDict",readDictFromJson(taskName))
        

    #     dataDict = parallelReadPartFile(taskName,filename, dataDict)
    #     saveDict2Json(taskName,dataDict.dataDict)
    #     print("blockSize {} {}".format(len(dataDict.get("unique_revBiblock")),len(dataDict.get("frequencyRevBiBlock"))))
    #     # generateHeatmapPic(taskName,dataDict)

    #     # addData2Excel(wb,taskName,isFirstSheet,dataDict)

    #     isFirstSheet=0
    #     timeEndPrint(taskName,processBeginTime)
    # excelGraphBuild(wb,processBeginTime)
    timeEndPrint("multiple taskList",processBeginTime)
if __name__ == "__main__":
    main()