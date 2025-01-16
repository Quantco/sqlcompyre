# Copyright (c) QuantCo 2024-2025
# SPDX-License-Identifier: BSD-3-Clause

from datetime import datetime
from typing import Protocol

import sqlalchemy as sa


class DialectProtocol(Protocol):
    """This class is to be used to ensure that a dialect implements all required methods
    & functionality to work within SQLCompyre.

    A dialect is essentially a collection of database-related functions that differ between
    database management systems. :class:`~sqlcompyre.analysis.table_comparison.TableComparison`
    and :class:`~sqlcompyre.analysis.schema_comparison.SchemaComparison` delegate all operations
    where SQLAlchemy cannot sensibly abstract the underlying database system to dialects.
    We make extended use of sqlalchemy's default dialects and extend them whenever possible.

    To ensure that all our extensions follow the same interface (and to get better IDE support)
    we therefore also implement this Protocol.
    """

    # variables that (in addition to sqlalchemy's variables) should be set for every dialect

    #: A unique identifier of the dialect, taken from SQLAlchemy.
    name: str
    #: The common name of the dialect.
    verbose_name: str
    #: Whether the database has a concept of schemas.
    supports_schemas: bool
    #: Whether the database supports multi-part schemas, i.e. queries across databases.
    supports_multi_part_schemas: bool
    #: Case-sensitive collation to use for string comparisons.
    case_sensitive_collation: str
    #: Case-insensitive collation to use for string comparisons.
    case_insensitive_collation: str
    #: Whether views have a notion of NOT NULL columns.
    views_support_notnull_columns: bool

    def get_table_creation_timestamps(
        self, engine: sa.Engine, tables: list[sa.Table]
    ) -> list[datetime]:
        """Obtain the creation timestamps from a list of tables.

        Args:
            engine: The engine to use for connecting to the database and querying creation
                timestamps.
            tables: The list of tables to query the creation dates for.

        Returns:
            The creation timestamps of the tables given to this method, ordered in the same way as
            the input.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support querying table creation timestamps"
        )
