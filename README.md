# sniper-pim


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

## Additional Step: Trainning XGB coefficients

If you wish to train your own XGB parameters, you can utilize the following command. Reviewing the `./training.sh` file will assist in understanding the file dependencies for the training process.

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