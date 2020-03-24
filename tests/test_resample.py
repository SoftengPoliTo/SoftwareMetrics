"""Test if metrics produced by tools are the same for resample"""

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
        ["SLOC", "LLOC", "CLOC"],
        "C-C++",
        "resample.c",
    )

    assert ret_value == 0
