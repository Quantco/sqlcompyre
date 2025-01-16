# Copyright (c) QuantCo 2024-2025
# SPDX-License-Identifier: BSD-3-Clause

from pathlib import Path

import pytest

from sqlcompyre.config import read_config


@pytest.mark.parametrize(
    "path,expected_tables,expected_table_columns",
    [
        (
            Path(__file__).parent / "resources" / "config_columns.yaml",
            ["table1"],
            {"table2": ["value"]},
        ),
        (Path(__file__).parent / "resources" / "config_tables.yaml", ["table1"], {}),
        (Path(__file__).parent / "resources" / "config_empty.yaml", [], {}),
    ],
)
def test_config_parsing(
    path: Path, expected_tables: list[str], expected_table_columns: dict[str, list[str]]
):
    config = read_config(path)
    assert config.ignore_tables == expected_tables
    assert config.ignore_table_columns == expected_table_columns
