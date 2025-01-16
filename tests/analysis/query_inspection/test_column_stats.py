# Copyright (c) QuantCo 2024-2025
# SPDX-License-Identifier: BSD-3-Clause

import sqlalchemy as sa

import sqlcompyre as sc


def test_column_stats_min(engine: sa.Engine, table_characters: sa.Table):
    inspection = sc.inspect_table(engine, table_characters)
    assert inspection.column_stats("age").min == 6
    assert inspection.column_stats("first_name").min == "Daisy"


def test_column_stats_max(engine: sa.Engine, table_characters: sa.Table):
    inspection = sc.inspect_table(engine, table_characters)
    assert inspection.column_stats("age").max == 65
    assert inspection.column_stats("first_name").max == "Scrooge"
