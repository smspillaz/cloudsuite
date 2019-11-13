#!/bin/bash

mkdir -p output/
chmod -R 777 output/
docker run -t \
    -e "TOOL_ARGS=dynamorio/build/bin64/drrun -t drcachesim -offline -outdir /output --" \
    -v $(pwd)/output:/output cloudsuite/data-caching:server
