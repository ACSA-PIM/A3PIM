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

class CTS:
    
    assemblyPath = glv._get("logPath")+ "assembly/"
    mem_cost = 60 + 30
    reg_cost = 30 #  value
    cluster_threshold = 0.05
    parallelism_threshlod = 16
    reAI_threshold = 0.5
    IC_threshold = 27
    ppressure_threshold = 5 
    
    def __init__(self,taskList):
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
        
class application_info(CTS):
    def __init__(self, name, path,prioriKnowDecision):
        self.name = name
        self.path = path
        prefix_name = self.assemblyPath + name
        self.targetAssembly = prefix_name + '.s'
        self.bblJsonFile = prefix_name + '_bbl.json'
        self.bblSCAFile = prefix_name + '_bbl.sca'
        self.bblSCAPickleFile = prefix_name + '_bbl_sca.pickle'
        self.bblDecisionFile = prefix_name + '_bbl.decision'
        self.ctsDecisionFile = prefix_name + '_bbl_cts.decision'
        self.cluster_list = []
        self.prioriKnowDecision = prioriKnowDecision
        
    def append(self, cluster):
        self.cluster_list.append(cluster)
    
        
    def cluster_decision(self):
        with open(self.ctsDecisionFile,"w") as f:
            for cluster in self.cluster_list:
                cluster.decision2file(f,self.prioriKnowDecision)
                
           

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
        return connectivity_value > self.cluster_threshold
        
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
            match_pattern = re.search(r"^.*([0-9x]*\(.*\)),.*$",line)
            if match_pattern:
                # ic(4)
                tmp_read_addr.add(match_pattern.group(1))
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
        if not checkFileExists(app_info.bblSCAPickleFile):
            bblHashDict = dict()
            with open(app_info.bblJsonFile, 'r') as f:
                bblHashDict = json.load(f)
            
            parallelGetSCAResult(app_info, bblHashDict)
        else:
            yellowPrint("{:<10} bblSCAPickleFile already existed".format(app_info.name))

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
        
        #decision 2 file
        app_info.cluster_decision()
        
        all_for_one.update_app_info(name,app_info)
    return all_for_one
    
    
def OffloadBySCA(all_for_one:CTS):
    for _,app_info in all_for_one.app_info_list.items():
        with open(app_info.bblSCAPickleFile, 'rb') as f:
            bblDict = pickle.load(f)
        prioriKnowDict = glv._get("prioriKnow")
        if app_info.name in prioriKnowDict and prioriKnowDict[app_info.name]["parallelism"] < 16:
            prioriKnowDecision = "Full-CPU"
        else:
            prioriKnowDecision = "No influence"
        decisionByManual(bblDict,app_info.bblDecisionFile, prioriKnowDecision)
            
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
