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
import typing as T

from exit_codes import ExitCode, log_conf, log_err, log_info

INPUT_DIR = pathlib.Path("Assets")
RESULTS_DIR = pathlib.Path("Results")
COMPARE_DIR = pathlib.Path("Compare")

# The extensions of files present in a directory
EXTENSIONS = {"C": ".c", "Rust": ".rs"}


class Conf(enum.Enum):
    """ Each configuration contains some information to compare a pair
        of programming languages """

    C_RUST = ["C", "Rust", "C-Rust"]


# Pair of files and configurations associated
FILE_DICT = {
    "binarytrees": Conf.C_RUST.value,
    "fannkuchredux": Conf.C_RUST.value,
    "fasta": Conf.C_RUST.value,
    "knucleotide": Conf.C_RUST.value,
    "mandelbrot": Conf.C_RUST.value,
    "nbody": Conf.C_RUST.value,
    "pidigits": Conf.C_RUST.value,
    "regexredux": Conf.C_RUST.value,
    "revcomp": Conf.C_RUST.value,
    "spectralnorm": Conf.C_RUST.value,
}


def run_subprocess(cmd: str, *args: T.Any) -> subprocess.CompletedProcess:
    return subprocess.run([cmd, *args], text=True, capture_output=True)


def build_json_name(directory: str, filename: str) -> pathlib.Path:
    output_file = directory + "_" + filename + EXTENSIONS[directory] + ".json"
    return RESULTS_DIR / directory / output_file


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

    # Compute the difference between json files
    ret_value = run_subprocess(
        "json-diff", "-j", first_json_filename, second_json_filename
    )

    # Interrupt the comparison if two files are identical
    if not ret_value.stdout:
        log_info(
            "\t{} and {} are identical.",
            first_json_filename,
            second_json_filename,
        )
        return None

    # Load json file of difference
    diff_json = json.loads(ret_value.stdout)

    # Maintain only global metrics for each file
    for single_file in diff_json["files"]:
        del single_file[1]["functions"]

    # Dump json file of difference
    output_path = COMPARE_DIR / output_dir / (filename + ".json")
    with open(output_path, "w") as output_file:
        json.dump(diff_json, output_file, indent=4)


def main() -> None:

    # Initialize logging functions
    log_conf(False)

    # Run comparisons
    for filename, language_conf in FILE_DICT.items():
        run_comparison(
            language_conf[0], language_conf[1], filename, language_conf[2],
        )


if __name__ == "__main__":
    main()
