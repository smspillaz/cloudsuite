import matplotlib
import matplotlib.pyplot as plt
import os

from systemconstants import *
from benchmarkdata import *
from decodedlogs import *

################################################################################
#                               Configuration                                  #
################################################################################

SHOW_PLOTS = True
LOGDIR = "logs/"
OUTDIR = "plots/"

if not os.path.exists(OUTDIR):
    os.makedirs(OUTDIR)

CMT1 = "d1 = cache misses, d2 = cache accesses"
CMT2 = "d1 = cach misses, d2 = cache hits"

matplotlib.rcParams.update({'font.size': 16})

def calculateMissRate(d1, d2, cmt):
    out = []
    if cmt is CMT1:
        for k, v in d1.items():
            loads = d2[k]
            misses = d1[k]
            out.append((1 - (misses/loads)) * 100)
    elif cmt is CMT2:
        for k, v in d1.items():
            hits = d2[k]
            misses = d1[k]
            tot = hits + misses
            out.append((1 - (misses/tot)) * 100)
    return out

def calculateMissRateAvgStd(d1, d2, cmt):
    out = []
    if cmt is CMT1:
        for k, v in d1.items():
            loads = d2[k]
            misses = d1[k]
            out.append((1 - (misses/loads)) * 100)
    elif cmt is CMT2:
        for k, v in d1.items():
            hits = d2[k]
            misses = d1[k]
            tot = hits + misses
            out.append((1 - (misses/tot)) * 100)
    return out



def plotCacheStats(system, logfile, loadkey, misskey, cachetype, maxtpbm, keys, maxtpthreads, maxtprps, cmt):
    ################################################################################
    # IPC over a range
    ################################################################################
    intel_xeon_throughput_cachebm = Benchmark(
        "==> Bench:",
        ["instructions:u", misskey, loadkey])
    intel_xeon_throughput_cachebm.decodeLog(LOGDIR + logfile)

    xeon_keys = keys[0]
    misses1_xeon = extractKVFromMap(extractMapFromMap(intel_xeon_throughput_cachebm.logVals, xeon_keys), misskey)
    loads1_xeon = extractKVFromMap(extractMapFromMap(intel_xeon_throughput_cachebm.logVals, xeon_keys), loadkey)
    hitrate1_xeon = calculateMissRate(misses1_xeon, loads1_xeon, cmt)

    xeon_keys = keys[1]
    misses2_xeon = extractKVFromMap(extractMapFromMap(intel_xeon_throughput_cachebm.logVals, xeon_keys), misskey)
    loads2_xeon = extractKVFromMap(extractMapFromMap(intel_xeon_throughput_cachebm.logVals, xeon_keys), loadkey)
    hitrate2_xeon = calculateMissRate(misses2_xeon, loads2_xeon, cmt)

    plt.figure()
    plt.title(system + " " + cachetype + " Hit rate with varying RPS")
    plt.plot([int(k.replace(" rps",'')) for k in loads1_xeon.keys()], hitrate1_xeon, label='4 threads')
    plt.plot([int(k.replace(" rps",'')) for k in loads2_xeon.keys()], hitrate2_xeon, label='8 threads')
    plt.legend()
    plt.xlabel("RPS")
    plt.ylabel("[%]")
    plt.show()

    ################################################################################
    # IPC in sweet spot
    ################################################################################

    keys = ["16384 keys", "65536 keys", "262114 keys"]
    conns = ["256 conns", "512 conns", "1024 conns"]

    width = 0.25
    toPlotLabels = []
    bars = []
    for c in conns:
        bar = []
        for k in keys:
            if cmt is CMT1:
                misses = maxtpbm.logVals[k][c][maxtpthreads][maxtprps][misskey]
                loads = maxtpbm.logVals[k][c][maxtpthreads][maxtprps][loadkey]
                toPlotLabels.append(k + ", " + c)
                bar.append((1 - (misses['avg']/loads['avg'])) * 100)
            elif cmt is CMT2:
                misses = maxtpbm.logVals[k][c][maxtpthreads][maxtprps][misskey]
                hits = maxtpbm.logVals[k][c][maxtpthreads][maxtprps][loadkey]
                total = misses['avg'] + hits['avg']
                toPlotLabels.append(k + ", " + c)
                bar.append((1 - (misses['avg']/total)) * 100)
        bars.append(bar)

    plt.figure()
    x = np.arange(len(bars))
    plt.bar(x - width, bars[0], width, label=keys[0])
    plt.bar(x,  bars[1], width, label=keys[1])
    plt.bar(x + width, bars[2], width, label=keys[2])
    plt.ylim(0.95*(min([min(b) for b in bars])),1.02*(max([max(b) for b in bars])))

    plt.xticks(range(len(conns)), conns, rotation = 20)
    plt.title(system + " " + cachetype + " Hit Rate with varying keys, connections @ max throughput")
    plt.ylabel("[%]")
    plt.legend()
    plt.show()

xeon_keys = [["65536 keys", "512 conns", "4 threads"], ["65536 keys", "512 conns", "8 threads"]]
arm_keys =  [["65536 keys", "512 conns", "6 threads"], ["65536 keys", "512 conns", "8 threads"]]

# LLC
plotCacheStats(
    "Xeon",
    "intel-throughput-2waysmt/intel.throughput.l2.log",
    "LLC-loads", 
    "LLC-load-misses", 
    "LLC",
    intel_xeon_max_throughput_llc,
    xeon_keys,
    "4 threads",
    "115000 rps",
    CMT1)

"""
plotCacheStats(
    "Arm",
    "arm-throughput-4waysmt/arm.cavium.throughput.l2.log",
    "armv8_pmuv3_0/l1i_cache/:u", 
    "armv8_pmuv3_0/l1i_cache_refill/:u", 
    "L2D",
    arm_cavium_max_throughput_l2,
    arm_keys)
"""



# L1D
plotCacheStats(
    "Xeon",
    "intel-throughput-2waysmt/intel.throughput.l1.log",
    "L1-dcache-loads", 
    "L1-dcache-load-misses", 
    "L1D",
    intel_xeon_max_throughput_l1d,
    xeon_keys,
    "4 threads",
    "115000 rps",
    CMT1)

plotCacheStats(
    "Arm",
    "arm-throughput-4waysmt/arm.cavium.throughput.l1.log",
    "L1-dcache-loads:u", 
    "L1-dcache-load-misses:u", 
    "L1D",
    arm_cavium_max_throughput_l1,
    arm_keys,
    "8 threads",
    "159000 rps",
    CMT1)

# L1I
plotCacheStats(
    "Xeon",
    "intel-throughput-2waysmt/intel.throughput.l1i.log",
    "icache.hit:u", 
    "L1-icache-load-misses", 
    "L1I",
    intel_xeon_max_throughput_l1i,
    xeon_keys,
    "4 threads",
    "115000 rps",
    CMT2)

plotCacheStats(
    "Arm",
    "arm-throughput-4waysmt/arm.cavium.throughput.l1.log",
    "armv8_pmuv3_0/l1i_cache/:u", 
    "armv8_pmuv3_0/l1i_cache_refill/:u", 
    "L1I",
    arm_cavium_max_throughput_l1,
    arm_keys,
    "8 threads",
    "159000 rps",
    CMT1)


print("Done")
