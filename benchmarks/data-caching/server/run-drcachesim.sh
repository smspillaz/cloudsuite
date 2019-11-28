#!/bin/bash

mkdir -p output/
chmod -R 777 output/

RETRACE_ID=${RETRACE_ID:?"Need to set RETRACE_ID (its a directory in output/)"}

docker rm -f run-retrace
docker run -it --name run-retrace --cap-add SYS_ADMIN  -v $(pwd)/output:/output smspillaz/data-caching:server ./dynamorio/build/bin64/drrun -t drcachesim $@ -indir /output/$RETRACE_ID/
