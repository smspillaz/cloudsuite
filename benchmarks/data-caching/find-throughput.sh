#!/bin/bash
START_CPU=${START_CPU:?"Need to set START_CPU"}
THREADS_PER_CORE=${THREADS_PER_CORE:?"Need to set THREADS_PER_CORE"}
PERF_ARGS=${PERF_ARGS:?"Need to set PERF_ARGS"}

set -x

KEYS="4096 16384 65536 262114" # Scale by factor 4
CONNS="256 512 1024"
THREADS="1 2 4 8"
RPS="27000 28000 29000 30000 31000 32000" # 16384

for keys in $KEYS; do
  for conns in $CONNS; do
    for threads in $THREADS; do
      for rps in $RPS; do
        echo "==> Bench: $keys keys $conns conns $threads threads $rps rps";
        max_conns=$(echo "$conns + 128" | bc)
        client_cores_spec=$START_CPU-$(echo "$START_CPU + $threads" | bc)
        CLIENT_CORES_SPEC="$client_cores_spec" CLIENT_ARGS="-r $rps -k $keys -c $conns -f 512 -w $threads" SEVER_ARGS="-t 1 -m 4096 -n 550 -c $max_conns" bash server/run-perf-tests.sh
      done
    done
  done
done

