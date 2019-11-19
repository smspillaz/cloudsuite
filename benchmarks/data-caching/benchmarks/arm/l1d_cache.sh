#!/bin/bash
export PERF_ARGS="-e L1-dcache-load-misses,L1-dcache-loads,instructions"
export SERVER_ARGS="-t 1 -m 4096 -n 550"

for i in 2 4 8 16 32 64 128 256 512 1024 2048 4096 8192 16384; do
  echo "L1D cache, $i keys"
  CLIENT_ARGS="-rps 180000 -k $i" bash server/run-perf-tests.sh
done

for i in 2 4 8 16 32 64 128 256 512 1024 2048 4096 8192 16384; do
  echo "L1D cache, 4096 keys, $i conncetions"
  CLIENT_ARGS="-rps 180000 -k 4096 -c $i" bash server/run-perf-tests.sh
done


