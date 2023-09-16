# satic code analyzer for offload decision algorithms
import pickle
import json
import global_variable as glv
from terminal_command import *
import re
from tqdm import tqdm
from multiProcess import parallelGetSCAResult, llvmCommand, decisionByXGB, decisionByManual
from tsjPython.tsjCommonFunc import *
from trainning.training_data import resultFromSCAFile
from icecream import ic
from disassembly import abstractBBLfromAssembly
from subProcessCommand import *
from analysis import string2int
import copy

class CTS:
    
    assemblyPath = glv._get("logPath")+ "assembly/"
    log_path = glv._get("logPath")
    graph = "kron-20"
    mem_cost = 60 + 30
    reg_cost = 30 #  value
    parallelism_threshlod = 16
    reAI_threshold = 0.5
    IC_threshold = 27
    ppressure_threshold = 5 
    
    def __init__(self,taskList):
        self.cluster_threshold = glv._get("tuning_cluster_threshold")
        self.app_info_list = {}
        for path, name in taskList.items():
            prioriKnowDict = glv._get("prioriKnow")
            if name in prioriKnowDict and prioriKnowDict[name]["parallelism"] < 16:
                prioriKnowDecision = "Full-CPU"
            else:
                prioriKnowDecision = "No influence"
            self.app_info_list[name] = application_info(name,path,prioriKnowDecision)
    
    def update_app_info(self,name,app_info):
        self.app_info_list[name] = app_info
        
    def delete_func_file(self):
        for _, app_info in self.app_info_list.items():
            app_info.delete_func_file()
            
    def compile_func_degree(self):
        for _, app_info in self.app_info_list.items():
            app_info.compile_func_degree()
    
    def disassembly_func_degree(self):
        for _, app_info in self.app_info_list.items():
            app_info.disassembly_func_degree()
    
    def print_sniper_command(self):
        for _, app_info in self.app_info_list.items():
            [command,targetFile] = app_info.sniper_command("cpu",1,glv._get("mode"))
            print(command)
            print(targetFile)
            [command,targetFile] = app_info.sniper_command("pim",32,glv._get("mode"))
            print(command)
            print(targetFile)
            
    def pimprof(self,bbls_func, core_num):
        for _, app_info in self.app_info_list.items():
            app_info.pimprof(bbls_func, core_num)
        
    def get_time_result(self):
        for _, app_info in self.app_info_list.items():
            app_info.get_time_result()
            
    def print_time_result(self):
        sum_greedy = 0
        sum_TUB = 0
        for _, app_info in self.app_info_list.items():
            [tmp1, tmp2] = app_info.print_time_result()
            sum_greedy += tmp1
            sum_TUB += tmp2
        size = len( self.app_info_list)
        print(f"Greedy Avg: {sum_greedy/size:2f} Avg TUB: {sum_TUB/size:2f}")
        
    def stacked_data(self):
        x_first = []
        x_second = []
        entryList = glv._get("graphEntryList")
        tmp_sum_time = {"CPU-ONLY":result_time("CPU",0,0,0,0,0),
                        "PIM-ONLY":result_time("PIM",0,0,0,0,0),
                        "MPKI-based":result_time("MPKI",0,0,0,0,0),
                        "Arch-Suity/Greedy":result_time("G",0,0,0,0,0),
                        "TUB-func":result_time("TUB",0,0,0,0,0),
                        "TUB-bbls":result_time("TUB",0,0,0,0,0),
                        "A3PIM-func":result_time("CTS",0,0,0,0,0),
                        "A3PIM-bbls":result_time("CTS",0,0,0,0,0),
                        }
        stack_name_map = {"CPU-ONLY":"CPU","PIM-ONLY":"PIM", 'MPKI-based':"MPKI",\
                "Arch-Suity/Greedy":"G","TUB-func":"TUB","TUB-bbls":"TUB", "A3PIM-func":"SCA", "A3PIM-bbls":"SCA"}
        tmp_list = [[],[],[],[]]
        for app_name, app_info in self.app_info_list.items():
            x_first += [app_name] * len(entryList)
            x_second += entryList
            # glv._set("graphEntryList",["CPU-ONLY","PIM-ONLY", 'MPKI-based',\
            #     "Arch-Suity/Greedy","TUB", "CTS"])
            bbls_cpu_time = app_info.detail_bbl_dict["CPU"].total
            func_cpu_time = app_info.detail_func_dict["CPU"].total
            for entry in entryList:
                if entry == "TUB-func":
                    to_add = app_info.detail_func_dict[stack_name_map[entry]].normalize24(func_cpu_time)
                elif entry == "A3PIM-func":
                    to_add = app_info.detail_func_dict[stack_name_map[entry]].normalize24(func_cpu_time)
                else:
                    to_add = app_info.detail_bbl_dict[stack_name_map[entry]].normalize24(bbls_cpu_time)
                # ic(to_add,tmp_list)
                tmp_sum_time[entry]+=to_add
                [x.append(copy.deepcopy(entry)) for x,entry in zip(tmp_list, to_add)]
                ic(entry,tmp_sum_time[entry].print(1))
                # ic(tmp_list)
        
        # add Avg "application"
        x_first += ["AVG"] * len(entryList)
        x_second += entryList     
        app_num = len(self.app_info_list)
        for entry in entryList:
            [x.append(entry0) for x,entry0 in zip(tmp_list, tmp_sum_time[entry].normalize24(app_num))]
            
        # data_dict
        data_dict = {}
        data_dict["CPU-Time"] = tmp_list[0]
        data_dict["PIM-Time"] = tmp_list[1]
        data_dict["CL-DM"] = tmp_list[2]
        data_dict["Context Switch"] = tmp_list[3]
        
        # x = [
        # 	["bc", "bc", "bc", "sssp", "sssp", "sssp"],
        # 	["CPU-ONLY", "PIM_ONLY", "PIMProf", "CPU-ONLY", "PIM_ONLY", "PIMProf",]
        # ]
        # data_dict["CPU-ONLY"] = relatied normalized data
        return [[x_first,x_second], data_dict]
    
    def avg_time(self, bbls_func, mode ):
        sum_time = 0
        for _, app_info in self.app_info_list.items():
            sum_time += app_info.mode_time(bbls_func, mode)
        size = len( self.app_info_list)
        return sum_time / size
            


class result_time():
    def __init__(self, mode_name, total, cpu, pim, CL_DM, cxt) -> None:
        self.mode = mode_name
        self.total = int(total)
        self.cpu = int(cpu)
        self.pim = int(pim)
        self.CL_DM = int(CL_DM)
        self.cxt = int(cxt)
        
    def normalize24(self, denominator):
        return [self.cpu/denominator, self.pim/denominator, self.CL_DM/denominator, self.cxt/denominator]
        
    def __iadd__(self, other):
        self.cpu += other[0]
        self.pim += other[1]
        self.CL_DM += other[2]
        self.cxt += other[3]
        return self
        
    def print(self, normalized_value):
        print(f"{self.mode:4} {self.total:12.0f} {100*(self.total/normalized_value):10.2f}% "
              f"{self.cpu:12.0f}  {100*(self.cpu/normalized_value):10.2f}% "
              f"{self.pim:12.0f}  {100*(self.pim/normalized_value):10.2f}% "
              f" {self.CL_DM:8.0f}  {100*(self.CL_DM/normalized_value):10.2f}% "
              f"{self.cxt:12.0f} {100*(self.cxt/normalized_value):10.2f}% ")
        
class application_info(CTS):
    def __init__(self, name, path,prioriKnowDecision):
        self.name = name
        self.path = re.match(r"^((.)*)/[a-z]*\.inj",path).group(1)
        self.inj = path
        self.fun_obj = self.inj + "f"
        self.prefix_name = self.assemblyPath + name
        
        self.func_assembly_file = self.prefix_name + '_fun.s'
        self.func_bblFile = self.prefix_name + "_fun.bbl"
        self.func_bblJsonFile = self.prefix_name + "_fun_bbl.json"
        self.func_tmpbblFile = self.prefix_name + "_fun.tmp"
        
        self.targetAssembly = self.prefix_name + '.s'
        self.bblJsonFile = self.prefix_name + '_bbl.json'
        self.bblSCAFile = self.prefix_name + '_bbl.sca'
        self.funcSCAFile = self.prefix_name + '_func.sca'
        self.bblSCAPickleFile = self.prefix_name + '_bbl_sca.pickle'
        self.funcSCAPickleFile = self.prefix_name + '_func_sca.pickle'
        self.bblDecisionFile = self.prefix_name + '_bbl.decision'
        self.funcDecisionFile = self.prefix_name + '_func.decision'
        self.ctsDecisionFile = self.prefix_name + '_bbl_cts.decision'
        self.cts_cluster_file = self.prefix_name + '_bbl_cts.cluster'
        self.cpu_log_path = self.log_path + self.classify(name)
        self.app_log_path = self.cpu_log_path + "/" + name + "_pimprof_cpu_" + "1"
        self.bbl_flow_file =  self.app_log_path + "/pimprofreuse.out"
        self.id_hash_map_file =  self.app_log_path + "/pimprofstats.out"
        self.cluster_list = []
        self.prioriKnowDecision = prioriKnowDecision
        
        self.pimprof_bbls_result = self.pimprofResultFile("bbls")
        self.pimprof_func_result = self.pimprofResultFile("func")
    
    def pimprofResultFile(self, bbls_func):
        taskName = self.name
        coreNums = 32
        if taskName in glv._get("gapbsList"):
            class1 = glv._get("gapbsGraphName") 
        elif taskName in glv._get("specialInputList"):
            class1 = "special" 
        else:
            class1 = "default"
        class1 += f"{'_func' if bbls_func=='func' else ''}"
        cpucore = 1
        pimprofResultPath = glv._get("resultPath")+class1+"_cpu_"+ str(cpucore)+"_pim_"+ str(coreNums)
        mkdir(pimprofResultPath)
        return pimprofResultPath+"/reusedecision_"+taskName+"_cpu_"+ str(cpucore)+"_pim_"+ str(coreNums)+".out" 
        
    def get_time_result(self):
        self.detail_bbl_dict = self.readListDetail(self.pimprof_bbls_result)
        self.detail_func_dict = self.readListDetail(self.pimprof_func_result)
        
    def print_time_result(self):
        print(f"\nbbls - func - {self.name}:")
        bbls_cpu_time = self.detail_bbl_dict["CPU"].total
        func_cpu_time = self.detail_func_dict["CPU"].total
        print(f"{'name':4} {'total':<25} {'cpu':<25} {'pim':<25} {'CL-DM':<21} {'cxt':<20}")
        for name , bbl in self.detail_bbl_dict.items():
            bbl.print(bbls_cpu_time)
            self.detail_func_dict[name].print(func_cpu_time)
        bbl_G_percentage = self.detail_bbl_dict["G"].total / bbls_cpu_time
        bbl_TUB_percentage = self.detail_bbl_dict["TUB"].total / bbls_cpu_time
        return [bbl_G_percentage, bbl_TUB_percentage]
    
    def mode_time(self, bbls_func, mode ): 
        bbls_cpu_time = self.detail_bbl_dict["CPU"].total
        func_cpu_time = self.detail_func_dict["CPU"].total
        if bbls_func == "func":
            return self.detail_func_dict[mode].total/func_cpu_time
        elif bbls_func == "bbls":
            return self.detail_bbl_dict[mode].total/bbls_cpu_time
        else:
            assert f"time mode is wrong: {bbls_func}"
            
    def readListDetail(self,filename):
        regexPattern = {
            1:"CPU only time \(ns\): (.*)$",
            2:"PIM only time \(ns\): (.*)$",
            3:"Instruction (.*)$",
            4:"MPKI offloading time \(ns\): (.*) = CPU (.*) \+ PIM (.*) \+ REUSE (.*) \+ SWITCH (.*)$",
            5:"Greedy offloading time \(ns\): (.*) = CPU (.*) \+ PIM (.*) \+ REUSE (.*) \+ SWITCH (.*)$",
            6:"Reuse offloading time \(ns\): (.*) = CPU (.*) \+ PIM (.*) \+ REUSE (.*) \+ SWITCH (.*)$",
            7:"CTS offloading time \(ns\): (.*) = CPU (.*) \+ PIM (.*) \+ REUSE (.*) \+ SWITCH (.*)$",
            8:"SCAFromfile offloading time \(ns\): (.*) = CPU (.*) \+ PIM (.*) \+ REUSE (.*) \+ SWITCH (.*)$",
            # 9:"SCA offloading time \(ns\): (.*) = CPU (.*) \+ PIM (.*) \+ REUSE (.*) \+ SWITCH (.*)$"
        }
        lineNum2Name = ["0","CPU","PIM","3","MPKI","G","TUB","CTS","SCA"]
        ic(filename)
        fread=open(filename, 'r') 
        useLineCount=8
        lineNum = 1
        result_dict={}
        while lineNum <= useLineCount:
            line = fread.readline()
            ic(line)

            if lineNum == 1:
                costTime = string2int(re.search(regexPattern[lineNum],line).group(1)) 
                result_dict["CPU"] = result_time("CPU", costTime, costTime, 0, 0, 0)    
            elif lineNum == 2:
                costTime = string2int(re.search(regexPattern[lineNum],line).group(1)) 
                result_dict["PIM"] = result_time("PIM", costTime, 0, costTime, 0, 0)
            elif lineNum == 3:
                lineNum = lineNum + 1
                continue
            else:
                total = string2int(re.search(regexPattern[lineNum],line).group(1)) 
                CPU = string2int(re.search(regexPattern[lineNum],line).group(2)) 
                PIM = string2int(re.search(regexPattern[lineNum],line).group(3)) 
                CL_DM = string2int(re.search(regexPattern[lineNum],line).group(4)) 
                cxt = string2int(re.search(regexPattern[lineNum],line).group(5)) 
                result_dict[lineNum2Name[lineNum]] = result_time(lineNum2Name[lineNum], 
                                                                total, CPU, PIM, CL_DM, cxt )
            lineNum = lineNum + 1
        ic(result_dict)
        return result_dict
        
    def delete_func_file(self):
        delete_file(self.fun_obj)
        delete_file(self.func_assembly_file)
        
    def compile_func_degree(self):
        ic(self.path)
        if not checkFileExists(self.fun_obj):
            # command_list = "cd " + self.path + " ; make injf"
            # COMMAND_LIST(command_list)
            CMD_PATH(["make injf"],self.path)
    
    def disassembly_func_degree(self):
        if not checkFileExists(self.func_assembly_file):
            command = "objdump -d " + self.fun_obj
            list=TIMEOUT_COMMAND_2FILE(1, command, self.func_assembly_file, glv._get("timeout"))
            ic(list)
            assert len(list)!=0
        abstractBBLfromAssembly(self.func_assembly_file,
                                self.func_bblFile,
                                self.func_bblJsonFile,
                                self.func_tmpbblFile)
        
        
    def classify(self,name):
        if name in glv._get("gapbsList"):
            return self.graph
        elif name in glv._get("specialInputList"):
            return "special"
        else:
            return "default"
        
    def sniper_command(self, cpu_pim, core_nums, bbls_func):
        if bbls_func == "bbls":
            if self.name in glv._get("gapbsList"):
                [_, command,targetFile] = gapbsInput(self.inj, self.name, cpu_pim, core_nums)
            elif self.name in glv._get("specialInputList"):
                [_, command,targetFile] = specialInput(self.inj, self.name, cpu_pim, core_nums)
            else:
                [_, command,targetFile] = defaultInput(self.inj, self.name, cpu_pim, core_nums)
        elif bbls_func == "func":
            if self.name in glv._get("gapbsList"):
                [_, command,targetFile] = gapbsInput(self.fun_obj, self.name, cpu_pim, core_nums)
            elif self.name in glv._get("specialInputList"):
                [_, command,targetFile] = specialInput(self.fun_obj, self.name, cpu_pim, core_nums)
            else:
                [_, command,targetFile] = defaultInput(self.fun_obj, self.name, cpu_pim, core_nums)
        else:
            assert("error bbls_func")
        return [command, targetFile]
    
    def pimprof(self,bbls_func, core_num):
        [command,targetFile, redirect2log] = self.pimprof_command(core_num, bbls_func)
        print(command)
        if not checkFileExists(targetFile):
            list=TIMEOUT_COMMAND_2FILE(1, command, redirect2log, glv._get("timeout"))
        
    def pimprof_command(self, coreCount, bbls_func="bbls"):
        taskName = self.name
        coreNums = coreCount
        if taskName in glv._get("gapbsList"):
            class1 = glv._get("gapbsGraphName") 
        elif taskName in glv._get("specialInputList"):
            class1 = "special" 
        else:
            class1 = "default"
        class1 += f"{'_func' if bbls_func=='func' else ''}"
        cpucore = 1
        cpulogPath = glv._get("logPath")+class1+\
                        "/"+taskName+"_pimprof_cpu_"+ str(cpucore)
        pimlogPath = glv._get("logPath")+class1+\
                        "/"+taskName+"_pimprof_pim_"+ str(coreNums)
        pimprofResultPath = glv._get("resultPath")+class1+"_cpu_"+ str(cpucore)+"_pim_"+ str(coreNums)
        mkdir(pimprofResultPath)
        pimprofResultFile = pimprofResultPath+"/reusedecision_"+taskName+"_cpu_"+ str(cpucore)+"_pim_"+ str(coreNums)+".out"
        # if bbls_func == "bbls":
        #     self.pimprof_bbls_result = pimprofResultFile
        # else:
        #     self.pimprof_func_result = pimprofResultFile     
        cpuprofstatsPath = cpulogPath + "/pimprofstats.out"
        pimprofstatsPath = pimlogPath + "/pimprofstats.out"
        pimprofreusePath = cpulogPath + "/pimprofreuse.out"
        redirect2log = pimprofResultPath +"/output_"+taskName+"_cpu_"+ str(cpucore)+"_pim_"+ str(coreNums)+".log"
        bblDecisionFile = glv._get("logPath")+ "assembly/" + taskName + "_" + f"{'func' if bbls_func=='func' else 'bbl'}"+ ".decision"
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
    
    def append(self, cluster):
        self.cluster_list.append(cluster)
                
        
    def cluster_decision(self):
        self.decision = {}
        with open(self.ctsDecisionFile,"w") as f:
            for cluster in self.cluster_list:
                self.decision[cluster] = cluster.decision2file(f,self.prioriKnowDecision)
       
    def read_id_hash_map(self):
        ic(self.id_hash_map_file)
        self.id_hash_map = {}
        with open(self.id_hash_map_file, 'r') as f:
            while True:
                line = f.readline()
                if line.startswith("  BBLID  "):
                    break
            
            for line in f:
                if line.startswith("======="):
                    break
                parts = line.split()
                id = int(parts[0])
                
                hash_first = parts[-2]
                hash_second = parts[-1]
                
                hash_value = re.sub(r'^0+','',hash_first) + '  ' + \
                            re.sub(r'^0+','',hash_second)
                            
                self.id_hash_map[hash_value] = id 
        # ic(self.id_hash_map)
                
    def read_bbl_flow(self):
        self.graph = {}
        with open(self.bbl_flow_file, 'r') as f:
            while True:
                line = f.readline()
                if line.startswith("BBLSwitchCount -"):
                    break
            
            for line in f:
                if line.startswith("======="):
                    break
                from_node, to_nodes = line.split("|")
                from_node = int(from_node.split("=")[1])
                for item in to_nodes.split():
                    to_node, weight = item.split(":")
                    to_node = int(to_node)
                    weight = int(weight)
                    
                    if from_node not in self.graph:
                        self.graph[from_node] = {}
                        
                    self.graph[from_node][to_node] = weight
        
    def check_connectivity(self, hashlist1, hashlist2):
        # ic(self.id_hash_map)
        idlist1 = [self.id_hash_map[hash1] for hash1 in hashlist1 if hash1 in self.id_hash_map]
        idlist2 = [self.id_hash_map[hash2] for hash2 in hashlist2 if hash2 in self.id_hash_map]
        adj1 = [neighbor for id1 in idlist1 if id1 in self.graph for neighbor in self.graph[id1] ]
        adj2 = [neighbor for id2 in idlist2 if id2 in self.graph for neighbor in self.graph[id2] ]
        for id1 in idlist1:
            if id1 in adj2:
                return True
        for id2 in idlist2:
            if id2 in adj1:
                return True
        return False

    def print_cluster(self):
        with open(self.cts_cluster_file, 'w') as f:
            for cluster in self.cluster_list:
                f.write(f"cluster decision is {self.decision[cluster]}\n")
                for bbl in cluster.bbls:
                    if bbl.hash in self.id_hash_map:
                        f.write(f"{bbl.hash} {self.id_hash_map[bbl.hash]}\n")
                    else:
                        f.write(f"{bbl.hash}\n")
                f.write("\n")
                        
                 
    
                
           

class cluster(application_info):
    
    def __init__(self, first_bbl):
        self.bbls = set()
        self.bbls.add(first_bbl)
        
    def __add__(self, other):
        return self.bbls.update(other.bbls)
    
    def __iadd__(self, other):
        self.bbls.update(other.bbls)
        return self
        
    def connectivity(self, cluster_b):
        mem_reuse = self.mem_overlapping(cluster_b)
        reg_resuse = self.reg_overlapping(cluster_b)
        max_ic = max(1,max(self.bbl_ic(), cluster_b.bbl_ic()))
        
        connectivity_value = (self.mem_cost * mem_reuse + self.reg_cost * reg_resuse)\
            / ( (self.mem_cost + self.reg_cost) * max_ic)
        return connectivity_value > glv._get("tuning_cluster_threshold")
        
    def bbl_ic(self):
        ic = 0
        for bbl in self.bbls:
            ic += bbl.instruction_count
        return ic
        
    def mem_overlapping(self, cluster_b):
        mem_count = 0
        write_address_union = self.union_bbls_value("write_address")
        for i in cluster_b.union_bbls_value("read_address"):
            if i in write_address_union:
                mem_count += 1
        return mem_count
                
    def reg_overlapping(self, cluster_b):
        reg_count = 0
        write_register_union = self.union_bbls_value("write_register")
        for i in cluster_b.union_bbls_value("read_register"):
            if i in write_register_union:
                reg_count += 1
        return reg_count

    def union_bbls_value(self,type):
        result_union = set()
        for i in self.bbls:
            if type == "write_register":
                result_union.update(i.write_register)
            elif type == "read_register":
                result_union.update(i.read_register)
            elif type == "write_address":
                # ic([j for j in i.write_address])
                result_union.update(i.write_address)
            elif type == "read_address":
                result_union.update(i.read_address)
            else:
                assert False, "Unknown type"
        return result_union   
    
    def print(self):
        print(f"cluster size is {len(self.bbls)}")     
        for bbl in self.bbls:
            bbl.print()
            
    def decision2file(self, f,prioriKnowDecision):
        if prioriKnowDecision == "Full-CPU":
            cluster_decsion = "CPU"
        else:
            vote_pim = 0 
            vote_cpu = 0
            for bbl in self.bbls:
                if bbl.decision() == "CPU":
                    vote_cpu+=1
                else:
                    vote_pim+=1
            if vote_pim > vote_cpu:
                cluster_decsion = "PIM"
            else:
                cluster_decsion = "CPU"
        
        # write 2 file
        for bbl in self.bbls:
            f.write(bbl.hash + " " + cluster_decsion + "\n")
        return cluster_decsion
    
    def hashlist(self):
        return [bbl.hash for bbl in self.bbls]
        
            
    
class basic_block(cluster):
    
    # self.instruction_count = 0
    # self.read_register = set()
    # self.write_register = set()
    # self.read_address = set()
    # self.write_address = set()
    
    def __init__(self, hash, bbl_assembly, sca_result):
        self.hash = hash
        self.analyse_block(bbl_assembly)
        # get sca_result
        self.reAI = sca_result[0]
        self.port_pressure = sca_result[1]
        
    def analyse_block(self, bbl_assembly):
        # analyze
        # ic(bbl_assembly)
        # ic(len(bbl_assembly))
        tmp_read_reg = set()
        tmp_read_addr = set()
        tmp_write_reg = set()
        tmp_write_addr = set()
        for line in bbl_assembly:
            # ic(line)
            match_pattern = re.search(r"^.*,(\%[a-z0-9]+)$",line)
            if match_pattern:
                # ic(1)
                tmp_write_reg.add(match_pattern.group(1))
            match_pattern = re.search(r"^.*(\%[a-z0-9]+),.*$",line)
            if match_pattern:
                # ic(2)
                tmp_read_reg.add(match_pattern.group(1))
            match_pattern = re.search(r"^.*,([0-9x]*\(.*\))$",line)
            if match_pattern:
                # ic(3)
                tmp_write_addr.add(match_pattern.group(1))
                contain_list = re.findall(r"\%[a-z0-9]*",match_pattern.group(1))
                for reg in contain_list:
                    tmp_write_reg.add(reg)
            match_pattern = re.search(r"^.*([0-9x]*\(.*\)),.*$",line)
            if match_pattern:
                # ic(4)
                tmp_read_addr.add(match_pattern.group(1))
                contain_list = re.findall(r"\%[a-z0-9]*",match_pattern.group(1))
                for reg in contain_list:
                    tmp_read_reg.add(reg)
        # sleepRandom(0.5)
        self.instruction_count = len(bbl_assembly)
        self.read_register = tmp_read_reg
        self.write_register = tmp_write_reg
        self.read_address = tmp_read_addr
        self.write_address = tmp_write_addr
    
    def decision(self):
        if self.port_pressure > self.ppressure_threshold\
            or self.reAI > self.reAI_threshold\
            or self.instruction_count > self.IC_threshold:
                return "PIM"
        else:
            return "CPU"
    
    def print(self):
        print(f"    hash: {self.hash}")
        ic(self.read_address,self.write_address,self.read_register,self.write_register)

class  DisjointSet:
    
    def __init__(self,size) -> None:
        self.parent = [i for i in range(size)]
        self.rank = [0 for i in range(size)]
        
    def find(self, i):
        if self.parent[i] == i:
            return i
        else:
            result = self.find(self.parent[i])
            self.parent[i] = result
            return result
    
    def union(self, x, y):
        rootx = self.find(x)
        rooty = self.find(y)
        if rootx != rooty:
            if self.rank[rootx] > self.rank[rooty]:
                self.parent[rooty] = rootx
            elif self.rank[rootx] < self.rank[rooty]:
                self.parent[rootx] = rooty
            else:
                self.parent[rooty] = rootx
                self.rank[rootx]+=1          
        
def loadStoreDataMove(bblHashDict, targetFile):
    with open(targetFile, 'w') as f:
        for bblHash, bbl in bblHashDict.items():
            loadSet = set()
            storeSet = set()
            f.write(bblHash+'\n')
            for command in bbl:
                ic(command)
                if re.match(r".*(\(.*\)).*$",command):
                    ic("Get load store")
                    if re.match(r".*(,.*\(.*\)).*$",command):
                        ic("Get store")
                        ic(re.match(r".*(,.*\(.*\)).*$",command).group(1))
                    elif re.match(r".*(\(.*\).*,).*$",command):
                        ic("Get load")
                        ic(re.match(r".*(\(.*\).*,).*$",command).group(1))
                    else:
                        assert("Not match load store command")
                    
    
# def regDataMovement(taskList):
#     for taskKey, taskName in taskList.items():
#         ic(taskKey, taskName)
#         assemblyPath = glv._get("logPath")+ "assembly/"
#         targetAssembly = assemblyPath + taskName + ".s"
#         bblJsonFile = targetAssembly[:-2] + "_bbl.json"
#         bblRegInfo
#         if not checkFileExists(bblDecisionFile):
#             bblHashDict = dict()
#             with open(bblJsonFile, 'r') as f:
#                 bblHashDict = json.load(f)
#             for bblHashStr, bblList in bblHashDict.items():
#                 ic(bblHashStr)
#                 # No need to collect for now
#         else:
#             yellowPrint("{} bblDecisionFile already existed".format(taskName))

def llvmAnalysis(all_for_one):
    for name, app_info in all_for_one.app_info_list.items():
        # bbls-grained analysis
        if not checkFileExists(app_info.bblSCAPickleFile):
            bblHashDict = dict()
            with open(app_info.bblJsonFile, 'r') as f:
                bblHashDict = json.load(f)
            
            parallelGetSCAResult(app_info.name, app_info.bblSCAFile, app_info.bblSCAPickleFile, bblHashDict)
        else:
            yellowPrint("{:<10} bblSCAPickleFile already existed".format(app_info.name))
        # func-grained analysis
        if not checkFileExists(app_info.funcSCAPickleFile):
            funcHashDict = dict()
            with open(app_info.func_bblJsonFile, 'r') as f:
                funcHashDict = json.load(f)
            
            parallelGetSCAResult(app_info.name, app_info.funcSCAFile, app_info.funcSCAPickleFile , funcHashDict)
        else:
            yellowPrint("{:<10} funcSCAPickleFile already existed".format(app_info.name))
        

def cluster_apps(all_for_one):
    for name, app_info in all_for_one.app_info_list.items():
        bblHashDict = dict()
        with open(app_info.bblJsonFile, 'r') as f:
            bblHashDict = json.load(f)
            
        with open(app_info.bblSCAPickleFile, 'rb') as f:
            bblDict = pickle.load(f)
        
        # init the cluster
        bbl2cluster = []
        for hash, assembly in bblHashDict.items():
            reAI = max(0,bblDict.dataDict["llvmLoadPressure"][hash]) +\
                max(0,bblDict.dataDict['llvmStorePressure'][hash])       
            port_pressure = max(0,bblDict.dataDict['llvmSBPort23Pressure'][hash])
            sca_result = [reAI, port_pressure]
            bbl2cluster.append(cluster(basic_block(hash,assembly,sca_result)))
        
        app_info.read_id_hash_map()
        app_info.read_bbl_flow()
        # cluster_without_bblflow(bbl2cluster,app_info)
        cluster_with_bblflow(bbl2cluster,app_info)
        #decision 2 file
        app_info.cluster_decision()
        app_info.print_cluster()
        
        all_for_one.update_app_info(name,app_info)
    return all_for_one

def cluster_with_bblflow(bbl2cluster, app_info):
    length = len(bbl2cluster)
    ic(length)
    dj = DisjointSet(length)
    i = 0
    pbar = tqdm(total=length) 
    while i < length:
        pbar.update(1)
        j = i + 1
        while j < length:
            if app_info.check_connectivity(bbl2cluster[i].hashlist(),bbl2cluster[j].hashlist()) \
                and bbl2cluster[i].connectivity(bbl2cluster[j]):
                dj.union(i,j)
            j += 1
        i += 1
    pbar.close()
        
    # count remain clusters num
    unique_cluster = set()
    for i in range(length):
        root = dj.find(i) 
        if root != i:
            bbl2cluster[root]+=bbl2cluster[i]
        unique_cluster.add(root)
    ic(len(unique_cluster))
    for i in unique_cluster:
        app_info.append(bbl2cluster[i])
    
    # print
    # ic(app_info.cluster_list[0].print())
    
    
    return app_info
      
def cluster_without_bblflow(bbl2cluster, app_info):
    # loop to cluster without bbl flow
    length = len(bbl2cluster)
    ic(length)
    tag = [0] * length
    i = 0
    pbar = tqdm(total=length) 
    while i < length:
        pbar.update(1)
        if tag[i] == 0:
            j = i + 1
            while j < length:
                if tag[j]==0 and bbl2cluster[i].connectivity(bbl2cluster[j]):
                    bbl2cluster[i] += bbl2cluster[j]
                    tag[j] = 1
                j += 1
        i += 1
    pbar.close()
        
    # count remain clusters num
    count_clusters = 0
    for i in range(length):
        if tag[i] == 0:
            count_clusters += 1
            app_info.append(bbl2cluster[i])
    ic(count_clusters)
        
    # print
    ic(app_info.cluster_list[0].print())
    return app_info
    
def OffloadBySCA(all_for_one:CTS):
    for _,app_info in all_for_one.app_info_list.items():
        with open(app_info.bblSCAPickleFile, 'rb') as f:
            bblDict = pickle.load(f)
        with open(app_info.funcSCAPickleFile, 'rb') as f:
            bblDict_func = pickle.load(f)
        prioriKnowDict = glv._get("prioriKnow")
        if app_info.name in prioriKnowDict and prioriKnowDict[app_info.name]["parallelism"] < 16:
            prioriKnowDecision = "Full-CPU"
        else:
            prioriKnowDecision = "No influence"
        # bbls-grained decision
        decisionByManual(bblDict,app_info.bblDecisionFile, prioriKnowDecision)
        # func-grained decision
        decisionByManual(bblDict_func,app_info.funcDecisionFile, prioriKnowDecision)
        
            
def llvmResult(bblList):
    command = llvmCommand(bblList)
    if not bblList: return [0,0,0]
    ic(bblList)
    # print(command)
    [list, errList]=TIMEOUT_severalCOMMAND(command, glv._get("timeout"))
    # ic(errList)
    if errList and errList[-1]=="error: no assembly instructions found.\n":
        cycles = 0
        pressure = 0
        decision = "None"
        return [decision, cycles, pressure]
    loadPortUsage = 0.0
    resourcePressure = 0.0
    registerPressure = 0.0
    memoryPressure = 0.0
    MayLoad = 0
    MayStore = 0
    MayLoadPostition = 3*7+1
    MayStorePostition = 4*7+1
    for i in range(len(list)):
        # ic(list[i])
# [1]    [2]    [3]    [4]    [5]    [6]    Instructions:
#  2      7     0.50    *                   paddq 3084(%rip), %xmm1
#  1      1     1.00           *            movdqu        %xmm2, (%r8,%rdx,8)
        if re.match(r".{"+str(MayLoadPostition)+r"}\*.*$",list[i]):
            MayLoad += 1
        if re.match(r".{"+str(MayStorePostition)+r"}\*.*$",list[i]):
            MayStore += 1
        if list[i].startswith('  - SBPort23 '):
            ic(list[i])
            matchPressure = re.match(r".*\[ ([0-9\.]*)% \](\s*)$",list[i])
            if not matchPressure:
                lsportPressure = -2
            else:
                lsportPressure = float(matchPressure.group(1))
            print(command)
            print(lsportPressure)
        if list[i].startswith('  Resource Pressure       '):
            # ic(list[i])
            matchPressure = re.match(r".*\[ ([0-9\.]*)% \](\s*)$",list[i])
            if not matchPressure:
                resourcePressure = -2
            else:
                resourcePressure = float(matchPressure.group(1))
            # ic(resourcePressure)
        if list[i].startswith('  - Register Dependencies ['):
            # ic(list[i])
            registerPressure = float(re.match(r".*\[ ([0-9\.]*)% \](\s*)$",list[i]).group(1))
            # ic(registerPressure)
        if list[i].startswith('  - Memory Dependencies   ['):
            # ic(list[i])
            memoryPressure = float(re.match(r".*\[ ([0-9\.]*)% \](\s*)$",list[i]).group(1))
            # ic(memoryPressure)
        # if list[i].startswith('Resource pressure per iteration'):
        #     ic(list[i])
        #     ic(list[i+1])
        #     ic(list[i+2])       
        #     matchPort = re.match(r".*(\s+)([0-9\.]+)(\s*)\n$",list[i+2])
        #     if not matchPort:
        #         loadPortUsage = -2
        #     else:
        #         ic(matchPort)
        #         ic(matchPort.group(0))
        #         ic(matchPort.group(1))
        #         ic(matchPort.group(2))
        #         loadPortUsage = float(matchPort.group(2))
        #     ic(loadPortUsage)
    # ic(list[2])
    # ic(list[11])
    instrNums = int(re.match(r"Instructions:(\s*)([0-9]*)(\s*)",list[1]).group(2))/100
    # ic(instrNums, MayLoad, MayStore)
    cycles = int(re.match(r"Total Cycles:(\s*)([0-9]*)(\s*)",list[2]).group(2))
    if list[11]=="No resource or data dependency bottlenecks discovered.\n":
        pressure = 0
    else:
        pressure = float(re.match(r"Cycles with backend pressure increase(\s*)\[ ([0-9\.]*)% \](\s*)",list[11]).group(2))
    if pressure < 70:
        decision = "CPU"
    else:
        decision = "PIM"
    # ic(decision, cycles, pressure)
    return [decision, cycles, pressure]
