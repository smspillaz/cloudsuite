#!/bin/bash

set -x

ARCH=$1
SYS=$2
OUTPUT=$3

mkdir -p $OUTPUT

for i in $(ls benchmarks/$ARCH) ; do
    path=$(pwd)/benchmarks/$ARCH/$i;
    bash ${path} > $OUTPUT/${i}.${ARCH}.${SYS}.log;
done
