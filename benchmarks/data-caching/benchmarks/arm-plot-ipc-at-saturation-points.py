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


ways_logs = [
    [
        Benchmark(
            "==> Bench:",
            ["instructions:u", "cycles:u"]
        )
        for i in range(0, 5)
    ] for j in range(0, 4)
]
for j in range(0, 4):
    for i in range(0, 5):
        ways_logs[j][i].decodeLog(os.path.join("logs", "arm-cavium-test-nway-throughput-prec-ipc-single", "arm.cavium.test.{}way.throughput.log.".format(j + 1) + str(i + 1)))

WAYS_RPS = [
    "31500 rps",
    "64500 rps",
    "95550 rps",
    "120000 rps"
]

instructions_ways = np.array([
    [
        l.logVals["65536 keys"]["512 conns"]["8 threads"][WAYS_RPS[i]]["instructions:u"]
        for l in ways_logs[i]
    ]
    for i in range(0, 4)
])

cycles_ways = np.array([
    [
        l.logVals["65536 keys"]["512 conns"]["8 threads"][WAYS_RPS[i]]["cycles:u"]
        for l in ways_logs[i]
    ]
    for i in range(0, 4)
])

instructions_div_cycles = instructions_ways / cycles_ways

instructions_div_cycles_1smt = instructions_ways / cycles_ways[0]
instructions_div_cycles_4smt = instructions_ways / cycles_ways[3]

# Now that we have that, we need to take the harmonic mean along the columns
mean_ipc_per_ways = hmean(instructions_div_cycles, axis=1)

#mean_instructions_ways = np.array([
#    get_average_value_for_key_in_logs(ways_logs[i], "65536 keys", "512 conns", "8 threads", WAYS_RPS[i], "instructions:u")
#    for i in range(0, 4)
#])

#mean_cycles_ways = np.array([
#    get_average_value_for_key_in_logs(ways_logs[i], "65536 keys", "512 conns", "8 threads", WAYS_RPS[i], "cycles:u")
#    for i in range(0, 4)
#])

#mean_ipc_per_ways = mean_instructions_ways / mean_cycles_ways

def autolabel(rects, ax, suffix):
    """
    Attach a text label above each bar displaying its height
    """
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
                '%d' % int(height) + suffix,
                ha='center', va='bottom')


SMT_labels = ["1 way", "2 way", "3 way", "4 way"]

SECONDS_TEST_RAN = 48

mean_mega_instructions_per_second_ways = instructions_ways.mean(axis=1) / (10 ** 6) / SECONDS_TEST_RAN

print(mean_mega_instructions_per_second_ways)
print(mean_mega_instructions_per_second_ways.max() + 1)

plt.figure()
width = 0.25
x = np.arange(len(mean_mega_instructions_per_second_ways))
bars = plt.bar(x, mean_mega_instructions_per_second_ways, 1, color=["C0", "C1", "C2", "C3"], edgecolor='black')
plt.xticks(range(len(SMT_labels)), SMT_labels, rotation = 20)
autolabel(bars, plt, '')
plt.title("Cavium Mega-Instructions per Second, per SMT level")
plt.ylabel("mIPS (User mode)")
plt.ylim(0,mean_mega_instructions_per_second_ways.max() + mean_mega_instructions_per_second_ways.max() * 0.20)

#for i, v in enumerate(mean_instructions_ways):
#    plt.text(i - 0.13, v + 0.01, "{:.2f}".format(v))

plt.legend()
plt.savefig("plots/caviumInstructionsPerSecond.pdf")
plt.show()


plt.figure()
width = 0.25
x = np.arange(len(mean_ipc_per_ways))
bars = plt.bar(x, mean_ipc_per_ways, 1, color=["C0", "C1", "C2", "C3"], edgecolor='black')
plt.xticks(range(len(SMT_labels)), SMT_labels, rotation = 20)
plt.title("Cavium IPC, per SMT level")
plt.ylabel("IPC (User mode)")
plt.ylim(0,0.8)

for i, v in enumerate(mean_ipc_per_ways):
    plt.text(i - 0.13, v + 0.01, "{:.2f}".format(v))

plt.legend()
plt.savefig("plots/caviumIPCPerSMT.pdf")
plt.show()


mean_ipc_1way_per_ways = hmean(instructions_div_cycles_1smt, axis=1)


plt.figure()
width = 0.25
x = np.arange(len(mean_ipc_1way_per_ways))
bars = plt.bar(x, mean_ipc_1way_per_ways, 1, color=["C0", "C1", "C2", "C3"], edgecolor='black')
plt.xticks(range(len(SMT_labels)), SMT_labels, rotation = 20)
plt.title("Cavium Instr. per 1way cycles, per SMT level")
plt.ylabel("IPC (User mode)")
plt.ylim(0,max(mean_ipc_1way_per_ways) + 0.2)

for i, v in enumerate(mean_ipc_1way_per_ways):
    plt.text(i - 0.13, v + 0.01, "{:.2f}".format(v))

plt.legend()
plt.savefig("plots/caviumIPC1wayPerSMT.pdf")
plt.show()

mean_ipc_4way_per_ways = hmean(instructions_div_cycles_4smt, axis=1)

plt.figure()
width = 0.25
x = np.arange(len(mean_ipc_4way_per_ways))
bars = plt.bar(x, mean_ipc_4way_per_ways, 1, color=["C0", "C1", "C2", "C3"], edgecolor='black')
plt.xticks(range(len(SMT_labels)), SMT_labels, rotation = 20)
plt.title("Cavium Instr. per 4way cycles, per SMT level")
plt.ylabel("IPC (User mode)")
plt.ylim(0,max(mean_ipc_4way_per_ways) + 0.2)

for i, v in enumerate(mean_ipc_4way_per_ways):
    plt.text(i - 0.13, v + 0.01, "{:.2f}".format(v))

plt.legend()
plt.savefig("plots/caviumIPC1wayPerSMT.pdf")
plt.show()

