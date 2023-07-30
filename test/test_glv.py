import sys
sys.path.append('./src')

import config  # 加载配置
import global_variable as glv
from SCA import *
from icecream import ic


a = "tuning_cluster_threshold"
print(glv._get(a))
print(glv._get("tuning_cluster_threshold"))
glv._set(a, -0.1)
print(glv._get(a))
print(glv._get("tuning_cluster_threshold"))

ic.enable()
a = basic_block("adwa",["movslq 0x0(%r13, %2, 23),%rdx"],[0,1])
a.print()