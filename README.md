# A3PIM

The initial release of A3PIM is described in the following paper:

[DATE'2024] Qingcai Jiang, Shaojie Tan, Junshi Chen and Hong An. [A3PIM: An Automated, Analytic and Accurate Processing-in-Memory Offloader](https://arxiv.org/abs/2402.18592), 27th Design, Automation and Test in Europe Conference (DATE), 2024. 


## Installation

You need have installed `python3-venv` with sudo permissions
```bash
python3 -m venv curPy
source curPy/bin/active
pip install -r requirements.txt
```

### Installation without sudo

```bash
pip install virtualenv
virtualenv myenv
source myenv/bin/activate
```

## Configuration

Prior to execution, it is necessary to properly configure the `src/config.py` file.

In addition to setting the conventional paths, the most crucial aspects involve specifying the application to be tested and its corresponding execution commands.

## Execution

Given the highly uneven temporal distribution of data collection by Sniper, it is highly recommended to split main.py into multiple files and run them in stages.

The dependencies among steps are as follows: `STEP3` and `STEP4` require the completion of the preceding three parts (`STEP1`, `STEP2.1`, `STEP2.2`), with no dependencies among the initial three parts.

### Step 1 : Obtain Static Information of Basic Blocks (BBLs)

```bash
source curPy/bin/active
python3 preScaTest.py
```

### Step 2 : Obtain Real Baseline Results Using Sniper

Parallel execution can be attempted; however, employing a single command for each application proves to be a more manageable approach. 

To obtain the individual Sniper collection commands for each application, please utilize the following instructions.

```bash
python ./src/printPIMcommand.py
```

#### Step 2.1 : Obtain Real CPU Baseline Results Using Sniper

The relevant code can be found in `main.py`.

#### Step 2.2 : Obtain Real PIM Baseline Results Using Sniper

```bash
source curPy/bin/active
python3 preParallelPimMode.py
```

### Step 3 and 4 : Decision Solver, Result Analysis, and Visualization

```bash
source curPy/bin/active
python3 preAnalyse.py
```

We are developing and testing a truly compile-time-scheduling framework using the following scripts:

```bash
python3 CTS.py 
```

## Additional Step: Trainning XGB coefficients

If you wish to train your own XGB parameters, you can utilize the following command. Reviewing the `./training.sh` file will assist in understanding the file dependencies for the training process.(The entire XGBoost training method has been deprecated and is currently in an incompatible state that cannot be executed.)

```bash
python src/trainning/main.py
```

## Common Installation Issue: 


### Missing Font Files

```bash
 raise FileNotFoundError(
FileNotFoundError: Matplotlib's TeX implementation searched for a file named 'cmr10.tfm' in your texmf tree, but could not find it 
```

<!-- 1. `wget http://mirrors.ctan.org/fonts/cm/tfm/cmr10.tfm`
2. Matplotlib set front search path  -->

### explaination

0 is global
1 is main 
```bash
  BBLID  Decision ctsDecision scaDecision   Parallelism       bbCount            CPU            PIM     Difference             Hash(hi)             Hash(lo)
      0         C           C           C            32             2          11007    6.30947e+07   -6.30837e+07                      0                      0
      1         P           C           C             1       1312156    1.13788e+06    4.01082e+06   -2.87294e+06                      1                      1
```

## Contact:
Qingcai Jiang: jqc9707@gmail.com
