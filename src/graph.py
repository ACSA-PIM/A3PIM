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
	species = glv._get("graphEntryList")
	dictData = normalizedGraphAppDict()
	ic(dictData)
	x = np.arange(len(species))  # the label locations
	width = 0.25  # the width of the bars
	multiplier = 0

	fig, ax = plt.subplots(layout='constrained')

	for attribute, measurement in dictData.items():
		offset = width * multiplier
		rects = ax.bar(x + offset, measurement, width, label=attribute)
		ax.bar_label(rects, padding=3)
		multiplier += 1

	# Add some text for labels, title and custom x-axis tick labels, etc.
	ax.set_ylabel('Normalized Execution Time')
	ax.set_title('Execution time breakdown of GAP and PARSEC workloads using different offloading decisions')
	ax.set_xticks(x + width, species)
	ax.legend(loc='upper left', ncols=3)
	ax.set_ylim(0, 2)
	plt.savefig(glv._get("graphlOutPath"))
 
def normalizedGraphAppDict():
    dictData = glv._get("graphAppDict")
    for key, List in dictData.items():
        baseline = List[0]
        for i in range(len(List)):
            List[i] = round(List[i]/baseline,2)
        dictData[key] = List
    return dictData
    