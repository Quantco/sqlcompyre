# Copyright (c) QuantCo 2024-2025
# SPDX-License-Identifier: BSD-3-Clause

"""This file contains tests that verify the column matching ability of table
comparisons."""

import pandas as pd
import pytest
import sqlalchemy as sa

import sqlcompyre as sc


def test_name_verification(
    engine: sa.Engine,
    table_students: sa.Table,
    table_students_renamed: sa.Table,
):
    with pytest.raises(ValueError) as exc_info:
        sc.compare_tables(
            engine,
            table_students,
            table_students_renamed,
            column_name_mapping={
                "name": "name_v2",
                "foo": "bar",
                "gpa_v2": "gpa",
            },
        )
    assert all([colname in exc_info.value.args[0] for colname in ["gpa_v2", "foo"]])


def test_name_verification_right_arbitrary_casing(
    engine: sa.Engine,
    table_students: sa.Table,
    table_students_renamed: sa.Table,
):
    with pytest.raises(ValueError) as exc_info:
        sc.compare_tables(
            engine,
            table_students,
            table_students_renamed,
            column_name_mapping={
                "name": "Name_V2",
                "age": "Missing",
            },
        )
    assert all([colname in exc_info.value.args[0] for colname in ["Missing"]])


def test_arbitrary_name_casing(
    engine: sa.Engine,
    table_students: sa.Table,
    table_students_renamed: sa.Table,
):
    with pytest.raises(ValueError):
        # Fail when not ignoring casing
        sc.compare_tables(
            engine,
            table_students,
            table_students_renamed,
            join_columns=["Id"],
            column_name_mapping={"NAME": "name_V2", "Age": "AGE_v2", "gpa": "GPA_V2"},
        )

    # Succeed when ignoring casing
    comparison = sc.compare_tables(
        engine,
        table_students,
        table_students_renamed,
        join_columns=["Id"],
        column_name_mapping={"NAME": "name_V2", "Age": "AGE_v2", "gpa": "GPA_V2"},
        ignore_casing=True,
    )
    assert len(comparison.column_names.in_common) == 0
    assert comparison.row_counts.diff == 1


def test_partly_renaming(
    engine: sa.Engine,
    table_students: sa.Table,
    table_students_partly_renamed: sa.Table,
):
    comparison = sc.compare_tables(
        engine,
        table_students,
        table_students_partly_renamed,
        column_name_mapping={"age": "age_v2", "gpa": "gpa_v2"},
    )
    assert len(comparison.column_names.in_common) == 2
    assert len(comparison.column_names.missing_left) == 0
    assert len(comparison.column_names.missing_right) == 0
    assert comparison.row_counts.diff == 1
    # Ensure that all columns are matched, one is primary key, 3 per table left
    assert pd.read_sql(comparison.row_matches.joined_equal, con=engine).shape[1] == 7

    comparison = sc.compare_tables(
        engine,
        table_students_partly_renamed,
        table_students,
        column_name_mapping={"age_v2": "age", "gpa_v2": "gpa"},
    )
    assert len(comparison.column_names.in_common) == 2
    assert len(comparison.column_names.missing_left) == 0
    assert len(comparison.column_names.missing_right) == 0
    assert comparison.row_counts.diff == 1
    # Ensure that all columns are matched, one is primary key, 3 per table left
    assert pd.read_sql(comparison.row_matches.joined_equal, con=engine).shape[1] == 7


def test_automatic_case_matching(
    engine: sa.Engine, table_students: sa.Table, table_students_cased: sa.Table
):
    with pytest.raises(ValueError):
        # Fail when not ignoring casing
        sc.compare_tables(engine, table_students, table_students_cased)

    # Succeed when ignoring casing
    comparison = sc.compare_tables(
        engine,
        table_students,
        table_students_cased,
        ignore_casing=True,
    )
    assert len(comparison.column_names.in_common) == 4
    assert comparison.row_counts.diff == 1


def test_row_matches_different_unmatched_cols(
    engine: sa.Engine,
    table_students_modified_1: sa.Table,
    table_students_renamed: sa.Table,
):
    row_matches = sc.compare_tables(
        engine,
        table_students_modified_1,
        table_students_renamed,
        column_name_mapping={col: f"{col}_v2" for col in ["id", "name", "age", "gpa"]},
    ).row_matches
    assert row_matches.n_unjoined_left == row_matches.n_unjoined_right == 1


def test_row_matches_different_matched_cols(
    engine: sa.Engine,
    table_students_modified_1: sa.Table,
    table_students_renamed: sa.Table,
):
    row_matches = sc.compare_tables(
        engine,
        table_students_modified_1,
        table_students_renamed,
        column_name_mapping={col: f"{col}_v2" for col in ["id", "name", "age", "gpa"]},
    ).row_matches
    assert row_matches.n_joined_equal == 2
    assert row_matches.n_joined_unequal == 1


def test_column_matches_percentages_different_dbs_cols(
    engine: sa.Engine,
    table_students_modified_1: sa.Table,
    table_students_renamed: sa.Table,
):
    column_matches = sc.compare_tables(
        engine,
        table_students_modified_1,
        table_students_renamed,
        column_name_mapping={col: f"{col}_v2" for col in ["id", "name", "age", "gpa"]},
    ).column_matches
    assert float(column_matches.fraction_same["name"]) == pytest.approx(1)
    assert float(column_matches.fraction_same["age"]) == pytest.approx(2 / 3)


def test_column_matches_percentages_selects(
    engine: sa.Engine,
    table_students_modified_1: sa.Table,
    table_students_renamed: sa.Table,
):
    column_matches = sc.compare_tables(
        engine,
        table_students_modified_1,
        table_students_renamed,
        column_name_mapping={col: f"{col}_v2" for col in ["id", "name", "age", "gpa"]},
    ).column_matches
    with engine.connect() as conn:
        assert conn.execute(column_matches.mismatch_selects["name"]).all() == []
        assert len(conn.execute(column_matches.mismatch_selects["age"]).all()) == 1
