# Copyright (c) QuantCo 2024-2024
# SPDX-License-Identifier: BSD-3-Clause

import pytest
from sqlalchemy.engine import Engine

import sqlcompyre as sc
from tests._shared import dialect_from_env

pytestmark = pytest.mark.skipif(
    not dialect_from_env().supports_schemas,
    reason="Database system does not support schemas.",
)


def test_table_counts(engine: Engine, schema_1: str, schema_2: str):
    comparison = sc.compare_schemas(engine, schema_1, schema_2)
    assert comparison.table_counts.left == 4
    assert comparison.table_counts.right == 3


def test_table_names(engine: Engine, schema_1: str, schema_2: str):
    comparison = sc.compare_schemas(engine, schema_1, schema_2)
    assert not comparison.table_names.equal
    assert comparison.table_names.in_common == ["table1", "table4"]
    assert comparison.table_names.missing_right == ["table2", "table3"]
    assert comparison.table_names.missing_left == ["table5"]


def test_table_counts_with_views(engine: Engine, schema_1: str, schema_2: str):
    comparison = sc.compare_schemas(engine, schema_1, schema_2, include_views=True)
    assert comparison.table_counts.left == 6
    assert comparison.table_counts.right == 4


def test_table_names_with_views(engine: Engine, schema_1: str, schema_2: str):
    comparison = sc.compare_schemas(engine, schema_1, schema_2, include_views=True)
    assert not comparison.table_names.equal
    assert comparison.table_names.in_common == ["table1", "table4", "view1"]
    assert comparison.table_names.missing_right == ["table2", "table3", "view2"]
    assert comparison.table_names.missing_left == ["table5"]


def test_report(engine: Engine, schema_1: str, schema_2: str):
    report = sc.compare_schemas(engine, schema_1, schema_2).summary_report()
    assert len(report.sections) == 2
