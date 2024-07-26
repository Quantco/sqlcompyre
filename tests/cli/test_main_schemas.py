# Copyright (c) QuantCo 2024-2024
# SPDX-License-Identifier: BSD-3-Clause

from pathlib import Path

import pytest
from pytest_console_scripts import ScriptRunner

from tests._shared import dialect_from_env

pytestmark = pytest.mark.skipif(
    not dialect_from_env().supports_schemas,
    reason="Database system does not support schemas.",
)


def test_compare_schemas(
    script_runner: ScriptRunner,
    connection_string_raw_string: str,
    schema_1: str,
    schema_2: str,
):
    run = script_runner.run(
        [
            "compyre",
            "schemas",
            schema_1,
            schema_2,
            "-s",
            connection_string_raw_string,
        ]
    )
    assert run.returncode == 0


def test_compare_schemas_with_tables(
    script_runner: ScriptRunner,
    connection_string_raw_string: str,
    schema_1: str,
    schema_2: str,
):
    run_unskipped = script_runner.run(
        [
            "compyre",
            "schemas",
            schema_1,
            schema_2,
            "-s",
            connection_string_raw_string,
            "--compare-tables",
        ]
    )
    assert run_unskipped.returncode == 0

    run_skipped = script_runner.run(
        [
            "compyre",
            "schemas",
            schema_1,
            schema_2,
            "-s",
            connection_string_raw_string,
            "--compare-tables",
            "--skip-equal",
        ]
    )
    assert run_skipped.returncode == 0

    assert len(run_skipped.stdout) < len(run_unskipped.stdout)


@pytest.mark.parametrize(
    ("config", "output_sections"),
    [("config_empty", 3), ("config_tables", 2), ("config_columns", 1)],
)
def test_compare_schemas_with_config(
    script_runner: ScriptRunner,
    connection_string_raw_string: str,
    schema_1: str,
    schema_2: str,
    config: str,
    output_sections: int,
):
    config_path = (
        Path(__file__).parent.parent / "config" / "resources" / f"{config}.yaml"
    )
    run = script_runner.run(
        [
            "compyre",
            "schemas",
            schema_1,
            schema_2,
            "-s",
            connection_string_raw_string,
            "--compare-tables",
            "--skip-equal",
            "--config",
            str(config_path),
        ]
    )
    assert run.returncode == 0
    # A single output section results in on "+--" blocks
    assert run.stdout.count("+--") == output_sections * (output_sections != 1) * 2
