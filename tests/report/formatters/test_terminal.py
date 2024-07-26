# Copyright (c) QuantCo 2024-2024
# SPDX-License-Identifier: BSD-3-Clause

import pytest
from pytest_lazyfixture import lazy_fixture

from sqlcompyre.report.formatters import TerminalFormatter
from sqlcompyre.report.schema import Metadata, Section
from sqlcompyre.results import ColumnMatches, Counts, Names, RowMatches


@pytest.fixture()
def expected_header() -> str:
    return """\
SQLCompyre Comparison of Tables
===============================

 -> 'table1' vs 'table2'
"""


# -------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("colored", [True, False])
def test_format(
    metadata: Metadata,
    names: Names,
    counts: Counts,
    row_matches: RowMatches,
    column_matches: ColumnMatches,
    colored: bool,
):
    formatter = TerminalFormatter(colored)
    formatter.format(
        metadata,
        [
            Section("Names", names),
            Section("Counts", counts),
            Section("Row Matches", row_matches),
            Section("Column Matches", column_matches),
        ],
    )


# -------------------------------------------------------------------------------------------------
# NAMES
# -------------------------------------------------------------------------------------------------


@pytest.fixture()
def expected_names(expected_header: str) -> str:
    txt = """
Names
=====
 Number in common: 1
 Missing in left:  ['hi', 'there']
 Missing in right: ['world']"""
    return expected_header + txt


def test_terminal_formatter_names(
    metadata: Metadata, names: Names, expected_names: str
):
    formatter = TerminalFormatter(colored=False)
    actual = formatter.format(metadata, [Section("Names", names)])
    assert actual == expected_names


# -------------------------------------------------------------------------------------------------
# COUNTS
# -------------------------------------------------------------------------------------------------


@pytest.fixture()
def expected_counts(expected_header: str) -> str:
    txt = """
Counts
======
 Count      |   999 | 1,024
 Difference |   -25 |   +25
 Fraction   | 0.976 | 1.025"""
    return expected_header + txt


def test_terminal_formatter_counts(
    metadata: Metadata, counts: Counts, expected_counts: str
):
    formatter = TerminalFormatter(colored=False)
    actual = formatter.format(metadata, [Section("Counts", counts)])
    assert actual == expected_counts


# -------------------------------------------------------------------------------------------------
# ROW MATCHES
# -------------------------------------------------------------------------------------------------


@pytest.fixture()
def expected_row_matches(expected_header: str) -> str:
    txt = """
Row Matches
===========
 Joined (identical/non-identical) | 1,800 [97.30%] |  50 [2.70%]
 Unjoined (left/right)            |   125  [6.33%] | 175 [8.64%]"""
    return expected_header + txt


def test_terminal_formatter_row_matches(
    metadata: Metadata, row_matches: RowMatches, expected_row_matches: str
):
    formatter = TerminalFormatter(colored=False)
    actual = formatter.format(metadata, [Section("Row Matches", row_matches)])
    assert actual == expected_row_matches


# -------------------------------------------------------------------------------------------------
# COLUMN MATCHES
# -------------------------------------------------------------------------------------------------


@pytest.fixture()
def expected_column_matches(expected_header: str) -> str:
    txt = """
Column Matches
==============
 col1     | 100.00%
 col2     |  97.93%
 unsorted |  25.00%"""
    return expected_header + txt


@pytest.fixture()
def expected_column_matches_hidden(expected_header: str) -> str:
    txt = """
Column Matches
==============
 col2     | 97.93%
 unsorted | 25.00%"""
    return expected_header + txt


@pytest.mark.parametrize(
    ("hide_matching_columns", "expected"),
    [
        (True, lazy_fixture("expected_column_matches_hidden")),
        (False, lazy_fixture("expected_column_matches")),
    ],
)
def test_terminal_formatter_column_matches(
    metadata: Metadata,
    column_matches: ColumnMatches,
    hide_matching_columns: bool,
    expected: str,
):
    formatter = TerminalFormatter(colored=False)
    actual = formatter.format(
        metadata,
        [Section("Column Matches", column_matches)],
        hide_matching_columns=hide_matching_columns,
    )
    assert actual == expected
