"""Test if metrics produced by tools are the same for resample"""

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
        ["SLOC", "LLOC"],
        "C-C++",
        "resample.c",
    )

    assert ret_value == 0


def test_rust_code_analysis_tokei_rust() -> None:
    """These tests evaluates if rust-code-analysis and tokei produce
       the same metrics values for Rust language.
    """

    ret_value = compare(
        "rust-code-analysis",
        "tokei",
        ["-g", "-f"],
        ["LLOC"], # Do not consider SLOC because it is wrong in Tokei
        "Rust",
        "resample.rs",
    )

    assert ret_value == 0
