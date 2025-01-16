# Copyright (c) QuantCo 2024-2025
# SPDX-License-Identifier: BSD-3-Clause

"""This file contains tests that verify basic behavior for determining row counts."""

import pytest
import sqlalchemy as sa

import sqlcompyre as sc


def test_row_counts_equal_counts(engine: sa.Engine, table_students: sa.Table):
    # Check row counts same in identical tables
    row_counts = sc.compare_tables(engine, table_students, table_students).row_counts
    assert row_counts.left == 5
    assert row_counts.right == 5


def test_row_counts_equal_equal(engine: sa.Engine, table_students: sa.Table):
    # Check row counts equal in identical tables
    row_counts = sc.compare_tables(engine, table_students, table_students).row_counts
    assert row_counts.equal


def test_row_counts_equal_diff(engine: sa.Engine, table_students: sa.Table):
    # Check row counts are not different in identical tables
    row_counts = sc.compare_tables(engine, table_students, table_students).row_counts
    assert not row_counts.diff


def test_row_counts_equal_prop(engine: sa.Engine, table_students: sa.Table):
    # Check row count proportion is 1 in identical tables
    row_counts = sc.compare_tables(engine, table_students, table_students).row_counts
    assert row_counts.fraction_left == pytest.approx(1)


def test_row_counts_unequal_counts(
    engine: sa.Engine,
    table_students: sa.Table,
    table_students_small: sa.Table,
):
    # Check row counts different in different tables
    row_counts = sc.compare_tables(
        engine, table_students, table_students_small
    ).row_counts
    assert row_counts.left == 5
    assert row_counts.right == 4
