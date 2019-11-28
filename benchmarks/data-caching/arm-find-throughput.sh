#!/bin/bash

export THREADS_PER_CORE=4
export START_CPU=112
export PERF_ARGS_L1_CACHES="-e instructions,L1-dcache-load-misses,L1-dcache-loads,armv8_pmuv3_0/l1i_cache_refill/,armv8_pmuv3_0/l1i_cache/"
export PERF_ARGS_L2_CACHES="-e instructions,armv8_pmuv3_0/l2d_cache_wb/,armv8_pmuv3_0/l2d_cache_refill/,armv8_pmuv3_0/l2d_cache_allocate/"

export PERF_ARGS_SW="instructions,cycles,armv8_pmuv3_0/br_mis_pred/,armv8_pmuv3_0/br_pred/"


set -x;
perf stat $PERF_ARGS_SW ls; perf stat $PERF_ARGS_L1_CACHES ls; perf stat $PERF_ARGS_L2_CACHES ls;

PERF_ARGS=$PERF_ARGS_L1_CACHES bash find-throughput.sh > arm.cavium.throughput.l1.log 2>&1
PERF_ARGS=$PERF_ARGS_L2_CACHES bash find-throughput.sh > arm.cavium.throughput.l2.log 2>&1
PERF_ARGS=$PERF_ARGS_SW bash find-throughput.sh > arm.cavium.throughput.sw.log 2>&1

