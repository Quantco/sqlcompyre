# Copyright (c) QuantCo 2024-2024
# SPDX-License-Identifier: BSD-3-Clause

from typing import Literal

import pytest
from sqlalchemy.engine import Engine

import sqlcompyre as sc
from tests._shared import dialect_from_env

pytestmark = pytest.mark.skipif(
    not dialect_from_env().supports_schemas,
    reason="Database system does not support schemas.",
)


def test_report(engine: Engine, schema_1: str, schema_2: str):
    report = sc.compare_schemas(engine, schema_1, schema_2).summary_report()
    assert len(report.sections) == 2


def test_table_reports(engine: Engine, schema_1: str, schema_2: str):
    reports = sc.compare_schemas(engine, schema_1, schema_2).table_reports()
    assert set(reports.keys()) == {"table1", "table4"}


@pytest.mark.parametrize(
    ("sort_by", "tables"),
    [("name", ["table1", "table4"]), ("creation_timestamp", ["table4", "table1"])],
)
def test_table_reports_sort_by(
    engine: Engine,
    schema_1: str,
    schema_2: str,
    sort_by: Literal["name", "creation_timestamp"],
    tables: list[str],
):
    reports = sc.compare_schemas(engine, schema_1, schema_2).table_reports(
        sort_by=sort_by
    )
    assert [key for key in reports] == tables


def test_table_reports_skip_equal(engine: Engine, schema_1: str, schema_2: str):
    reports = sc.compare_schemas(engine, schema_1, schema_2).table_reports(
        skip_equal=True
    )
    assert len(reports) == 1


def test_table_reports_no_join_columns(engine: Engine, schema_duplicate_table: str):
    reports = sc.compare_schemas(
        engine, schema_duplicate_table, schema_duplicate_table
    ).table_reports(skip_equal=True)
    assert len(reports) == 0


def test_table_reports_ignore_full(engine: Engine, schema_1: str, schema_2: str):
    reports = sc.compare_schemas(engine, schema_1, schema_2).table_reports(
        ignore_tables=["table4"], skip_equal=True
    )
    assert len(reports) == 1


def test_table_reports_ignore_full_regex(engine: Engine, schema_1: str, schema_2: str):
    reports = sc.compare_schemas(engine, schema_1, schema_2).table_reports(
        ignore_tables=[r"table.*"], skip_equal=True
    )
    assert len(reports) == 0


def test_table_reports_ignore_column(engine: Engine, schema_1: str, schema_2: str):
    reports = sc.compare_schemas(engine, schema_1, schema_2).table_reports(
        ignore_table_columns={"table1": ["value"]}, skip_equal=True
    )
    assert len(reports) == 0
