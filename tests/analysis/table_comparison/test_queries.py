# Copyright (c) QuantCo 2024-2025
# SPDX-License-Identifier: BSD-3-Clause

import sqlalchemy as sa

import sqlcompyre as sc


def test_compare_queries_join_columns_inferred(
    engine: sa.Engine, table_students: sa.Table
):
    comparison = sc.compare_tables(
        engine, sa.select(table_students), sa.select(table_students)
    )
    assert comparison.join_columns == ["id"]


def test_compare_queries_select(engine: sa.Engine, table_students: sa.Table):
    comparison = sc.compare_tables(
        engine,
        sa.select(table_students).where(table_students.c["age"] >= 30),
        sa.select(table_students).where(table_students.c["age"] >= 20),
    )
    assert comparison.row_counts.diff == 2
    assert comparison.row_matches.n_joined_total == 2


def test_compare_queries_subquery(engine: sa.Engine, table_students: sa.Table):
    comparison = sc.compare_tables(
        engine,
        sa.select(table_students).where(table_students.c["age"] >= 30).subquery(),
        sa.select(table_students).where(table_students.c["age"] >= 20).subquery(),
    )
    assert comparison.row_counts.diff == 2
    assert comparison.row_matches.n_joined_total == 2
