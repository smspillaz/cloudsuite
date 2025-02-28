#!/bin/bash
export PERF_ARGS="-e LLC-loads,LLC-load-misses"
export SERVER_ARGS="-t 1 -m 4096 -n 550"

for i in 2 4 8 16 32 64 128 256 512 1024 2048 4096 8192 16384; do
  echo "LLC cache, $i keys"
  CLIENT_ARGS="-rps 180000 -k $i -f 512" bash server/run-perf-tests.sh
done

for i in 2 4 8 16 32 64 128 256 512 1024 2048 4096 8192 16384; do
  echo "LLC cache, 4096 keys, $i conncetions"
  max_conns=$(echo "$i + 128" | bc)
  CLIENT_ARGS="-rps 180000 -k 4096 -c $i -f 512" SERVER_ARGS="$SERVER_ARGS -c $max_conns" bash server/run-perf-tests.sh
done


