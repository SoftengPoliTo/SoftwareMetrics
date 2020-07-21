"""Test if metrics produced by tools are the same for bubble_sort"""

import typing as T

import pytest

from common import compare


def test_rust_code_analysis_tokei_c() -> None:
    """These tests evaluates if rust-code-analysis and tokei produce
       the same metrics values for C language.
    """

    ret_value = compare(
        "rust-code-analysis",
        "tokei",
        ["-g", "-f"],
        ["SLOC", "LLOC", "CLOC"],
        "C-C++",
        "bubble_sort.c",
    )

    assert ret_value == 0


def test_rust_code_analysis_tokei_Rust() -> None:
    """These tests evaluates if rust-code-analysis and tokei produce
       the same metrics values for Rust language.
    """

    ret_value = compare(
        "rust-code-analysis",
        "tokei",
        ["-g", "-f"],
        ["SLOC", "LLOC", "CLOC"],
        "Rust",
        "bubble_sort.rs",
    )

    assert ret_value == 0
