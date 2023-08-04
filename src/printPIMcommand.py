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
            #  gapbsTaskfilePath+"bc.inj": "bc",
            #  gapbsTaskfilePath+"sssp.inj": "sssp",
            #  gapbsTaskfilePath+"cc.inj": "cc",
            #  gapbsTaskfilePath+"bfs.inj": "bfs",
            #  gapbsTaskfilePath+"pr.inj": "pr",
            #  taskfilePath+"gemv/gemv.inj": "gemv", 
            #  taskfilePath+"spmv/spmv.inj": "spmv", #./spmv -f ./data/bcsstk30.mtx 
            #  taskfilePath+"select/select.inj": "select", # ./sel -i 1258291200 -t 4
            #  taskfilePath+"unique/unique.inj": "unique", # first default
            #  taskfilePath+"hashJoin/hashjoin.inj": "hashjoin", # ./hashjoin.inj checker/R.file checker/S.file hash 40
             taskfilePath+"mlp/mlp.inj": "mlp", # 3.9s
            #  taskfilePath+"svm/svm.inj": "svm" # 2.7s ./svm.inj ./SVM-RFE/outData.txt 253 15154 4
         }
    processBeginTime=timeBeginPrint("multiple taskList")


    for diffGraph in glv._get("gapbsGraphNameList"):
        glv._set("gapbsGraphName", diffGraph)
        # parallelTask( taskList, singlePIMMode, coreCount=32 )
        coreNums = 32
        all_for_one = CTS(taskList)
        all_for_one.print_sniper_command()
        # for taskKey, taskName in taskList.items():
        #     passPrint("cpu 1\n")
        #     if taskName in glv._get("gapbsList"):
        #         [core, command,targetFile] = gapbsInput(taskKey, taskName, "cpu", 1)
        #     elif taskName in glv._get("specialInputList"):
        #         [core, command,targetFile] = specialInput(taskKey, taskName, "cpu", 1)
        #     else:
        #         [core, command,targetFile] = defaultInput(taskKey, taskName, "cpu", 1)
        #     print(command)
        #     print(targetFile)
        #     passPrint(f"pim {coreNums}\n")
        #     if taskName in glv._get("gapbsList"):
        #         [core, command,targetFile] = gapbsInput(taskKey, taskName, "pim", coreNums)
        #     elif taskName in glv._get("specialInputList"):
        #         [core, command,targetFile] = specialInput(taskKey, taskName, "pim", coreNums)
        #     else:
        #         [core, command,targetFile] = defaultInput(taskKey, taskName, "pim", coreNums)
        #     print(command)
        #     print(targetFile)
        
    timeEndPrint("multiple taskList",processBeginTime)

if __name__ == "__main__":
    main()