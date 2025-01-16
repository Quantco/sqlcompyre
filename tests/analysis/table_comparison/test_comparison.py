# Copyright (c) QuantCo 2024-2025
# SPDX-License-Identifier: BSD-3-Clause

"""This file contains general that verify SQLCompyre's table comparison."""

import logging

import pytest
import sqlalchemy as sa

import sqlcompyre as sc
from tests._shared import dialect_from_env


@pytest.mark.skipif(
    not dialect_from_env().supports_schemas,
    reason="Database system does not support schemas.",
)
def test_comparison_different_schema(
    engine: sa.Engine,
    table_students: sa.Table,
    table_students_other_schema: sa.Table,
):
    comparison = sc.compare_tables(engine, table_students, table_students_other_schema)
    assert comparison.column_names.equal


@pytest.mark.skipif(
    not dialect_from_env().supports_schemas,
    reason="Database system does not support schemas.",
)
def test_comparison_string_tables(
    engine: sa.Engine,
    table_students: sa.Table,
    table_students_other_schema: sa.Table,
):
    comparison = sc.compare_tables(
        engine, str(table_students), str(table_students_other_schema)
    )
    assert comparison.column_names.equal


def test_comparison_string_views(
    caplog: pytest.LogCaptureFixture, engine: sa.Engine, view_students: sa.Table
):
    # Views don't have primary keys. Without inferring them, the report should only have two
    # sections
    with caplog.at_level(logging.WARNING):
        report = sc.compare_tables(
            engine, view_students, view_students, infer_primary_keys=False
        ).summary_report()
        assert len(report.sections) == 2
    assert (
        len(caplog.records) == 1
        and "dropping row and column matches" in caplog.records[0].msg
    )

    # Inferring primary keys allows comparing views
    report = sc.compare_tables(
        engine, view_students, view_students, infer_primary_keys=True
    ).summary_report()

    assert len(report.sections) == 4
