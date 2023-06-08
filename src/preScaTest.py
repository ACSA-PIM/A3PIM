import config  # 加载配置
import global_variable as glv
from analysis import *
from config import pasteFullFileName
from graph import *
from input_process import inputParameters, isIceEnable
from logPrint import *
# from excel import *
from multiProcess import *
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
            #  taskfilePath+"gemv/gemv.inj": "gemv", 
             taskfilePath+"spmv/spmv.inj": "spmv", #./spmv -f ./data/bcsstk30.mtx 
             taskfilePath+"select/select.inj": "select", # ./sel -i 1258291200 -t 4
             taskfilePath+"unique/unique.inj": "unique" # first default
            #  taskfilePath+"hashJoin/hashjoin.inj": "hashjoin", # ./hashjoin.inj checker/R.file checker/S.file hash 40
            #  taskfilePath+"mlp/mlp.inj": "mlp", # 3.9s
            #  taskfilePath+"svm/svm.inj": "svm" # 2.7s ./svm.inj ./SVM-RFE/outData.txt 253 15154 4
         }
    processBeginTime=timeBeginPrint("multiple taskList")

    for diffGraph in glv._get("gapbsGraphNameList"):
        glv._set("gapbsGraphName", diffGraph)
        # Step1: manual compile all exe before run-sniper phase
        errorPrint("-----------------------------------{}----------------------------------------".format(diffGraph))
        errorPrint("-----------------------------------STEP1----------------------------------------")
        
        
        errorPrint("-----------------------------------STEP SCA BB abstract----------------------------------------")
        parallelTask(taskList, singleDisassembly)
        

        OffloadBySCA(taskList)
        

    timeEndPrint("multiple taskList",processBeginTime)

if __name__ == "__main__":
    main()