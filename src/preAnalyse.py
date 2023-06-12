import config  # 加载配置
from config import pasteFullFileName
import global_variable as glv
from input_process import inputParameters, isIceEnable
# from excel import *
from multiProcess import *
from logPrint import *
from analysis import *
from graph import *
from SCA import OffloadBySCA

def main():
    ## icecream & input
    args=inputParameters()
    isIceEnable(args.debug)

    gapbsTaskfilePath = "/staff/shaojiemike/github/sniper_PIMProf/PIMProf/gapbs/"
    taskfilePath = "/staff/shaojiemike/github/sniper_PIMProf/PIMProf/"
    taskList = {
             gapbsTaskfilePath+"bc.inj": "bc",
             gapbsTaskfilePath+"sssp.inj": "sssp",
             gapbsTaskfilePath+"cc.inj": "cc",
             gapbsTaskfilePath+"bfs.inj": "bfs",
             gapbsTaskfilePath+"pr.inj": "pr",
             taskfilePath+"gemv/gemv.inj": "gemv", 
             taskfilePath+"spmv/spmv.inj": "spmv0", #./spmv -f ./data/bcsstk30.mtx 
            #  taskfilePath+"spmv/spmv.inj": "spmv", 
             taskfilePath+"select/select.inj": "select", # ./sel -i 1258291200 -t 4
             taskfilePath+"unique/unique.inj": "unique", # first default
            #  taskfilePath+"hashJoin/hashjoin.inj": "hashjoin", # ./hashjoin.inj checker/R.file checker/S.file hash 40
             taskfilePath+"mlp/mlp.inj": "mlp" # 3.9s
            #  taskfilePath+"svm/svm.inj": "svm" # 2.7s ./svm.inj ./SVM-RFE/outData.txt 253 15154 4
         }
    processBeginTime=timeBeginPrint("multiple taskList")

    for diffGraph in glv._get("gapbsGraphNameList"):
        glv._set("gapbsGraphName", diffGraph)
        
        errorPrint("-----------------------------------STEP3----------------------------------------")
        # Step3: run modified PIMProf result
        parallelTask(taskList, pimprof, coreCount=32 ) # 
        
        errorPrint("-----------------------------------STEP4----------------------------------------")
        # Step4: build excel & graphics to analyse results
        analyseResults(taskList, coreCount=32 ) 
        maxValue = generateAppComparisonGraph()
        
        errorPrint("-----------------------------------STEP4.1----------------------------------------")
        
        # generateAppStackedBar()
        generateAppStackedBarPlotly(maxValue)
        passPrint("-----------------------------------{}----------------------------------------".format(diffGraph))

    timeEndPrint("multiple taskList",processBeginTime)

if __name__ == "__main__":
    main()