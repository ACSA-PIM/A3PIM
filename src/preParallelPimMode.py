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

    taskList = glv._get("taskList")
    processBeginTime=timeBeginPrint("multiple taskList")

    for diffGraph in glv._get("gapbsGraphNameList"):
        glv._set("gapbsGraphName", diffGraph)
        parallelTask( taskList, singlePIMMode, coreCount=32 )



if __name__ == "__main__":
    main()