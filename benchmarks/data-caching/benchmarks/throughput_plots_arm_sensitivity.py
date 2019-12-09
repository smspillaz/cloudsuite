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


def read_arm_throughput_for_ways(ways):
    arm_cavium_throughput = [
        Benchmark("==> Bench:", ["instructions:u"], endString="Ran for ")
        for i in range(5)
    ]
    rps1_cavium_keys = ["65536 keys", "512 conns", "8 threads"]
    rps1_cavium_rps_keys, rps1_cavium_rps_values = read_logs("arm-cavium-test-nway-throughput-prec/arm.cavium.test.{ways}way.throughput.log.{{}}".format(ways=ways),
                                                             endString=None,
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

cavium_1way_keys, avg_cavium_1way, std_cavium_1way = read_arm_throughput_for_ways(1)
cavium_2way_keys, avg_cavium_2way, std_cavium_2way = read_arm_throughput_for_ways(2)
cavium_3way_keys, avg_cavium_3way, std_cavium_3way = read_arm_throughput_for_ways(3)
cavium_4way_keys, avg_cavium_4way, std_cavium_4way = read_arm_throughput_for_ways(4)

cavium_1way_int_keys = np.array(sorted([int(k.replace(" rps",'')) for k in cavium_1way_keys]))
cavium_2way_int_keys = np.array(sorted([int(k.replace(" rps",'')) for k in cavium_2way_keys]))
cavium_3way_int_keys = np.array(sorted([int(k.replace(" rps",'')) for k in cavium_3way_keys]))
cavium_4way_int_keys = np.array(sorted([int(k.replace(" rps",'')) for k in cavium_4way_keys]))

cavium_smt_breakpoint1 = find_breakpoint(cavium_1way_int_keys, avg_cavium_1way, y_top=200)
cavium_smt_breakpoint2 = find_breakpoint(cavium_2way_int_keys, avg_cavium_2way, y_top=200)
cavium_smt_breakpoint3 = find_breakpoint(cavium_3way_int_keys, avg_cavium_3way, y_top=200)
cavium_smt_breakpoint4 = find_breakpoint(cavium_4way_int_keys, avg_cavium_4way, y_top=200)

plt.figure(figsize=(9, 6))
plt.title("Average Total Outstanding Client Requests, ARM (Cavium)")
plot_with_variance(cavium_1way_int_keys, avg_cavium_1way, std_cavium_1way, cavium_smt_breakpoint1, linestyle="--", label="1 way", color="red", n=20)
plot_with_variance(cavium_2way_int_keys, avg_cavium_2way, std_cavium_2way, cavium_smt_breakpoint1, linestyle="--", label="2 way", color="green", n=20)
plot_with_variance(cavium_3way_int_keys, avg_cavium_3way, std_cavium_3way, cavium_smt_breakpoint1, linestyle="--", label="3 way", color="blue", n=20)
plot_with_variance(cavium_4way_int_keys, avg_cavium_4way, std_cavium_4way, cavium_smt_breakpoint1, linestyle="--", label="4 way", color="black", n=25)
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

print(cavium_smt_breakpoints)