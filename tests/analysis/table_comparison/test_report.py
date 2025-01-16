# Copyright (c) QuantCo 2024-2025
# SPDX-License-Identifier: BSD-3-Clause

"""This file contains tests that verify the report generation of a table comparison."""

import pytest
import sqlalchemy as sa

import sqlcompyre as sc


@pytest.fixture
def expected_description() -> str:
    return """Joining on columns:
  - 'id' = 'id'"""


def test_report_simple(
    engine: sa.Engine,
    table_students_modified_1: sa.Table,
    table_students_modified_2: sa.Table,
    expected_description: str,
):
    report = sc.compare_tables(
        engine, table_students_modified_1, table_students_modified_2
    ).summary_report()
    assert len(report.sections) == 4
    assert report.meta.description == expected_description
