# Copyright (c) QuantCo 2024-2024
# SPDX-License-Identifier: BSD-3-Clause

from dataclasses import dataclass

from sqlalchemy.sql import selectable


@dataclass
class ColumnMatches:
    """Investigate column value changes between database tables."""

    #: Dictionary mapping the name of the left-table column to the fraction of joined rows for
    #: which that column has the same value in both tables.
    fraction_same: dict[str, float]
    #: Dictionary mapping the name of the left-table column to a query of all joined rows for
    #: which the column does not have the same value in both tables.
    mismatch_selects: dict[str, selectable.Select]
