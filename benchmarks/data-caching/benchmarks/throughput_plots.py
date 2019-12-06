import matplotlib
import matplotlib.pyplot as plt
import os
from systemconstants import *
from benchmarkdata import *

matplotlib.rcParams.update({'font.size': 16})

################################################################################
#                               Configuration                                  #
################################################################################
SHOW_PLOTS = True
LOGDIR = "logs/"

OUTDIR = "plots/"

if not os.path.exists(OUTDIR):
    os.makedirs(OUTDIR)
    
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


plt.figure(figsize=(9, 6))
plt.title("Average Total Outstanding Client Requests (Cavium)")
plt.plot([int(k.replace(" rps",'')) for k in rps1_cavium.keys()], list(rps1_cavium.values()), label=', '.join(rps1_cavium_keys))
plt.plot([int(k.replace(" rps",'')) for k in rps2_cavium.keys()], list(rps2_cavium.values()), label=', '.join(rps2_cavium_keys))
plt.plot([int(k.replace(" rps",'')) for k in rps1_cavium.keys()], avg_cavium, label='Average', linestyle="--", color="b")
plt.legend()
plt.xlabel("RPS")
plt.ylabel("Outstanding Requests")
plt.savefig(OUTDIR + "throughputOverRps_cavium.pdf")
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

plt.figure(figsize=(9, 6))
plt.title("Average Total Outstanding Client Requests (Xeon)")
plt.plot([int(k.replace(" rps",'')) for k in rps1_xeon.keys()], list(rps1_xeon.values()), label=', '.join(rps1_xeon_keys))
plt.plot([int(k.replace(" rps",'')) for k in rps2_xeon.keys()], list(rps2_xeon.values()), label=', '.join(rps2_xeon_keys))
plt.plot([int(k.replace(" rps",'')) for k in rps1_xeon.keys()], avg_xeon, label='Average', linestyle="--", color="b")
plt.legend()
plt.xlabel("RPS")
plt.ylabel("Outstanding Requests")
plt.tight_layout()
plt.savefig(OUTDIR + "throughputOverRps_xeon.pdf")
plt.show()

################################################################################
# Compared average throughput 
################################################################################
plt.figure(figsize=(9, 6))
plt.title("Average Total Outstanding Client Requests")
plt.plot([int(k.replace(" rps",'')) for k in rps2_cavium.keys()], avg_cavium, label='Cavium')
plt.axvline(159000,linestyle='--', color='black')
plt.plot([int(k.replace(" rps",'')) for k in rps2_xeon.keys()], avg_xeon, label='Xeon')
plt.axvline(115000,linestyle='--', color='black')
plt.legend()
plt.xlabel("RPS")
plt.ylabel("Outstanding Requests")
plt.tight_layout()
plt.savefig(OUTDIR + "throughputCombined.pdf")
plt.show()
