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
        Benchmark("==> Bench:", ["instructions:u"], endString=endString)
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
    rps1_cavium_rps_keys, rps1_cavium_rps_values = read_logs("arm-throughput-smt-sensitivity/arm.cavium.test.{ways}way.throughput.log.{{}}".format(ways=ways),
                                                             endString="Ran for ",
                                                             n=5,
                                                             searchKeys=rps1_cavium_keys)

    avg_cavium = np.mean(rps1_cavium_rps_values, axis=0)

    return rps1_cavium_rps_keys, avg_cavium

################################################################################
# ARM throughput 
################################################################################

keys, avg_cavium_1way = read_arm_throughput_for_ways(1)
keys, avg_cavium_2way = read_arm_throughput_for_ways(2)
keys, avg_cavium_3way = read_arm_throughput_for_ways(3)
keys, avg_cavium_4way = read_arm_throughput_for_ways(4)

plt.figure(figsize=(9, 6))
plt.title("Average Total Outstanding Client Requests, ARM (Cavium)")
#plt.plot([int(k.replace(" rps",'')) for k in rps1_cavium_keys], list(rps1_cavium.values()), linestyle="--", label=', '.join(rps1_cavium_keys), color="black")
plt.semilogy(sorted([int(k.replace(" rps",'')) for k in keys]), avg_cavium_1way, label='1 way', linestyle="-", color="red")
plt.semilogy(sorted([int(k.replace(" rps",'')) for k in keys]), avg_cavium_2way, label='2 way', linestyle="-", color="blue")
plt.semilogy(sorted([int(k.replace(" rps",'')) for k in keys]), avg_cavium_3way, label='3 way', linestyle="-", color="green")
plt.semilogy(sorted([int(k.replace(" rps",'')) for k in keys]), avg_cavium_4way, label='4 way', linestyle="-", color="black")
plt.legend()
plt.xlabel("RPS")
plt.ylabel("Outstanding Requests")
plt.savefig(OUTDIR + "throughputCaviumNWay.pdf")
plt.show()
