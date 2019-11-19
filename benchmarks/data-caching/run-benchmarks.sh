#!/bin/bash

ARCH=$1
OUTPUT=$2

mkdir -p $OUTPUT

for i in $(ls benchmarks/$ARCH) ; do
    PATH=$(pwd)/benchmarks/$ARCH/$i;
    bash ${PATH} > $OUTPUT/${i}.${ARCH}.log;
done
