# Copyright (c) QuantCo 2024-2024
# SPDX-License-Identifier: BSD-3-Clause

"""This file contains tests that verify basic behavior for determining column name
matches."""

import sqlalchemy as sa
from sqlalchemy.engine import Engine

import sqlcompyre as sc


def test_column_names_equal_same_names(engine: Engine, table_students: sa.Table):
    # Check that column names are matched in two identical tables
    comparison = sc.compare_tables(engine, table_students, table_students)
    assert comparison.column_names.equal


def test_column_names_equal_missing_1(engine: Engine, table_students: sa.Table):
    # Check that there are no missing columns in two identical tables
    comparison = sc.compare_tables(engine, table_students, table_students)
    assert not comparison.column_names.missing_left


def test_column_names_equal_missing_2(engine: Engine, table_students: sa.Table):
    # Check that there are no missing columns in two identical tables
    comparison = sc.compare_tables(engine, table_students, table_students)
    assert not comparison.column_names.missing_right


def test_column_names_equal_missing_renamed_1(
    engine: Engine,
    table_students_modified_2: sa.Table,
    table_students_renamed: sa.Table,
):
    # Check that there are no missing columns in two different tables with renamings
    comparison = sc.compare_tables(
        engine,
        table_students_modified_2,
        table_students_renamed,
        column_name_mapping={
            "id": "id_v2",
            "name": "name_v2",
            "age": "age_v2",
            "gpa": "gpa_v2",
        },
    )
    assert not comparison.column_names.missing_left


def test_column_names_equal_missing_renamed_2(
    engine: Engine,
    table_students_modified_2: sa.Table,
    table_students_renamed: sa.Table,
):
    # Check that there are no missing columns in two different tables with renamings
    comparison = sc.compare_tables(
        engine,
        table_students_modified_2,
        table_students_renamed,
        column_name_mapping={
            "id": "id_v2",
            "name": "name_v2",
            "age": "age_v2",
            "gpa": "gpa_v2",
        },
    )
    assert not comparison.column_names.missing_right


def test_column_names_unequal_same_names(
    engine: Engine,
    table_students: sa.Table,
    table_students_narrow: sa.Table,
):
    # Check that column names are not matched in two different tables
    comparison = sc.compare_tables(engine, table_students, table_students_narrow)
    assert not comparison.column_names.equal


def test_column_names_unequal_missing_1(
    engine: Engine,
    table_students: sa.Table,
    table_students_narrow: sa.Table,
):
    # check that additional column is detected in first table
    comparison = sc.compare_tables(engine, table_students, table_students_narrow)
    assert comparison.column_names.missing_right[0] == "gpa"


def test_column_names_unequal_missing_2(
    engine: Engine,
    table_students: sa.Table,
    table_students_narrow: sa.Table,
):
    # Check that no extra columns are reported missing in second table
    comparison = sc.compare_tables(engine, table_students, table_students_narrow)
    assert not comparison.column_names.missing_left
