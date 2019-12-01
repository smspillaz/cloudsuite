import matplotlib
import matplotlib.pyplot as plt
import os

from systemconstants import *

################################################################################
#                               Configuration                                  #
################################################################################

SHOW_PLOTS = True
LOGDIR = "logs/"
OUTDIR = "plots/"
if not os.path.exists(OUTDIR):
    os.makedirs(OUTDIR)


SERVER_REQ_STR = "Outstanding requests per worker:"

################################################################################
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
            parseServerReqs = False
            segmentCount = 0
            segmentKeys = []
            serverReqs = []
            for line in f.readlines():
                if self.endString in line:
                    # Compute avg. outstanding requests
                    self.addToMap(self.logVals, segmentKeys +
                        ["Server queue"], sum(serverReqs) / len(serverReqs))

                    inSegment = False
                    segmentKeys = []
                    serverReqs = []
                    segmentCount += 1

                
                if inSegment:
                    # Parse server outstanding requests
                    if parseServerReqs:
                        #Format = "# # # # ..."
                        vals = [int(v) for v in line.strip().split(' ')]
                        serverReqs.append(sum(vals) / len(vals))
                        parseServerReqs = False

                    if SERVER_REQ_STR in line:
                        # Parse server outstanding requests in next line
                        parseServerReqs = True



                    # Parse performance counter stats
                    # Format: "#####    value       #comment"
                    tokens = line.split()
                    if len(tokens) > 1 and (tokens[1] in self.values):
                        k = tokens[1]
                        v = int(tokens[0])
                        self.addToMap(self.logVals, segmentKeys + [k], v)
                        #logVals[k].append(v)
                
                if line.startswith(self.key) and not inSegment:
                    #Format: "self.key, # x, # y, ..."
                    segments = line.replace(self.key,'').strip().split(",")
                    for seg in segments:
                        seg = seg.strip()
                        segmentKeys.append(seg)
                    inSegment = True


def appendIfNotInlist(l, v):
    if v not in l:
        l.append(v)

def extract2DValues(d, key):
    x = []
    y = []
    z = []

    for k1, v1 in d.items():
        x.append(k1)
        z_vals = []
        for k2, v2 in v1.items():
            appendIfNotInlist(y, k2)
            z_vals.append(v2[key])
        z.append(z_vals)

    return (x,y,z)

def extractMapFromMap(m, keys):
    if len(keys) > 0:
        return extractMapFromMap(m[keys[0]], keys[1:])
    else:
        return m

def extractKVFromMap(m, valueKey):
    # Assumes that the map is 1 level deep
    return { k: m[k][valueKey] for k, v in m.items()}
    

################################################################################
# ARM throughput 
################################################################################
arm_cavium_throughput_l1 = Benchmark(
    "==> Bench:",
    ["instructions:u", "L1-dcache-load-misses:u", "L1-dcache-loads:u", "armv8_pmuv3_0/l1i_cache_refill/:u", "armv8_pmuv3_0/l1i_cache/:u"])
arm_cavium_throughput_l1.decodeLog(LOGDIR + "arm-throughput-4waysmt/arm.cavium.throughput.l1.log")

rps1_cavium_keys = ["65536 keys", "512 conns", "6 threads"]
rps1_cavium = extractKVFromMap(extractMapFromMap(arm_cavium_throughput_l1.logVals, rps1_cavium_keys), "Server queue")
rps2_cavium_keys = ["65536 keys", "512 conns", "8 threads"]
rps2_cavium = extractKVFromMap(extractMapFromMap(arm_cavium_throughput_l1.logVals,rps2_cavium_keys ), "Server queue")
avg_cavium = []
for k, v in rps2_cavium.items():
    avg_cavium.append((rps1_cavium[k] + rps2_cavium[k])/2)


plt.figure()
plt.title("Average Total Outstanding Client Requests (Cavium)")
plt.plot([int(k.replace(" rps",'')) for k in rps1_cavium.keys()], rps1_cavium.values(), label=', '.join(rps1_cavium_keys))
plt.plot([int(k.replace(" rps",'')) for k in rps2_cavium.keys()], rps2_cavium.values(), label=', '.join(rps2_cavium_keys))
plt.plot([int(k.replace(" rps",'')) for k in rps1_cavium.keys()], avg_cavium, label='Average', linestyle="--", color="b")
plt.legend()
plt.xlabel("RPS")
plt.ylabel("Outstanding Requests")
plt.show()


################################################################################
# Intel throughput 
################################################################################

intel_xeon_throughput_sw = Benchmark(
    "==> Bench:",
    ["instructions:u", "instructions:k", "cycles:u", "cycles:k"])
intel_xeon_throughput_sw.decodeLog(LOGDIR + "intel-throughput-2waysmt/intel.throughput.sw.log")

rps1_xeon_keys = ["65536 keys", "512 conns", "4 threads"]
rps1_xeon = extractKVFromMap(extractMapFromMap(intel_xeon_throughput_sw.logVals, rps1_xeon_keys), "Server queue")
rps2_xeon_keys = ["65536 keys", "512 conns", "8 threads"]
rps2_xeon = extractKVFromMap(extractMapFromMap(intel_xeon_throughput_sw.logVals,rps2_xeon_keys ), "Server queue")
avg_xeon = []
for k, v in rps2_xeon.items():
    avg_xeon.append((rps1_xeon[k] + rps2_xeon[k])/2)

plt.figure()
plt.title("Average Total Outstanding Client Requests (Intel)")
plt.plot([int(k.replace(" rps",'')) for k in rps1_xeon.keys()], rps1_xeon.values(), label=', '.join(rps1_xeon_keys))
plt.plot([int(k.replace(" rps",'')) for k in rps2_xeon.keys()], rps2_xeon.values(), label=', '.join(rps2_xeon_keys))
plt.plot([int(k.replace(" rps",'')) for k in rps1_xeon.keys()], avg_xeon, label='Average', linestyle="--", color="b")
plt.legend()
plt.xlabel("RPS")
plt.ylabel("Outstanding Requests")
plt.show()

################################################################################
# Compared average throughput 
################################################################################
plt.figure()
plt.title("Average Total Outstanding Client Requests")
plt.plot([int(k.replace(" rps",'')) for k in rps2_cavium.keys()], avg_cavium, label='Cavium')
plt.axvline(159000,linestyle='--', color='black')
plt.plot([int(k.replace(" rps",'')) for k in rps2_xeon.keys()], avg_xeon, label='Xeon')
plt.axvline(115000,linestyle='--', color='black')
plt.legend()
plt.xlabel("RPS")
plt.ylabel("Outstanding Requests")
plt.show()

################################################################################
# IPC 
################################################################################
xeon_keys = ["65536 keys", "512 conns", "4 threads"]
userinstr1_xeon = extractKVFromMap(extractMapFromMap(intel_xeon_throughput_sw.logVals, xeon_keys), "instructions:u")
kerninstr1_xeon = extractKVFromMap(extractMapFromMap(intel_xeon_throughput_sw.logVals, xeon_keys), "instructions:k")
usercycles1_xeon = extractKVFromMap(extractMapFromMap(intel_xeon_throughput_sw.logVals, xeon_keys), "cycles:u")
kerncycles1_xeon = extractKVFromMap(extractMapFromMap(intel_xeon_throughput_sw.logVals, xeon_keys), "cycles:k")
#instr1_xeon = []
#cycles1_xeon = []
ipc1_xeon = []
for k, v in userinstr1_xeon.items():
    instr = userinstr1_xeon[k] + kerninstr1_xeon[k]
    cycles = usercycles1_xeon[k] + kerncycles1_xeon[k]
    ipc1_xeon.append(instr/cycles)

xeon_keys = ["65536 keys", "512 conns", "8 threads"]
userinstr2_xeon = extractKVFromMap(extractMapFromMap(intel_xeon_throughput_sw.logVals, xeon_keys), "instructions:u")
kerninstr2_xeon = extractKVFromMap(extractMapFromMap(intel_xeon_throughput_sw.logVals, xeon_keys), "instructions:k")
usercycles2_xeon = extractKVFromMap(extractMapFromMap(intel_xeon_throughput_sw.logVals, xeon_keys), "cycles:u")
kerncycles2_xeon = extractKVFromMap(extractMapFromMap(intel_xeon_throughput_sw.logVals, xeon_keys), "cycles:k")
#instr2_xeon = []
#cycles2_xeon = []
ipc2_xeon = []
for k, v in userinstr2_xeon.items():
    instr = userinstr2_xeon[k] + kerninstr2_xeon[k]
    cycles = usercycles2_xeon[k] + kerncycles2_xeon[k]
    ipc2_xeon.append(instr/cycles)

plt.figure()
plt.title("IPC with varying RPS")
plt.plot([int(k.replace(" rps",'')) for k in rps2_xeon.keys()], ipc1_xeon, label='1')
plt.plot([int(k.replace(" rps",'')) for k in rps2_xeon.keys()], ipc2_xeon, label='2')
plt.legend()
plt.xlabel("RPS")
plt.ylabel("Outstanding Requests")
plt.show()




################################################################################
# User/Kernel instructions, cycles, Dynamic instruction count

# Intel x86 system 1    : x
# Intel x86 system 2    : 
# Arm Cavium            : N/A                   Cannot count kernel nor total instructions
# Amazon EC2 A1         : x

################################################################################
intel_InstrMix = Benchmark(
    "Instructions Stack",
    ["instructions:k", "cycles:k", "instructions:u", "cycles:u", "instructions"])
intel_InstrMix.decodeLog(LOGDIR + "instructions-stack.sh.intel.xeon.log")

arm_amazon_InstrMix = Benchmark(
    "Instructions Stack",
    ["instructions:k", "cycles:k", "instructions:u", "cycles:u", "instructions"])
arm_amazon_InstrMix.decodeLog(LOGDIR + "instructions-stack.sh.arm.amazon.log")

############################### Data Extraction ################################
connections = []

x86_connections = []
x86_user_i_ratio = []
x86_kernel_i_ratio = []
x86_user_c_ratio = []
x86_kernel_c_ratio = []
x86_instr = []
for k, v in intel_InstrMix.logVals['4096 keys'].items():
    if "conncetions" in k:
        appendIfNotInlist(x86_connections, k.split()[0])
        kernel_i = v['instructions:k']
        user_i = v['instructions:u']
        kernel_c = v['cycles:k']
        user_c = v['cycles:u']
        i_tot = kernel_i + user_i
        c_tot = kernel_c + user_c
        x86_instr.append(i_tot)

        x86_user_i_ratio.append((user_i / i_tot) * 100)
        x86_kernel_i_ratio.append((kernel_i / i_tot) * 100)
        x86_user_c_ratio.append((user_c / c_tot) * 100)
        x86_kernel_c_ratio.append((kernel_c / c_tot) * 100)

arm_amazon_connections = []
arm_amazon_user_i_ratio = []
arm_amazon_kernel_i_ratio = []
arm_amazon_user_c_ratio = []
arm_amazon_kernel_c_ratio = []
arm_amazon_instr = []

for k, v in arm_amazon_InstrMix.logVals['4096 keys'].items():
    if "conncetions" in k:
        appendIfNotInlist(arm_amazon_connections, k.split()[0])
        kernel_i = v['instructions:k']
        user_i = v['instructions:u']
        kernel_c = v['cycles:k']
        user_c = v['cycles:u']
        arm_amazon_instr.append(v['instructions'])
        i_tot = kernel_i + user_i
        c_tot = kernel_c + user_c

        arm_amazon_user_i_ratio.append((user_i / i_tot) * 100)
        arm_amazon_kernel_i_ratio.append((kernel_i / i_tot) * 100)
        arm_amazon_user_c_ratio.append((user_c / c_tot) * 100)
        arm_amazon_kernel_c_ratio.append((kernel_c / c_tot) * 100)

################################### Plotting ###################################
plt.figure()
title = "Kernel vs. Total Instruction Ratio @ 4096 Keys, Varying Connections"
plt.plot(x86_kernel_i_ratio, label="User, Intel (Xeon)")
plt.plot(arm_amazon_kernel_i_ratio, label="User, ARM (Graviton)")
plt.ylabel("[%]")
plt.legend()
# plt.twinx()
# plt.plot(x86_kernel_i_ratio, label="Kernel, Intel", color="orange")
# plt.plot(arm_amazon_kernel_i_ratio, label="Kernel, ARM (Graviton)", color="orange")
#plt.ylabel("Kernel instr / Instr tot [%]")
plt.xticks(range(len(arm_amazon_connections)), arm_amazon_connections, rotation=20)
plt.xlabel("Connections")
plt.legend()
plt.title(title)
plt.tight_layout()
plt.savefig(OUTDIR + title.replace(' ','_').replace(',','').replace('.','') + ".pdf")
if SHOW_PLOTS:
    plt.show()

plt.figure()
plt.plot(x86_instr, label="x86 (Xeon)")
plt.plot(arm_amazon_instr, label="ARM (Graviton)")
plt.xticks(range(len(arm_amazon_connections)), arm_amazon_connections, rotation=20)
plt.ylabel("[%]")
plt.xlabel("Connections")
plt.legend()
title = "Dynamic Instruction Count"
plt.title(title)
plt.tight_layout()
plt.savefig(OUTDIR + title.replace(' ','_').replace(',','').replace('.','') + ".pdf")
if SHOW_PLOTS:
    plt.show()

## Ratio stackplot
#plt.subplot(2,2,2)
#plt.stackplot(range(len(user_i_ratio)), x86_user_i_ratio, x86_kernel_i_ratio, labels=["User", "Kernel"])
#plt.ylabel("Instructions")
#plt.legend()
#
#plt.xticks(range(len(connections)), connections)
#plt.xlabel("Keys")
#plt.legend()

## Cycle ratio
#plt.subplot(2,2,3)
#plt.plot(x86_user_c_ratio, label="User, Intel")
#plt.plot(arm_amazon_user_c_ratio, label="User, ARM (Graviton)")
#plt.ylabel("User cycles per total cycles [%]")
#plt.legend()
#plt.twinx()
#plt.plot(x86_kernel_c_ratio, label="Kernel, Intel", color="orange")
#plt.plot(arm_amazon_kernel_c_ratio, label="Kernel, ARM (Graviton)", color="orange")
#plt.xticks(range(len(arm_amazon_connections)), arm_amazon_connections)
#plt.ylabel("Kernel cycles per total cycles [%]")
#plt.xlabel("Keys")
#plt.legend()



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
intel_branchPredictor.decodeLog(LOGDIR + "branch_predictor.sh.intel.xeon.log")

arm_cavium_branchPredictor = Benchmark(
    "Branch predictor",
    ["armv8_pmuv3_0/br_mis_pred/:u", "armv8_pmuv3_0/br_pred/:u", "instructions:u"])
arm_cavium_branchPredictor.decodeLog(LOGDIR + "branch_predictor.sh.arm.cavium.log")

arm_amazon_branchPredictor = Benchmark(
    "Branch predictor",
    ["armv8_pmuv3_0/br_mis_pred/", "armv8_pmuv3_0/br_pred/", "instructions"])
arm_amazon_branchPredictor.decodeLog(LOGDIR + "branch_predictor.sh.arm.amazon.log")

############################### Data Extraction ################################
# 4096 keys, varying connections
# Branch misses
connections = []
x86_br_hit = []
x86_br_mix = []
for k, v in intel_branchPredictor.logVals['4096 keys'].items():
    if "conncetions" in k:
        appendIfNotInlist(connections, k)
        missRatio = (1 - v['branch-misses'] / v['branch-instructions']) * 100 
        brRatio = (v['branch-instructions'] / v['instructions']) * 100
        x86_br_hit.append(missRatio)
        x86_br_mix.append(brRatio)

arm_cavium_br_hit = []
arm_cavium_br_mix = []
for k, v in arm_cavium_branchPredictor.logVals['4096 keys'].items():
    if "conncetions" in k:
        appendIfNotInlist(connections, k)
        miss = v['armv8_pmuv3_0/br_mis_pred/:u']
        predict = v['armv8_pmuv3_0/br_pred/:u']
        total = miss + predict
        missRatio = (1 - miss / total) * 100 
        brRatio = (total / v['instructions:u']) * 100
        arm_cavium_br_hit.append(missRatio)
        arm_cavium_br_mix.append(brRatio)

arm_amazon_br_hit = []
arm_amazon_br_mix = []
for k, v in arm_amazon_branchPredictor.logVals['4096 keys'].items():
    if "conncetions" in k:
        appendIfNotInlist(connections, k)
        miss = v['armv8_pmuv3_0/br_mis_pred/']
        predict = v['armv8_pmuv3_0/br_pred/']
        total = miss + predict
        missRatio = (1 - miss / total) * 100 
        brRatio = (total / v['instructions']) * 100
        arm_amazon_br_hit.append(missRatio)
        arm_amazon_br_mix.append(brRatio)


# Just show the number of connections (Format of key is: "# connections")
connections = [x.split(' ')[0] for x in connections]

################################### Plotting ###################################
plt.figure()
plt.plot(x86_br_hit, label="x86 (Xeon)")
plt.plot(arm_cavium_br_hit, label="ARM (Cavium)")
plt.plot(arm_amazon_br_hit, label="ARM (Graviton)")
plt.xticks(range(len(connections)), connections, rotation=20)
plt.ylabel("[%]")
plt.xlabel("Connections")
plt.legend()
title = "Branch Hit Rate"
plt.title(title)
plt.tight_layout()
plt.savefig(OUTDIR + title.replace(' ','_').replace(',','').replace('.','') + ".pdf")
if SHOW_PLOTS:
    plt.show()

# Branch instruction mix
plt.figure()
plt.plot(x86_br_mix, label="x86 (Xeon)")
plt.plot(arm_cavium_br_mix, label="ARM (Cavium)")
plt.plot(arm_amazon_br_mix, label="ARM (Graviton)")
plt.xticks(range(len(connections)), connections,rotation=20)
plt.ylabel("[%]")
plt.xlabel("Connections")
plt.legend()
title = "Branch Instruction Density"
plt.title(title)
plt.tight_layout()
plt.savefig(OUTDIR + title.replace(' ','_').replace(',','').replace('.','') + ".pdf")
if SHOW_PLOTS:
    plt.show()





################################################################################
# L1I Cache
# Intel x86 system 1    : x
# Intel x86 system 2    : 
# Arm Cavium            : x
# Amazon EC2 A1         : x
################################################################################
intel_L1icache = Benchmark(
    "L1 cache",
    ["L1-icache-load-misses", "icache.hit", "instructions"])
intel_L1icache.decodeLog(LOGDIR + "l1i_cache.sh.intel.xeon.log")

arm_cavium_L1icache = Benchmark(
    "L1I cache",
    ["armv8_pmuv3_0/l1i_cache_refill/:u", "armv8_pmuv3_0/l1i_cache/:u", "instructions:u"])
arm_cavium_L1icache.decodeLog(LOGDIR + "l1i_cache.sh.arm.cavium.log")

arm_amazon_L1icache = Benchmark(
    "L1I cache",
    ["armv8_pmuv3_0/l1i_cache_refill/", "armv8_pmuv3_0/l1i_cache/", "instructions"])
arm_amazon_L1icache.decodeLog(LOGDIR + "l1i_cache.sh.arm.amazon.log")

############################### Data Extraction ################################
connections = []
keys = []
x86_xeon_hitrate_varkeys = []
x86_xeon_hitrate_varconn = []
for k, v in intel_L1icache.logVals.items():
    if "keys" in k:
        # Varying keys
        appendIfNotInlist(keys, k.split()[0])
        hits = v['icache.hit']
        misses = v['L1-icache-load-misses']
        total = hits + misses
        hitRatio = (hits / total) * 100 
        x86_xeon_hitrate_varkeys.append(hitRatio)
    if k == '4096 keys':
        # Varying connections, stored as nested dictionaries
        for i, j in v.items():
            if(type(j) is dict):
                appendIfNotInlist(connections, i.split()[0])
                hits = j['icache.hit']
                misses = j['L1-icache-load-misses']
                total = hits + misses
                hitRatio = (hits / total) * 100 
                x86_xeon_hitrate_varconn.append(hitRatio)

arm_cavium_hitrate_varkeys = []
arm_cavium_hitrate_varconn = []
for k, v in arm_cavium_L1icache.logVals.items():
    if "keys" in k:
        # Varying keys
        appendIfNotInlist(keys, k.split()[0])
        ratio = (1 - (v['armv8_pmuv3_0/l1i_cache_refill/:u'] / v['armv8_pmuv3_0/l1i_cache/:u'])) * 100 
        arm_cavium_hitrate_varkeys.append(ratio)
    
    if k == '4096 keys':
        # Varying connections, stored as nested dictionaries
        for i, j in v.items():
            if(type(j) is dict):
                appendIfNotInlist(connections, i.split()[0])
                ratio = (1 - (j['armv8_pmuv3_0/l1i_cache_refill/:u'] / j['armv8_pmuv3_0/l1i_cache/:u'])) * 100 
                arm_cavium_hitrate_varconn.append(ratio)

arm_amazon_hitrate_varkeys = []
arm_amazon_hitrate_varconn = []
for k, v in arm_amazon_L1icache.logVals.items():
    if "keys" in k:
        # Varying keys
        appendIfNotInlist(keys, k.split()[0])
        ratio = (1 - (v['armv8_pmuv3_0/l1i_cache_refill/'] / v['armv8_pmuv3_0/l1i_cache/'])) * 100 
        arm_amazon_hitrate_varkeys.append(ratio)
    
    if k == '4096 keys':
        # Varying connections, stored as nested dictionaries
        for i, j in v.items():
            if(type(j) is dict):
                appendIfNotInlist(connections, i.split()[0])
                ratio = (1 - (j['armv8_pmuv3_0/l1i_cache_refill/'] / j['armv8_pmuv3_0/l1i_cache/'])) * 100 
                arm_amazon_hitrate_varconn.append(ratio)

################################### Plotting ###################################

# Varying keys
plt.figure()
plt.plot(x86_xeon_hitrate_varkeys, label="x86 (Xeon)")
plt.plot(arm_amazon_hitrate_varkeys, label="x86 (Amazon)")
plt.plot(arm_cavium_hitrate_varkeys, label="x86 (Cavium)")
plt.xticks(range(len(connections)), connections, rotation=20)
plt.title(title)
plt.ylabel("L1I Hit Ratio [%]")
plt.xlabel("Connections")
plt.legend()
title = "L1I Cache"
plt.title(title)
plt.tight_layout()
plt.savefig(OUTDIR + title.replace(' ','_').replace(',','').replace('.','') + ".pdf")
if SHOW_PLOTS:
    plt.show()

# Varying connections
plt.figure()
plt.plot(x86_xeon_hitrate_varconn, label="x86 (Xeon)")
plt.plot(arm_amazon_hitrate_varconn, label="x86 (Amazon)")
plt.plot(arm_cavium_hitrate_varconn, label="x86 (Cavium)")
plt.xticks(range(len(connections)), connections, rotation=20)
plt.title(title)
plt.ylabel("L1I Hit Ratio [%]")
plt.xlabel("Connections")
plt.legend()
title = "L1I Cache"
plt.title(title)
plt.tight_layout()
plt.savefig(OUTDIR + title.replace(' ','_').replace(',','').replace('.','') + ".pdf")
if SHOW_PLOTS:
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
intel_L1dcache.decodeLog(LOGDIR + "l1d_cache.sh.intel.xeon.log")

arm_cavium_L1dcache = Benchmark(
    "L1D cache",
    ["L1-dcache-load-misses:u", "L1-dcache-loads:u", "instructions"])
arm_cavium_L1dcache.decodeLog(LOGDIR + "l1d_cache.sh.arm.cavium.log")

arm_amazon_L1dcache = Benchmark(
    "L1D cache",
    ["L1-dcache-load-misses", "L1-dcache-loads", "instructions"])
arm_amazon_L1dcache.decodeLog(LOGDIR + "l1d_cache.sh.arm.amazon.log")


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

# Arm amazon
arm_amazon_l1d_hitrate_varyingkeys = []
arm_amazon_l1d_hitrate_4096_connections = []
for k, v in arm_amazon_L1dcache.logVals.items():
    if "keys" in k:
        # Varying keys
        appendIfNotInlist(keys, k.split()[0])
        hitratio = (1 - (v['L1-dcache-load-misses'] / v['L1-dcache-loads'])) * 100 
        arm_amazon_l1d_hitrate_varyingkeys.append(hitratio)
    
    if k == '4096 keys':
        # Varying connections, stored as nested dictionaries
        for i, j in v.items():
            if(type(j) is dict):
                appendIfNotInlist(connections, i.split()[0])
                arm_amazon_l1d_hitrate_4096_connections.append(hitratio)
                hitratio = (1 - (j['L1-dcache-load-misses'] / j['L1-dcache-loads'])) * 100 


# x86
x86_l1d_hitrate_varyingkeys = []
x86_l1d_hitrate_4096_connections = []
for k, v in intel_L1dcache.logVals.items():
    if "keys" in k:
        # Varying keys
        appendIfNotInlist(keys, k.split()[0])
        hitratio = (1 - (v['L1-dcache-load-misses'] / v['L1-dcache-loads'])) * 100 
        x86_l1d_hitrate_varyingkeys.append(hitratio),
    
    if k == '4096 keys':
        # Varying connections, stored as nested dictionaries
        for i, j in v.items():
            if(type(j) is dict):
                appendIfNotInlist(connections, i.split()[0])
                hitratio = (1 - (j['L1-dcache-load-misses'] / j['L1-dcache-loads'])) * 100 
                x86_l1d_hitrate_4096_connections.append(hitratio)

################################### Plotting ###################################
# Varying key size
plt.figure()
plt.plot(x86_l1d_hitrate_varyingkeys, label="x86 (Xeon)")
plt.plot(arm_cavium_l1d_hitrate_varyingkeys, label="ARM (Cavium)")
plt.plot(arm_amazon_l1d_hitrate_varyingkeys, label="ARM (Graviton)")
plt.xticks(range(len(keys)), keys, rotation=20)
plt.title("L1D Hit Rate With Varying Keys")
plt.ylabel("[%]")
plt.xlabel("Keys")
plt.legend()
title = "L1D Hit Rate with varying key and connection count"
plt.title(title)
plt.tight_layout()
plt.savefig(OUTDIR + title.replace(' ','_').replace(',','').replace('.','') + ".pdf")
if SHOW_PLOTS:
    plt.show()

# Varying connections
plt.figure()
plt.plot(x86_l1d_hitrate_4096_connections, label="x86 (Xeon)")
plt.plot(arm_cavium_l1d_hitrate_4096_connections, label="ARM (Cavium)")
plt.plot(arm_amazon_l1d_hitrate_4096_connections, label="ARM (Graviton)")
plt.xticks(range(len(connections)), connections, rotation=20)
plt.xlabel("Connections")
plt.ylabel("[%]")
plt.legend()
title = "L1D Hit Rate @ 4096 Keys, Varying Connections"
plt.title(title)
plt.tight_layout()
plt.savefig(OUTDIR + title.replace(' ','_').replace(',','').replace('.','') + ".pdf")
if SHOW_PLOTS:
    plt.show()





################################################################################
# L2D Cache
# Intel x86 system 1    : 
# Intel x86 system 2    : 
# Arm Cavium            : x
# Amazon EC2 A1         : x
################################################################################

arm_cavium_L2dcache = Benchmark(
    "L2D cache",
    ["armv8_pmuv3_0/l2d_cache/:u", "armv8_pmuv3_0/l2d_cache_refill/:u", "instructions"])
arm_cavium_L2dcache.decodeLog(LOGDIR + "l2d_cache.sh.arm.cavium.log")

arm_amazon_L2dcache = Benchmark(
    "L2D cache",
    ["armv8_pmuv3_0/l2d_cache/", "armv8_pmuv3_0/l2d_cache_refill/", "instructions"])
arm_amazon_L2dcache.decodeLog(LOGDIR + "l2d_cache.sh.arm.amazon.log")

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

arm_amazon_refillRatio_var_keys = []
arm_amazon_refillRatio_var_conn = []
for k, v in arm_amazon_L2dcache.logVals.items():
    if "keys" in k:
        # Varying keys
        appendIfNotInlist(keys, k.split()[0])
        ratio = (1 - (v['armv8_pmuv3_0/l2d_cache_refill/'] / v['armv8_pmuv3_0/l2d_cache/'])) * 100 
        arm_amazon_refillRatio_var_keys.append(ratio)
    
    if k == '4096 keys':
        # Varying connections, stored as nested dictionaries
        for i, j in v.items():
            if(type(j) is dict):
                appendIfNotInlist(connections, i.split()[0])
                ratio = (1 - (j['armv8_pmuv3_0/l2d_cache_refill/'] / j['armv8_pmuv3_0/l2d_cache/'])) * 100 
                arm_amazon_refillRatio_var_conn.append(ratio)


################################### Plotting ###################################
# Varying key size
plt.figure()
plt.plot(arm_cavium_refillRatio_var_keys, label="Arm (Cavium)")
plt.plot(arm_amazon_refillRatio_var_keys, label="Arm (Amazon)")
plt.xticks(range(len(keys)), keys, rotation=20)
plt.ylabel("[%]")
plt.xlabel("Keys")
plt.legend()
title = "L2D Hit Ratio with Varying Keys"
plt.title(title)
plt.tight_layout()
plt.savefig(OUTDIR + title.replace(' ','_').replace(',','').replace('.','') + ".pdf")
if SHOW_PLOTS:
    plt.show()

# Varying connections
plt.figure()
plt.plot(arm_cavium_refillRatio_var_conn, label="Arm (Cavium)")
plt.plot(arm_amazon_refillRatio_var_conn, label="Arm (Amazon)")
plt.xticks(range(len(connections)), connections, rotation=20)
plt.ylabel("[%]")
plt.xlabel("Connections")
plt.legend()
title = "L2D Hit Ratio @ 4096 Keys, Varying Connections"
plt.title(title)
plt.tight_layout()
plt.savefig(OUTDIR + title.replace(' ','_').replace(',','').replace('.','') + ".pdf")
if SHOW_PLOTS:
    plt.show()




################################################################################
# LLC Cache
# Intel x86 system 1    : x
# Intel x86 system 2    : 
# Arm Cavium            : N/A                   No performance counters for LLC
# Amazon EC2 A1         : N/A                   No performance counters for LLC
################################################################################
intel_LLCcache = Benchmark(
    "LLC cache",
    ["LLC-loads", "LLC-load-misses"])
intel_LLCcache.decodeLog(LOGDIR + "llc.sh.intel.xeon.log")

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
plt.figure()
plt.plot(VarKeysHitRatio, label="x86 (Xeon)")
plt.xticks(range(len(keys)), keys, rotation = 20)
plt.ylabel("[%]")
plt.xlabel("Keys")
plt.legend()
title = "LLC Hit Ratio With Varying Key Size"
plt.title(title)
plt.tight_layout()
plt.savefig(OUTDIR + title.replace(' ','_').replace(',','').replace('.','') + ".pdf")
if SHOW_PLOTS:
    plt.show()

# Varying connections
plt.figure()
plt.plot(VarConnHitRatio, label="x86 (Xeon)")
plt.xticks(range(len(connections)), connections,rotation=20)
plt.ylabel("[%]")
plt.xlabel("Connections")
plt.legend()
title = "LLC Hit Ratio @ 4096 Keys, Varying Connections"
plt.title(title)
plt.tight_layout()
plt.savefig(OUTDIR + title.replace(' ','_').replace(',','').replace('.','') + ".pdf")
if SHOW_PLOTS:
    plt.show()
