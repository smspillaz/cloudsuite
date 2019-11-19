#!/bin/bash
export PERF_ARGS="-e armv8_pmuv3_0/l2d_cache/,armv8_pmuv3_0/l2d_cache_wb/,armv8_pmuv3_0/l2d_cache_refill/,armv8_pmuv3_0/l2d_cache_allocate/,instructions"
export SERVER_ARGS="-t 1 -m 4096 -n 550"

for i in 2 4 8 16 32 64 128 256 512 1024 2048 4096 8192 16384; do
  echo "L1D cache, $i keys"
  CLIENT_ARGS="-rps 180000 -k $i" bash server/run-perf-tests.sh
done

for i in 2 4 8 16 32 64 128 256 512 1024 2048 4096 8192 16384; do
  echo "L1D cache, 4096 keys, $i conncetions"
  CLIENT_ARGS="-rps 180000 -k 4096 -c $i" bash server/run-perf-tests.sh
done


