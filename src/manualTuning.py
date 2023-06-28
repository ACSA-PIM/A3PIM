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
import plotly.graph_objects as go
from scipy.interpolate import griddata
from mpl_toolkits.mplot3d.axes3d import get_test_data

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
Z = []  # avgTime
Z2 = [] # availAppCount

def main():
    ## icecream & input
    args=inputParameters()
    isIceEnable(args.debug)
    tuningLabel = "Withhashjoin"
    # tuningLabel = "nohashjoin"
    # tuningLabel = "nohashjoinMlp"
    StartEndStep = [0,100,5] # both
    # StartEndStep = [65,85,2.5] # withhash
    # StartEndStep = [72,80,1] # withhash
    # StartEndStep = [0,5,0.5] # nohash
    # StartEndStep = [0,2,0.1] # nohash
    tuningLabel += f"_{StartEndStep[0]}_{StartEndStep[1]}_{StartEndStep[2]}"
    tuningLSpressure(tuningLabel, StartEndStep)
    StartEndStep2 = [0.000001,1,10] # both
    # StartEndStep2 = [0.0001,0.01,2] # withhash
    # StartEndStep2 = [0.000005,0.001,2] # withhash
    # StartEndStep2 = [0.0001,0.01,2] # nohash
    # StartEndStep2 = [0.00002,0.001,1.5] # nohash
    tuningLabel += f"_{StartEndStep2[0]}_{StartEndStep2[1]}_{StartEndStep2[2]}"
    tuning2D(tuningLabel, StartEndStep, StartEndStep2)

def plot_wireframe(xx, yy, z, color='#0066FF', linewidth=1):
    line_marker = dict(color=color, width=linewidth)
    lines = []
    for i, j, k in zip(xx, yy, z):
        lines.append(go.Scatter3d(x=i, y=j, z=k, mode='lines', line=line_marker))
    for i, j, k in zip(list(zip(*xx)), list(zip(*yy)), list(zip(*z))):
        lines.append(go.Scatter3d(x=i, y=j, z=k, mode='lines', line=line_marker))
        
    layout = go.Layout(showlegend=False)
    return go.Figure(data=lines, layout=layout)

def LoopCore(i, j):
    # change tuning parameters
    glv._set("tuning_lspressure",i)
    glv._set("tuning_dataThreshold",j)
    glv._set("graphAppDict",{})
    glv._set("graphAppDetailDict",{})
    
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
    
    # parallelTask(taskList, singleDisassembly)
    
    errorPrint("-----------------------------------STEP 1.2 llvm-mca result of BBLs----------------------------------------")
    # get the llvm-mca result of BBLs
    # llvmAnalysis(taskList)

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
    
    [maxValue, scaAvgTime, availAppCount] = generateAppComparisonGraph()   
    # generateAppStackedBar()
    generateAppStackedBarPlotly(maxValue)
    
    passPrint(f"SCA AVG Time is {scaAvgTime}\n")
    passPrint(f"SCA AVG SpeedUp is {round(1/scaAvgTime,2)}\n")
    passPrint(f"availAppCount is {availAppCount}\n")
    
    return [source_folder,scaAvgTime, availAppCount]

def tuning2D(tuningLabel, StartEndStep, StartEndStep2):
    processBeginTime=timeBeginPrint("multiple taskList")
    [tuningStart, tuningEnd, tuningStep] = StartEndStep
    [tuningStart2, tuningEnd2, tuningStep2] = StartEndStep2
    bestAvgTimeAndPos = [100,0,0]
    bestAppcountAndPos = [0,0,0]
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
                        data = json.load(f)
                    scaAvgTime = data["scaAvgTime"]
                    availAppCount = data["availAppCount"]
                    X.append(i)
                    Y.append(j)
                    Z.append(scaAvgTime)
                    Z2.append(availAppCount)
                    if scaAvgTime < bestAvgTimeAndPos[0]:
                        bestAvgTimeAndPos = [scaAvgTime, i, j]
                    if availAppCount > bestAppcountAndPos[0]:
                        bestAppcountAndPos = [availAppCount, i, j]
                    passPrint(f"-----------------------------------already get tuning {i} {j} Result {scaAvgTime}----------------------------------------")
                    j *= tuningStep2
                    continue
                
                [source_folder,scaAvgTime, availAppCount] = LoopCore(i, j)
                
                X.append(i)
                Y.append(j)
                Z.append(scaAvgTime)
                Z2.append(availAppCount)
                if scaAvgTime < bestAvgTimeAndPos[0]:
                    bestAvgTimeAndPos = [scaAvgTime, i, j]
                if availAppCount > bestAppcountAndPos[0]:
                    bestAppcountAndPos = [availAppCount, i, j]
                errorPrint(f"-----------------------------------Finished tuning {i} {j}----------------------------------------")
                
                # save result file
                mkdir(target_folder)
                shutil.rmtree(target_folder)
                shutil.move(source_folder, target_folder)
                
                data = {
                    "scaAvgTime":scaAvgTime,
                    "availAppCount":availAppCount
                }
                # save result to file
                with open(result_file, "w") as f:
                    json.dump(data, f)
                j *= tuningStep2
        
        passPrint("-----------------------------------{}----------------------------------------".format(diffGraph))
    timeEndPrint("multiple taskList",processBeginTime)
    print(f"bestX {bestAvgTimeAndPos[1]} bestY {bestAvgTimeAndPos[2]} bestAvgTime {bestAvgTimeAndPos[0]} ")
    print(f"bestX {bestAppcountAndPos[1]} bestY {bestAppcountAndPos[2]} bestAvailAppCount {bestAppcountAndPos[0]} ")
            
def tuningLSpressure(tuningLabel, StartEndStep):
    processBeginTime=timeBeginPrint("multiple taskList")
    [tuningStart, tuningEnd, tuningStep] = StartEndStep
    iList = []    
    scaAvgTimeList = []
    availAppCountList = []
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
                    data = json.load(f)
                scaAvgTime = data["scaAvgTime"]
                availAppCount = data["availAppCount"]
                iList.append(i)
                scaAvgTimeList.append(scaAvgTime)
                availAppCountList.append(availAppCount)
                passPrint(f"-----------------------------------already get tuning {i} Result {scaAvgTime}----------------------------------------")
                continue
            
            [source_folder,scaAvgTime, availAppCount] = LoopCore(i, 0.0001)
            
            iList.append(i)
            scaAvgTimeList.append(scaAvgTime)
            availAppCountList.append(availAppCount)
            
            errorPrint(f"-----------------------------------Finished tuning {i}----------------------------------------")
            
            # save result file
            mkdir(target_folder)
            shutil.rmtree(target_folder)
            shutil.move(source_folder, target_folder)
            
            # save result to file
            data = {
                    "scaAvgTime":scaAvgTime,
                    "availAppCount":availAppCount
                }
            # save result to file
            with open(result_file, "w") as f:
                json.dump(data, f)
                 
        passPrint("-----------------------------------{}----------------------------------------".format(diffGraph))
        X = [str(i) for i in iList]
        
        # loadStorePressure
        Y = scaAvgTimeList
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
        plt.close()
        
        # availAppCount
        Y = availAppCountList
        fig, ax = plt.subplots(figsize=(10, 6))
        
        plt.plot(X, Y, marker='o')
        plt.xlabel('Threshold Percentage(\%)', fontsize=12)
        plt.ylabel('Avail App Count', fontsize=12)
        plt.title('Tuning load store pressure', fontsize=14)
        
        for i in range(len(X)):
            plt.text(X[i], Y[i], Y[i], ha='center', va='bottom')
        
        plt.savefig(glv._get("resultPath")+f"tuning/{tuningLabel}/availAppCount.png", dpi=300)
        plt.close()


    timeEndPrint("multiple taskList",processBeginTime)

def scatterGraph(inputZ):
    fig = px.scatter_3d(x=X, y=Y, z=inputZ,
                    color=inputZ,
                    # size=x, size_max=20,
                    title="3D Scatter Plot"
                    )
    fig.update_layout(scene=dict(
        yaxis=dict(type="log"),
        zaxis=dict(type="log")
    ))
    return fig

def gridGraph(inputZ):
    # surface diagram
    x = np.array(X)
    y = np.array(Y)
    z = np.array(inputZ)

    # Generate a one-dimensional array xi with 100 elements, 
    # ranging from the minimum value of the x array to the maximum value.
    xi = np.linspace(x.min(), x.max(), 100)
    yi = np.logspace(np.log10(y.min()), np.log10(y.max()), 100)

    # Create a two-dimensional grid X and Y based on the values of xi and yi. 
    # Both X and Y have a shape of (100, 100).
    X1,Y1 = np.meshgrid(xi,yi)

    # Perform interpolation using the 'cubic' method on the given data points (x, y) 
    # and their corresponding values z, over the two-dimensional grid (X, Y). 
    # The interpolated result is stored in Z.
    Z1 = griddata((x,y),z,(X1,Y1), method='linear')
    
    fig = go.Figure(go.Surface(x=xi,y=yi,z=Z1))
    fig.update_layout(scene=dict(
        yaxis=dict(type="log"),
        zaxis=dict(type="log")
    ))
    
    # Curve graph
    ic(X1,Y1,Z1)
    fig1 = plot_wireframe(X1, Y1, Z1)
    fig1.update_layout(scene=dict(
        yaxis=dict(type="log"),
        zaxis=dict(type="log")
    ))
    return [fig,fig1]
    
if __name__ == "__main__": 
    main()

    fig0 = scatterGraph(Z)
    cfig0 = scatterGraph(Z2)
    
    [fig,fig1] = gridGraph(Z)
    [cfig,cfig1] = gridGraph(Z2)
    

    # dash to show
    app = Dash(__name__)
    app.layout = html.Div(children=[
        dcc.Graph(
            id='grid',
            figure=fig1,
            style = {'height': '100vh'}
        ),
        dcc.Graph(
            id='scatter',
            figure=fig0,
            style = {'height': '100vh'}
        ),
        dcc.Graph(
            id='Curve',
            figure=fig,
            style = {'height': '100vh'}
        ),
        dcc.Graph(
            id='grid1',
            figure=cfig1,
            style = {'height': '100vh'}
        ),
        dcc.Graph(
            id='scatter1',
            figure=cfig0,
            style = {'height': '100vh'}
        ),
        dcc.Graph(
            id='Curve1',
            figure=cfig,
            style = {'height': '100vh'}
        )
    ])
    
    app.run_server(debug=True)
    
