import matplotlib
import matplotlib.pyplot as plt
import os
from systemconstants import *
from benchmarkdata import *

LOGDIR = "logs/"
OUTDIR = "plots/"

if not os.path.exists(OUTDIR):
    os.makedirs(OUTDIR)

################################################################################
#                Intel at max throughput (repeated tests)                      #
################################################################################
intel_xeon_max_throughput_br = []
intel_xeon_max_throughput_l1d = []
intel_xeon_max_throughput_l1i = []
intel_xeon_max_throughput_llc = []
intel_xeon_max_throughput_sw = []

for i in range(5):
    # branch
    bm = Benchmark(
            "==> Bench:",
            ["instructions:u", "branch-misses:u", "branch-instructions:u"])
    bm.decodeLog(LOGDIR + "intel-at-max-throughput/intel.throughput.br.log." + str(i + 1))
    intel_xeon_max_throughput_br.append(bm)

    # L1d
    bm = Benchmark(
            "==> Bench:",
            ["instructions:u", "L1-dcache-load-misses", "L1-dcache-loads"])
    bm.decodeLog(LOGDIR + "intel-at-max-throughput/intel.throughput.l1.log." + str(i + 1))
    intel_xeon_max_throughput_l1d.append(bm)

    # L1i
    bm = Benchmark(
            "==> Bench:",
            ["instructions:u", "L1-icache-load-misses", "icache.hit:u"])
    bm.decodeLog(LOGDIR + "intel-at-max-throughput/intel.throughput.l1i.log." + str(i + 1))
    intel_xeon_max_throughput_l1i.append(bm)

    # LLC
    bm = Benchmark(
            "==> Bench:",
            ["instructions:u", "LLC-loads", "LLC-load-misses"])
    bm.decodeLog(LOGDIR + "intel-at-max-throughput/intel.throughput.l2.log." + str(i + 1))
    intel_xeon_max_throughput_llc.append(bm)

    # SW
    bm = Benchmark(
            "==> Bench:",
            ["instructions:u", "instructions:k", "cycles:u", "cycles:k"])
    bm.decodeLog(LOGDIR + "intel-at-max-throughput/intel.throughput.sw.log." + str(i + 1))
    intel_xeon_max_throughput_sw.append(bm)

intel_xeon_max_throughput_br = genAvgStdDevForLogVals(intel_xeon_max_throughput_br)
intel_xeon_max_throughput_l1d = genAvgStdDevForLogVals(intel_xeon_max_throughput_l1d)
intel_xeon_max_throughput_l1i = genAvgStdDevForLogVals(intel_xeon_max_throughput_l1i)
intel_xeon_max_throughput_llc = genAvgStdDevForLogVals(intel_xeon_max_throughput_llc)
intel_xeon_max_throughput_sw = genAvgStdDevForLogVals(intel_xeon_max_throughput_sw)

################################################################################
#                Arm cavium at max throughput (repeated tests)                      #
################################################################################
arm_cavium_max_throughput_l1 = []
arm_cavium_max_throughput_llc = []
arm_cavium_max_throughput_sw = []

for i in range(5):
    # L1i / L1d
    bm = Benchmark(
            "==> Bench:",
            ["instructions:u", "L1-dcache-load-misses:u", "L1-dcache-loads:u", "armv8_pmuv3_0/l1i_cache_refill/:u"
            , "armv8_pmuv3_0/l1i_cache/:u"])
    bm.decodeLog(LOGDIR + "arm-at-max-throughput/arm.cavium.throughput.l1.log." + str(i + 1))
    arm_cavium_max_throughput_l1.append(bm)

    # L2d
    bm = Benchmark(
            "==> Bench:",
            ["instructions:u", "armv8_pmuv3_0/l2d_cache_wb/:u", "armv8_pmuv3_0/l2d_cache_refill/:u",
            "armv8_pmuv3_0/l2d_cache_allocate/:u"])
    bm.decodeLog(LOGDIR + "arm-at-max-throughput/arm.cavium.throughput.l2.log." + str(i + 1))
    arm_cavium_max_throughput_llc.append(bm)

    # L2d
    bm = Benchmark(
            "==> Bench:",
            ["instructions:u", "cycles:u", "armv8_pmuv3_0/br_mis_pred/:u",
            "armv8_pmuv3_0/br_pred/:u"])
    bm.decodeLog(LOGDIR + "arm-at-max-throughput/arm.cavium.throughput.sw.log." + str(i + 1))
    arm_cavium_max_throughput_sw.append(bm)

arm_cavium_max_throughput_l1 = genAvgStdDevForLogVals(arm_cavium_max_throughput_l1)
arm_cavium_max_throughput_llc = genAvgStdDevForLogVals(arm_cavium_max_throughput_llc)
arm_cavium_max_throughput_sw = genAvgStdDevForLogVals(arm_cavium_max_throughput_sw)


print("Decoding done")