"""Test if metrics produced by tools are effectively identical"""

import pathlib
import subprocess
import typing as T

import pytest

INPUT_DIR = pathlib.Path("Assets")
RESULTS_DIR = pathlib.Path("Results")


def _run_subprocess(cmd: str, *args: T.Any) -> int:
    ret = subprocess.run([cmd, *args])
    return ret.returncode


def _build_metrics_path(folder: str, tool_name: str) -> pathlib.Path:
    output_file = folder + "_" + tool_name + ".json"
    return RESULTS_DIR / folder / output_file


def compare(
    first_tool_name: str,
    second_tool_name: str,
    metrics: T.List[str],
    folder: str,
    filename: str,
) -> int:

    input_file = INPUT_DIR / folder / filename
    output_file = RESULTS_DIR / folder

    ret_value = _run_subprocess(
        "./analyzer.py",
        "-tm",
        "-t",
        first_tool_name,
        second_tool_name,
        "-p",
        input_file,
        output_file,
    )

    if ret_value != 0:
        return 1

    ret_value = _run_subprocess(
        "./metric-diff.py",
        "-m",
        *metrics,
        "-i",
        _build_metrics_path(folder, first_tool_name),
        _build_metrics_path(folder, second_tool_name),
    )

    if ret_value != 0:
        return 1

    return 0


def test_tokei_rust_code_analysis() -> None:
    """These tests evaluates if different tools produce same metrics values.
    """

    ret_value = compare(
        "tokei",
        "rust-code-analysis",
        ["SLOC", "LOC"],
        "C-C++",
        "bubble_sort.c",
    )

    assert ret_value == 0
