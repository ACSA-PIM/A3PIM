import config  # 加载配置
import global_variable as glv
from analysis import *
from config import pasteFullFileName
from graph import *
from input_process import inputParameters, isIceEnable
from logPrint import *
# from excel import *
from multiProcess import *
from SCA import OffloadBySCA, llvmAnalysis
import shutil
import matplotlib.pyplot as plt
import numpy as np
from dash import Dash, html, dcc
import pandas as pd
import plotly.express as px

gapbsTaskfilePath = "/staff/shaojiemike/github/sniper_PIMProf/PIMProf/gapbs/"
taskfilePath = "/staff/shaojiemike/github/sniper_PIMProf/PIMProf/"
taskList = {
            gapbsTaskfilePath+"bc.inj": "bc",
            gapbsTaskfilePath+"sssp.inj": "sssp",
            gapbsTaskfilePath+"cc.inj": "cc",
            gapbsTaskfilePath+"bfs.inj": "bfs",
            gapbsTaskfilePath+"pr.inj": "pr",
            taskfilePath+"gemv/gemv.inj": "gemv", 
        #  taskfilePath+"spmv/spmv.inj": "spmv0", #./spmv -f ./data/bcsstk30.mtx 
        #  taskfilePath+"spmv/spmv.inj": "spmv", #./spmv -f ./data/bcsstk30.mtx 
            taskfilePath+"select/select.inj": "select", # ./sel -i 1258291200 -t 4
            taskfilePath+"unique/unique.inj": "unique", # first default
            taskfilePath+"hashJoin/hashjoin.inj": "hashjoin", # ./hashjoin.inj checker/R.file checker/S.file hash 40
            taskfilePath+"mlp/mlp.inj": "mlp", # 3.9s
        #  taskfilePath+"svm/svm.inj": "svm" # 2.7s ./svm.inj ./SVM-RFE/outData.txt 253 15154 4
        }
X = []    
Y = []
Z = []

def main():
    ## icecream & input
    args=inputParameters()
    isIceEnable(args.debug)
    tuningLabel = "Withhashjoin"
    # tuningLabel = "nohashjoin"
    StartEndStep = [0,100,5]
    tuningLabel += f"_{StartEndStep[0]}_{StartEndStep[1]}_{StartEndStep[2]}"
    # tuningLSpressure(tuningLabel, tuningStart, tuningEnd, tuningStep)
    StartEndStep2 = [0.000001,1,10]
    tuningLabel += f"_{StartEndStep2[0]}_{StartEndStep2[1]}_{StartEndStep2[2]}"
    tuning2D(tuningLabel, StartEndStep, StartEndStep2)
     
def LoopCore(i, j):
    # change tuning parameters
    glv._set("tuning_lspressure",i)
    glv._set("tuning_dataThreshold",j)
    
    # delete other result tmp file
    if checkFileExists(glv._get("resultPath")+"default_cpu_1_pim_32"):
        shutil.rmtree(glv._get("resultPath")+"default_cpu_1_pim_32")
    if checkFileExists(glv._get("resultPath")+"kron-20_cpu_1_pim_32"):
        shutil.rmtree(glv._get("resultPath")+"kron-20_cpu_1_pim_32")
    if checkFileExists(glv._get("resultPath")+"special_cpu_1_pim_32"):
        shutil.rmtree(glv._get("resultPath")+"special_cpu_1_pim_32")
    
    # Step1: manual compile all exe before run-sniper phase
    errorPrint("-----------------------------------STEP1----------------------------------------")
    
    # disassembly to get the instructions of BBLs
    errorPrint("-----------------------------------STEP 1.1 disassembly----------------------------------------")
    
    parallelTask(taskList, singleDisassembly)
    
    errorPrint("-----------------------------------STEP 1.2 llvm-mca result of BBLs----------------------------------------")
    # get the llvm-mca result of BBLs
    llvmAnalysis(taskList)

    errorPrint("-----------------------------------STEP 1.3 static decision based on llvm-mca result ----------------------------------------")
    # get the static decision from the llvm-mca result
    OffloadBySCA(taskList)
    
    errorPrint("-----------------------------------STEP3: Get the real time base one different ways----------------------------------------")
    # Step3: run modified PIMProf result
    parallelTask(taskList, pimprof, coreCount=32 ) # 
    
    errorPrint("-----------------------------------STEP4----------------------------------------")
    # Step4: build excel & graphics to analyse results
    errorPrint("-----------------------------------STEP4.1: Read key value from real result file----------------------------------------")
    # save to global variable graphAppDict && graphAppDetailDict
    source_folder = analyseResults(taskList, coreCount=32 ) 
    
    errorPrint("-----------------------------------STEP4.2: Normalized data & Visualization ----------------------------------------")
    
    [maxValue, scaAvgTime] = generateAppComparisonGraph()   
    # generateAppStackedBar()
    generateAppStackedBarPlotly(maxValue)
    
    passPrint(f"SCA AVG Time is {scaAvgTime}\n")
    passPrint(f"SCA AVG SpeedUp is {round(1/scaAvgTime,2)}\n")
    
    return [source_folder,scaAvgTime]

def tuning2D(tuningLabel, StartEndStep, StartEndStep2):
    processBeginTime=timeBeginPrint("multiple taskList")
    [tuningStart, tuningEnd, tuningStep] = StartEndStep
    [tuningStart2, tuningEnd2, tuningStep2] = StartEndStep2
    for diffGraph in glv._get("gapbsGraphNameList"):
        glv._set("gapbsGraphName", diffGraph)
        errorPrint("-----------------------------------{}----------------------------------------".format(diffGraph))
    
        i = tuningStart - tuningStep
        while i <= tuningEnd - tuningStep:
            i = round(tuningStep+i,2)
            j = tuningStart2
            while j <= tuningEnd2:
                errorPrint(f"----------------------------------- tuning {i} {j}----------------------------------------")
                target_folder = glv._get("resultPath")+f"tuning/{tuningLabel}/manual_{i}_{j}"
                result_file = target_folder + f"/scaResult.txt"
                
                # skip if already have result
                if checkFileExists(target_folder):
                    with open(result_file, "r") as f:
                        scaAvgTime = json.load(f)
                    X.append(i)
                    Y.append(j)
                    Z.append(scaAvgTime)
                    passPrint(f"-----------------------------------already get tuning {i} {j} Result {scaAvgTime}----------------------------------------")
                    j *= tuningStep2
                    continue
                
                [source_folder,scaAvgTime] = LoopCore(i, j)
                
                X.append(i)
                Y.append(j)
                Z.append(scaAvgTime)
                errorPrint(f"-----------------------------------Finished tuning {i} {j}----------------------------------------")
                
                # save result file
                mkdir(target_folder)
                shutil.rmtree(target_folder)
                shutil.move(source_folder, target_folder)
                
                # save result to file
                with open(result_file, "w") as f:
                    json.dump(scaAvgTime, f)
                j *= tuningStep2
        
        passPrint("-----------------------------------{}----------------------------------------".format(diffGraph))
    timeEndPrint("multiple taskList",processBeginTime)
            
def tuningLSpressure(tuningLabel, tuningStart, tuningEnd, tuningStep):
    processBeginTime=timeBeginPrint("multiple taskList")
    metricValue = []    
    accuracyResult = []
    for diffGraph in glv._get("gapbsGraphNameList"):
        glv._set("gapbsGraphName", diffGraph)
        errorPrint("-----------------------------------{}----------------------------------------".format(diffGraph))
    
        i = tuningStart - tuningStep
        while i <= tuningEnd - tuningStep:
            i = round(tuningStep+i,2)
            errorPrint(f"----------------------------------- tuning {i}----------------------------------------")
            target_folder = glv._get("resultPath")+f"tuning/{tuningLabel}/manual_lspressure_{i}"
            result_file = target_folder + f"/scaResult.txt"
            
            # skip if already have result
            if checkFileExists(target_folder):
                with open(result_file, "r") as f:
                    scaAvgTime = json.load(f)
                metricValue.append(i)
                accuracyResult.append(scaAvgTime)
                passPrint(f"-----------------------------------already get tuning {i} Result {scaAvgTime}----------------------------------------")
                continue
            
            scaAvgTime = LoopCore(i, 0.01)
            
            metricValue.append(i)
            accuracyResult.append(scaAvgTime)
            errorPrint(f"-----------------------------------Finished tuning {i}----------------------------------------")
            
            # save result file
            mkdir(target_folder)
            shutil.rmtree(target_folder)
            shutil.move(source_folder, target_folder)
            
            # save result to file
            with open(result_file, "w") as f:
                json.dump(scaAvgTime, f)
                 
        passPrint("-----------------------------------{}----------------------------------------".format(diffGraph))
        X = [str(i) for i in metricValue]
        Y = accuracyResult
        print(X)
        print(Y)
        fig, ax = plt.subplots(figsize=(10, 6))
        
        plt.plot(X, Y, marker='o')
        plt.xlabel('Threshold Percentage(\%)', fontsize=12)
        plt.ylabel('Average Execution Time of Static Method', fontsize=12)
        plt.title('Tuning load store pressure', fontsize=14)
        
        for i in range(len(X)):
            plt.text(X[i], Y[i], Y[i], ha='center', va='bottom')
        
        plt.savefig(glv._get("resultPath")+f"tuning/{tuningLabel}/loadStorePressure.png", dpi=300)


    timeEndPrint("multiple taskList",processBeginTime)

if __name__ == "__main__": 
    main()
    fig = px.scatter_3d(x=X, y=Y, z=Z,
                    color=Z,
                    # size=x, size_max=20,
                    title="3D Scatter Plot")

    # dash to show
    app = Dash(__name__)
    app.layout = html.Div(children=[
        dcc.Graph(
            id='example-graph',
            figure=fig,
            style = {'height': '100vh'}
        )
    ])
    app.run_server(debug=True)
    