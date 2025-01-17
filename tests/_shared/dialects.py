# Copyright (c) QuantCo 2024-2025
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

import os

import sqlalchemy as sa

from sqlcompyre.analysis.dialects import DialectProtocol


def dialect_from_env() -> DialectProtocol:
    """Read the dialect from the process environment.

    This function assumes that ``DB_CONNECTION_STRING`` is set to a proper database
    connection string. **Use this function with care!** Typically, it should only be
    used for ``pytest.mark.skipif`` statements.
    """
    conn = sa.make_url(os.environ["DB_CONNECTION_STRING"])
    return dialect_from_connection_url(conn)


def dialect_from_connection_url(conn_url: sa.URL) -> DialectProtocol:
    """Get dialect metadata from the connection URL."""
    dialect = sa.create_engine(conn_url).dialect
    match dialect.name:
        case "mssql":
            from sqlcompyre.analysis.dialects import MssqlDialect

            return MssqlDialect()
        case "sqlite":
            from sqlcompyre.analysis.dialects import SQLiteDialect

            return SQLiteDialect()
        case "duckdb":
            from sqlcompyre.analysis.dialects import DuckDBDialect

            return DuckDBDialect()  # type: ignore
        case _:
            raise NotImplementedError
