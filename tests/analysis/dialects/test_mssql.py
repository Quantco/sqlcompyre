# Copyright (c) QuantCo 2024-2025
# SPDX-License-Identifier: BSD-3-Clause

import time
import uuid
from datetime import datetime

import pytest
import sqlalchemy as sa

from sqlcompyre.analysis.dialects import MssqlDialect
from tests._shared import SchemaFactory, TableFactory, dialect_from_env

pytestmark = pytest.mark.skipif(
    dialect_from_env().name != "mssql",
    reason="Tests only run for Microsoft SQL Server.",
)


def table_columns() -> list[sa.Column]:
    return [sa.Column("id", sa.Integer(), primary_key=True, autoincrement=False)]


@pytest.fixture(scope="session")
def creation_timestamp() -> datetime:
    return datetime.utcnow()


@pytest.fixture()  # do not use a scope here as this fixture is modified in tests
def schema_and_tables_and_views(
    engine: sa.Engine,
    schema_factory: SchemaFactory,
    creation_timestamp: datetime,  # keep here to initialize the fixture
) -> tuple[str, sa.Table, sa.Table, sa.Table]:
    schema = schema_factory.create(str(uuid.uuid4()))
    factory = TableFactory(engine, schema)
    table1 = factory.create("table1", table_columns(), [])
    time.sleep(0.01)
    table2 = factory.create("table2", table_columns(), [])
    time.sleep(0.01)
    view1 = factory.create_view("view1", sa.select(table1))
    return schema, table1, table2, view1


# -------------------------------------------------------------------------------------------------


def test_get_table_creation_timestamps(
    engine: sa.Engine,
    schema_and_tables_and_views: tuple[str, sa.Table, sa.Table, sa.Table],
    creation_timestamp: datetime,
):
    _, table1, table2, view1 = schema_and_tables_and_views
    timestamps = engine.dialect.get_table_creation_timestamps(  # type: ignore
        engine,
        tables=[table2, table1, view1],
    )
    assert len(timestamps) == 3
    assert all(t > creation_timestamp for t in timestamps)
    assert timestamps[0] > timestamps[1]
    assert timestamps[2] > timestamps[1]
    assert timestamps[2] > timestamps[0]


def test_get_table_creation_timestamps_different_database(
    engine: sa.Engine,
    schema_and_tables_and_views: tuple[str, sa.Table, sa.Table, sa.Table],
):
    _, table1, table2, _ = schema_and_tables_and_views
    table1.schema = "unknown.dbo"
    dialect = MssqlDialect()
    with pytest.raises(ValueError, match="within a single database"):
        dialect.get_table_creation_timestamps(engine, tables=[table2, table1])


def test_get_table_creation_timestamps_different_multipart(
    engine: sa.Engine,
    schema_and_tables_and_views: tuple[str, sa.Table, sa.Table, sa.Table],
):
    _, table1, table2, _ = schema_and_tables_and_views
    table1.schema = table1.schema.split(".")[-1]  # type: ignore
    dialect = MssqlDialect()
    with pytest.raises(ValueError, match="must have the same number of schema parts"):
        dialect.get_table_creation_timestamps(engine, tables=[table2, table1])
