# Copyright (c) QuantCo 2024-2025
# SPDX-License-Identifier: BSD-3-Clause

"""This file contains tests that verify basic behavior of the column-specific
comparison."""

import math
from typing import Any

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
        sa.Column("value_1", sa.Integer(), nullable=True),
    ]


@pytest.fixture(scope="module")
def anonymous_table_lhs(table_factory: TableFactory) -> sa.Table:
    data: list[dict[str, Any]] = [
        dict(id=1, value=2, value_1=3),
        dict(id=2, value=4, value_1=5),
    ]
    return table_factory.create("anon_1", table_columns(), data)


@pytest.fixture(scope="module")
def anonymous_table_rhs(table_factory: TableFactory) -> sa.Table:
    data: list[dict[str, Any]] = [
        dict(id=1, value=2, value_1=3),
        dict(id=2, value=4, value_1=5),
    ]
    return table_factory.create("anon_2", table_columns(), data)


# -------------------------------------------------------------------------------------------------
# TESTS
# -------------------------------------------------------------------------------------------------


def test_column_matches_percentages_different(
    engine: sa.Engine,
    table_students_modified_1: sa.Table,
    table_students_modified_2: sa.Table,
):
    column_matches = sc.compare_tables(
        engine, table_students_modified_1, table_students_modified_2
    ).column_matches
    assert math.isclose(column_matches.fraction_same["name"], 1)
    assert math.isclose(column_matches.fraction_same["age"], 2 / 3, rel_tol=1e-6)


def test_column_matches_percentages_different_dbs(
    engine: sa.Engine,
    table_students_modified_1: sa.Table,
    table_students_modified_2: sa.Table,
):
    column_matches = sc.compare_tables(
        engine, table_students_modified_1, table_students_modified_2
    ).column_matches
    assert math.isclose(column_matches.fraction_same["name"], 1)
    assert math.isclose(column_matches.fraction_same["age"], 2 / 3, rel_tol=1e-6)


def test_column_matches_percentages_same(engine: sa.Engine, table_students: sa.Table):
    column_matches = sc.compare_tables(
        engine, table_students, table_students
    ).column_matches
    assert math.isclose(column_matches.fraction_same["name"], 1)
    assert math.isclose(column_matches.fraction_same["age"], 1)


def test_column_matches_percentages_same_selects(
    engine: sa.Engine, table_students: sa.Table
):
    column_matches = sc.compare_tables(
        engine, table_students, table_students
    ).column_matches
    with engine.connect() as conn:
        assert all(
            conn.execute(q).all() == []
            for q in column_matches.mismatch_selects.values()
        )


def test_column_matches_anonymous_table_column_naming(
    engine: sa.Engine, anonymous_table_lhs: sa.Table, anonymous_table_rhs: sa.Table
):
    column_matches = sc.compare_tables(
        engine, anonymous_table_lhs, anonymous_table_rhs
    ).column_matches
    assert math.isclose(column_matches.fraction_same["value"], 1)
