FROM ubuntu:16.04
MAINTAINER Arash Pourhabibi Zarandi <arash.pourhabibi@epfl.ch>

# This is based on the official memcached Dockerfile

# add our user and group first to make sure their IDs get assigned consistently, regardless of whatever dependencies get added
RUN groupadd -r memcache && useradd -r -g memcache memcache

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get -y --no-install-recommends install \
	apt-transport-https \
	ca-certificates \
	gnupg \
	software-properties-common \
	wget \
	build-essential
RUN wget -O - https://apt.kitware.com/keys/kitware-archive-latest.asc 2>/dev/null | apt-key add -
RUN apt-add-repository 'deb https://apt.kitware.com/ubuntu/ xenial main'

RUN apt-get update && apt-get install -y --no-install-recommends \
		libevent-2.0-5 \
		git \
                build-essential \
                libarchive-dev \
                libbz2-dev \
                libcurl4-openssl-dev \
                libexpat-dev \
                liblzma-dev \
                libssl-dev \
                libncurses5-dev \
                libuv1-dev \
                python3-sphinx \
                zlib1g-dev \
	&& rm -rf /var/lib/apt/lists/*

RUN git clone git://github.com/kitware/CMake && cd CMake && ./bootstrap && make && make install

ENV MEMCACHED_VERSION 1.4.24
ENV MEMCACHED_SHA1 32a798a37ef782da10a09d74aa1e5be91f2861db

RUN git clone git://github.com/smspillaz/dynamorio && \
	cd dynamorio && \
	mkdir build && \
	cd build && \
	cmake .. -DCMAKE_INSTALL_PREFIX=/usr && \
	make && \
	make && \
  make install

RUN apt-get update && apt-cache search linux-tools && apt-get install -y linux-tools-generic linux-tools-aws linux-tools-4.15.0-1051-aws;

RUN buildDeps='curl gcc libc6-dev libevent-dev make perl' \
	&& set -x \
	&& apt-get update && apt-get install -y $buildDeps --no-install-recommends \
	&& rm -rf /var/lib/apt/lists/* \
	&& curl -SL "http://memcached.org/files/memcached-$MEMCACHED_VERSION.tar.gz" -o memcached.tar.gz \
	&& echo "$MEMCACHED_SHA1 memcached.tar.gz" | sha1sum -c - \
	&& mkdir -p /usr/src/memcached \
	&& tar -xzf memcached.tar.gz -C /usr/src/memcached --strip-components=1 \
	&& rm memcached.tar.gz \
	&& cd /usr/src/memcached \
	&& CFLAGS="-g -O3 -pthread" ./configure \
	&& make CFLAGS="-g -O3 -pthread" \
	&& make install \
	&& cd / && rm -rf /usr/src/memcached \
	&& apt-get purge -y --auto-remove $buildDeps

USER memcache
EXPOSE 11211
CMD ["dynamorio/build/bin64/drrun", "-t", "drcachesim", "-offline", "-outdir", "/output", "--", "memcached", "-t", "2", "-m", "2048", "-n", "550"]
