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
        # Do not consider BLANK for this case because TOKEI
        # counts blank lines inside comments.
        # Do not consider CLOC because comments are counted differently
        # among the two software.
        ["SLOC", "PLOC"],
        "C",
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
        # Do not consider SLOC because it is computed wrong in Tokei.
        # Do not consider CLOC because comments are counted differently
        # among the two software.
        ["PLOC", "BLANK"],
        "Rust",
        "resample.rs",
    )

    assert ret_value == 0
