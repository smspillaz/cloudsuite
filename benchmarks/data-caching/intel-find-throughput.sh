#!/bin/bash

RUN=${RUN:?Need to set run in the environment}

echo "Run is $RUN"

export THREADS_PER_CORE=2
export SERVER_CORES="0,1"
export START_CPU=24
export PERF_ARGS_L1_CACHES="-e instructions:u,L1-dcache-load-misses:u,L1-dcache-loads:u"
export PERF_ARGS_L1_I_CACHES="-e instructions:u,L1-icache-load-misses:u,icache.hit:u"
export PERF_ARGS_L2_CACHES="-e instructions:u,LLC-loads:u,LLC-load-misses:u"

export PERF_ARGS_BR="-e instructions:u,branch-misses:u,branch-instructions:u"
export PERF_ARGS_SW="-e instructions:u,instructions:k,cycles:k,cycles:u"

# Benchmark configuration
export KEYS="16384 65536 262114" # Scale by factor 4
export CONNS="256 512 1024"
export THREADS="4"
#export RPS="55000 60000 70000 80000 81000 82000 83000 84000 85000"
#export RPS="104000 108000 112000 116000 120000 124000 128000"
#export RPS="100000 110000 120000" # 55000 60000 70000 80000 81000 82000 83000 84000 85000
export RPS="115000"

set -x;
perf stat $PERF_ARGS_SW ls;
perf stat $PERF_ARGS_L1_CACHES ls;
perf stat $PERF_ARGS_L1_I_CACHES ls;
perf stat $PERF_ARGS_BR ls;
perf stat $PERF_ARGS_L2_CACHES ls;

PERF_ARGS=$PERF_ARGS_L1_CACHES bash find-throughput.sh > intel.throughput.l1.log.${RUN} 2>&1
PERF_ARGS=$PERF_ARGS_L1_I_CACHES bash find-throughput.sh > intel.throughput.l1i.log.${RUN} 2>&1
PERF_ARGS=$PERF_ARGS_L2_CACHES bash find-throughput.sh > intel.throughput.l2.log.${RUN} 2>&1
PERF_ARGS=$PERF_ARGS_BR bash find-throughput.sh > intel.throughput.br.log.${RUN} 2>&1
PERF_ARGS=$PERF_ARGS_SW bash find-throughput.sh > intel.throughput.sw.log.${RUN} 2>&1

