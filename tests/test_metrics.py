"""Test if metrics produced by tools are effectively identical"""

import typing as T

import pytest

from common import compare


def test_rust_code_analysis_tokei() -> None:
    """These tests evaluates if rust-code-analysis and tokei produce
       the same metrics values.
    """

    ret_value = compare(
        "rust-code-analysis",
        "tokei",
        ["-g", "-f"],
        ["SLOC", "LLOC"],
        "C-C++",
        "bubble_sort.c",
    )

    assert ret_value == 0


def test_rust_code_analysis_halstead() -> None:
    """These tests evaluates if rust-code-analysis and Halstead produce
       the same metrics values.
    """

    ret_value = compare(
        "rust-code-analysis",
        "halstead",
        ["-f"],
        ["HALSTEAD"],
        "C-C++",
        "bubble_sort.c",
    )

    assert ret_value == 0


def test_rust_code_analysis_cccc() -> None:
    """These tests evaluates if rust-code-analysis and CCCC produce
       the same metrics values.
    """

    ret_value = compare(
        "rust-code-analysis",
        "cccc",
        ["-fu"],
        ["CC"],
        "C-C++",
        "bubble_sort.c",
    )

    assert ret_value == 0


def test_rust_code_analysis_mi() -> None:
    """These tests evaluates if rust-code-analysis and MI produce
       the same metrics values.
    """

    ret_value = compare(
        "rust-code-analysis",
        "mi",
        ["-fu"],
        ["CC"],
        "C-C++",
        "bubble_sort.c",
    )

    assert ret_value == 0
