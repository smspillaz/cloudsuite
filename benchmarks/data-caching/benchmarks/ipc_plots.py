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
# Intel IPC over varying RPS
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

keys = ["16384 keys", "65536 keys", "262114 keys"]
conns = ["256 conns", "512 conns", "1024 conns"]

toPlotLabels = []
bars = []
for c in conns:
    bar = []
    for k in keys:
        instr_u = intel_xeon_max_throughput_sw.logVals[k][c]["4 threads"]["115000 rps"]["instructions:u"]
        #instr_k = intel_xeon_max_throughput_sw.logVals[k][c]["4 threads"]["115000 rps"]["instructions:k"]
        cycles_u = intel_xeon_max_throughput_sw.logVals[k][c]["4 threads"]["115000 rps"]["cycles:u"]
        #cycles_k = intel_xeon_max_throughput_sw.logVals[k][c]["4 threads"]["115000 rps"]["cycles:k"]
        ipc_u = instr_u["avg"] / cycles_u["avg"]
        #ipc_k = instr_k["avg"] / cycles_k["avg"]
        toPlotLabels.append(k + ", " + c)
        bar.append(ipc_u)
    bars.append(bar)

plt.figure()
width = 0.25
x = np.arange(len(bars))
plt.bar(x - width, bars[0], width, label=keys[0])
plt.bar(x,  bars[1], width, label=keys[1])
plt.bar(x + width, bars[2], width, label=keys[2])
plt.xticks(range(len(conns)), conns, rotation = 20)
plt.title("Xeon IPC with varying keys, connections @/ max throughput")
plt.ylabel("IPC (User mode)")
plt.ylim(0,0.8)
plt.legend()
plt.show()












################################################################################
# ARM IPC over varying RPS
################################################################################
arm_cavium_throughput_sw = Benchmark(
    "==> Bench:",
    ["instructions:u", "cycles:u"])
arm_cavium_throughput_sw.decodeLog(LOGDIR + "arm-throughput-4waysmt/arm.cavium.throughput.sw.log")

arm_keys = ["65536 keys", "512 conns", "6 threads"]
userinstr1_arm = extractKVFromMap(extractMapFromMap(arm_cavium_throughput_sw.logVals, arm_keys), "instructions:u")
usercycles1_arm = extractKVFromMap(extractMapFromMap(arm_cavium_throughput_sw.logVals, arm_keys), "cycles:u")
ipc1_arm = []
for k, v in userinstr1_arm.items():
    instr = userinstr1_arm[k] + kerninstr1_arm[k]
    cycles = usercycles1_arm[k] + kerncycles1_arm[k]
    ipc1_arm.append(instr/cycles)

arm_keys = ["65536 keys", "512 conns", "8 threads"]
userinstr2_arm = extractKVFromMap(extractMapFromMap(arm_cavium_throughput_sw.logVals, arm_keys), "instructions:u")
usercycles2_arm = extractKVFromMap(extractMapFromMap(arm_cavium_throughput_sw.logVals, arm_keys), "cycles:u")
#instr2_arm = []
#cycles2_arm = []
ipc2_arm = []
for k, v in userinstr2_arm.items():
    instr = userinstr2_arm[k] + kerninstr2_arm[k]
    cycles = usercycles2_arm[k] + kerncycles2_arm[k]
    ipc2_arm.append(instr/cycles)

plt.figure()
plt.title("IPC with varying RPS")
plt.plot([int(k.replace(" rps",'')) for k in userinstr1_arm.keys()], ipc1_arm, label='1')
plt.plot([int(k.replace(" rps",'')) for k in userinstr2_arm.keys()], ipc2_arm, label='2')
plt.legend()
plt.xlabel("RPS")
plt.ylabel("Outstanding Requests")
plt.show()

################################################################################
# IPC in sweet spot
################################################################################

keys = ["16384 keys", "65536 keys", "262114 keys"]
conns = ["256 conns", "512 conns", "1024 conns"]

toPlotLabels = []
bars = []
for c in conns:
    bar = []
    for k in keys:
        instr_u = intel_arm_max_throughput_sw.logVals[k][c]["4 threads"]["115000 rps"]["instructions:u"]
        #instr_k = intel_arm_max_throughput_sw.logVals[k][c]["4 threads"]["115000 rps"]["instructions:k"]
        cycles_u = intel_arm_max_throughput_sw.logVals[k][c]["4 threads"]["115000 rps"]["cycles:u"]
        #cycles_k = intel_arm_max_throughput_sw.logVals[k][c]["4 threads"]["115000 rps"]["cycles:k"]
        ipc_u = instr_u["avg"] / cycles_u["avg"]
        #ipc_k = instr_k["avg"] / cycles_k["avg"]
        toPlotLabels.append(k + ", " + c)
        bar.append(ipc_u)
    bars.append(bar)

plt.figure()
width = 0.25
x = np.arange(len(bars))
plt.bar(x - width, bars[0], width, label=keys[0])
plt.bar(x,  bars[1], width, label=keys[1])
plt.bar(x + width, bars[2], width, label=keys[2])
plt.xticks(range(len(conns)), conns, rotation = 20)
plt.title("arm IPC with varying keys, connections @/ max throughput")
plt.ylabel("IPC (User mode)")
plt.ylim(0,0.8)
plt.legend()
plt.show()











print("Done")
