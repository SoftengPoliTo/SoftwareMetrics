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
Repository: updated at 2019-11-06.

Used for: LOC, CLOC

    * Building: Ok
    * Local installation: Ok

    Can analyze an entire directory


### CCCC
Repository: last available version + some patches.

Used for: C&K, CC, WMC

    * Building: Ok
    * Local installation: Ok


### Halstead Metrics Tool
Repository: last available version.

Used for: Halstead

    * Building: Ok (simple copy)
    * Local installation: Ok (simple copy)

    It has been corrected (Volume calculation was wrong).
    A CLI interface has been added.

    Can analyze a file at a time only.


### Maintainability Index
Repository: last available version.

Used for: MI

    * Dependencies: pep8, pylint, nose (for python3)
    * MI is calculated w/ the 3-Metrics equations, but its value is divided by 1.71!

    Can analyze an entire directory

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

 - **LOC:** Lines of Code. It returns the number of instructions and comment lines in a file.

 - **LLOC:** Logical Lines of Code. It returns the number of logical lines in a file (statements)

 - **CLOC:** Comment Lines of Code, it returns the number of comment lines in a file.

 - **STAT:** Statements. It counts the number of statements in a method/class. (a more precise LLOC)

 - **NOM:** Number of Methods. It counts the number of methods in a file.

 - **CC:** McCabe's Cyclomatic Complexity.

 - **Halstead:** It calculates the Halstead suite.

 - **MI:** Maintainability Index. It is a suite to measure the maintainability of a code. It is calculated both for files and functions.

### Metrics to be implemented

 - **CHANGE:** It analyses different versions of the same code.

### Class metrics (not to be implemented)

 - **MPC:** Message Passing Coupling, it is a metric from the Li & Henry suite.

 - **NPM:** Number of Public Methods. It returns the number of methods in a class that are declared as public.

 - **WMC:** McCabe's Weighted Methods Count. It sums the CC of each methods in a class. Hence, it is a per-class calculated function.

 - **C&K:** Chidamber & Kemerer can be computed per-class only. Currently, we support only 4 of the 6 metrics defined by this metric suite.

 - **LCOM2:** Lack of Cohesion in methods. Evolution of LCOM by C&K.

 - **CE:** Efferent Coupling, it can be computed per-class only.
