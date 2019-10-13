FROM ubuntu:16.04
LABEL maintainer="Arash Pourhabibi Zarandi <arash.pourhabibi@epfl.ch>"

# add our user and group first to make sure their IDs get assigned consistently, regardless of whatever dependencies get added
RUN groupadd -r memcache && useradd -r -g memcache memcache

ENV DEBIAN_FRONTEND noninteractive

RUN mkdir -p /usr/src
COPY memcached /usr/src/memcached

RUN apt-get update && apt-get install -y libevent-2.0-5 vim valgrind gdb telnet --no-install-recommends \
	&& rm -rf /var/lib/apt/lists/*

RUN buildDeps='curl gcc libc6-dev libevent-dev make' \
	&& set -x \
	&& apt-get update && apt-get install -y $buildDeps --no-install-recommends \
	&& rm -rf /var/lib/apt/lists/* \
	&& cd /usr/src/memcached/memcached_client \
	&& make CFLAGS="-g -O3" \
	&& chown -R memcache:memcache /usr/src/memcached \
	&& apt-get purge -y --auto-remove $buildDeps

COPY docker-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

USER memcache
CMD ["-rps", "18000"]
