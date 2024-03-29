import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.font_manager import FontProperties
import matplotlib
import global_variable as glv
from tsjPython.tsjCommonFunc import *
from logPrint import *
import sys
import plotly.graph_objects as go
import plotly
import plotly.io as pio
from itertools import zip_longest


def generateAppStackedBar():
	species = (
		"Adelie\n $\\mu=$3700.66g",
		"Chinstrap\n $\\mu=$3733.09g",
		"Gentoo\n $\\mu=5076.02g$",
	)
	weight_counts = {
		"Below": np.array([70, 31, 58]),
		"Above": np.array([82, 37, 66]),
	}
	width = 0.5

	fig, ax = plt.subplots()
	bottom = np.zeros(3)

	for boolean, weight_count in weight_counts.items():
		p = ax.bar(species, weight_count, width, label=boolean, bottom=bottom)
		bottom += weight_count

	ax.set_title("Number of penguins with above average body mass")
	ax.legend(loc="upper right")


	# show plot
	plt.savefig(glv._get("graphlOutPathTest1"))

def generateAppStackedBarPlotly(maxY,all_for_one):
	maxY = max(1.2, maxY)
	# maxY = 2
	# [x, barDict] = detailNormalizedGraphAppDict()
	[x, barDict] = all_for_one.stacked_data()
	ic(x)
	# x = [
	# 	["bc", "bc", "bc", "sssp", "sssp", "sssp"],
	# 	["CPU-ONLY", "PIM_ONLY", "PIMProf", "CPU-ONLY", "PIM_ONLY", "PIMProf",]
	# ]
	fig = go.Figure()

	# color from https://stackoverflow.com/questions/68596628/change-colors-in-100-stacked-barchart-plotly-python
	color_list = ['rgb(29, 105, 150)', \
            	'rgb(56, 166, 165)', \
				'rgb(15, 133, 84)',\
        		'rgb(95, 70, 144)']
	sumList = [0 for i in range(len(x[0]))]
	for i, entry in enumerate( barDict.items()):
		barName=entry[0]
		yList = entry[1]
		ic(sumList,yList)
		sumList = [x + y for x, y in zip(yList, sumList)]
		fig.add_bar(x=x,y=yList, 
              name=barName, 
              text =[f'{val:.2f}' for val in yList], 
              textposition='inside',
              marker=dict(color=color_list[i]),
              textfont=dict(size=8)
		)

	for i, entry in enumerate(sumList):
		if entry > maxY+0.01:
			ic(x[0][i],x[1][i])
			# 添加 "bc" 列的注释
			fig.add_annotation(
				x=[x[0][i],x[1][i]],  # 注释的 x 坐标为 "bc"
				y=maxY,  # 注释的 y 坐标为该列的最大值
				text=f'{entry:.2f}',  # 注释的文本内容
				showarrow=True,  # 显示箭头
				arrowhead=1,  # 箭头样式
				ax=0,  # 箭头 x 偏移量
				ay=-10,  # 箭头 y 偏移量，负值表示向下偏移
				# bgcolor="rgba(255, 255, 255, 0.8)",  # 注释框背景颜色
				# font=dict(size=4)  # 注释文本字体大小
				font=dict(size=8)  # 注释文本字体大小
			)
		else:
			fig.add_annotation(
				x=[x[0][i],x[1][i]],  # 注释的 x 坐标为 "bc"
				y=entry+maxY/25,  # 注释的 y 坐标为该列的最大值
				text=f'{entry:.2f}',  # 注释的文本内容
				showarrow=False,  # 显示箭头
				# bgcolor="rgba(255, 255, 255, 0.8)",  # 注释框背景颜色
				font=dict(size=6)  # 注释文本字体大小
			)
 

	# fig.add_bar(x=x,y=[10,2,3,4,5,6], name="CPU")
	# fig.add_bar(x=x,y=[6,5,4,3,2,1], name="DataMove")
	# fig.add_bar(x=x,y=[6,5,4,3,2,1], name="PIM")
	ic(maxY)
	width=1200
	height=400
	fig.update_layout(barmode="relative", 
					title={
						"text": "Execution time breakdown of GAP and PrIM workloads using different offloading decisions",
						"x": 0.5,  # Set the title's x position to 0.5 for center alignment
						"pad": {"t": 30}  # Adjust the padding of the title
					},
     				xaxis_title="GAP and PrIM workloads",
					yaxis_title="Normalized Execution Time",
					yaxis_range=[0,maxY],
					legend_title="Legend Title",
					font=dict(
						family="serif",
						size=12,
						color="Black"
					),
					height=height, width=width, # 图片的长宽
					template = "plotly_white", # https://plotly.com/python/templates/
					margin=dict(b=60, t=40, l=20, r=20),
					bargap=0.2
     )
	pio.write_image(fig, glv._get("graphlOutPathTest2"), format="png", scale=3)
  
    
def generateAppComparisonGraph():
    [species,dictData, maxVal, scaMaxVal, scaAvgTime, availAppCount] = normalizedGraphAppDict()
    ic(dictData)
    BreakdownGraph(species,dictData, scaMaxVal)
    SpeedUpGraph(species,dictData)
    return [scaMaxVal, scaAvgTime, availAppCount]


def SpeedUpGraph(species,dictData):
    # matplotlib.use("pgf")
	matplotlib.rcParams.update({
        "pgf.texsystem": "pdflatex",
        'font.family': 'serif',
        'text.usetex': True,
        'pgf.rcfonts': False,
    })
    # data from https://allisonhorst.github.io/palmerpenguins/
	
	x = np.arange(len(species))  # the label locations
	width = 0.25/2  # the width of the bars
	multiplier = 0

	fig, ax = plt.subplots(layout='constrained')
	fig.set_size_inches(w=10.1413*2.5, h=5.75) #(8, 6.5)

	maxVal = 0
	for attribute, measurement in dictData.items():
		for i in range(len(measurement)):
			measurement[i] = round(1/measurement[i],2)
		ic(measurement)
		maxVal = max(maxVal, max(measurement))
		offset = width * multiplier
		rects = ax.bar(x + offset, measurement, width, label=attribute)
		ax.bar_label(rects, padding=3, fontsize=8) # Distance of label from the end of the bar, in points.
		multiplier += 1

	# Add some text for labels, title and custom x-axis tick labels, etc.
	ax.set_ylabel('Acceleration Relative to CPU Execution Time')
	ax.set_title('SpeedUp Analysis of GAP and PrIM workloads using different offloading decisions')
	ax.set_xticks(x + 2 * width, species)
	ax.legend(loc='upper left', ncols=3)
	if(maxVal > 15):
		plt.yscale('log',base=10)
		ax.set_ylim(0.1, maxVal+100) # 2
	else:
		plt.yscale('linear')
		ax.set_ylim(0, maxVal+2) # 2
	ic(maxVal)
	# plt.savefig(glv._get("graphlOutPathTest1"), dpi=300)

def BreakdownGraph(species,dictData, maxVal):
    # matplotlib.use("pgf")
	ic("BreakdownGraph")
 

	# # 创建FontProperties对象，并设置字体搜索路径
	# custom_font_prop = FontProperties()
	# custom_font_prop.set_file(glv._get("custom_font_dir"))  # 设置自定义字体搜索路径

	# # 修改Matplotlib的字体设置
	# plt.rcParams.update({
	# 	'font.family': custom_font_prop.get_name()  # 设置自定义字体
	# })
	matplotlib.rcParams.update({
        "pgf.texsystem": "pdflatex",
        'font.family': 'serif',
        'text.usetex': True,
        'pgf.rcfonts': False,
    })
    # data from https://allisonhorst.github.io/palmerpenguins/
	
	x = np.arange(len(species))  # the label locations
	width = 0.25/2  # the width of the bars
	multiplier = 0

	ic("BreakdownGraph why stucked 0")
	matplotlib.use('Agg') # 禁止交互式窗口
	fig, ax = plt.subplots()
	ic("BreakdownGraph why stucked 0.5")
 
	fig.set_size_inches(w=10.1413*2.5, h=5.75) #(8, 6.5)

	if(maxVal > 15):
		max_value =  maxVal+100
	else:
		max_value = maxVal+2
  
	ic("BreakdownGraph why stucked 1")
	for attribute, measurement in dictData.items():
		ic(measurement)
		offset = width * multiplier
		rects = ax.bar(x + offset, measurement, width, label=attribute)
		ax.bar_label(rects, padding=3, fontsize=8) # Distance of label from the end of the bar, in points.
		multiplier += 1
  
		ic(measurement,rects)
		# 判断柱子是否超出最大范围
		for rect, value in zip(rects, measurement):
			if value > max_value:
				# 添加波浪线和标注
				ax.annotate(f'{value}', xy=(rect.get_x() + rect.get_width() / 2, max_value), xytext=(0, -20),
							textcoords='offset points', ha='center', va='bottom',
							arrowprops=dict(arrowstyle='fancy'))

	ic("BreakdownGraph why stucked 2")

	# Add some text for labels, title and custom x-axis tick labels, etc.
	ax.set_ylabel('Normalized Execution Time')
	ax.set_title('Execution time of GAP and PrIM workloads using different offloading decisions')
	ax.set_xticks(x + 2 * width, species)
	ax.legend(loc='upper left', ncols=3)
	if(maxVal > 15):
		plt.yscale('log',base=10)
		ax.set_ylim(0.1, maxVal+100) # 2
	else:
		plt.yscale('linear')
		ax.set_ylim(0, maxVal+2) # 2
	ic(maxVal)
	# plt.savefig(glv._get("graphlOutPath"), dpi=300)
 
def normalizedGraphAppDict():
    entryList = glv._get("graphEntryList")
    dictData = glv._get("graphAppDict")
    tmpTotalList = []
    # count available application: sca better than others except PIMProf
    availAppCount = 0
    # First, get the sca & PIMProf index
    scaEntryIndex = 0
    pimprofEntryIndex = 0
    for i in range(len(entryList)):
        if entryList[i] == "PIMProf":
            pimprofEntryIndex = i
        if entryList[i] == "SCAFromfile":
            scaEntryIndex = i
    for key, List in dictData.items():
        baseline = List[0]
        for i in range(len(List)):
            List[i] = round(List[i]/baseline,2)  
        dictData[key] = List
        tmpTotalList = [x + y for x, y in zip_longest(tmpTotalList, List, fillvalue=0)]
        ic(key, List, tmpTotalList)
        # check if app avail
        flag = 0
        for i in range(min(len(List),len(entryList))):
            if i == scaEntryIndex or i == pimprofEntryIndex:
                continue
            if List[i] < List[scaEntryIndex]:
                flag = -1
                break
        if flag == 0:
            availAppCount += 1
    # add avg application
    applicationNum = len(dictData)
    dictData['AVG'] = [round(i/applicationNum,2) for i in tmpTotalList]
    ic(dictData)
    # exit(0)
	
    # Application Name
    species = []
    # graph data . eg: graphData["PIMProf"] = [i in all application]
    graphData = {}
    maxVal = 0
    scaMaxVal = 0
    ic(dictData)
    for key, List in dictData.items():
        ic(key, List)
        species.append(key)
        scaMaxVal = max(scaMaxVal,List[len(entryList)-1])
        for i in range(min(len(List),len(entryList))):
            maxVal = max(List[i], maxVal)
            if entryList[i] not in graphData:
                graphData[entryList[i]] = [List[i]]  
            else:
                graphData[entryList[i]].append(List[i])   
    ic(scaMaxVal)
    return [species, graphData, maxVal, scaMaxVal, dictData['AVG'][len(entryList)-1], availAppCount] 

def detailNormalizedGraphAppDict():
    x = []
    xClass1 = []
    xClass2 = []
    entryList = glv._get("graphEntryList")
    entryListSize = len(entryList)
    detailAppDictData = glv._get("graphAppDetailDict")
    ic(detailAppDictData)
    tmpTotalList = []
    count = 0
    exe_time_sum = 0
    data_movement_sum = 0
    CL_DM_sum = 0
    REG_DM_sum = 0
    skip_list = ["cc", "gemv", "hashjoin", "mlp"]
    for appName, appDataDict in detailAppDictData.items():
        xClass1 += [appName] * entryListSize
        xClass2 += entryList
        # nornalize
        baseline = appDataDict[0][0] # CPU Total
        for i, line in enumerate(appDataDict):
            ic(line)
            for j, entry in enumerate(line):
                appDataDict[i][j] = round(entry/baseline, 7)
        ic(appDataDict)
        if appName not in skip_list:
            count += 1
            tmptotal = sum(tmp for tmp in appDataDict[3]) 
            tmp_exe_time = appDataDict[3][0] + appDataDict[3][1]
            tmp_data_movement = appDataDict[3][2] + appDataDict[3][3]
            print(f"{appName} &{round(tmp_exe_time*100/tmptotal,2)}\\% \
                    &{round(appDataDict[3][2]*100/tmptotal,2)}\\% \
                    &{round(appDataDict[3][3]*100/tmptotal,2)}\\% \
                        \\\\  ")
            exe_time_sum += tmp_exe_time*100/tmptotal
            data_movement_sum += tmp_data_movement*100/tmptotal
            CL_DM_sum += appDataDict[3][2]*100/tmptotal
            REG_DM_sum += appDataDict[3][3]*100/tmptotal
        tmpTotalList = addList(tmpTotalList,appDataDict)
        ic(tmpTotalList)
    print(f"AVERAGE &{round(exe_time_sum/count,2)}\\% &{round(CL_DM_sum/count,2)}\\% &{round(REG_DM_sum/count,2)}\\% \\\\")
    print(f"AVERAGE &{round(exe_time_sum/count,2)}\\% &{round(data_movement_sum/count,2)}\\% \\\\")
	# add avg application
    applicationNum = len(detailAppDictData)
    detailAppDictData['AVG'] = [[round(i/applicationNum,2) for i in row]for row in tmpTotalList]
    xClass1 += ['AVG'] * entryListSize
    xClass2 += entryList
    
    # x = [
	# 	["bc", "bc", "bc", "sssp", "sssp", "sssp"],
	# 	["CPU-ONLY", "PIM_ONLY", "PIMProf", "CPU-ONLY", "PIM_ONLY", "PIMProf",]
	# ]
    x.append(xClass1)
    x.append(xClass2)
    ic(x)
    barDict = {}
    detailList = glv._get("graphDetailList")
    for i, detailName in enumerate(detailList):
        tmp = []
        for _ , appDataDict in detailAppDictData.items():
            appDataDict=appDataDict[:len(entryList)]
            for line in appDataDict:
                tmp.append(line[i])
        # ic(tmp)
        barDict[detailName]=tmp
    return [x, barDict]

def addList(list1,list2):
	rows = max(len(list1), len(list2))
	cols = max(len(row) for row in list1 + list2)

	result = [[0] * cols for _ in range(rows)]

	for i in range(rows):
		for j in range(cols):
			if i < len(list1) and j < len(list1[i]):
				result[i][j] += list1[i][j]
			if i < len(list2) and j < len(list2[i]):
				result[i][j] += list2[i][j]

	return result