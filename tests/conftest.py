# Copyright (c) QuantCo 2024-2025
# SPDX-License-Identifier: BSD-3-Clause

import os

import pytest
import sqlalchemy as sa

from tests._shared import SchemaFactory, TableFactory, dialect_from_env


@pytest.fixture(autouse=True)
def skip_for_dialect(request, engine):
    marker_name = "skip_dialect"
    if request.node.get_closest_marker(marker_name):
        # marker will only have one argument, so accessing args[0] is fine
        dialect = request.node.get_closest_marker(marker_name).args[0]
        if dialect in engine.name:
            pytest.skip(f"test was skipped for engine dialect: {dialect}")


# -------------------------------------------------------------------------------------------------
# DATABASE CONNECTION
# -------------------------------------------------------------------------------------------------


@pytest.fixture(scope="session")
def connection_string() -> sa.URL:
    return sa.make_url(os.environ["DB_CONNECTION_STRING"])


@pytest.fixture(scope="session")
def connection_string_raw_string(connection_string: sa.URL) -> str:
    return connection_string.render_as_string(hide_password=False)


@pytest.fixture(scope="session")
def engine(connection_string: sa.URL) -> sa.Engine:
    return sa.create_engine(connection_string)


# -------------------------------------------------------------------------------------------------
# SCHEMA FACTORIES
# -------------------------------------------------------------------------------------------------


@pytest.fixture(scope="session")
def schema_factory(connection_string: sa.URL) -> SchemaFactory:
    return SchemaFactory(connection_string)


# -------------------------------------------------------------------------------------------------
# TABLE FACTORIES
# -------------------------------------------------------------------------------------------------


@pytest.fixture(scope="session")
def table_factory(engine: sa.Engine, schema_factory: SchemaFactory) -> TableFactory:
    if not engine.dialect.supports_schemas:  # type: ignore
        return TableFactory(engine, None)
    schema = schema_factory.create("compyre_test")
    return TableFactory(engine, schema)


@pytest.mark.skipif(
    not dialect_from_env().supports_schemas,
    reason="Database system does not support schemas.",
)
@pytest.fixture(scope="session")
def table_factory_extra(
    engine: sa.Engine, schema_factory: SchemaFactory
) -> TableFactory:
    schema = schema_factory.create("compyre_test_extra")
    return TableFactory(engine, schema)
