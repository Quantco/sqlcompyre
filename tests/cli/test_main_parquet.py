# Copyright (c) QuantCo 2024-2024
# SPDX-License-Identifier: BSD-3-Clause

from pathlib import Path

import polars as pl
from pytest_console_scripts import ScriptRunner


def test_compare_parquet(script_runner: ScriptRunner, tmp_path: Path):
    df1 = pl.DataFrame({"id": [1, 2, 3, 4], "value": [1, 2, 4, 4]})
    df1.write_parquet(tmp_path / "df1.parquet")

    df2 = pl.DataFrame({"id": [1, 2, 3], "value": [1, 2, 3]})
    df2.write_parquet(tmp_path / "df2.parquet")

    result = script_runner.run(
        [
            "compyre",
            "parquet",
            str(tmp_path / "df1.parquet"),
            str(tmp_path / "df2.parquet"),
            "--join-columns",
            "id",
        ]
    )
    assert result.returncode == 0
