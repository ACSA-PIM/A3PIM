import re
from icecream import ic
targetA = "MPKI offloading time (ns): 9.09858e+08 = CPU 5.74075e+08 + PIM 2.19384e+08 + REUSE 1.164e+08 + SWITCH 0"          
regexA = "MPKI offloading time \(ns\): ([0-9e\.\+]*) = CPU ([0-9e\.\+]*) \+ PIM(.*)$"
p = re.search(regexA,targetA)
ic(p.group(2))
ic(p.group(3))