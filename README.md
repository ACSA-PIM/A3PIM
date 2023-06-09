# sniper-pim


## Installation

```bash
pip -m venv curPy
source curPy/bin/active
pip install -r requirements.txt
```
## Config

运行前需要配置好 `src/config.py`

除开常规路径设置，最重要的是 待测的应用，以及应用对应的执行命令。

## Running

由于sniper采集真实数据的时间极不均衡，强烈建议`main.py`拆开成多个文件分阶段运行。

Step依赖关系是，STEP3、4需要前面三部分(STEP1, STEP2.1, STEP2.2)运行完，前三部分间无依赖。

### Step 1

```bash
source curPy/bin/active
python3 preScaTest.py
```

### Step 2.1

main.py 对应部分

### Step 2.2

```bash
source curPy/bin/active
python3 preParallelPimMode.py
```

### Step 3、4

```bash
source curPy/bin/active
python3 preAnalyse.py
```

## Trainning coefficients

```bash
python src/trainning/main.py
```

大失败： 线性和逻辑回归，完全找不到规律。