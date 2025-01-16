# Copyright (c) QuantCo 2024-2025
# SPDX-License-Identifier: BSD-3-Clause

from dataclasses import dataclass

import sqlalchemy as sa


@dataclass
class RowMatches:
    """Investigate (un-)matched rows between database tables."""

    #: Number of columns in the left table that could not be joined
    n_unjoined_left: int
    #: Number of columns in the right table that could not be joined
    n_unjoined_right: int
    #: Number of rows that were joined for which the values in both tables were identical
    n_joined_equal: int
    #: Number of rows that were joined for which the values in both tables were not identical
    n_joined_unequal: int
    #: Number of rows that could be joined
    n_joined_total: int
    #: Query for obtaining all rows from the left table that could not be joined.
    unjoined_left: sa.Select
    #: Query for obtaining all rows from the right table that could not be joined.
    unjoined_right: sa.Select
    #: Query for obtaining all rows that could be joined and were identical across the two tables.
    joined_equal: sa.Select
    #: Query for obtaining all rows that could be joined but were not identical.
    joined_unequal: sa.Select
    #: Query for obtaining all rows that were joined, regardless of equality.
    joined_total: sa.Select
