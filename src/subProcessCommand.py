import global_variable as glv
from terminal_command import mkdir

def gapbsInput(taskPath, taskName, mode, coreNums):
    
    gapbslogPath = glv._get("logPath")+glv._get("gapbsGraphName")+\
    				"/"+taskName+"_pimprof_"+mode+"_"+ str(coreNums)
	# "export OMP_NUM_THREADS="+ str(coreNums) + " && " +\
    if taskName=="sssp":
        pregraphFullName = glv._get("gapbsGraphPath")+glv._get("gapbsGraphName")+".wsg"
    else:
        pregraphFullName = glv._get("gapbsGraphPath")+glv._get("gapbsGraphName")+".sg"
		
    command = glv._get("run-sniperPath") +" --roi -n " + str(coreNums)+\
		 " -c pimprof_"+mode+" -d "+gapbslogPath+\
		 " -- "+ taskPath + " -f "+ pregraphFullName +" -n1"
    ic(command)
    # print("command : {}".format(command))
    return [coreNums, command, gapbslogPath+"/pimprofreuse.out"]

def pimprofInput(taskPath, taskName, coreNums):
    cpucore = 1
    cpulogPath = glv._get("logPath")+glv._get("gapbsGraphName")+\
    				"/"+taskName+"_pimprof_cpu_"+ str(cpucore)
    pimlogPath = glv._get("logPath")+glv._get("gapbsGraphName")+\
    				"/"+taskName+"_pimprof_pim_"+ str(coreNums)
    pimprofResultPath = glv._get("resultPath")+glv._get("gapbsGraphName")+"_cpu_"+ str(cpucore)+"_pim_"+ str(coreNums)
    mkdir(pimprofResultPath)
    pimprofResultFile = pimprofResultPath+"/reusedecision_"+taskName+"_cpu_"+ str(cpucore)+"_pim_"+ str(coreNums)+".out"
    cpuprofstatsPath = cpulogPath + "/pimprofstats.out"
    pimprofstatsPath = pimlogPath + "/pimprofstats.out"
    pimprofreusePath = cpulogPath + "/pimprofreuse.out"
    redirect2log = pimprofResultPath +"/output_"+taskName+"_cpu_"+ str(cpucore)+"_pim_"+ str(coreNums)+".log"
    command = glv._get("PIMProfSolverPath")+" reuse -c "+cpuprofstatsPath+\
                " -p " + pimprofstatsPath + \
                " -r " + pimprofreusePath + \
                " -o " + pimprofResultFile
    # print("command : {}".format(command))
    ic(command)
    return [command, pimprofResultFile, redirect2log]
    
    