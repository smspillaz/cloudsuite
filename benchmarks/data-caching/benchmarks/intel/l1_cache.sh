#!/bin/bash
export PERF_ARGS="-e L1-icache-load-misses,L1-icache-loads,instructions"
export SERVER_ARGS="-t 1 -m 4096 -n 550"

for i in 64 4096; do
  echo "L1 cache, $i keys"
  CLIENT_ARGS="-rps 180000 -k $i" bash server/run-perf-tests.sh
done

for i in 2 64; do
  echo "L1 cache, 4096 keys, $i conncetions"
  CLIENT_ARGS="-rps 180000 -k 4096 -c $i" bash server/run-perf-tests.sh
done


