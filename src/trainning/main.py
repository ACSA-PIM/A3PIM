import sys
sys.path.append('./src')

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
import numpy as np
from xgboost import XGBClassifier
from xgboost import plot_tree
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegression
from sklearn.compose import make_column_transformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import FunctionTransformer
from sklearn.metrics import accuracy_score, recall_score, f1_score, confusion_matrix, mean_squared_error
from training_data import resultFromPIMProf, resultFromSCA
import math
import json
import numpy as np
import pickle


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


gapbsTaskfilePath = "/staff/shaojiemike/github/sniper_PIMProf/PIMProf/gapbs/"
taskfilePath = "/staff/shaojiemike/github/sniper_PIMProf/PIMProf/"
taskList = {
            gapbsTaskfilePath+"bc.inj": "bc",
            gapbsTaskfilePath+"sssp.inj": "sssp",
            gapbsTaskfilePath+"cc.inj": "cc",
            gapbsTaskfilePath+"bfs.inj": "bfs",
            gapbsTaskfilePath+"pr.inj": "pr",
            taskfilePath+"gemv/gemv.inj": "gemv", 
            # taskfilePath+"spmv/spmv.inj": "spmv0", #./spmv -f ./data/bcsstk30.mtx 
            taskfilePath+"select/select.inj": "select", # ./sel -i 1258291200 -t 4
            taskfilePath+"unique/unique.inj": "unique", # first default
            taskfilePath+"hashJoin/hashjoin.inj": "hashjoin", # ./hashjoin.inj checker/R.file checker/S.file hash 40
            taskfilePath+"mlp/mlp.inj": "mlp", # 3.9s
        #  taskfilePath+"svm/svm.inj": "svm" # 2.7s ./svm.inj ./SVM-RFE/outData.txt 253 15154 4
        }

def XGBClassifierFunc(bbhashXDict, bbhashYDict):
    # XGB no need to normalize
    X = np.array([value for _ , value in bbhashXDict.items()])

    y = np.array([1 if bbhashYDict[key][0] > bbhashYDict[key][1] else 0 for key , _ in bbhashXDict.items()])
    weights = [abs(bbhashYDict[key][0] - bbhashYDict[key][1]) for key , _ in bbhashXDict.items()]
    
    # default n_estimators = 100 max_depth = 5
    n_estimators = glv._get("xgb_n_estimators")
    max_depth = glv._get("xgb_max_depth")
    model = XGBClassifier(learning_rate = 0.000001, 
                          subsample = 1,
                          colsample_bytree = 1,
                          colsample_bynode = 1,
                          n_estimators=n_estimators, max_depth=max_depth, objective='binary:logistic')
    model.fit(X, y, sample_weight=weights)
    
    # 获取模型的决策树列表
    # trees = model.get_booster().get_dump()
    # 打印每个决策树的参数
    # for i, tree in enumerate(trees):
    #     print(f"决策树 {i+1} 参数:")
    #     print(tree)
    #     print()
    
    # 获取模型参数
    coefficients = model.get_params()
    
    y_pred = model.predict(X)
    ic(len(y_pred))
    ic(y_pred)

    # 将预测结果转换为二分类问题的类别（0或1）
    threshold = 0.5
    y_pred_binary = [1 if pred >= threshold else 0 for pred in y_pred]
    y_true = [1 if pred >= threshold else 0 for pred in y]

    accuracy = accuracy_score(y_true, y_pred_binary)
    recall = recall_score(y_true, y_pred_binary)
    f1 = f1_score(y_true, y_pred_binary)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred_binary).ravel()
    false_positive_rate = fp / (fp + tn)

    # 打印指标值
    passPrint("XGB Classifier\n")
    print("accuracy:", accuracy)
    print("recall:", recall)
    print("f1_score:", f1)
    print("false_positive_rate:", false_positive_rate)

    TrueCount = 0
    index = 0
    with open(f"./src/trainning/detailsXGB_{n_estimators}.txt",'w') as f:
        for key , _ in bbhashXDict.items():
            value = X[index]
            y_pred = model.predict([value])
            index += 1
            y_true = bbhashYDict[key][0] > bbhashYDict[key][1]
            # y_pred_proba = model.predict_proba([value])
            # ic(y_true, y_pred,y_pred_proba)
            if y_pred ^ y_true:
                flag = "F"
            else:
                flag = "T"
                TrueCount += 1
            f.writelines("{:20} {}: y_true {:>5f} \ty_pred {:<5f} \n".\
                format(key, flag, y_true, y_pred[0]))
    print("accuracy:", TrueCount/index)

    ic("saving model")
    # 保存模型参数到文件
    model.save_model(f"./src/trainning/xgb_model_{n_estimators}.bin")
    
    mkdir("./src/trainning/xgb/")
    for i in range(model.n_estimators):
        # 绘制前 5 棵决策树的图像
        ic(i)
        if i > 3:
            return 0
        plot_tree(model, num_trees=i)
        ic(i)
        plt.savefig(f"./src/trainning/xgb/xgb_model_{i}.png", dpi=300)
        plt.close()
    
    

        
def LogisticRegressionFunc(bbhashXDict, bbhashYDict):
    normalizedXDict = dict()
    data = np.array([value for _ , value in bbhashXDict.items()])
    scaler = MinMaxScaler()
    # normalize
    X = scaler.fit_transform(data)

    y = np.array([1 if bbhashYDict[key][0] > bbhashYDict[key][1] else 0 for key , _ in bbhashXDict.items()])
    
    model = LogisticRegression()
    model.fit(X, y)
    
    # 获取模型参数
    coefficients =list( model.coef_)
    coefficients = list(coefficients[0])
    intercept = model.intercept_[0]
    
    y_pred = model.predict(X)

    # 将预测结果转换为二分类问题的类别（0或1）
    threshold = 0.5
    y_pred_binary = [1 if pred >= threshold else 0 for pred in y_pred]
    y_true = [1 if pred >= threshold else 0 for pred in y]

    accuracy = accuracy_score(y_true, y_pred_binary)
    recall = recall_score(y_true, y_pred_binary)
    f1 = f1_score(y_true, y_pred_binary)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred_binary).ravel()
    false_positive_rate = fp / (fp + tn)

    # 打印指标值
    passPrint("Logistic RegressionModel\n")
    print("accuracy:", accuracy)
    print("recall:", recall)
    print("f1_score:", f1)
    print("false_positive_rate:", false_positive_rate)

    TrueCount = 0
    index = 0
    with open('./src/trainning/details.txt','w') as f:
        for key , _ in bbhashXDict.items():
            value = X[index]
            y_pred = model.predict([value])
            index += 1
            y_true = bbhashYDict[key][0] > bbhashYDict[key][1]
            y_calculate = sum([x * y for x, y in zip(value, coefficients)]) + intercept
            if y_pred ^ y_true:
                flag = "F"
            else:
                flag = "T"
                TrueCount += 1
            f.writelines("{:20} {}: y_true {:>5f} \ty_pred {:<5f} \t {} sigmoid {:<5f} \t y_calculate {:<5f}\n".\
                format(key, flag, y_true, y_pred[0],(y_calculate>0)==y_pred ,sigmoid(y_calculate),y_calculate))
    print("accuracy:", TrueCount/index)

    # 打印模型参数
    print("Coefficients:", coefficients)
    # y = b0 + b1 * x ,  Intercept is b0
    print("Intercept: {}\n".format(intercept))
    with open('./src/trainning/Coefficients.txt','w') as f:
        json.dump({"coefficients":coefficients, "intercept":intercept}, f)
    
def LinearRegressionFunc(bbhashXDict, bbhashYDict):
    
    data = np.array([value for _ , value in bbhashXDict.items()])
    scaler = MinMaxScaler()
    # normalize
    X = scaler.fit_transform(data)
    # log(CPU/PIM)
    y = np.array([math.log(float(bbhashYDict[key][0])/bbhashYDict[key][1]) for key , _ in bbhashXDict.items()])
    
      
    ic(X,y)

    model = LinearRegression()
    model.fit(X, y)

    # 获取模型参数
    coefficients =list( model.coef_)
    intercept = model.intercept_
    
    y_pred = model.predict(X)

    # 将预测结果转换为二分类问题的类别（0或1）
    threshold = 0
    y_pred_binary = [1 if pred >= threshold else 0 for pred in y_pred]
    y_true = [1 if pred >= threshold else 0 for pred in y]

    accuracy = accuracy_score(y_true, y_pred_binary)
    recall = recall_score(y_true, y_pred_binary)
    f1 = f1_score(y_true, y_pred_binary)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred_binary).ravel()
    false_positive_rate = fp / (fp + tn)

    # 打印指标值
    passPrint("Linear Regression Model\n")
    print("accuracy:", accuracy)
    print("recall:", recall)
    print("f1_score:", f1)
    print("false_positive_rate:", false_positive_rate)
    mse = mean_squared_error(y, y_pred)
    print("mean_squared_error:", mse)

    TrueCount = 0
    index = 0
    with open('./src/trainning/details0.txt','w') as f:
        for key , _ in bbhashXDict.items():
            value = X[index]
            y_pred = model.predict([value])
            index += 1
            y_true = math.log(float(bbhashYDict[key][0])/bbhashYDict[key][1])
            if y_pred * y_true > 0:
                flag = "T"
                TrueCount += 1
            else:
                flag = "F"
            f.writelines("{:20} {}: y_true {:>5f} \ty_pred {:<5f}\n".format(key, flag, y_true, y_pred[0]))
    print("accuracy:", TrueCount/index)
    

    # 打印模型参数
    print("Coefficients:", coefficients)
    # y = b0 + b1 * x ,  Intercept is b0
    print("Intercept: {}\n".format(intercept))

    with open('./src/trainning/Coefficients0.txt','w') as f:
        json.dump({"coefficients":coefficients, "intercept":intercept}, f)

def main():
    ## icecream & input
    args=inputParameters()
    isIceEnable(args.debug)


    processBeginTime=timeBeginPrint("multiple taskList")

    bbhashXDict = dict() # key: bbhash, value: [SCA Metrics]
    bbhashYDict = dict() # key: bbhash, value: [CPU，PIM]
    for diffGraph in glv._get("gapbsGraphNameList"):
        glv._set("gapbsGraphName", diffGraph)
        # parallelTask( taskList, singlePIMMode, coreCount=32 )
        coreNums = 32
        for taskKey, taskName in taskList.items():
            # Inmportant entries & Y DATA: from PIMProf result 
            tmpbbhashYDict = resultFromPIMProf(taskKey, taskName)
            bbhashYDict.update(tmpbbhashYDict)
            
            # X Data： from SCA result
            bbhashXDict.update(resultFromSCA(taskKey, taskName, tmpbbhashYDict))
            
        ic(bbhashXDict)
        ic(bbhashYDict) # CPU, PIM
        # I think there is no need to PCA(Principal Component Analysis) and normalize
        LinearRegressionFunc(bbhashXDict, bbhashYDict)
        LogisticRegressionFunc(bbhashXDict, bbhashYDict)
        XGBClassifierFunc(bbhashXDict, bbhashYDict)

        
    timeEndPrint("multiple taskList",processBeginTime)

if __name__ == "__main__":
    main()