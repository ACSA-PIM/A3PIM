import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib
import global_variable as glv
from tsjPython.tsjCommonFunc import *
from logPrint import *
import sys

def generateAppComparisonGraph():
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
	ax.set_ylim(0, maxVal+2) # 2
	# matplotlib.use("pgf")
	matplotlib.rcParams.update({
        "pgf.texsystem": "pdflatex",
        'font.family': 'serif',
        'text.usetex': True,
        'pgf.rcfonts': False,
    })
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
    return [result1, result2, maxVal]
    