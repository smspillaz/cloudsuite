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

def autolabel(rects, ax, suffix):
    """
    Attach a text label above each bar displaying its height
    """
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
                '%d' % int(height) + suffix,
                ha='center', va='bottom')

def read_logs(filename, endString, n, searchKeys):
    arm_cavium_throughput = [
        Benchmark("==> Bench:", ["L1-dcache-load-misses", "L1-dcache-loads" "armv8_pmuv3_0/l2d_cache/", "armv8_pmuv3_0/l2d_cache_refill/"], endString=endString)
        for i in range(n)
    ]
    values = []
    keys = []

    for i, bench in enumerate(arm_cavium_throughput):
        bench.decodeLog(LOGDIR + filename.format(i + 1))
        rps1_cavium = extractKVFromMap(extractMapFromMap(bench.logVals,searchKeys ), "Server queue")
        bench_keys, bench_values = list(zip(*[
            (k, v) for k, v in rps1_cavium.items() if k != "12000 rps"
        ]))
        values.append(bench_values)
        keys = bench_keys

    return keys, np.array(values)


def read_arm_throughput_for_ways(directory, ways, endString=None):
    arm_cavium_throughput = [
        Benchmark("==> Bench:", ["instructions:u"], endString=None)
        for i in range(5)
    ]
    rps1_cavium_keys = ["65536 keys", "512 conns", "8 threads"]
    rps1_cavium_rps_keys, rps1_cavium_rps_values = read_logs(os.path.join(directory, "arm.cavium.test.{ways}way.throughput.log.{{}}".format(ways=ways)),
                                                             endString=endString,
                                                             n=5,
                                                             searchKeys=rps1_cavium_keys)

    avg_cavium = np.mean(rps1_cavium_rps_values, axis=0)
    std_cavium = np.std(rps1_cavium_rps_values, axis=0)

    return rps1_cavium_rps_keys, avg_cavium, std_cavium


def find_breakpoint(x, y, y_top):
    """Find the breapoint where we reached saturation."""
    first_derivative = np.gradient(np.array([y[i] for i in range(len(y)) if y[max(i - 1, 0)] < y_top]))
    second_derivative = np.gradient(first_derivative)

    change_index = np.argmax(second_derivative)

    return x[change_index]


def plot_with_variance(x, y, std, breakpoint, label, linestyle, color, y_top=200, n=None):
    x = x[:n]
    y = y[:n]
    std = std[:n]

    first_derivative = np.gradient(np.array([y[i] for i in range(len(y)) if y[max(i - 1, 0)] < y_top]))
    second_derivative = np.gradient(first_derivative)

    change_index = np.argmax(second_derivative)

    plt.plot(x, y, label=label, linestyle=linestyle, color=color)
    plt.fill_between(x, y + std, y - std, alpha=0.2, facecolor=color)
    plt.axvline(x[change_index], color=color, linestyle="-.")
    plt.ylim(bottom=0, top=y_top)


################################################################################
# ARM throughput 
################################################################################

cavium_1way_keys, avg_cavium_1way, std_cavium_1way = read_arm_throughput_for_ways("arm-throughput-smt-sensitivity", 1, endString="Ran for ")
cavium_2way_keys, avg_cavium_2way, std_cavium_2way = read_arm_throughput_for_ways("arm-throughput-smt-sensitivity", 2, endString="Ran for ")
cavium_3way_keys, avg_cavium_3way, std_cavium_3way = read_arm_throughput_for_ways("arm-throughput-smt-sensitivity", 3, endString="Ran for ")
cavium_4way_keys, avg_cavium_4way, std_cavium_4way = read_arm_throughput_for_ways("arm-throughput-smt-sensitivity", 4, endString="Ran for ")

int_keys = np.array(sorted([int(k.replace(" rps",'')) for k in cavium_1way_keys]))

cavium_1way_keys_prec, avg_cavium_1way_prec, std_cavium_1way_prec = read_arm_throughput_for_ways("arm-cavium-test-nway-throughput-prec", 1)
cavium_2way_keys_prec, avg_cavium_2way_prec, std_cavium_2way_prec = read_arm_throughput_for_ways("arm-cavium-test-nway-throughput-prec", 2)
cavium_3way_keys_prec, avg_cavium_3way_prec, std_cavium_3way_prec = read_arm_throughput_for_ways("arm-cavium-test-nway-throughput-prec", 3)
cavium_4way_keys_prec, avg_cavium_4way_prec, std_cavium_4way_prec = read_arm_throughput_for_ways("arm-cavium-test-nway-throughput-prec", 4)

cavium_1way_int_keys_prec = np.array(sorted([int(k.replace(" rps",'')) for k in cavium_1way_keys_prec]))
cavium_2way_int_keys_prec = np.array(sorted([int(k.replace(" rps",'')) for k in cavium_2way_keys_prec]))
cavium_3way_int_keys_prec = np.array(sorted([int(k.replace(" rps",'')) for k in cavium_3way_keys_prec]))
cavium_4way_int_keys_prec = np.array(sorted([int(k.replace(" rps",'')) for k in cavium_4way_keys_prec]))

cavium_smt_breakpoint1 = find_breakpoint(cavium_1way_int_keys_prec, avg_cavium_1way_prec, y_top=200)
cavium_smt_breakpoint2 = find_breakpoint(cavium_2way_int_keys_prec, avg_cavium_2way_prec, y_top=200)
cavium_smt_breakpoint3 = find_breakpoint(cavium_3way_int_keys_prec, avg_cavium_3way_prec, y_top=200)
cavium_smt_breakpoint4 = find_breakpoint(cavium_4way_int_keys_prec, avg_cavium_4way_prec, y_top=200)

plt.figure(figsize=(9, 6))
plt.title("Average Total Outstanding Client Requests, ARM (Cavium)")
plot_with_variance(cavium_1way_int_keys, avg_cavium_1way, std_cavium_1way, cavium_smt_breakpoint1, linestyle="-", label="1 way", color="C0", n=20)
plot_with_variance(cavium_2way_int_keys, avg_cavium_2way, std_cavium_2way, cavium_smt_breakpoint1, linestyle="-", label="2 way", color="C1", n=20)
plot_with_variance(cavium_3way_int_keys, avg_cavium_3way, std_cavium_3way, cavium_smt_breakpoint1, linestyle="-", label="3 way", color="C2", n=20)
plot_with_variance(cavium_4way_int_keys, avg_cavium_4way, std_cavium_4way, cavium_smt_breakpoint1, linestyle="-", label="4 way", color="C3", n=25)

plt.legend()
plt.xlabel("RPS")
plt.ylabel("Outstanding Requests")
plt.savefig(OUTDIR + "throughputCaviumNWay.pdf")
plt.show()

cavium_smt_breakpoints = [0, cavium_smt_breakpoint1, cavium_smt_breakpoint2, cavium_smt_breakpoint3, cavium_smt_breakpoint4]
cavium_smt_breakpoints_gains = [cavium_smt_breakpoints[i + 1] - cavium_smt_breakpoints[i] for i in range(len(cavium_smt_breakpoints) -1)]

plt.figure(figsize=(9, 6))
plt.title("Marginal gain with each SMT added, ARM (Cavium)")
plt.plot([1, 2, 3, 4], cavium_smt_breakpoints_gains)
plt.xlabel("SMT")
plt.ylabel("Marginal gain in average RPS")
plt.savefig(OUTDIR + "marginalGainRPSCaviumNWay.pdf")
plt.show()

cavium_smt_breakpoints_gains_percent = [((sum(cavium_smt_breakpoints_gains[0:i+1]) / cavium_smt_breakpoints_gains[0])) * 100 for i, _ in enumerate(cavium_smt_breakpoints_gains)]
SMT_labels = ["1 way", "2 way","3 way","4 way"]
plt.figure(figsize=(9, 6))
plt.title("Relative gain per SMT level, ARM (Cavium)")
bars = plt.bar(np.arange(len(SMT_labels)), cavium_smt_breakpoints_gains_percent, 1, label=SMT_labels,color=["C0", "C1", "C2", "C3"], edgecolor='black')
autolabel(bars, plt, '%')
plt.xlabel("SMT")
plt.ylabel("RPS gain [%]")
plt.xticks(range(len(SMT_labels)), SMT_labels, rotation = 20)
plt.ylim(0,max(cavium_smt_breakpoints_gains_percent)*1.15)
plt.savefig(OUTDIR + "marginalGainRPSCaviumNWayBar.pdf")
plt.show()

print(cavium_smt_breakpoints)

# Show cache sensitivity for each 

CMT1 = "d1 = cache misses, d2 = cache accesses"
CMT2 = "d1 = cach misses, d2 = cache hits"

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


COLORS = ["blue", "orange"]


def plotCacheStats(system, log_directory, loadkeys, misskeys, cachetypes, keys, cmt, ways):
    ################################################################################
    # IPC over a range
    ################################################################################
    loads_keys = None

    def iterate_hit_miss_rates(n, keyset):
        nonlocal loads_keys

        cachebm = Benchmark(
            "==> Bench:",
            ["instructions:u", misskeys[keyset], loadkeys[keyset]])
        cachebm.decodeLog(os.path.join(LOGDIR, log_directory, "arm.cavium.test.{ways}way.throughput.log.{n}".format(n=n + 1, ways=ways)))

        misses1 = extractKVFromMap(extractMapFromMap(cachebm.logVals, keys), misskeys[keyset])
        loads1 = extractKVFromMap(extractMapFromMap(cachebm.logVals, keys), loadkeys[keyset])
        hitrate1 = calculateMissRate(misses1, loads1, cmt)

        loads_keys = list(loads1.keys())

        return hitrate1

    hitrate_matrices = [
        np.array([
            iterate_hit_miss_rates(n, keyset=i) for n in range(5)
        ])
        for i in range(len(loadkeys))
    ]
    hitrate_means = [
        hitrate_matrix.mean(axis=0)
        for hitrate_matrix in hitrate_matrices
    ]
    hitrate_stds = [
        hitrate_matrix.std(axis=0)
        for hitrate_matrix in hitrate_matrices
    ]

    int_keys = [int(k.replace(" rps",'')) for k in loads_keys]

    plt.figure()
    plt.title(system + " cache hit rate with varying RPS ({} ways)".format(ways))
    for i in range(len(loadkeys)):
        plt.plot(int_keys, hitrate_means[i], label=cachetypes[i])
        plt.fill_between(int_keys, hitrate_means[i] + hitrate_stds[i], hitrate_means[i] - hitrate_stds[i], alpha=0.2, facecolor=COLORS[i])
    plt.xlabel("RPS")
    plt.ylabel("[%]")
    plt.legend()
    plt.show()


plotCacheStats(
    "Arm",
    "arm-cavium-test-nway-throughput-prec",
    ["L1-dcache-loads:u", "armv8_pmuv3_0/l2d_cache/:u"], 
    ["L1-dcache-load-misses:u", "armv8_pmuv3_0/l2d_cache_refill/:u"], 
    ["L1D", "L2D"],
    ["65536 keys", "512 conns", "8 threads"],
    CMT1,
    ways=1)


plotCacheStats(
    "Arm",
    "arm-cavium-test-nway-throughput-prec",
    ["L1-dcache-loads:u", "armv8_pmuv3_0/l2d_cache/:u"], 
    ["L1-dcache-load-misses:u", "armv8_pmuv3_0/l2d_cache_refill/:u"], 
    ["L1D", "L2D"],
    ["65536 keys", "512 conns", "8 threads"],
    CMT1,
    ways=2)


plotCacheStats(
    "Arm",
    "arm-cavium-test-nway-throughput-prec",
    ["L1-dcache-loads:u", "armv8_pmuv3_0/l2d_cache/:u"], 
    ["L1-dcache-load-misses:u", "armv8_pmuv3_0/l2d_cache_refill/:u"], 
    ["L1D", "L2D"],
    ["65536 keys", "512 conns", "8 threads"],
    CMT1,
    ways=3)


plotCacheStats(
    "Arm",
    "arm-cavium-test-nway-throughput-prec",
    ["L1-dcache-loads:u", "armv8_pmuv3_0/l2d_cache/:u"], 
    ["L1-dcache-load-misses:u", "armv8_pmuv3_0/l2d_cache_refill/:u"], 
    ["L1D", "L2D"],
    ["65536 keys", "512 conns", "8 threads"],
    CMT1,
    ways=4)
