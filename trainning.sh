#!/bin/bash

# set -e
# set -v

cd /staff/shaojiemike/github/sniper-pim
source ./pyEnv/bin/activate

k=2  # loop times

for ((i=1; i<=k; i++))
do
    echo "Iteration $i"

    # trainning
    python ./src/trainning/main.py -d no

    # delete exist inter files 
    rm -rf ./Summary/default_cpu_1_pim_32 ./Summary/kron-20_cpu_1_pim_32 ./Summary/special_cpu_1_pim_32

    # data test
    python ./src/preScaTest.py -d no
    python ./src/preAnalyse.py -d no
done