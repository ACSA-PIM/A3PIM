import global_variable as glv
from terminal_command import mkdir

def disassemblyInput(taskPath, taskName):
    assemblyPath = glv._get("logPath")+ "assembly/"
    mkdir(assemblyPath)
    targetAssembly = assemblyPath + taskName + ".s"
    command = "objdump -d " +  taskPath 
    # + " 2>&1 > " + targetAssembly # weird, can not parallel objdump > Difffile
    ic(command)
    return [command, targetAssembly]
    
def gapbsInput(taskPath, taskName, mode, coreNums):
    gapbslogPath = f"{glv._get('logPath')}{glv._get('gapbsGraphName')}{'_func' if glv._get('mode') == 'func' else ''}"\
                        f"/{taskName}_pimprof_{mode}_{str(coreNums)}"
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

def defaultInput(taskPath, taskName, mode, coreNums):
    # gemv select unique mlp
    defaultLogPath = f"{glv._get('logPath')}default{'_func' if glv._get('mode') == 'func' else ''}"\
                        f"/{taskName}_pimprof_{mode}_{str(coreNums)}"
    command = glv._get("run-sniperPath") +" --roi -n " + str(coreNums)+\
		 " -c pimprof_"+mode+" -d "+defaultLogPath+\
		 " -- "+ taskPath 
    ic(command)
    # print("command : {}".format(command))
    return [coreNums, command, defaultLogPath+"/pimprofreuse.out"]

def specialInput(taskPath, taskName, mode, coreNums):
    specialLogPath = f"{glv._get('logPath')}special{'_func' if glv._get('mode') == 'func' else ''}"+\
                        f"/{taskName}_pimprof_{mode}_{str(coreNums)}"
        
    if taskName == "spmv0":
        dataPath = glv._get("taskfilePath") + "spmv/data/bcsstk30.mtx"
        command = glv._get("run-sniperPath") +" --roi -n " + str(coreNums)+\
		 " -c pimprof_"+mode+" -d "+specialLogPath+\
		 " -- "+ taskPath + " -f " + dataPath
    elif taskName == "spmv":
        dataPath = glv._get("taskfilePath") + "spmv/data/bcsstk30.mtx.16.mtx"
        command = glv._get("run-sniperPath") +" --roi -n " + str(coreNums)+\
		 " -c pimprof_"+mode+" -d "+specialLogPath+\
		 " -- "+ taskPath + " -f " + dataPath
    elif taskName == "hashjoin":
        dataPath = glv._get("taskfilePath") + "hashJoin/checker/"
        Rfile = dataPath + "R.file"
        Sfile = dataPath + "S.file"
        command = glv._get("run-sniperPath") +" --roi -n " + str(coreNums)+\
		 " -c pimprof_"+mode+" -d "+specialLogPath+\
		 " -- "+ taskPath + " " + Rfile + " " + Sfile + " hash 40"
    elif taskName == "svm":
        dataPath = glv._get("taskfilePath") + "svm/SVM-RFE/outData.txt"
        command = glv._get("run-sniperPath") +" --roi -n " + str(coreNums)+\
		 " -c pimprof_"+mode+" -d "+specialLogPath+\
		 " -- "+ taskPath + " " + dataPath + " 253 15154 4"
    else:
        assert("error speacial application!")
    ic(command)
    # print("command : {}".format(command))
    return [coreNums, command, specialLogPath+"/pimprofreuse.out"]

def pimprofInput(taskPath, taskName, coreNums, class1):
    cpucore = 1
    cpulogPath = glv._get("logPath")+class1+\
    				"/"+taskName+"_pimprof_cpu_"+ str(cpucore)
    pimlogPath = glv._get("logPath")+class1+\
    				"/"+taskName+"_pimprof_pim_"+ str(coreNums)
    pimprofResultPath = glv._get("resultPath")+class1+"_cpu_"+ str(cpucore)+"_pim_"+ str(coreNums)
    mkdir(pimprofResultPath)
    pimprofResultFile = pimprofResultPath+"/reusedecision_"+taskName+"_cpu_"+ str(cpucore)+"_pim_"+ str(coreNums)+".out"
    cpuprofstatsPath = cpulogPath + "/pimprofstats.out"
    pimprofstatsPath = pimlogPath + "/pimprofstats.out"
    pimprofreusePath = cpulogPath + "/pimprofreuse.out"
    redirect2log = pimprofResultPath +"/output_"+taskName+"_cpu_"+ str(cpucore)+"_pim_"+ str(coreNums)+".log"
    bblDecisionFile = glv._get("logPath")+ "assembly/" + taskName + "_bbl.decision"
    ctsDecisionFile = glv._get("logPath")+ "assembly/" + taskName + "_bbl_cts.decision"
    command = glv._get("PIMProfSolverPath")+" reuse -c "+cpuprofstatsPath+\
                " -p " + pimprofstatsPath + \
                " -r " + pimprofreusePath + \
                " -o " + pimprofResultFile +\
                " -s " + bblDecisionFile +\
                " -t " + ctsDecisionFile +\
                " -d " + str(glv._get("tuning_dataThreshold"))
    # print("command : {}".format(command))
    ic(command)
    return [command, pimprofResultFile, redirect2log]