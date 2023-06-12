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

def generateAppStackedBarPlotly(maxY):
	[x, barDict] = detailNormalizedGraphAppDict()
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
	for i, entry in enumerate( barDict.items()):
		barName=entry[0]
		yList = entry[1]
		fig.add_bar(x=x,y=yList, name=barName, marker=dict(color=color_list[i]))
	# fig.add_bar(x=x,y=[10,2,3,4,5,6], name="CPU")
	# fig.add_bar(x=x,y=[6,5,4,3,2,1], name="DataMove")
	# fig.add_bar(x=x,y=[6,5,4,3,2,1], name="PIM")
	ic(maxY)
	fig.update_layout(barmode="relative", 
					title="Execution time breakdown of GAP and PARSEC workloads using different offloading decisions",
					xaxis_title="GAP and PARSEC workloads",
					yaxis_title="Normalized Execution Time",
					yaxis_range=[0,maxY],
					legend_title="Legend Title",
					font=dict(
						family="serif",
						size=12,
						color="Black"
					),
					height=600, width=1200, # 图片的长宽
					template = "plotly_white", # https://plotly.com/python/templates/
					margin=dict(b=60, t=20, l=20, r=20))
	fig.write_image(glv._get("graphlOutPathTest2"))
  
    
def generateAppComparisonGraph():
    [species,dictData, maxVal, scaMaxVal] = normalizedGraphAppDict()
    ic(dictData)
    BreakdownGraph(species,dictData, scaMaxVal)
    SpeedUpGraph(species,dictData)
    return scaMaxVal


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
	fig.set_size_inches(w=10.1413, h=5.75) #(8, 6.5)

	maxVal = 0
	for attribute, measurement in dictData.items():
		for i in range(len(measurement)):
			measurement[i] = round(1/measurement[i],2)
		ic(measurement)
		maxVal = max(maxVal, max(measurement))
		offset = width * multiplier
		rects = ax.bar(x + offset, measurement, width, label=attribute)
		ax.bar_label(rects, padding=3) # Distance of label from the end of the bar, in points.
		multiplier += 1

	# Add some text for labels, title and custom x-axis tick labels, etc.
	ax.set_ylabel('Normalized Execution Time')
	ax.set_title('Execution time breakdown of GAP and PARSEC workloads using different offloading decisions')
	ax.set_xticks(x + 2 * width, species)
	ax.legend(loc='upper left', ncols=3)
	if(maxVal > 15):
		plt.yscale('log',base=10)
		ax.set_ylim(0.1, maxVal+100) # 2
	else:
		plt.yscale('linear')
		ax.set_ylim(0, maxVal+2) # 2
	ic(maxVal)
	plt.savefig(glv._get("graphlOutPathTest1"))

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
 
	fig.set_size_inches(w=10.1413, h=5.75) #(8, 6.5)

	ic("BreakdownGraph why stucked 1")
	for attribute, measurement in dictData.items():
		ic(measurement)
		offset = width * multiplier
		rects = ax.bar(x + offset, measurement, width, label=attribute)
		ax.bar_label(rects, padding=3) # Distance of label from the end of the bar, in points.
		multiplier += 1

	ic("BreakdownGraph why stucked 2")

	# Add some text for labels, title and custom x-axis tick labels, etc.
	ax.set_ylabel('Normalized Execution Time')
	ax.set_title('Execution time breakdown of GAP and PARSEC workloads using different offloading decisions')
	ax.set_xticks(x + 2 * width, species)
	ax.legend(loc='upper left', ncols=3)
	if(maxVal > 15):
		plt.yscale('log',base=10)
		ax.set_ylim(0.1, maxVal+100) # 2
	else:
		plt.yscale('linear')
		ax.set_ylim(0, maxVal+2) # 2
	ic(maxVal)
	plt.savefig(glv._get("graphlOutPath"))
 
def normalizedGraphAppDict():
    entryList = glv._get("graphEntryList")
    dictData = glv._get("graphAppDict")
    for key, List in dictData.items():
        baseline = List[0]
        for i in range(len(List)):
            List[i] = round(List[i]/baseline,2)
        dictData[key] = List
    result1 = []
    result2 = {}
    maxVal = 0
    scaMaxVal = 0
    ic(dictData)
    for key, List in dictData.items():
        ic(key, List)
        result1.append(key)
        scaMaxVal = max(scaMaxVal,List[len(entryList)-1])
        for i in range(min(len(List),len(entryList))):
            maxVal = max(List[i], maxVal)
            if entryList[i] not in result2:
                result2[entryList[i]] = [List[i]]  
            else:
                result2[entryList[i]].append(List[i])   
    ic(scaMaxVal)
    return [result1, result2, maxVal, scaMaxVal]

def detailNormalizedGraphAppDict():
    x = []
    xClass1 = []
    xClass2 = []
    entryList = glv._get("graphEntryList")
    entryListSize = len(entryList)
    detailAppDictData = glv._get("graphAppDetailDict")
    ic(detailAppDictData)
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