# Copyright (c) QuantCo 2024-2025
# SPDX-License-Identifier: BSD-3-Clause

"""This file contains tests that verify SQLCompyre's behavior for comparing string
values under various collections."""

from typing import Any

import pytest
import sqlalchemy as sa

import sqlcompyre as sc
from tests._shared import TableFactory

# -------------------------------------------------------------------------------------------------
# TABLES
# -------------------------------------------------------------------------------------------------


def table_columns(engine: sa.Engine) -> list[sa.Column]:
    return [
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=False),
        sa.Column(
            "value",
            sa.String(collation=engine.dialect.case_insensitive_collation),  # type: ignore
        ),
        sa.Column(
            "value_case_sensitive",
            sa.String(collation=engine.dialect.case_sensitive_collation),  # type: ignore
        ),
        sa.Column("non_str_value", sa.Integer()),
    ]


@pytest.fixture(scope="module")
def table_lhs(table_factory: TableFactory, engine: sa.Engine) -> sa.Table:
    data: list[dict[str, Any]] = [
        dict(id=1, value="test", value_case_sensitive="test", non_str_value=1),
        dict(id=2, value="Test", value_case_sensitive="Test", non_str_value=1),
    ]
    return table_factory.create("str_lhs", table_columns(engine), data)


@pytest.fixture(scope="module")
def table_rhs(table_factory: TableFactory, engine: sa.Engine) -> sa.Table:
    data: list[dict[str, Any]] = [
        dict(id=1, value="test", value_case_sensitive="test", non_str_value=1),
        dict(id=2, value="TEST", value_case_sensitive="TEST", non_str_value=1),
    ]
    return table_factory.create("str_rhs", table_columns(engine), data)


# -------------------------------------------------------------------------------------------------
# TESTS
# -------------------------------------------------------------------------------------------------


def test_str_equal_no_collation(
    engine: sa.Engine, table_lhs: sa.Table, table_rhs: sa.Table
):
    column_matches = sc.compare_tables(engine, table_lhs, table_rhs).column_matches
    assert column_matches.fraction_same["value"] == 1
    assert column_matches.fraction_same["value_case_sensitive"] == 0.5
    assert column_matches.fraction_same["non_str_value"] == 1


def test_str_equal_case_sensitive_collation(
    engine: sa.Engine,
    table_lhs: sa.Table,
    table_rhs: sa.Table,
):
    column_matches = sc.compare_tables(
        engine,
        table_lhs,
        table_rhs,
        collation=engine.dialect.case_sensitive_collation,  # type: ignore
    ).column_matches
    assert column_matches.fraction_same["value"] == 0.5
    assert column_matches.fraction_same["value_case_sensitive"] == 0.5
    assert column_matches.fraction_same["non_str_value"] == 1
