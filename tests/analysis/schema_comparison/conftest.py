# Copyright (c) QuantCo 2024-2025
# SPDX-License-Identifier: BSD-3-Clause

import time

import pytest
import sqlalchemy as sa

from tests._shared import SchemaFactory, TableFactory


def table_columns() -> list[sa.Column]:
    return [
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=False),
        sa.Column("value", sa.Integer()),
    ]


def table_columns_no_pk() -> list[sa.Column]:
    return [sa.Column("id", sa.Integer())]


@pytest.fixture(scope="session")
def schema_1(engine: sa.Engine, schema_factory: SchemaFactory) -> str:
    schema = schema_factory.create("compyre_full_1")
    factory = TableFactory(engine, schema)
    factory.create("table4", table_columns(), [])
    time.sleep(0.5)  # sleep to ensure that timing tests succeed
    table1 = factory.create("table1", table_columns(), [dict(id=1, value=5)])
    time.sleep(0.5)  # sleep to ensure that timing tests succeed
    table2 = factory.create("table2", table_columns(), [])
    time.sleep(0.5)  # sleep to ensure that timing tests succeed
    factory.create("table3", table_columns(), [])
    factory.create_view("view1", sa.select(table1))
    factory.create_view("view2", sa.select(table2))
    return schema


@pytest.fixture(scope="session")
def schema_2(engine: sa.Engine, schema_factory: SchemaFactory) -> str:
    schema = schema_factory.create("compyre_full_2")
    factory = TableFactory(engine, schema)
    table1 = factory.create("table1", table_columns(), [dict(id=1, value=4)])
    time.sleep(0.5)  # sleep to ensure that timing tests succeed
    factory.create("table4", table_columns(), [])
    time.sleep(0.5)  # sleep to ensure that timing tests succeed
    factory.create("table5", table_columns(), [])
    factory.create_view("view1", sa.select(table1))
    return schema


@pytest.fixture(scope="session")
def schema_duplicate_table(engine: sa.Engine, schema_factory: SchemaFactory) -> str:
    schema = schema_factory.create("compyre_full_3")
    factory = TableFactory(engine, schema)
    factory.create("table1", table_columns_no_pk(), [dict(id=1), dict(id=1)])
    return schema
