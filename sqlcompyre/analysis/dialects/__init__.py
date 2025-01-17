# Copyright (c) QuantCo 2024-2025
# SPDX-License-Identifier: BSD-3-Clause

from sqlalchemy.dialects import registry

from ._base import DialectProtocol

__all__ = ["DialectProtocol"]

# -------------------------------------------------------------------------------------------------
# MSSQL
# -------------------------------------------------------------------------------------------------

try:
    from .mssql import MssqlDialect  # noqa

    MssqlDialect.supports_statement_cache = False
    registry.register(
        "mssql.pyodbc",
        "sqlcompyre.analysis.dialects",
        "MssqlDialect",
    )
except ImportError:
    pass

# -------------------------------------------------------------------------------------------------
# SQLite
# -------------------------------------------------------------------------------------------------

try:
    from .sqlite import SQLiteDialect  # noqa

    registry.register(
        "sqlite",
        "sqlcompyre.analysis.dialects",
        "SQLiteDialect",
    )
except ImportError:
    pass

# -------------------------------------------------------------------------------------------------
# DuckDB
# -------------------------------------------------------------------------------------------------

try:
    from .duckdb import DuckDBDialect  # noqa

    registry.register(
        "duckdb",
        "sqlcompyre.analysis.dialects",
        "DuckDBDialect",
    )
except ImportError:
    pass
