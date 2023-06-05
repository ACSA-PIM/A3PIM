import global_variable as glv
from collections import defaultdict
import time

glv._init()

working_fold="/staff/shaojiemike/github/sniper-pim/"
glv._set("logPath", working_fold+"log/")
glv._set("resultPath", working_fold+"Summary/")

glv._set("specialInputList", [
    "spmv",
    "hashjoin",
    "svm"
]) 
glv._set("gapbsList", [
    "bc",
    "cc",
    "bfs",
    "pr",
    "sssp"
])  # abbreviation of applications in gapbs benchmark
gapbsTaskfilePath = "/staff/shaojiemike/github/sniper_PIMProf/PIMProf/gapbs/"
taskfilePath = "/staff/shaojiemike/github/sniper_PIMProf/PIMProf/"
glv._set("taskfilePath", taskfilePath)
# glv._set("gapbsGraphNameList",["kron-5","kron-10","kron-15","kron-20"])
glv._set("gapbsGraphNameList",["kron-20"])
glv._set("gapbsGraphName", "kron-5")
glv._set("gapbsGraphPath", gapbsTaskfilePath+"benchmark/")
glv._set("taskList",
         {
             gapbsTaskfilePath+"bc.inj": "bc",
             gapbsTaskfilePath+"sssp.inj": "sssp",
             gapbsTaskfilePath+"cc.inj": "cc",
             gapbsTaskfilePath+"bfs.inj": "bfs",
             gapbsTaskfilePath+"pr.inj": "pr",
             taskfilePath+"gemv/gemv.inj": "gemv", 
             taskfilePath+"spmv/spmv.inj": "spmv", #./spmv -f ./data/bcsstk30.mtx 
             taskfilePath+"select/select.inj": "select", # ./sel -i 1258291200 -t 4
             taskfilePath+"unique/unique.inj": "unique", # first default
             taskfilePath+"hashJoin/hashjoin.inj": "hashjoin", # ./hashjoin.inj checker/R.file checker/S.file hash 40
             taskfilePath+"mlp/mlp.inj": "mlp", # 3.9s
             taskfilePath+"svm/svm.inj": "svm" # 2.7s ./svm.inj ./SVM-RFE/outData.txt 253 15154 4
         })  # exe name &  abbreviation

glv._set("run-sniperPath", "/staff/shaojiemike/github/sniper_PIMProf/run-sniper")
glv._set("PIMProfSolverPath", "/staff/shaojiemike/github/PIMProf/debug/PIMProfSolver/Solver.exe")
# glv._set("graphEntryList",["CPU-ONLY","PIM-ONLY", 'MPKI-based',\
#                 "Architecture-Suitability/Greedy","PIMProf", "SCAFromfile", "SCA"])
glv._set("graphEntryList",["CPU-ONLY","PIM-ONLY", 'MPKI-based',\
                "Architecture-Suitability/Greedy","PIMProf", "SCAFromfile"])
glv._set("graphAppDict",{})
glv._set("graphAppDetailDict",{})
glv._set("graphDetailList",["CPU-Time","PIM-Time", 'DataMove',\
                "Context Switch Time"])
glv._set("ProcessNum",40)
# glv._set("failedRetryTimes",3)
# glv._set("failedSleepTime",1)
glv._set("timeout",3600*120)
glv._set("debug","yes")


def pasteFullFileName(taskfilenameWithoutPath):
    taskfilePath = glv._get("taskfilePath")
    taskfilename = "{}/{}".format(taskfilePath, taskfilenameWithoutPath)
    return taskfilename
