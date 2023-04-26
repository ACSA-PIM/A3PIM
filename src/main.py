

import config  # 加载配置
from config import pasteFullFileName
import global_variable as glv
from input_process import inputParameters, isIceEnable
# from excel import *
from multiProcess import *
from logPrint import *
from analysis import *
from graph import *

def main():
    ## icecream & input
    args=inputParameters()
    isIceEnable(args.debug)

    taskList = glv._get("taskList")
    processBeginTime=timeBeginPrint("multiple taskList")

    for diffGraph in glv._get("gapbsGraphNameList"):
        glv._set("gapbsGraphName", diffGraph)
        # Step1: manual compile all exe before run-sniper phase
        errorPrint("-----------------------------------{}----------------------------------------".format(diffGraph))
        errorPrint("-----------------------------------STEP1----------------------------------------")
        
        
        errorPrint("-----------------------------------STEP2.1----------------------------------------")
        # Step2: run-sniper phase
        # Step2.1: parallel run single cpu mode
        parallelTask( taskList, singleCpuMode)
        errorPrint("-----------------------------------STEP2.2----------------------------------------")
        
        # Step2.2: consecutive run multi pim-cores mode
        multiCorePIMMode(taskList, 32)

        errorPrint("-----------------------------------STEP3----------------------------------------")
        # Step3: run modified PIMProf result
        parallelTask(taskList, pimprof, coreCount=32 ) # 
        
        # Step4: build excel & graphics to analyse results
        analyseResults(taskList, coreCount=32 ) 
        generateAppComparisonGraph()
        passPrint("-----------------------------------{}----------------------------------------".format(diffGraph))

    #     # addData2Excel(wb,taskName,isFirstSheet,dataDict)

    #     isFirstSheet=0
    #     timeEndPrint(taskName,processBeginTime)
    # excelGraphBuild(wb,processBeginTime)
    timeEndPrint("multiple taskList",processBeginTime)
if __name__ == "__main__":
    main()