#!/bin/bash

export THREADS_PER_CORE=4
export SERVER_CORES="0,1,2,3" # 4-way SMT
export START_CPU=112
export PERF_ARGS_L1_CACHES="-e instructions,L1-dcache-load-misses,L1-dcache-loads,armv8_pmuv3_0/l1i_cache_refill/,armv8_pmuv3_0/l1i_cache/"
export PERF_ARGS_L2_CACHES="-e instructions,armv8_pmuv3_0/l2d_cache_wb/,armv8_pmuv3_0/l2d_cache_refill/,armv8_pmuv3_0/l2d_cache_allocate/"

export PERF_ARGS_SW="instructions,cycles,armv8_pmuv3_0/br_mis_pred/,armv8_pmuv3_0/br_pred/"

# Benchmark configuration
export KEYS="4096 16384 65536 262114" # Scale by factor 4
export CONNS="256 512 1024"
export THREADS="1 2 4 8"
export RPS="" #"27000 28000 29000 30000 31000 32000" # 16384

set -x;
perf stat $PERF_ARGS_SW ls; perf stat $PERF_ARGS_L1_CACHES ls; perf stat $PERF_ARGS_L2_CACHES ls;

PERF_ARGS=$PERF_ARGS_L1_CACHES bash find-throughput.sh > arm.cavium.throughput.l1.log 2>&1
PERF_ARGS=$PERF_ARGS_L2_CACHES bash find-throughput.sh > arm.cavium.throughput.l2.log 2>&1
PERF_ARGS=$PERF_ARGS_SW bash find-throughput.sh > arm.cavium.throughput.sw.log 2>&1

