# Copyright (c) QuantCo 2024-2025
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property, lru_cache
from typing import Any

import sqlalchemy as sa


class QueryInspection:
    """Inspect the results of a SQL query.

    Note:
        This class should never be initialized directly. Use the :meth:`~sqlcompyre.api.inspect`
        or :meth:`~sqlcompyre.api.inspect_table` functions instead.
    """

    def __init__(self, engine: sa.Engine, query: sa.FromClause):
        """
        Args:
            engine: The engine to use for connecting to the database.
            query: The query whose results to inspect.
        """
        self.engine = engine
        self.query = query

    @cached_property
    def row_count(self) -> int:
        """Get the number of rows returned by the query."""
        with self.engine.connect() as conn:
            return conn.execute(
                sa.select(sa.func.count()).select_from(self.query)
            ).scalar_one()

    @lru_cache
    def distinct_row_count(self, *columns: str) -> int:
        """Get the number of rows with distinct values wrt. to the provided column(s).

        Args:
            columns: The set of columns to compute the number of distinct values for. If no
                columns are provided, the number of distinct rows (across all columns) is computed.

        Returns:
            The number of distinct rows.
        """

        if len(columns) == 0:
            data_query = sa.select(self.query).distinct()

        else:
            data_query = (
                sa.select(sa.text(", ".join(columns)))
                .distinct()
                .select_from(self.query)
            )

        count_query = sa.select(sa.func.count()).select_from(data_query.subquery())
        with self.engine.connect() as conn:
            return conn.execute(count_query).scalar_one()

    @lru_cache
    def column_stats(self, column: str) -> ColumnStats:
        """Obtain statistics about a single column.

        Args:
            column: The name of the column to obtain information about.

        Returns:
            An object providing access to column statistics.
        """
        return ColumnStats(self.engine, self.query.c[column])


# ----------------------------------------- COLUMN STATS ---------------------------------------- #


@dataclass
class ColumnStats:
    """Obtain statistics about column values in a table."""

    def __init__(self, engine: sa.Engine, column: sa.ColumnElement):
        self.engine = engine
        self.column = column

    @cached_property
    def min(self) -> Any | None:
        """The minimum value in the column."""
        query = sa.select(sa.func.min(self.column))
        with self.engine.connect() as conn:
            return conn.execute(query).scalar()

    @cached_property
    def max(self) -> Any | None:
        """The maximum value in the column."""
        query = sa.select(sa.func.max(self.column))
        with self.engine.connect() as conn:
            return conn.execute(query).scalar()
