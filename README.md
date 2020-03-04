# SoftwareMetrics
## Usage

```
git clone --recurse-submodules -j8 https://github.com/SoftengPoliTo/SoftwareMetrics
make install_local_all
./analyzer.py -p <path_to_the_code_to_analyze>
```

## Used tools:

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

## METRICS:

### All the desired metrics
CC
Ce
CHANGE
C&K
CLOC
Halstead
JLOC
LOC
LCOM2
MI
MPC
NOM
NPM
STAT
WMC

### Not used
 -	**CHANGE:** We do not consider this one now, because it is a metric that analyse different versions of the same code.

 -	**JLOC:** JavaDoc Lines of Code, it returns the number of JavaDoc lines. It can only be applied to Java code, but it is possible to create a similar metric for Rust.

### Not yet added
 -	**LCOM2:** Lack of Cohesion in methods. Evolution of LCOM, by C&K.
 
 -	**STAT:** it counts the Number of Statements in a method.
 
 -	**MPC:** Message Passing Coupling, it is a metric from the Li & Henry suite.
 
 -	**NPM:** Number of Public Methods. It returns the number of all the methods of a class that are declared as public.

 -	**Ce:** Efferent Coupling, it can be computed per-class only.

### Used ones:
 -	**LOC:** sometimes called SLOC, returns the number of non-blank lines in a code. It can be calculated in different ways, since it does sot have a precise definition. It can refer to a Logical LOC (LLOC) or to a Physical LOC (LOC). Here we use LOC to indicate the Physical LOC.
 
 -  **LLOC:** Logical lines of Code.
 
 -	**SLOC:** Source Lines of Code. It returns the total number of lines in a file.

 -	**CLOC:** Comment Lines of Code, it returns the number of comment lines.
 
 -	**CC:** McCabe's Cyclomatic Complexity.

 -	**C&K:** Chidamber & Kemerer, it can be computed per-class only. Currently, we support only 4 of the 6 metrics defined by this suite.

 -	**Halstead:** it calculates the the Halstead suite.

 -	**MI:** Maintainability Index, it is per-function calculated metric.

 -	**WMC:** McCabe's Weighted Methods Count, it sums the CC of each methods of a class. Hence, it is a per-class calculated function.

 -	**NOM:** Number of Methods. It is a per-class and per-file metric.