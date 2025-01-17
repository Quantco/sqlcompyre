# Copyright (c) QuantCo 2025-2025
# SPDX-License-Identifier: BSD-3-Clause

from duckdb_engine import Dialect as SqlAlchemyDuckdbDialect

from ._base import DialectProtocol


class DuckDBDialect(SqlAlchemyDuckdbDialect, DialectProtocol):  # type: ignore
    name: str = "duckdb"
    verbose_name: str = "DuckDB"
    supports_schemas: bool = False
    supports_multi_part_schemas: bool = False
    case_sensitive_collation: str = "BINARY"
    case_insensitive_collation: str = "NOCASE"
    views_support_notnull_columns: bool = False
