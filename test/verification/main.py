import sys
sys.path.append('./src')

import config  # 加载配置
from config import pasteFullFileName
import global_variable as glv
from input_process import inputParameters, isIceEnable

def main():
    # For each application, the PIMProf outcomes were parsed independently to render distinct plots of the CPU and PIM 
    # scatter data points, with the graphical renderings persisted for subsequent analysis.
    args=inputParameters()
    isIceEnable(args.debug)

if __name__ == "__main__":
    main()