# Copyright (c) QuantCo 2024-2025
# SPDX-License-Identifier: BSD-3-Clause


from functools import cached_property, lru_cache

import sqlalchemy as sa


class QueryInspection:
    """Inspect the results of a SQL query.

    Note:
        This class should never be initialized directly. Use the :meth:`~sqlcompyre.api.inspect`
        or :meth:`~sqlcompyre.api.inspect_table` functions instead.
    """

    def __init__(self, engine: sa.Engine, selectable: sa.Select):
        """
        Args:
            engine: The engine to use for connecting to the database.
            query: The query whose results to inspect.
        """
        self.engine = engine
        self.query = selectable

    @cached_property
    def row_count(self) -> int:
        """Get the number of rows returned by the query."""
        with self.engine.connect() as conn:
            return conn.execute(
                sa.select(sa.func.count()).select_from(self.query.subquery())
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
            data_query = self.query.distinct()

        else:
            subquery = self.query.subquery()
            data_query = (
                sa.select(sa.text(", ".join(columns))).distinct().select_from(subquery)
            )

        count_query = sa.select(sa.func.count()).select_from(data_query.subquery())
        with self.engine.connect() as conn:
            return conn.execute(count_query).scalar_one()
