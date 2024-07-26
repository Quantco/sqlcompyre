# Copyright (c) QuantCo 2024-2024
# SPDX-License-Identifier: BSD-3-Clause


from sqlalchemy.dialects.sqlite import dialect as SqlAlchemySqliteDialect  # noqa: N812

from ._base import DialectProtocol


class SQLiteDialect(SqlAlchemySqliteDialect, DialectProtocol):  # type: ignore
    name: str = "sqlite"
    verbose_name: str = "SQLite"
    supports_schemas: bool = False
    supports_multi_part_schemas: bool = False
    case_sensitive_collation: str = "BINARY"
    case_insensitive_collation: str = "NOCASE"
    views_support_notnull_columns: bool = False
