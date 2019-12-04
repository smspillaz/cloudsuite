import matplotlib
import matplotlib.pyplot as plt
import os

from systemconstants import *
from benchmarkdata import *
from decodedlogs import intel_xeon_max_throughput_sw

################################################################################
#                               Configuration                                  #
################################################################################

SHOW_PLOTS = True
LOGDIR = "logs/"
OUTDIR = "plots/"

if not os.path.exists(OUTDIR):
    os.makedirs(OUTDIR)
    

################################################################################
# IPC over a range
################################################################################
intel_xeon_throughput_sw = Benchmark(
    "==> Bench:",
    ["instructions:u", "instructions:k", "cycles:u", "cycles:k"])
intel_xeon_throughput_sw.decodeLog(LOGDIR + "intel-throughput-2waysmt/intel.throughput.sw.log")

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
plt.plot([int(k.replace(" rps",'')) for k in userinstr1_xeon.keys()], ipc1_xeon, label='1')
plt.plot([int(k.replace(" rps",'')) for k in userinstr2_xeon.keys()], ipc2_xeon, label='2')
plt.legend()
plt.xlabel("RPS")
plt.ylabel("Outstanding Requests")
plt.show()

################################################################################
# IPC in sweet spot
################################################################################

xeon_keys = ["65536 keys", "512 conns", "4 threads", ""]

keys = ["16384 keys", "65536 keys", "262114 keys"]
conns = ["256 conns", "512 conns", "1024 conns"]

toPlot = []

for k in keys:
    for c in conns:
        instr_u = intel_xeon_max_throughput_sw.logVals[k][c]["4 threads"]["115000 rps"]["instructions:u"]
        instr_k = intel_xeon_max_throughput_sw.logVals[k][c]["4 threads"]["115000 rps"]["instructions:k"]
        cycles_u = intel_xeon_max_throughput_sw.logVals[k][c]["4 threads"]["115000 rps"]["cycles:u"]
        cycles_k = intel_xeon_max_throughput_sw.logVals[k][c]["4 threads"]["115000 rps"]["cycles:k"]
        ipc_u = instr_u["avg"] / cycles_u["avg"]
        ipc_k = instr_k["avg"] / cycles_k["avg"]

        toPlot.append(([k + ", " + c], {"user" : ipc_u, "kernel" : ipc_k}))

plt.figure()
x = np.arange(len(toPlot))  # the label locations
width = 0.35  # the width of the bars
userIPC = []
kernelIPC = []
labels = []
for p in toPlot:
    labels.append(p[0])
    userIPC.append(p[1]['user'])
    kernelIPC.append(p[1]['kernel'])

plt.bar(x - width/2, userIPC, width, label='User IPC')
plt.bar(x + width/2, kernelIPC, width, label='Kernel IPC')
plt.xticks(range(len(labels)), labels, rotation = 20)
plt.title("Xeon IPC with varying keys, connections w/ max throughput")
plt.ylabel("IPC")
plt.legend()
plt.show()

print("Done")