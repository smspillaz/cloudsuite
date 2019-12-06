import matplotlib
import matplotlib.pyplot as plt
import os

from systemconstants import *
from benchmarkdata import *
from decodedlogs import intel_xeon_max_throughput_br

################################################################################
#                               Configuration                                  #
################################################################################

SHOW_PLOTS = True
LOGDIR = "logs/"
OUTDIR = "plots/"

if not os.path.exists(OUTDIR):
    os.makedirs(OUTDIR)


################################################################################
# Branch hit rate over a range
################################################################################
intel_xeon_throughput_br = Benchmark(
    "==> Bench:",
    ["instructions:u", "branch-misses:u", "branch-instructions:u"])
intel_xeon_throughput_br.decodeLog(LOGDIR + "intel-throughput-2waysmt/intel.throughput.br.log")

xeon_keys = ["65536 keys", "512 conns", "4 threads"]
misses1_xeon = extractKVFromMap(extractMapFromMap(intel_xeon_throughput_br.logVals, xeon_keys), "branch-misses:u")
total1_xeon = extractKVFromMap(extractMapFromMap(intel_xeon_throughput_br.logVals, xeon_keys), "branch-instructions:u")
hitrate1_xeon = []
for k, v in total1_xeon.items():
    misses = misses1_xeon[k]
    total = total1_xeon[k]
    hitrate1_xeon.append((1 - (misses/total)) * 100)

xeon_keys = ["65536 keys", "512 conns", "8 threads"]
misses2_xeon = extractKVFromMap(extractMapFromMap(intel_xeon_throughput_br.logVals, xeon_keys), "branch-misses:u")
total2_xeon = extractKVFromMap(extractMapFromMap(intel_xeon_throughput_br.logVals, xeon_keys), "branch-instructions:u")
hitrate2_xeon = []
for k, v in total2_xeon.items():
    misses = misses2_xeon[k]
    total = total2_xeon[k]
    hitrate2_xeon.append((1 - (misses/total)) * 100)

plt.figure()
plt.title("Xeon branch hit rate with varying RPS")
plt.plot([int(k.replace(" rps",'')) for k in total1_xeon.keys()], hitrate1_xeon, label='4 threads')
plt.plot([int(k.replace(" rps",'')) for k in total2_xeon.keys()], hitrate2_xeon, label='8 threads')
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
        misses = intel_xeon_max_throughput_br.logVals[k][c]["4 threads"]["115000 rps"]["branch-misses:u"]
        loads = intel_xeon_max_throughput_br.logVals[k][c]["4 threads"]["115000 rps"]["branch-instructions:u"]
        toPlotLabels.append(k + ", " + c)
        bar.append((1 - (misses['avg']/loads['avg'])) * 100)
    bars.append(bar)

plt.figure()
x = np.arange(len(bars))
plt.bar(x - width, bars[0], width, label=keys[0])
plt.bar(x,  bars[1], width, label=keys[1])
plt.bar(x + width, bars[2], width, label=keys[2])
plt.ylim(0.98*(min([min(b) for b in bars])),1.02*(max([max(b) for b in bars])))

plt.xticks(range(len(conns)), conns, rotation = 20)
plt.title("Xeon branch hit rate with varying keys, connections @ max throughput")
plt.ylabel("[%]")
plt.legend()
plt.show()


print("Done")
