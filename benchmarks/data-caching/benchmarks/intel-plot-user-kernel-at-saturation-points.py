import matplotlib
import matplotlib.pyplot as plt
import os
from scipy.stats import hmean

from systemconstants import *
from benchmarkdata import *
from decodedlogs import *


def get_average_value_for_key_in_logs(benchmarks, keys, conns, threads, rps, metric):
    print(benchmarks[1].logVals.keys())
    return np.mean([
        l.logVals[keys][conns][threads][rps][metric]
        for l in benchmarks[1:]
    ])


kernel_user_instruction_logs = [
    Benchmark(
        "==> Bench:",
        ["instructions:u", "instructions:k"]
    )
    for i in range(0, 5)
]

for i in range(0, 5):
    kernel_user_instruction_logs[i].decodeLog(os.path.join("logs", "intel-at-max-throughput", "intel.throughput.sw.log.{}".format(i + 1)))

user_instructions = np.array([
    l.logVals["65536 keys"]["512 conns"]["4 threads"]["115000 rps"]["instructions:u"]
    for l in kernel_user_instruction_logs
])

kernel_instructions = np.array([
    l.logVals["65536 keys"]["512 conns"]["4 threads"]["115000 rps"]["instructions:k"]
    for l in kernel_user_instruction_logs
])

kernel_instructions_share = (kernel_instructions / (user_instructions + kernel_instructions)).mean()
kernel_instructions_share_var = (kernel_instructions / (user_instructions + kernel_instructions)).std()

print((kernel_instructions / (user_instructions + kernel_instructions)))

print(r"Spending {:.2f} ± {:.2f}% of time in the kernel".format(kernel_instructions_share * 100, kernel_instructions_share_var * 100))
