#!/bin/bash

set -e
set -v

cd /staff/shaojiemike/github/sniper-pim
source ./pyEnv/bin/activate

# trainning
# python ./src/trainning/main.py

# delete exist inter files 
rm -rf ./log/assembly
rm -rf ./Summary/default_cpu_1_pim_32 ./Summary/kron-20_cpu_1_pim_32 ./Summary/special_cpu_1_pim_32

# data test
python ./src/preScaTest.py -d no
python ./src/preAnalyse.py