import matplotlib
import matplotlib.pyplot as plt
import os

from systemconstants import *
from benchmarkdata import *
from decodedlogs import intel_xeon_max_throughput_l1d, intel_xeon_max_throughput_llc

################################################################################
#                               Configuration                                  #
################################################################################

SHOW_PLOTS = True
LOGDIR = "logs/"
OUTDIR = "plots/"

if not os.path.exists(OUTDIR):
    os.makedirs(OUTDIR)


def plotCacheStats(system, logfile, loadkey, misskey, cachetype, maxtpbm):
    ################################################################################
    # IPC over a range
    ################################################################################
    intel_xeon_throughput_cachebm = Benchmark(
        "==> Bench:",
        ["instructions:u", misskey, loadkey])
    intel_xeon_throughput_cachebm.decodeLog(LOGDIR + logfile)

    xeon_keys = ["65536 keys", "512 conns", "4 threads"]
    misses1_xeon = extractKVFromMap(extractMapFromMap(intel_xeon_throughput_cachebm.logVals, xeon_keys), misskey)
    loads1_xeon = extractKVFromMap(extractMapFromMap(intel_xeon_throughput_cachebm.logVals, xeon_keys), loadkey)
    hitrate1_xeon = []
    for k, v in loads1_xeon.items():
        loads = loads1_xeon[k]
        misses = misses1_xeon[k]
        hitrate1_xeon.append((1 - (misses/loads)) * 100)

    xeon_keys = ["65536 keys", "512 conns", "8 threads"]
    misses2_xeon = extractKVFromMap(extractMapFromMap(intel_xeon_throughput_cachebm.logVals, xeon_keys), misskey)
    loads2_xeon = extractKVFromMap(extractMapFromMap(intel_xeon_throughput_cachebm.logVals, xeon_keys), loadkey)
    hitrate2_xeon = []
    for k, v in loads2_xeon.items():
        loads = loads2_xeon[k]
        misses = misses2_xeon[k]
        hitrate2_xeon.append((1 - (misses/loads)) * 100)

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
            misses = maxtpbm.logVals[k][c]["4 threads"]["115000 rps"][misskey]
            loads = maxtpbm.logVals[k][c]["4 threads"]["115000 rps"][loadkey]
            toPlotLabels.append(k + ", " + c)
            bar.append((1 - (misses['avg']/loads['avg'])) * 100)
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

# LLC
plotCacheStats(
    "Xeon",
    "intel-throughput-2waysmt/intel.throughput.l2.log",
    "LLC-loads", 
    "LLC-load-misses", 
    "LLC",
    intel_xeon_max_throughput_llc)

# L1D
plotCacheStats(
    "Xeon",
    "intel-throughput-2waysmt/intel.throughput.l1.log",
    "L1-dcache-loads", 
    "L1-dcache-load-misses", 
    "L1D",
    intel_xeon_max_throughput_l1d)


print("Done")
