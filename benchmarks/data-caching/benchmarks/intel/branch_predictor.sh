#!/bin/bash
export PERF_ARGS="-e branch-misses,branch-instructions,instructions"
export SERVER_ARGS="-t 1 -m 4096 -n 550"

for i in 64 128 256 512 1024 2048 4096 8192; do
  echo "Branch predictor, $i keys"
  CLIENT_ARGS="-rps 180000 -k $i" bash server/run-perf-tests.sh
done


