#!/bin/bash
export PERF_ARGS="-e instructions:u"
export SERVER_ARGS="-t 1 -m 4096 -n 550"

echo "Instructions, 4096 keys, 1 connection"
CLIENT_ARGS="-rps 180000 -k 4096 -c 1" bash server/run-perf-tests.sh
