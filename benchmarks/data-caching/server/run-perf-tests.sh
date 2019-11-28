#!/bin/bash

CLIENT_CORES_SPEC=${CLIENT_CORES_SPEC:-112}

mkdir -p output/
chmod -R 777 output/

docker network rm caching_network || true;
docker network create caching_network || true;

echo "Starting server with perf args ${PERF_ARGS} server args ${SERVER_ARGS}"
docker rm -f dc-server || true;
docker run --cpuset-cpus="$CLIENT_CORES_SPEC" -t --name dc-server --net caching_network \
    --cap-add SYS_ADMIN \
    -e TOOL_ARGS="/usr/lib/linux-tools/4.15.0-66-generic/perf stat ${PERF_ARGS}" \
    -p 11211:11211 \
    -v $(pwd)/output:/output smspillaz/data-caching:server bash docker-entrypoint.sh memcached ${SERVER_ARGS} &

echo "Starting client with ${CLIENT_ARGS}"

docker rm -f cloudsuite-data-caching-perf-test-client || true;
docker run --cpuset-cpus="1" -t --name cloudsuite-data-caching-perf-test-client --net caching_network \
    smspillaz/data-caching:client ${CLIENT_ARGS}

echo "Done, sending SIGINT to memcached"
MEMCACHED_PID="$(docker exec -it dc-server pidof memcached 2>&1)"
echo "memcached pid is: $MEMCACHED_PID"
docker exec -it dc-server ps aux
docker exec -it dc-server bash -c 'kill -INT $(pidof memcached)'
