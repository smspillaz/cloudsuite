#!/bin/bash
export PERF_ARGS="-e branch-misses,branch-instructions,instructions"
export SERVER_ARGS="-t 1 -m 4096 -n 550"

for i in 64 128 256 512 1024 2048 4096 8192; do
  echo "Branch predictor, $i keys"
  CLIENT_ARGS="-rps 180000 -k $i" bash server/run-perf-tests.sh
done

for i in 2 4 8 16 32 64; do
  echo "Branch predictor, 4096 keys, $i conncetions"
  CLIENT_ARGS="-rps 180000 -k 4096 -c $i" bash server/run-perf-tests.sh
done


