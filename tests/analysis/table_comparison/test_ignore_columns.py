# Copyright (c) QuantCo 2024-2025
# SPDX-License-Identifier: BSD-3-Clause

import sqlalchemy as sa

import sqlcompyre as sc


def test_ignore_columns(
    engine: sa.Engine,
    table_students_small: sa.Table,
    table_students_modified_1: sa.Table,
):
    comparison_all = sc.compare_tables(
        engine, table_students_small, table_students_modified_1
    )
    assert not comparison_all.equal

    comparison_ignored = sc.compare_tables(
        engine, table_students_small, table_students_modified_1, ignore_columns=["age"]
    )
    assert comparison_ignored.equal
