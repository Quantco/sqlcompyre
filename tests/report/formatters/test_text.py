# Copyright (c) QuantCo 2024-2024
# SPDX-License-Identifier: BSD-3-Clause

from sqlcompyre.report.formatters import TextFormatter
from sqlcompyre.report.schema import Metadata, Section
from sqlcompyre.results import ColumnMatches, Counts, Names, RowMatches


def test_format(
    metadata: Metadata,
    names: Names,
    counts: Counts,
    row_matches: RowMatches,
    column_matches: ColumnMatches,
):
    formatter = TextFormatter()
    formatter.format(
        metadata,
        [
            Section("Names", names),
            Section("Counts", counts),
            Section("Row Matches", row_matches),
            Section("Column Matches", column_matches),
        ],
    )
