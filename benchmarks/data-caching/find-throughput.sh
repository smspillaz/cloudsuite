#!/bin/bash
START_CPU=${START_CPU:?"Need to set START_CPU"}
THREADS_PER_CORE=${THREADS_PER_CORE:?"Need to set THREADS_PER_CORE"}
SERVER_CORES=${SERVER_CORES:?"Need to set SERVER_CORES"}
PERF_ARGS=${PERF_ARGS:?"Need to set PERF_ARGS"}

set -x

for keys in $KEYS; do
  for conns in $CONNS; do
    for threads in $THREADS; do
      for rps in $RPS; do
        echo "==> Bench: $keys keys, $conns conns, $threads threads, $rps rps";
        max_conns=$(echo "$conns + 128" | bc)
        client_cores_spec=$START_CPU-$(echo "$START_CPU + $threads" | bc)
        CLIENT_CORES_SPEC="$client_cores_spec" CLIENT_ARGS="-r $rps -k $keys -c $conns -f 512 -w $threads" SERVER_ARGS="-t ${THREADS_PER_CORE} -m 4096 -n 550 -c $max_conns" bash server/run-perf-tests.sh
      done
    done
  done
done

