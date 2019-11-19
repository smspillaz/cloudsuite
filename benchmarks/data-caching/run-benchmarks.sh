#!/bin/bash

ARCH=$1

for i in $(ls benchmarks/$ARCH) ; do
    PATH=$(pwd)/benchmarks/$ARCH/$i;
    bash ${PATH};
done
