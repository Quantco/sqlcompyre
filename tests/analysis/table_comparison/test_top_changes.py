# Copyright (c) QuantCo 2024-2025
# SPDX-License-Identifier: BSD-3-Clause

"""This file contains tests that verify the "top changes" comparison."""

import sqlalchemy as sa

import sqlcompyre as sc


def test_by_top_changes_same(engine: sa.Engine, table_students: sa.Table):
    comp = sc.compare_tables(engine, table_students, table_students)
    assert not comp.get_top_changes("age")
    assert not comp.get_top_changes("name")


def test_column_matches_changes_different(
    engine: sa.Engine,
    table_students_modified_1: sa.Table,
    table_students_modified_2: sa.Table,
):
    comp = sc.compare_tables(
        engine, table_students_modified_1, table_students_modified_2
    )
    assert comp.get_top_changes("age") == {"18 -> 17": 1}
