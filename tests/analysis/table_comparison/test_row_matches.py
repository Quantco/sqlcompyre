# Copyright (c) QuantCo 2024-2025
# SPDX-License-Identifier: BSD-3-Clause

"""This file contains tests that verify basic behavior for determining row matches."""

import pandas as pd
import sqlalchemy as sa

import sqlcompyre as sc


def test_row_matches_same_n_matched(engine: sa.Engine, table_students: sa.Table):
    row_matches = sc.compare_tables(engine, table_students, table_students).row_matches
    assert row_matches.n_joined_equal == 5
    assert row_matches.n_joined_unequal == 0


def test_row_matches_same_n_unjoined(engine: sa.Engine, table_students: sa.Table):
    row_matches = sc.compare_tables(engine, table_students, table_students).row_matches
    assert row_matches.n_unjoined_left == row_matches.n_unjoined_right == 0


def test_row_matches_same_unjoined(engine: sa.Engine, table_students: sa.Table):
    comp = sc.compare_tables(engine, table_students, table_students)
    with engine.connect() as conn:
        left_res = conn.execute(comp.row_matches.unjoined_left).all()
        right_res = conn.execute(comp.row_matches.unjoined_right).all()
    assert left_res == right_res == []


def test_row_matches_same_joined(engine: sa.Engine, table_students: sa.Table):
    comp = sc.compare_tables(engine, table_students, table_students)
    with engine.connect() as conn:
        joined_unequal_res = conn.execute(comp.row_matches.joined_unequal).all()
        joined_equal_res = conn.execute(comp.row_matches.joined_equal).all()
        joined_total_res = conn.execute(comp.row_matches.joined_total).all()
    assert joined_unequal_res == []
    assert len(joined_equal_res) == len(joined_total_res) == 5


def test_row_matches_n_different_unjoined(
    engine: sa.Engine,
    table_students_modified_1: sa.Table,
    table_students_modified_2: sa.Table,
):
    row_matches = sc.compare_tables(
        engine, table_students_modified_1, table_students_modified_2
    ).row_matches
    assert row_matches.n_unjoined_left == row_matches.n_unjoined_right == 1


def test_row_matches_n_different_joined(
    engine: sa.Engine,
    table_students_modified_1: sa.Table,
    table_students_modified_2: sa.Table,
):
    row_matches = sc.compare_tables(
        engine, table_students_modified_1, table_students_modified_2
    ).row_matches
    assert row_matches.n_joined_equal == 2
    assert row_matches.n_joined_unequal == 1


def test_row_matches_different_unjoined(
    engine: sa.Engine,
    table_students_modified_1: sa.Table,
    table_students_modified_2: sa.Table,
):
    comp = sc.compare_tables(
        engine, table_students_modified_1, table_students_modified_2
    )
    with engine.connect() as conn:
        left_res = conn.execute(comp.row_matches.unjoined_left).all()
        right_res = conn.execute(comp.row_matches.unjoined_right).all()
    assert len(left_res) == len(right_res) == 1


def test_row_matches_different_joined(
    engine: sa.Engine,
    table_students_modified_1: sa.Table,
    table_students_modified_2: sa.Table,
):
    comp = sc.compare_tables(
        engine, table_students_modified_1, table_students_modified_2
    )
    with engine.connect() as conn:
        joined_unequal_res = conn.execute(comp.row_matches.joined_unequal).all()
        joined_equal_res = conn.execute(comp.row_matches.joined_equal).all()
        joined_total_res = conn.execute(comp.row_matches.joined_total).all()
    assert len(joined_unequal_res) == 1
    assert len(joined_equal_res) == 2
    assert len(joined_total_res) == 3


def test_row_matches_unjoined_columns(
    engine: sa.Engine, table_students: sa.Table, table_students_small: sa.Table
):
    # Check that selects on unjoined rows only contain columns of corresponding table
    row_matches = sc.compare_tables(
        engine, table_students, table_students_small
    ).row_matches
    unjoined_left = pd.read_sql(row_matches.unjoined_left, con=engine)
    unjoined_right = pd.read_sql(row_matches.unjoined_right, con=engine)

    assert len(unjoined_left) == 1
    assert set(unjoined_left.columns) == {"id", "name", "age", "gpa"}
    assert len(unjoined_right) == 0
    assert set(unjoined_right.columns) == {"id", "name", "age", "gpa"}


def test_row_matches_unjoined_columns_mapped(
    engine: sa.Engine, table_students: sa.Table, table_students_renamed: sa.Table
):
    # Check that selects on unjoined rows only contain columns of corresponding table even if
    # column names are mapped
    row_matches = sc.compare_tables(
        engine,
        table_students,
        table_students_renamed,
        column_name_mapping={col: f"{col}_v2" for col in ["id", "name", "age", "gpa"]},
    ).row_matches
    unjoined_left = pd.read_sql(row_matches.unjoined_left, con=engine)
    unjoined_right = pd.read_sql(row_matches.unjoined_right, con=engine)

    assert len(unjoined_left) == 1
    assert set(unjoined_left.columns) == {"id", "name", "age", "gpa"}
    assert len(unjoined_right) == 0
    assert set(unjoined_right.columns) == {"id_v2", "name_v2", "age_v2", "gpa_v2"}


def test_row_matches_column_names(engine: sa.Engine, table_students: sa.Table):
    row_matches = sc.compare_tables(engine, table_students, table_students).row_matches
    equal = pd.read_sql(row_matches.joined_equal, con=engine)

    # Test 'joined_' for primary key and 'left_', 'right_' for other keys
    assert set(equal.columns) == {
        "joined_id",
        "left_name",
        "right_name",
        "left_age",
        "right_age",
        "left_gpa",
        "right_gpa",
    }


def test_row_matches_float_precision(
    engine: sa.Engine, table_students: sa.Table, table_students_modified_3: sa.Table
):
    row_matches_1 = sc.compare_tables(
        engine, table_students, table_students_modified_3
    ).row_matches
    assert row_matches_1.n_joined_equal == 0
    assert row_matches_1.n_joined_unequal == 5

    row_matches_2 = sc.compare_tables(
        engine, table_students, table_students_modified_3, float_precision=0.2
    ).row_matches
    assert row_matches_2.n_joined_equal == 5
    assert row_matches_2.n_joined_unequal == 0
