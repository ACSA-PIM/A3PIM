import global_variable as glv


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
    
    
    