# Copyright (c) QuantCo 2024-2025
# SPDX-License-Identifier: BSD-3-Clause

from typing import Any

import pytest
import sqlalchemy as sa

import sqlcompyre as sc
from tests._shared import TableFactory

# -------------------------------------------------------------------------------------------------
# TABLES
# -------------------------------------------------------------------------------------------------


def table_columns() -> list[sa.Column]:
    return [sa.Column("id", sa.Integer())]


@pytest.fixture(scope="module")
def table_with_null_1(table_factory: TableFactory) -> sa.Table:
    data: list[dict[str, Any]] = [dict(id=None), dict(id=2)]
    return table_factory.create("equal_with_null_1", table_columns(), data)


@pytest.fixture(scope="module")
def table_with_null_2(table_factory: TableFactory) -> sa.Table:
    data: list[dict[str, Any]] = [dict(id=2), dict(id=3)]
    return table_factory.create("equal_with_null_2", table_columns(), data)


@pytest.fixture(scope="module")
def table_with_duplicates_1(table_factory: TableFactory) -> sa.Table:
    data: list[dict[str, Any]] = [dict(id=2), dict(id=2), dict(id=3)]
    return table_factory.create("equal_with_duplicates_1", table_columns(), data)


@pytest.fixture(scope="module")
def table_with_duplicates_2(table_factory: TableFactory) -> sa.Table:
    data: list[dict[str, Any]] = [dict(id=2), dict(id=2), dict(id=3), dict(id=4)]
    return table_factory.create("equal_with_duplicates_2", table_columns(), data)


# -------------------------------------------------------------------------------------------------
# TESTS
# -------------------------------------------------------------------------------------------------


def test_equal_ok(engine: sa.Engine, table_students: sa.Table):
    comparison = sc.compare_tables(engine, table_students, table_students)
    assert comparison.equal


def test_equal_err_count(
    engine: sa.Engine, table_students: sa.Table, table_students_small: sa.Table
):
    comparison = sc.compare_tables(engine, table_students, table_students_small)
    assert not comparison.equal


def test_equal_err_columns(
    engine: sa.Engine, table_students: sa.Table, table_students_narrow: sa.Table
):
    comparison = sc.compare_tables(engine, table_students, table_students_narrow)
    assert not comparison.equal


def test_equal_err_joined_unequal(
    engine: sa.Engine, table_students: sa.Table, table_students_modified_3: sa.Table
):
    comparison = sc.compare_tables(engine, table_students, table_students_modified_3)
    assert not comparison.equal


def test_equal_ok_no_join_columns_null(engine: sa.Engine, table_with_null_1: sa.Table):
    comparison = sc.compare_tables(engine, table_with_null_1, table_with_null_1)
    assert comparison.equal


def test_equal_err_no_join_columns_null(
    engine: sa.Engine, table_with_null_1: sa.Table, table_with_null_2: sa.Table
):
    comparison = sc.compare_tables(engine, table_with_null_1, table_with_null_2)
    assert not comparison.equal


def test_equal_ok_no_join_columns_duplicates(
    engine: sa.Engine, table_with_duplicates_1: sa.Table
):
    comparison = sc.compare_tables(
        engine, table_with_duplicates_1, table_with_duplicates_1
    )
    assert comparison.equal


def test_equal_err_no_join_columns_duplicates(
    engine: sa.Engine,
    table_with_duplicates_1: sa.Table,
    table_with_duplicates_2: sa.Table,
):
    comparison = sc.compare_tables(
        engine, table_with_duplicates_1, table_with_duplicates_2
    )
    assert not comparison.equal
