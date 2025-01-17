# Copyright (c) QuantCo 2024-2025
# SPDX-License-Identifier: BSD-3-Clause

"""This file contains tests that verify SQLCompyre's behavior for NULL values."""

from typing import Any

import pandas as pd
import pytest
import sqlalchemy as sa

import sqlcompyre as sc
from tests._shared import TableFactory

# -------------------------------------------------------------------------------------------------
# TABLES
# -------------------------------------------------------------------------------------------------


def table_columns() -> list[sa.Column]:
    return [
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=False),
        sa.Column("value", sa.Integer(), nullable=True),
    ]


@pytest.fixture(scope="module")
def table_lhs(table_factory: TableFactory) -> sa.Table:
    data: list[dict[str, Any]] = [
        dict(id=1, value=5),
        dict(id=2, value=4),
        dict(id=3, value=3),
        dict(id=4, value=None),
    ]
    return table_factory.create("null_lhs", table_columns(), data)


@pytest.fixture(scope="module")
def table_rhs(table_factory: TableFactory) -> sa.Table:
    data: list[dict[str, Any]] = [
        dict(id=1, value=5),
        dict(id=2, value=6),
        dict(id=3, value=None),
        dict(id=4, value=None),
    ]
    return table_factory.create("null_rhs", table_columns(), data)


# -------------------------------------------------------------------------------------------------
# TESTS
# -------------------------------------------------------------------------------------------------


def test_null_equal(engine: sa.Engine, table_lhs: sa.Table, table_rhs: sa.Table):
    row_matches = sc.compare_tables(engine, table_lhs, table_rhs).row_matches
    assert row_matches.n_joined_total == 4
    assert row_matches.n_joined_equal == 2
    assert row_matches.n_joined_unequal == 2


def test_null_column_matches(
    engine: sa.Engine, table_lhs: sa.Table, table_rhs: sa.Table
):
    column_matches = sc.compare_tables(engine, table_lhs, table_rhs).column_matches
    assert column_matches.fraction_same["value"] == 0.5

    mismatch_values = pd.read_sql(column_matches.mismatch_selects["value"], con=engine)
    assert mismatch_values.shape[0], 2


def test_null_top_changes(
    engine: sa.Engine,
    table_lhs: sa.Table,
    table_rhs: sa.Table,
):
    top_changes = sc.compare_tables(engine, table_lhs, table_rhs).get_top_changes(
        "value"
    )
    expected = {"3 -> NULL": 1, "4 -> 6": 1}
    assert top_changes == expected
