# SoftwareMetrics

## Usage

```
git clone --recurse-submodules -j8 https://github.com/SoftengPoliTo/SoftwareMetrics
make install
./analyzer.py -p <path_to_the_code_to_analyze>
```

To update submodules:

```
git submodule update --recursive --remote
make clean
make install
```

## Used tools

### Tokei
Repo updated @ 2019-11-06.
Used for: LOC, CLOC

    * Building: Ok
    * Local installation: Ok

    Can analyze an entire Directory


### CCCC
Repo @ last available version + already patched.
Used for: C&K, CC, WMC

    * Building: Ok
    * Local installation: Ok

    Can analyze a file at a time only.


### Halstead Metrics Tool
Repo @ last available version.
Used for: Halstead

    * Building:	Ok (simple copy)
    * Local installation: Ok (simple copy)

    It has been corrected (Volume calculation was wrong).
    A CLI interface has been added.

    Can analyze a file at a time only.


### Maintainability Index
Repo @ last available version.
Used for: MI

    * Dependencies: pep8, pylint, nose (for python3)
    * MI is calculated w/ the 3-Metrics equations, but its value is divided by 1.71!

    Can analyze an entire Directory

## Metrics

### Considered metrics

- SLOC
- LOC
- LLOC
- CLOC
- CC
- Halstead
- MI
- NOM
- STAT
- CHANGE
- MPC
- NPM
- WMC
- C&K
- LCOM2
- CE

### Implemented metrics

 - **SLOC:** Source Lines of Code. It returns the total number of lines in a file.

 - **LOC:** Lines of Code. It returns the number of instruction and comment lines in a file.

 - **LLOC:** Logical Lines of Code. It returns the number of logical and comment lines in a file

 - **CLOC:** Comment Lines of Code, it returns the number of comment lines in a file.

 - **CC:** McCabe's Cyclomatic Complexity.

 - **Halstead:** It calculates the Halstead suite.

### Metrics to be implemented

 - **MI:** Maintainability Index, it is per-function calculated metric.

 - **NOM:** Number of Methods. It is a per-class and per-file metric.

 - **STAT:** It counts the Number of Statements in a method.

 - **CHANGE:** It analyses different versions of the same code.

### Class metrics (not to be implemented)

 - **MPC:** Message Passing Coupling, it is a metric from the Li & Henry suite.

 - **NPM:** Number of Public Methods. It returns the number of methods in a class that are declared as public.

 - **WMC:** McCabe's Weighted Methods Count. It sums the CC of each methods in a class. Hence, it is a per-class calculated function.

 - **C&K:** Chidamber & Kemerer can be computed per-class only. Currently, we support only 4 of the 6 metrics defined by this metric suite.

 - **LCOM2:** Lack of Cohesion in methods. Evolution of LCOM by C&K.

 - **CE:** Efferent Coupling, it can be computed per-class only.
