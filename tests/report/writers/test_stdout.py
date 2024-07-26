# Copyright (c) QuantCo 2024-2024
# SPDX-License-Identifier: BSD-3-Clause

import pytest

from sqlcompyre.report import Report
from sqlcompyre.report.formatters import TerminalFormatter
from sqlcompyre.report.writers import StdoutWriter


def test_stdout_writer(capsys: pytest.CaptureFixture, reports: dict[str, Report]):
    formatter = TerminalFormatter()
    writer = StdoutWriter(formatter)
    writer.write(reports)
    captured = capsys.readouterr()
    assert captured.out.startswith("+---")
    assert (
        len([l for l in captured.out.split("\n") if l.startswith("+---")]) == 4  # noqa
    )


def test_stdout_writer_single(
    capsys: pytest.CaptureFixture, reports: dict[str, Report]
):
    formatter = TerminalFormatter(colored=False)
    writer = StdoutWriter(formatter)
    writer.write({"first": reports["first"]})
    captured = capsys.readouterr()
    assert captured.out.startswith("SQLCompyre Comparison")
    assert (
        len([l for l in captured.out.split("\n") if l.startswith("+---")]) == 0  # noqa
    )
