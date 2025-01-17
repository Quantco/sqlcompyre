# Copyright (c) QuantCo 2024-2025
# SPDX-License-Identifier: BSD-3-Clause

import pytest
import sqlalchemy as sa

from tests._shared import SchemaFactory, TableFactory


def table_columns() -> list[sa.Column]:
    return [
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=False),
        sa.Column("value", sa.Integer()),
    ]


def table_columns_alt() -> list[sa.Column]:
    return [sa.Column("new_id", sa.Integer(), primary_key=True, autoincrement=False)]


@pytest.fixture(scope="session")
def schema_1(engine: sa.Engine, schema_factory: SchemaFactory) -> str:
    schema = schema_factory.create("compyre_cli_1")
    factory = TableFactory(engine, schema)
    factory.create("table1", table_columns(), [dict(id=1, value=5)])
    factory.create("table2", table_columns(), [dict(id=1, value=5)])
    factory.create("table3", table_columns(), [])
    return schema


@pytest.fixture(scope="session")
def schema_2(engine: sa.Engine, schema_factory: SchemaFactory) -> str:
    schema = schema_factory.create("compyre_cli_2")
    factory = TableFactory(engine, schema)
    factory.create("table1", table_columns(), [dict(id=1, value=4)])
    factory.create("table2", table_columns(), [dict(id=1, value=4)])
    factory.create("table3", table_columns(), [])
    return schema


@pytest.fixture(scope="session")
def table_1(table_factory: TableFactory) -> sa.Table:
    return table_factory.create("cli_1", table_columns(), [dict(id=1)])


@pytest.fixture(scope="session")
def table_2(table_factory: TableFactory) -> sa.Table:
    return table_factory.create("cli_2", table_columns(), [dict(id=2)])


@pytest.fixture(scope="session")
def table_3(table_factory: TableFactory) -> sa.Table:
    return table_factory.create("cli_3", table_columns_alt(), [dict(new_id=2)])
