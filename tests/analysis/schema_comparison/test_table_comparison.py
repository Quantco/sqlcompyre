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


def test_table_comparison_case_sensitive(engine: Engine, schema_1: str, schema_2: str):
    comparison = sc.compare_schemas(engine, schema_1, schema_2)

    with pytest.raises(ValueError):
        comparison.compare_matched_table("missing")
    with pytest.raises(ValueError):
        comparison.compare_matched_table("TABLE1")
    assert comparison.compare_matched_table("table1").row_counts.diff == 0


def test_table_comparison_case_insensitive(
    engine: Engine, schema_1: str, schema_2: str
):
    comparison = sc.compare_schemas(engine, schema_1, schema_2, ignore_casing=True)

    with pytest.raises(ValueError):
        comparison.compare_matched_table("missing")
    assert comparison.compare_matched_table("TABLE1").row_counts.diff == 0
