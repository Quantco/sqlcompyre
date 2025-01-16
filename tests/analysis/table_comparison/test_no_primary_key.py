# Copyright (c) QuantCo 2024-2025
# SPDX-License-Identifier: BSD-3-Clause

"""This file contains tests that verify SQLCompyre's behavior when tables contain no
matching primary keys."""

from typing import Any

import pytest
import sqlalchemy as sa

import sqlcompyre as sc
from tests._shared import TableFactory

# -------------------------------------------------------------------------------------------------
# TABLES
# -------------------------------------------------------------------------------------------------


def table_columns() -> list[sa.Column]:
    return [sa.Column("id", sa.Integer(), nullable=False)]


def only_nullable_columns() -> list[sa.Column]:
    return [sa.Column("id", sa.Integer())]


def nullable_table_columns() -> list[sa.Column]:
    return [
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("other_with_null", sa.Integer()),
        sa.Column("other_without_null", sa.Integer()),
    ]


@pytest.fixture(scope="module")
def table_lhs(table_factory: TableFactory) -> sa.Table:
    data: list[dict[str, Any]] = [dict(id=1), dict(id=2)]
    return table_factory.create("no_pk_lhs", table_columns(), data)


@pytest.fixture(scope="module")
def table_rhs(table_factory: TableFactory) -> sa.Table:
    data: list[dict[str, Any]] = [dict(id=1), dict(id=2)]
    return table_factory.create("no_pk_rhs", table_columns(), data)


@pytest.fixture(scope="module")
def table_rhs_duplicate(table_factory: TableFactory) -> sa.Table:
    data: list[dict[str, Any]] = [dict(id=1), dict(id=1)]
    return table_factory.create("no_pk_rhs_duplicate", table_columns(), data)


@pytest.fixture(scope="module")
def table_lhs_nullable(table_factory: TableFactory) -> sa.Table:
    data: list[dict[str, Any]] = [
        dict(id=1, other_with_null=None, other_without_null=2),
        dict(id=2, other_with_null=3, other_without_null=6),
    ]
    return table_factory.create("no_pk_lhs_nullable", nullable_table_columns(), data)


@pytest.fixture(scope="module")
def table_rhs_nullable(table_factory: TableFactory) -> sa.Table:
    data: list[dict[str, Any]] = [
        dict(id=1, other_with_null=4, other_without_null=2),
        dict(id=2, other_with_null=3, other_without_null=6),
    ]
    return table_factory.create("no_pk_rhs_nullable", nullable_table_columns(), data)


@pytest.fixture(scope="module")
def table_only_null(table_factory: TableFactory) -> sa.Table:
    data: list[dict[str, Any]] = [dict(id=None)]
    return table_factory.create("only_null", only_nullable_columns(), data)


# -------------------------------------------------------------------------------------------------
# TESTS
# -------------------------------------------------------------------------------------------------


def test_no_pk_row_matches(engine: sa.Engine, table_lhs: sa.Table, table_rhs: sa.Table):
    # Do not fail immediately if not inferring primary keys...
    comparison = sc.compare_tables(engine, table_lhs, table_rhs)
    assert comparison.row_counts.equal
    assert comparison.column_names.equal

    with pytest.raises(ValueError):
        # ...but when calling row_matches
        comparison.row_matches

    # Succeed if inferring primary key
    row_matches = sc.compare_tables(
        engine, table_lhs, table_rhs, infer_primary_keys=True
    ).row_matches
    assert row_matches.n_joined_equal == 2
    assert row_matches.n_joined_unequal == 0


def test_no_pk_row_matches_duplicates(
    engine: sa.Engine, table_lhs: sa.Table, table_rhs_duplicate: sa.Table
):
    with pytest.raises(ValueError, match="would cause duplicates"):
        sc.compare_tables(
            engine, table_lhs, table_rhs_duplicate, infer_primary_keys=True
        ).row_matches


def test_no_pk_row_matches_nulls(engine: sa.Engine, table_only_null: sa.Table):
    with pytest.raises(ValueError, match="no non-null columns"):
        sc.compare_tables(
            engine, table_only_null, table_only_null, infer_primary_keys=True
        ).row_matches


def test_no_pk_row_matches_nullable_columns(
    engine: sa.Engine, table_lhs_nullable: sa.Table, table_rhs_nullable: sa.Table
):
    comparison = sc.compare_tables(
        engine, table_lhs_nullable, table_rhs_nullable, infer_primary_keys=True
    )
    assert comparison.join_columns == ["id", "other_without_null"]

    # When joining on ID and other_without_null, this should cause...
    row_matches = comparison.row_matches
    assert row_matches.n_joined_equal == 1
    assert row_matches.n_joined_unequal == 1
