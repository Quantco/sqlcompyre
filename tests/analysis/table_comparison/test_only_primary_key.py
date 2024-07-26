# Copyright (c) QuantCo 2024-2024
# SPDX-License-Identifier: BSD-3-Clause

"""This file contains tests that verify SQLCompyre's behavior when tables contain only
primary keys."""

from typing import Any

import pytest
import sqlalchemy as sa
from sqlalchemy import Column, Integer
from sqlalchemy.engine import Engine

import sqlcompyre as sc
from tests._shared import TableFactory

# -------------------------------------------------------------------------------------------------
# TABLES
# -------------------------------------------------------------------------------------------------


def table_columns() -> list[Column]:
    return [Column("id", Integer(), primary_key=True)]


@pytest.fixture(scope="module")
def table_lhs(table_factory: TableFactory) -> sa.Table:
    data: list[dict[str, Any]] = [dict(id=1), dict(id=2)]
    return table_factory.create("pk_lhs", table_columns(), data)


@pytest.fixture(scope="module")
def table_rhs(table_factory: TableFactory) -> sa.Table:
    data: list[dict[str, Any]] = [dict(id=1), dict(id=2)]
    return table_factory.create("pk_rhs", table_columns(), data)


# -------------------------------------------------------------------------------------------------
# TESTS
# -------------------------------------------------------------------------------------------------


def test_only_pk_row_matches(engine: Engine, table_lhs: sa.Table, table_rhs: sa.Table):
    row_matches = sc.compare_tables(engine, table_lhs, table_rhs).row_matches
    assert row_matches.n_joined_equal == 2
    assert row_matches.n_joined_unequal == 0
