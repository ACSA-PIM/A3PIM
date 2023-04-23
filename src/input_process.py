from icecream import ic
from icecream import install
import global_variable as glv
from tsjPython.tsjCommonFunc import *
import argparse

def inputParameters():
    yellowPrint("In addition to entering some parameters, you can also modify all parameters in config.py")
    parser = argparse.ArgumentParser()
    parser.description = "please enter some parameters"
    # parser.add_argument(
    #     "-b",
    #     "--BHiveCount",
    #     help="Bhive执行时代码展开次数 / BHive Count Num (maybe useless depends on bin/bhive use)",
    #     dest="BHiveCount",
    #     type=int, default="500"
    # )
    # parser.add_argument(
    #     "-p",
    #     "--ProcessNum",
    #     help="并行核数 / multiple Process Numbers",
    #     dest="ProcessNum",
    #     type=int, default="20"
    # )
    # parser.add_argument(
    #     "-t",
    #     "--timeout",
    #     help="子进程超时的时限(单位秒) sub program interrupt time(eg. llvm-mca, bhive, OSACA. less time causes less useful output",
    #     dest="timeout",
    #     type=int, default="10"
    # )
    parser.add_argument(
        "-d",
        "--debug",
        help="是否打印Debug信息 is print debug informations",
        dest="debug",
        type=str,
        choices=["yes", "no"],
        default="yes",
    )
    # parser.add_argument(
    #     "-hB",
    #     "--historyBhive",
    #     help="是否使用HistoryDataFile的excel里的Bhive历史数据 is use history Bhive data",
    #     dest="useBhiveHistoryData",
    #     type=str,
    #     required=True,
    #     choices=["yes", "no"],
    #     default="yes",
    # )
    # parser.add_argument(
    #     "-hl",
    #     "--historyLLVM",
    #     help="是否使用HistoryDataFile的excel里的llvm-mca历史数据 is use history llvm-mca data",
    #     dest="useLLVMHistoryData",
    #     type=str,
    #     required=True,
    #     choices=["yes", "no"],
    #     default="yes",
    # )
    # parser.add_argument(
    #     "-k",
    #     "--KendallIndex",
    #     help="is calculate Kendall Index",
    #     dest="KendallIndex",
    #     type=str,
    #     required=True,
    #     choices=["yes", "no"],
    #     default="no",
    # )
    # parser.add_argument(
    #     "-hb",
    #     "--historyBaseline",
    #     help="是否使用HistoryDataFile的excel里的llvm-mca基准历史数据 is use history llvm-mca Baseline data",
    #     dest="useBaselineHistoryData",
    #     type=str,
    #     required=True,
    #     choices=["yes", "no"],
    #     default="yes",
    # )
    # parser.add_argument(
    #     "-hO",
    #     "--historyOSACA",
    #     help="是否使用HistoryDataFile的excel里的OSACA历史数据 is use history OSACA data",
    #     dest="useOSACAHistoryData",
    #     type=str,
    #     required=True,
    #     choices=["yes", "no"],
    #     default="yes",
    # )
    # parser.add_argument(
    #     "-pu",
    #     "--printUnsupportedBlock",
    #     help="excel文件是否保留llvm-mca，Bhive或者OSACA不支持的基本块 is print Unsupported Block to excel",
    #     dest="printUnsupportedBlock",
    #     type=str,
    #     choices=["yes", "no"],
    #     default="no",
    # )
    args = parser.parse_args()
    # glv._set("BHiveCount",args.BHiveCount)
    # glv._set("ProcessNum",args.ProcessNum)
    # glv._set("timeout",args.timeout)
    glv._set("debug",args.debug)
    # glv._set("useBhiveHistoryData",args.useBhiveHistoryData)
    # glv._set("useLLVMHistoryData",args.useLLVMHistoryData)
    # glv._set("KendallIndex",args.KendallIndex)
    # glv._set("useBaselineHistoryData",args.useBaselineHistoryData)
    # glv._set("useOSACAHistoryData",args.useOSACAHistoryData)
    # glv._set("printUnsupportedBlock",args.printUnsupportedBlock)
    # pPrint(glv.GLOBALS_DICT)
    # passPrint("parameter BHiveCount is : %s" % args.BHiveCount)
    # passPrint("parameter ProcessNum is : %s" % args.ProcessNum)
    # passPrint("parameter timeout is : %d " % args.timeout)
    passPrint("parameter debug is : %s " % args.debug)
    # passPrint("parameter useBhiveHistoryData is : %s " % args.useBhiveHistoryData)
    # passPrint("parameter useLLVMHistoryData is : %s " % args.useLLVMHistoryData)
    # passPrint("parameter KendallIndex is : %s " % args.KendallIndex)
    # passPrint("parameter useBaselineHistoryData is : %s " % args.useBaselineHistoryData)
    # passPrint("parameter useOSACAHistoryData is : %s " % args.useOSACAHistoryData)
    # passPrint("parameter printUnsupportedBlock is : %s " % args.printUnsupportedBlock)
    # yellowPrint("less timeout causes less or no Bhive output!!!")
    return args

def isIceEnable(isYes):
    install()
    ic.configureOutput(prefix='Debug -> ', outputFunction=yellowPrint)
    if isYes=="yes" : 
        ic.enable()
    else:
        ic.disable()