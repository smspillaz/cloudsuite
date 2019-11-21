#!/bin/bash
export PERF_ARGS="-e armv8_pmuv3_0/l1i_cache_refill/,armv8_pmuv3_0/l1i_cache/,instructions"
export SERVER_ARGS="-t 1 -m 4096 -n 550"

for i in 2 4 8 16 32 64 128 256 512 1024 2048 4096 8192 16384 32768 65536; do
  echo "L1I cache, $i keys"
  CLIENT_ARGS="-rps 180000 -k $i -f 512" bash server/run-perf-tests.sh
done

for i in 2 4 8 16 32 64 128 256 512 1024 2048 4096 8192 16384; do
  echo "L1I cache, 4096 keys, $i conncetions"
  max_conns=$(echo "$i + 128" | bc)
  CLIENT_ARGS="-rps 180000 -k 4096 -c $i -f 512" SERVER_ARGS="$SERVER_ARGS -c $max_conns" bash server/run-perf-tests.sh
done


