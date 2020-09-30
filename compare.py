#!/usr/bin/env python3

"""compare

Compares two json files produced by rust-code-analysis and prints their
differences in an output json file.
"""
import enum
import json
import pathlib
import subprocess
import sys
import tempfile
import typing as T

from exit_codes import ExitCode, log_conf, log_err, log_info

INPUT_DIR = pathlib.Path("Assets")
RESULTS_DIR = pathlib.Path("Results")
COMPARE_DIR = pathlib.Path("Compare")

# The extensions of files present in a directory
EXTENSIONS = {
    "C": ".c",
    "Rust": ".rs",
    "C++": ".cpp",
    "Python": ".py",
    "JavaScript": ".js",
    "TypeScript": ".ts"
}


class Conf(enum.Enum):
    """ Each configuration contains some information to compare a pair
        of programming languages """

    C_CPP = ("C", "C++", "C-C++")
    C_JS = ("C", "JavaScript", "C-JavaScript")
    C_TS = ("C", "TypeScript", "C-TypeScript")
    C_PYTHON = ("C", "Python", "C-Python")
    C_RUST = ("C", "Rust", "C-Rust")
    CPP_JS = ("C++", "JavaScript", "C++-JavaScript")
    CPP_PYTHON = ("C++", "Python", "C++-Python")
    CPP_RUST = ("C++", "Rust", "C++-Rust")
    JS_TS = ("JavaScript", "TypeScript", "JavaScript-TypeScript")
    RUST_JS = ("Rust", "JavaScript", "Rust-JavaScript")
    RUST_TS = ("Rust", "TypeScript", "Rust-TypeScript")
    RUST_PYTHON = ("Rust", "Python", "Rust-Python")


# All supported configurations for files
GLOBAL_CONF = (
    Conf.C_CPP.value,
    Conf.C_JS.value,
    Conf.C_TS.value,
    Conf.C_PYTHON.value,
    Conf.C_RUST.value,
    Conf.CPP_JS.value,
    Conf.CPP_PYTHON.value,
    Conf.CPP_RUST.value,
    Conf.JS_TS.value,
    Conf.RUST_JS.value,
    Conf.RUST_TS.value,
    Conf.RUST_PYTHON.value,
)

# Pidigits configuration, since it is not implemented in JavaScript and TypeScript
PIDIGITS_CONF = (
    Conf.C_CPP.value,
    Conf.C_PYTHON.value,
    Conf.C_RUST.value,
    Conf.CPP_PYTHON.value,
    Conf.CPP_RUST.value,
    Conf.RUST_PYTHON.value,
)

# Pair of files and configurations associated
FILE_DICT = {
    "binarytrees": GLOBAL_CONF,
    "bubble_sort": (Conf.C_CPP.value, Conf.C_RUST.value),
    "fannkuchredux": GLOBAL_CONF,
    "fasta": GLOBAL_CONF,
    "knucleotide": GLOBAL_CONF,
    "mandelbrot": GLOBAL_CONF,
    "nbody": GLOBAL_CONF,
    "pidigits": PIDIGITS_CONF,
    "regexredux": GLOBAL_CONF,
    "revcomp": GLOBAL_CONF,
    "spectralnorm": GLOBAL_CONF,
}


def run_subprocess(cmd: str, *args: T.Any) -> subprocess.CompletedProcess:
    return subprocess.run(
        [cmd, *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def build_json_name(directory: str, filename: str) -> pathlib.Path:
    output_file = "rust-code-analysis" + "_" + filename + EXTENSIONS[directory]
    return RESULTS_DIR / directory / (output_file + ".json")


def compute_metrics(directory: str, filename: str) -> None:

    input_file = INPUT_DIR / directory / filename
    output_file = RESULTS_DIR / directory

    ret_value = run_subprocess(
        "./analyzer.py",
        "-tm",
        "-t",
        "rust-code-analysis",
        "-p",
        input_file,
        output_file,
    )

    if ret_value.returncode != 0:
        log_err(
            "\tAn error occurred computing the metrics for {}",
            ExitCode.PROGRAMMING_ERROR,
            input_file,
        )
        sys.exit(1)


def run_comparison(
    first_dir: str, second_dir: str, filename: str, output_dir: str
) -> None:
    """Run programming languages comparison."""

    # Compute metrics for the first file
    compute_metrics(first_dir, filename + EXTENSIONS[first_dir])

    # Compute metrics for the second file
    compute_metrics(second_dir, filename + EXTENSIONS[second_dir])

    # Open first json file
    first_json_filename = build_json_name(first_dir, filename)

    # Open second json file
    second_json_filename = build_json_name(second_dir, filename)

    # Compute the difference between two json files
    with tempfile.TemporaryFile(mode = "w+") as fp:
        subprocess.call(
            ["json-diff", "-j", first_json_filename, second_json_filename],
            stdout=fp,
        )
        fp.seek(0)
        json_diff_str = fp.read()

    # Interrupt the comparison if the two json files are identical
    if not json_diff_str:
        log_info(
            "\t{} and {} are identical.",
            first_json_filename,
            second_json_filename,
        )
        return None

    # Load the json diff object
    diff_json = json.loads(json_diff_str)

    # Maintain only global metrics for each file
    for single_file in diff_json["files"]:
        del single_file[1]["spaces"]

    # Dump json file of difference
    output_path = COMPARE_DIR / output_dir / (filename + ".json")
    with open(output_path, "w") as output_file:
        json.dump(diff_json, output_file, indent=4)


def main() -> None:

    # Initialize logging functions
    log_conf(False)

    # Run comparisons
    for filename, languages_conf in FILE_DICT.items():
        for language_conf in languages_conf:
            run_comparison(
                language_conf[0],
                language_conf[1],
                filename,
                language_conf[2],
            )


if __name__ == "__main__":
    main()
