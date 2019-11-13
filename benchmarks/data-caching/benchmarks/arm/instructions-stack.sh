#!/bin/bash
export PERF_ARGS="-e instructions:k,cycles:k,instructions:u,cycles:u"
export SERVER_ARGS="-t 1 -m 4096 -n 550"

for i in 2 4 8 16 32 64; do
  echo "Instructions Stack, 4096 keys, $i conncetions"
  CLIENT_ARGS="-rps 180000 -k 4096 -c $i" bash server/run-perf-tests.sh
done
