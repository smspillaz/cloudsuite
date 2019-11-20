import matplotlib
import matplotlib.pyplot as plt
import pprint

LOGDIR = "logs/"

class Benchmark:
    def __init__(self, key, values):
        self.key = key
        self.values = values
        self.startString = "Signal handled: Interrupt"
        self.endString = "seconds time elapsed"
        self.logVals = {}
    
    def addToMap(self, dictToUpdate, keySeq, v):
        if len(keySeq) == 1:
            dictToUpdate[keySeq[0]] = v
        else:
            if keySeq[0] not in dictToUpdate:
                dictToUpdate[keySeq[0]] = {}
            self.addToMap(dictToUpdate[keySeq[0]], keySeq[1:], v)

    def decodeLog(self, filename):
        with open(filename, "r") as f:
            # Pretty naive, but works
            inSegment = False
            segmentCount = 0
            segmentKeys = []
            for line in f.readlines():
                if self.endString in line:
                    inSegment = False
                    segmentKeys = []
                    segmentCount += 1
                
                if inSegment:
                    # Parse performance counter stats
                    # Format: "#####    value       #comment"
                    tokens = line.split()
                    if len(tokens) > 1 and (tokens[1] in self.values):
                        k = tokens[1]
                        v = int(tokens[0])
                        self.addToMap(self.logVals, segmentKeys + [k], v)
                        #logVals[k].append(v)
                
                if self.key in line and not inSegment:
                    #Format: "self.key, # x, # y, ..."
                    segments = line.strip().split(",")
                    if self.key != segments[0]:
                        print("Parse error, expected key")
                    segments = segments[1:]
                    for seg in segments:
                        seg = seg.strip()
                        segmentKeys.append(seg)
                    inSegment = True


pp = pprint.PrettyPrinter(indent=4)


def appendIfNotInlist(l, v):
    if v not in l:
        l.append(v)

################################################################################
# User/Kernel instructions & Cycles

# Intel x86 system 1    : x
# Intel x86 system 2    : 
# Arm Cavium            : N/A                   No kernel instructions in logs
# Amazon EC2 A1         : 

# @todo: We need to compare this with total instruction count, to see how the
# ratios change wrt. total instructions
################################################################################
intel_InstrMix = Benchmark(
    "Instructions Stack",
    ["instructions:k", "cycles:k", "instructions:u", "cycles:u"])
intel_InstrMix.decodeLog(LOGDIR + "instructions-stack.sh.intel.log")

############################### Data Extraction ################################
connections = []
user_i_ratio = []
kernel_i_ratio = []
user_c_ratio = []
kernel_c_ratio = []
for k, v in intel_InstrMix.logVals['4096 keys'].items():
    if "conncetions" in k:
        appendIfNotInlist(connections, k)
        kernel_i = v['instructions:k']
        user_i = v['instructions:u']
        kernel_c = v['cycles:k']
        user_c = v['cycles:u']
        i_tot = kernel_i + user_i
        c_tot = kernel_c + user_c

        user_i_ratio.append((user_i / i_tot) * 100)
        kernel_i_ratio.append((kernel_i / i_tot) * 100)
        user_c_ratio.append((user_c / c_tot) * 100)
        kernel_c_ratio.append((kernel_c / c_tot) * 100)

################################### Plotting ###################################
plt.subplot(2,2,1)
plt.title("User versus Kernel instruction mix")
plt.plot(user_i_ratio, label="User, Intel")
plt.ylabel("User instr / Instr tot [%]")
plt.legend()
plt.twinx()
plt.plot(kernel_i_ratio, label="Kernel, Intel", color="orange")
plt.ylabel("Kernel instr / Instr tot [%]")
plt.xticks(range(len(connections)), connections)
plt.xlabel("Keys")
plt.legend()

# Ratio stackplot
plt.subplot(2,2,2)
plt.stackplot(range(len(user_i_ratio)), user_i_ratio, kernel_i_ratio, labels=["User", "Kernel"])
plt.ylabel("Instructions")
plt.legend()

plt.xticks(range(len(connections)), connections)
plt.xlabel("Keys")
plt.legend()

# Cycle ratio
plt.subplot(2,2,3)
plt.plot(user_c_ratio, label="User, Intel")
plt.ylabel("User cycles per total cycles [%]")
plt.legend()
plt.twinx()
plt.plot(kernel_c_ratio, label="Kernel, Intel", color="orange")
plt.xticks(range(len(connections)), connections)
plt.ylabel("Kernel cycles per total cycles [%]")
plt.xlabel("Keys")
plt.legend()
plt.show()





################################################################################
# Branch predictor
# Intel x86 system 1    : x
# Intel x86 system 2    : 
# Arm Cavium            : x
# Amazon EC2 A1         : 
################################################################################
intel_branchPredictor = Benchmark(
    "Branch predictor",
    ["branch-misses", "branch-instructions", "instructions"])
intel_branchPredictor.decodeLog(LOGDIR + "branch_predictor.sh.intel.log")

arm_cavium_branchPredictor = Benchmark(
    "Branch predictor",
    ["armv8_pmuv3_0/br_mis_pred/:u", "armv8_pmuv3_0/br_pred/:u", "instructions:u"])
arm_cavium_branchPredictor.decodeLog(LOGDIR + "branch_predictor.sh.arm.cavium.log")


############################### Data Extraction ################################
# 4096 keys, varying connections
# Branch misses
plt.subplot(2,1,1)
connections = []
x86_br_miss = []
x86_br_mix = []
for k, v in intel_branchPredictor.logVals['4096 keys'].items():
    if "conncetions" in k:
        appendIfNotInlist(connections, k)
        missRatio = (v['branch-misses'] / v['branch-instructions']) * 100 
        brRatio = (v['branch-instructions'] / v['instructions']) * 100
        x86_br_miss.append(missRatio)
        x86_br_mix.append(brRatio)

arm_cavium_br_miss = []
arm_cavium_br_mix = []
for k, v in arm_cavium_branchPredictor.logVals['4096 keys'].items():
    if "conncetions" in k:
        appendIfNotInlist(connections, k)
        miss = v['armv8_pmuv3_0/br_mis_pred/:u']
        predict = v['armv8_pmuv3_0/br_pred/:u']
        total = miss + predict
        missRatio = (miss / total) * 100 
        brRatio = (total / v['instructions:u']) * 100
        arm_cavium_br_miss.append(missRatio)
        arm_cavium_br_mix.append(brRatio)

# Just show the number of connections (Format of key is: "# connections")
connections = [x.split(' ')[0] for x in connections]

################################### Plotting ###################################
plt.plot(x86_br_miss, label="x86")
plt.plot(arm_cavium_br_miss, label="ARM (Cavium)")
plt.title("Branch misses & branch instructions")
plt.xticks(range(len(connections)), connections)
plt.ylabel("Branch misses per branch instruction [%]")
plt.xlabel("Connections")
plt.legend()

# Branch instruction mix
plt.subplot(2,1,2)
plt.plot(x86_br_mix, label="x86")
plt.plot(arm_cavium_br_mix, label="ARM (Cavium)")
plt.xticks(range(len(connections)), connections)
plt.ylabel("Branch instructions per instruction [%]")
plt.xlabel("Connections")
plt.legend()
plt.show()





################################################################################
# L1I Cache
# Intel x86 system 1    : x
# Intel x86 system 2    : 
# Arm Cavium            : N/A                                   Needs a rerun
# Amazon EC2 A1         : 
################################################################################
intel_L1icache = Benchmark(
    "L1 cache",
    ["L1-icache-load-misses", "icache.hit", "instructions"])
intel_L1icache.decodeLog(LOGDIR + "l1_cache.sh.intel.log")
pp.pprint(intel_L1icache.logVals)

############################### Data Extraction ################################
connections = []
hitrate = []
for k, v in intel_L1icache.logVals.items():
    if k == '4096 keys':
        # Varying connections, stored as nested dictionaries
        for i, j in v.items():
            if(type(j) is dict):
                appendIfNotInlist(connections, i.split()[0])
                connections.append(i.split()[0]) # Just grab the number
                hits = j['icache.hit']
                misses = j['L1-icache-load-misses']
                total = hits + misses
                hitRatio = (hits / total) * 100 
                hitrate.append(hitRatio)

################################### Plotting ###################################
# Varying connections
plt.subplot(1,1,1)
plt.plot(hitrate, label="x86")
plt.xticks(range(len(connections)), connections)
plt.title("L1I Cache")
plt.ylabel("L1I Hit Ratio [%]")
plt.xlabel("Connections")
plt.legend()

plt.show()

################################################################################
# L1D Cache
# Intel x86 system 1    : x
# Intel x86 system 2    : 
# Arm Cavium            : x
# Amazon EC2 A1         : 
################################################################################
intel_L1dcache = Benchmark(
    "L1D cache",
    ["L1-dcache-load-misses", "L1-dcache-loads", "instructions"])
intel_L1dcache.decodeLog(LOGDIR + "l1d_cache.sh.intel.log")

arm_cavium_L1dcache = Benchmark(
    "L1D cache",
    ["L1-dcache-load-misses:u", "L1-dcache-loads:u", "instructions"])
arm_cavium_L1dcache.decodeLog(LOGDIR + "l1d_cache.sh.arm.cavium.log")

keys = []
connections = []

############################### Data Extraction ################################

# Arm cavium
arm_cavium_l1d_hitrate_varyingkeys = []
arm_cavium_l1d_hitrate_4096_connections = []
for k, v in arm_cavium_L1dcache.logVals.items():
    if "keys" in k:
        # Varying keys
        appendIfNotInlist(keys, k.split()[0])
        hitratio = (1 - (v['L1-dcache-load-misses:u'] / v['L1-dcache-loads:u'])) * 100 
        arm_cavium_l1d_hitrate_varyingkeys.append(hitratio)
    
    if k == '4096 keys':
        # Varying connections, stored as nested dictionaries
        for i, j in v.items():
            if(type(j) is dict):
                appendIfNotInlist(connections, i.split()[0])
                arm_cavium_l1d_hitrate_4096_connections.append(hitratio)
                hitratio = (1 - (j['L1-dcache-load-misses:u'] / j['L1-dcache-loads:u'])) * 100 

# x86
x86_l1d_hitrate_varyingkeys = []
x86_l1d_hitrate_4096_connections = []
for k, v in intel_L1dcache.logVals.items():
    if "keys" in k:
        # Varying keys
        appendIfNotInlist(keys, k.split()[0])
        hitratio = (1 - (v['L1-dcache-load-misses'] / v['L1-dcache-loads'])) * 100 
        x86_l1d_hitrate_varyingkeys.append(hitratio)
    
    if k == '4096 keys':
        # Varying connections, stored as nested dictionaries
        for i, j in v.items():
            if(type(j) is dict):
                appendIfNotInlist(connections, i.split()[0])
                hitratio = (1 - (j['L1-dcache-load-misses'] / j['L1-dcache-loads'])) * 100 
                x86_l1d_hitrate_4096_connections.append(hitratio)

################################### Plotting ###################################
# Varying key size
plt.subplot(2,1,1)
plt.title("L1D Properties with varying key and connection count")
plt.plot(x86_l1d_hitrate_varyingkeys, label="x86")
plt.plot(arm_cavium_l1d_hitrate_varyingkeys, label="ARM (Cavium)")
plt.xticks(range(len(keys)), keys)
plt.ylabel("L1D Hit Ratio [%]")
plt.xlabel("Keys")
plt.legend()

# Varying connections
plt.subplot(2,1,2)
plt.plot(x86_l1d_hitrate_4096_connections, label="x86")
plt.plot(arm_cavium_l1d_hitrate_4096_connections, label="ARM (Cavium)")
plt.xticks(range(len(connections)), connections)
plt.ylabel("L1D Hit Ratio [%]")
plt.xlabel("Connections")
plt.legend()

plt.show()





################################################################################
# L2D Cache
# Intel x86 system 1    : 
# Intel x86 system 2    : 
# Arm Cavium            : x
# Amazon EC2 A1         : 
################################################################################

arm_cavium_L2dcache = Benchmark(
    "L2D cache",
    ["armv8_pmuv3_0/l2d_cache/:u", "armv8_pmuv3_0/l2d_cache_refill/:u", "instructions"])
arm_cavium_L2dcache.decodeLog(LOGDIR + "l2d_cache.sh.arm.cavium.log")

############################### Data Extraction ################################
keys = []
connections = []
arm_cavium_refillRatio_var_keys = []
arm_cavium_refillRatio_var_conn = []
for k, v in arm_cavium_L2dcache.logVals.items():
    if "keys" in k:
        # Varying keys
        appendIfNotInlist(keys, k.split()[0])
        ratio = (1 - (v['armv8_pmuv3_0/l2d_cache_refill/:u'] / v['armv8_pmuv3_0/l2d_cache/:u'])) * 100 
        arm_cavium_refillRatio_var_keys.append(ratio)
    
    if k == '4096 keys':
        # Varying connections, stored as nested dictionaries
        for i, j in v.items():
            if(type(j) is dict):
                appendIfNotInlist(connections, i.split()[0])
                ratio = (1 - (j['armv8_pmuv3_0/l2d_cache_refill/:u'] / j['armv8_pmuv3_0/l2d_cache/:u'])) * 100 
                arm_cavium_refillRatio_var_conn.append(ratio)

################################### Plotting ###################################
# Varying key size
plt.subplot(2,1,1)
plt.title("L2D Refill ratio")
plt.plot(arm_cavium_refillRatio_var_keys, label="Arm (Cavium)")
plt.xticks(range(len(keys)), keys)
plt.ylabel("L2D Refill Ratio [%]")
plt.xlabel("Keys")
plt.legend()

# Varying connections
plt.subplot(2,1,2)
plt.plot(arm_cavium_refillRatio_var_conn, label="Arm (Cavium)")
plt.xticks(range(len(connections)), connections)
plt.ylabel("LLC Refill Ratio [%]")
plt.xlabel("Connections")
plt.legend()

plt.show()





################################################################################
# LLC Cache
# Intel x86 system 1    : x
# Intel x86 system 2    : 
# Arm Cavium            : N/A                   No performance counters for LLC
# Amazon EC2 A1         : 
################################################################################
intel_LLCcache = Benchmark(
    "LLC cache",
    ["LLC-loads", "LLC-load-misses"])
intel_LLCcache.decodeLog(LOGDIR + "llc.sh.intel.log")
pp.pprint(intel_LLCcache.logVals)


############################### Data Extraction ################################
keys = []
connections = []
VarKeysHitRatio = []
VarConnHitRatio = []
for k, v in intel_LLCcache.logVals.items():
    if "keys" in k:
        # Varying keys
        appendIfNotInlist(keys, k.split()[0])
        hitRatio = (1 - (v['LLC-load-misses'] / v['LLC-loads'])) * 100 
        VarKeysHitRatio.append(hitRatio)
    
    if k == '4096 keys':

        # Varying connections, stored as nested dictionaries
        for i, j in v.items():
            if(type(j) is dict):
                appendIfNotInlist(connections, i.split()[0])
                hitRatio = (1 - (j['LLC-load-misses'] / j['LLC-loads'])) * 100 
                VarConnHitRatio.append(hitRatio)

################################### Plotting ###################################
# Varying key size
plt.subplot(2,1,1)
plt.title("LLC Properties with varying key and connection count")
plt.plot(VarKeysHitRatio, label="x86")
plt.xticks(range(len(keys)), keys)
plt.ylabel("LLC Hit Ratio [%]")
plt.xlabel("Keys")
plt.legend()

# Varying connections
plt.subplot(2,1,2)
plt.plot(VarConnHitRatio, label="x86")
plt.xticks(range(len(connections)), connections)
plt.ylabel("LLC Hit Ratio [%]")
plt.xlabel("Connections")
plt.legend()

plt.show()
