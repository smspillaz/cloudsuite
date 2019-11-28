#!/bin/bash
set -e
set -x


# default configuration
echo "dc-server, 11211" > "/usr/src/memcached/memcached_client/servers.txt"
# We just want it to run for a certain amount of time, preloaded data and with
# the args we pass to it, that's it.
/usr/src/memcached/memcached_client/loader \
	-a /usr/src/memcached/twitter_dataset/twitter_dataset_5x \
	-s /usr/src/memcached/memcached_client/servers.txt \
	-t 30 -T 5 $@
