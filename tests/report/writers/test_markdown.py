# Copyright (c) QuantCo 2024-2024
# SPDX-License-Identifier: BSD-3-Clause

import pytest

from sqlcompyre.report import Report
from sqlcompyre.report.formatters import TerminalFormatter
from sqlcompyre.report.writers import MarkdownWriter


def test_markdown_writer(capsys: pytest.CaptureFixture, reports: dict[str, Report]):
    formatter = TerminalFormatter()
    writer = MarkdownWriter(formatter)
    writer.write(reports)
    captured = capsys.readouterr()
    assert captured.out.startswith("<details><summary>")
    assert "<summary><b>first</b></summary>" in captured.out
    assert "<summary><b>second</b></summary>" in captured.out
