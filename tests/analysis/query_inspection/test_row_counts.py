# Copyright (c) QuantCo 2024-2024
# SPDX-License-Identifier: BSD-3-Clause


import pytest
import sqlalchemy as sa

import sqlcompyre as sc


def test_row_count(engine: sa.Engine, table_characters: sa.Table):
    inspection = sc.inspect_table(engine, table_characters)
    assert inspection.row_count == 8


def test_row_count_table_string(engine: sa.Engine, table_characters: sa.Table):
    inspection = sc.inspect_table(engine, str(table_characters))
    assert inspection.row_count == 8


def test_row_count_query(engine: sa.Engine, table_characters: sa.Table):
    inspection = sc.inspect(
        engine,
        sa.select(table_characters).where(
            table_characters.columns["last_name"] == "Duck"
        ),
    )
    assert inspection.row_count == 6


def test_row_count_raw_query(engine: sa.Engine, table_characters: sa.Table):
    inspection = sc.inspect(
        engine,
        f"""
        SELECT characters.first_name, characters.last_name, characters.age
        FROM {str(table_characters)}
        WHERE characters.last_name = 'Duck'
        """,
    )

    assert inspection.row_count == 6
    assert inspection.distinct_row_count() == 5
    assert inspection.distinct_row_count("last_name") == 1
    assert inspection.distinct_row_count("last_name", "age") == 3


@pytest.mark.parametrize(
    ("columns", "expected"),
    [([], 7), (["last_name"], 3), (["last_name", "age"], 5)],
)
def test_distinct_row_count(
    engine: sa.Engine, table_characters: sa.Table, columns: list[str], expected: int
):
    inspection = sc.inspect_table(engine, table_characters)
    assert inspection.distinct_row_count(*columns) == expected
