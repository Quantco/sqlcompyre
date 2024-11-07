# Copyright (c) QuantCo 2024-2024
# SPDX-License-Identifier: BSD-3-Clause

import pytest

from sqlcompyre.report.schema import Metadata
from sqlcompyre.results import ColumnMatches, Counts, Names, RowMatches


@pytest.fixture()
def metadata() -> Metadata:
    return Metadata("tables", "table1", "table2", None)


@pytest.fixture()
def metadata_description() -> Metadata:
    return Metadata("tables", "table1", "table2", "This is a\nmultiline description")


@pytest.fixture()
def names() -> Names:
    return Names(
        left={"hello", "world"},
        right={"hello", "hi", "there"},
        name_mapping=None,
        ignore_casing=False,
    )


@pytest.fixture()
def counts() -> Counts:
    return Counts(left=999, right=1024)


@pytest.fixture()
def row_matches() -> RowMatches:
    return RowMatches(
        n_unjoined_left=125,
        n_unjoined_right=175,
        n_joined_equal=1800,
        n_joined_unequal=50,
        n_joined_total=1850,
        joined_equal=None,  # type: ignore
        joined_unequal=None,  # type: ignore
        joined_total=None,  # type: ignore
        unjoined_left=None,  # type: ignore
        unjoined_right=None,  # type: ignore
    )


@pytest.fixture()
def column_matches() -> ColumnMatches:
    return ColumnMatches(
        fraction_same={"unsorted": 0.25, "col1": 1, "col2": 0.9793221},
        mismatch_selects={},
    )
