import matplotlib
import matplotlib.pyplot as plt
import pprint

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
                    segmentCount += 1
                
                if inSegment:
                    # Parse test parameters
                    if self.key in line:
                        #Format: "self.key, # x, # y, ..."
                        segments = line.strip().split(",")
                        if self.key != segments[0]:
                            print("Parse error, expected key")
                        segments = segments[1:]
                        for seg in segments:
                            seg = seg.strip()
                            segmentKeys.append(seg)

                    else:
                        # Parse performance counter stats
                        # Format: "#####    value       #comment"
                        tokens = line.split()
                        if len(tokens) > 1 and (tokens[1] in self.values):
                            k = tokens[1]
                            v = int(tokens[0])
                            self.addToMap(self.logVals, segmentKeys + [k], v)
                            #logVals[k].append(v)
                
                if self.startString in line:
                    inSegment = True
                    segmentKeys = []


pp = pprint.PrettyPrinter(indent=4)

################################################################################
# User/Kernel instructions & Cycles

# @todo: We need to compare this with total instruction count, to see how the
# ratios change wrt. total instructions
################################################################################
intel_InstrMix = Benchmark(
    "Instructions Stack",
    ["instructions:k", "cycles:k", "instructions:u", "cycles:u"])
intel_InstrMix.decodeLog("instructions-stack.sh.intel.log")
pp.pprint(intel_InstrMix.logVals)

if True:
    connections = []
    user_i_ratio = []
    kernel_i_ratio = []
    user_c_ratio = []
    kernel_c_ratio = []
    for k, v in intel_InstrMix.logVals['4096 keys'].items():
        if "conncetions" in k:
            connections.append(k)
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
    
    plt.subplot(2,1,1)
    plt.plot(user_i_ratio, label="User, Intel")
    plt.ylabel("User instr / Instr tot [%]")
    plt.legend()
    plt.twinx()
    plt.plot(kernel_i_ratio, label="Kernel, Intel", color="orange")
    plt.ylabel("Kernel instr / Instr tot [%]")
    plt.xticks(range(len(connections)), connections)
    plt.xlabel("Keys")
    plt.legend()

    # Branch instruction mix
    plt.subplot(2,1,2)
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
################################################################################
intel_branchPredictor = Benchmark(
    "Branch predictor",
    ["branch-misses", "branch-instructions", "instructions"])
intel_branchPredictor.decodeLog("branch_predictor.sh.intel.log")
pp.pprint(intel_branchPredictor.logVals)

# 4096 keys, varying connections
if True:
    # Branch misses
    plt.subplot(2,1,1)
    connections = []
    br_miss = []
    br_mix = []
    for k, v in intel_branchPredictor.logVals['4096 keys'].items():
        if "conncetions" in k:
            connections.append(k)
            missRatio = (v['branch-misses'] / v['branch-instructions']) * 100 
            brRatio = (v['branch-instructions'] / v['instructions']) * 100
            br_miss.append(missRatio)
            br_mix.append(brRatio)

    plt.plot(br_miss, label="Intel")
    plt.xticks(range(len(connections)), connections)
    plt.ylabel("Branch misses per branch instruction [%]")
    plt.xlabel("Keys")
    plt.legend()

    # Branch instruction mix
    plt.subplot(2,1,2)
    plt.plot(br_mix, label="Intel")
    plt.xticks(range(len(connections)), connections)
    plt.ylabel("Branch instructions per instruction [%]")
    plt.xlabel("Keys")
    plt.legend()
    plt.show()


################################################################################
# L1I Cache
################################################################################
intel_L1icache = Benchmark(
    "L1 cache",
    ["L1-icache-load-misses", "L1-icache-loads", "instructions"])
intel_L1icache.decodeLog("l1_cache.sh.intel.log")
pp.pprint(intel_L1icache.logVals)


################################################################################
# LLC Cache
################################################################################
intel_LLCcache = Benchmark(
    "LLC cache",
    ["LLC-loads", "LLC-load-misses"])
intel_LLCcache.decodeLog("llc.sh.intel.log")
pp.pprint(intel_LLCcache.logVals)

keys = []
connections = []
VarKeysHitRatio = []
VarConnHitRatio = []
for k, v in intel_LLCcache.logVals.items():
    if "keys" in k:
        # Varying keys
        keys.append(k.split()[0]) # Just grab the number
        hitRatio = (1 - (v['LLC-load-misses'] / v['LLC-loads'])) * 100 
        VarKeysHitRatio.append(hitRatio)
    
    if k == '4096 keys':

        # Varying connections, stored as nested dictionaries
        for i, j in v.items():
            if(type(j) is dict):
                connections.append(i.split()[0]) # Just grab the number
                hitRatio = (1 - (j['LLC-load-misses'] / j['LLC-loads'])) * 100 
                VarConnHitRatio.append(hitRatio)

# Varying key size
plt.subplot(2,1,1)
plt.title("LLC Properties with varying key and connection count")
plt.plot(VarKeysHitRatio, label="Intel")
plt.xticks(range(len(keys)), keys)
plt.ylabel("LLC Hit Ratio [%]")
plt.xlabel("Keys")
plt.legend()

# Varying connections
plt.subplot(2,1,2)
plt.plot(VarConnHitRatio, label="Intel")
plt.xticks(range(len(connections)), connections)
plt.ylabel("LLC Hit Ratio [%]")
plt.xlabel("Connections")
plt.legend()

plt.show()
