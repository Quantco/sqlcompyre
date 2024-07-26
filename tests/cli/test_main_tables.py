# Copyright (c) QuantCo 2024-2024
# SPDX-License-Identifier: BSD-3-Clause

import sqlalchemy as sa
from pytest_console_scripts import ScriptRunner


def test_compare_tables(
    script_runner: ScriptRunner,
    connection_string_raw_string: str,
    table_1: sa.Table,
    table_2: sa.Table,
):
    run = script_runner.run(
        [
            "compyre",
            "tables",
            str(table_1),
            str(table_2),
            "-s",
            connection_string_raw_string,
        ]
    )
    assert run.returncode == 0


def test_compare_tables_only_pk(
    script_runner: ScriptRunner, connection_string_raw_string: str, table_3: sa.Table
):
    run = script_runner.run(
        [
            "compyre",
            "tables",
            str(table_3),
            str(table_3),
            "-s",
            connection_string_raw_string,
        ]
    )
    assert run.returncode == 0
