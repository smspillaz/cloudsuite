#!/bin/bash

set -x

ARCH=$1
OUTPUT=$2

mkdir -p $OUTPUT

for i in $(ls benchmarks/$ARCH) ; do
    path=$(pwd)/benchmarks/$ARCH/$i;
    bash ${path} > $OUTPUT/${i}.${ARCH}.log;
done
