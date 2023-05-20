import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
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

def generateAppStackedBarPlotly():
	[x, barDict, maxY] = detailNormalizedGraphAppDict()
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
    # matplotlib.use("pgf")
	matplotlib.rcParams.update({
        "pgf.texsystem": "pdflatex",
        'font.family': 'serif',
        'text.usetex': True,
        'pgf.rcfonts': False,
    })
    # data from https://allisonhorst.github.io/palmerpenguins/
	
	[species,dictData, maxVal] = normalizedGraphAppDict()
	ic(dictData)
	x = np.arange(len(species))  # the label locations
	width = 0.25/2  # the width of the bars
	multiplier = 0

	fig, ax = plt.subplots(layout='constrained')
	fig.set_size_inches(w=10.1413, h=5.75) #(8, 6.5)

	for attribute, measurement in dictData.items():
		ic(measurement)
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
    for key, List in dictData.items():
        result1.append(key)
        for i in range(len(List)):
            maxVal = max(List[i], maxVal)
            if entryList[i] not in result2:
                result2[entryList[i]] = [List[i]]  
            else:
                result2[entryList[i]].append(List[i])   
    return [result1, result2, int(maxVal)]

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
    maxY = 0
    for i, detailName in enumerate(detailList):
        tmp = []
        for _ , appDataDict in detailAppDictData.items():
            for line in appDataDict:
                maxY = max(line[i], maxY)
                tmp.append(line[i])
        ic(tmp)
        barDict[detailName]=tmp
    return [x, barDict, maxY]