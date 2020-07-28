# SoftwareMetrics

## Goal

`SoftwareMetrics` compares different programming languages in order to determine
which one is better than another according to a specific set of metrics.

Applying a series of tool on an algorithm written in different
programming languages, we obtain a set of metrics necessary to make the comparisons between languages.

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

Used for: SLOC, LLOC, CLOC, BLANK

    * Building: Ok
    * Local installation: Ok

    Can analyze either a single file or an entire directory

### Rust Code Analysis

Used for: SLOC, PLOC, LLOC, CLOC, BLANK, NOM, CC, HALSTEAD, MI

    * Building: Ok
    * Local installation: Ok

    Can analyze either a single file or an entire directory

## Comparisons among different programming languages

To run the series of comparisons among the metrics produced by
`rust-code-analysis` on some codes written in different programming languages,
it is necessary to install `json-diff`:

1. Install `npm` as described [here](https://nodejs.org/en/download/)
2. Install `json-diff` following these [instructions](https://www.npmjs.com/package/json-diff)

At this point, the results of the comparisons can be obtained in this way:

```
./compare.py
```

## Considered Metrics

- SLOC
- PLOC
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

 - **PLOC:** Physical Lines of Code. It returns the number of instructions and comment lines in a file.

 - **LLOC:** Logical Lines of Code. It returns the number of logical lines (statements) in a file.

 - **CLOC:** Comment Lines of Code. It returns the number of comment lines in a file.

 - **STAT:** Statements. It is a LLOC applied only on methods/classes.

 - **NOM:** Number of Methods. It counts the number of methods in a file.

 - **CC:** McCabe's Cyclomatic Complexity. It calculates the code complexity
   examining the control flow of a program.

 - **Halstead:** It calculates the Halstead suite.

 - **MI:** Maintainability Index. It is a suite to measure the maintainability of a code.
   It is calculated both on files and functions.

### Metrics to be implemented

 - **CHANGE:** It analyses different versions of the same code.

### Class metrics (not to be implemented)

 - **MPC:** Message Passing Coupling. It is a metric from the Li & Henry suite.

 - **NPM:** Number of Public Methods. It returns the number of methods
   in a class declared as public.

 - **WMC:** McCabe's Weighted Methods Count. It sums the CC of each methods
   in a class. Hence, it is a per-class calculated metric.

 - **C&K:** Chidamber & Kemerer. It can be computed per-class only.
   Currently, we support only 4 of the 6 metrics defined by this metric suite.

 - **LCOM2:** Lack of Cohesion 2. An alternative way to calculate LCOM by C&K.

 - **CE:** Efferent Coupling. It can be computed per-class only.
