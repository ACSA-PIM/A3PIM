#!/bin/bash

# set -e
# set -v

cd /staff/shaojiemike/github/sniper-pim
source ./pyEnv/bin/activate

k=1  # loop times

for ((i=1; i<=k; i++))
do
    # data test
    python ./src/preScaTest.py -d no

    # delete exist inter files 
    rm -rf ./Summary/default_cpu_1_pim_32 ./Summary/kron-20_cpu_1_pim_32 ./Summary/special_cpu_1_pim_32

    python ./src/preAnalyse.py 
done