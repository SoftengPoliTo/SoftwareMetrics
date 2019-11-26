# SoftwareMetrics
## Usage
make install_local_all
./Analyzer.sh <path_to_the_code>

## Used tools:

### Tokei
Repo updated @ 2019-11-06.
Used for: LOC, CLOC

    * Building: Ok
    * Local installation: Ok

    Can analyze an entire Directory


### CCCC
Repo @ last available version + already patched.
Used for: C&K, CC, ¿WMC?

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
	* MI is calculated w/ the 3-Metrics equations, but its value is divided by 1.71 !

    Can analyze an entire Directory
