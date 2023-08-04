import config  # 加载配置
from config import pasteFullFileName
import global_variable as glv
from input_process import inputParameters, isIceEnable
# from excel import *
from multiProcess import *
from logPrint import *
from analysis import *
from graph import *
from SCA import *

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
            #  taskfilePath+"spmv/spmv0.inj": "spmv0", #./spmv -f ./data/bcsstk30.mtx 
            #  taskfilePath+"spmv/spmv.inj": "spmv", 
             taskfilePath+"select/select.inj": "select", # ./sel -i 1258291200 -t 4
             taskfilePath+"unique/unique.inj": "unique", # first default
             taskfilePath+"hashJoin/hashjoin.inj": "hashjoin", # ./hashjoin.inj checker/R.file checker/S.file hash 40
             taskfilePath+"mlp/mlp.inj": "mlp" # 3.9s
            #  taskfilePath+"svm/svm.inj": "svm" # 2.7s ./svm.inj ./SVM-RFE/outData.txt 253 15154 4
         }
    processBeginTime=timeBeginPrint("multiple taskList")

    for diffGraph in glv._get("gapbsGraphNameList"):
        glv._set("gapbsGraphName", diffGraph)
        
        errorPrint("-----------------------------------STEP3: Get the real time base one different ways----------------------------------------")
        # Step3: run modified PIMProf result
        all_for_one = CTS(taskList)
        parallelTask(all_for_one, pimprof, coreCount=32 ) # 
        
        errorPrint("-----------------------------------STEP3.1: Get the real time base one different ways----------------------------------------")
        all_for_one.pimprof("func", 32)
        
        errorPrint("-----------------------------------STEP4----------------------------------------")
        # Step4: build excel & graphics to analyse results
        errorPrint("-----------------------------------STEP4.1: Read key value from real result file----------------------------------------")
        # save to global variable graphAppDict && graphAppDetailDict
        analyseResults(taskList, coreCount=32 ) 
        all_for_one.get_time_result()
        all_for_one.print_time_result()
        errorPrint("-----------------------------------STEP4.2: Normalized data & Visualization ----------------------------------------")
        
        # [maxValue, scaAvgTime,availAppCount] = generateAppComparisonGraph()   
        # generateAppStackedBar()
        generateAppStackedBarPlotly(2,all_for_one)
        
        scaAvgTime = all_for_one.avg_time("bbls", "SCA")
        passPrint(f"SCA AVG Time is {scaAvgTime}\n")
        passPrint(f"SCA AVG SpeedUp is {round(1/scaAvgTime,2)}\n")
        
        passPrint("-----------------------------------{}----------------------------------------".format(diffGraph))

    timeEndPrint("multiple taskList",processBeginTime)

if __name__ == "__main__":
    main()