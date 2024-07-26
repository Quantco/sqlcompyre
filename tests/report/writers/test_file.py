# Copyright (c) QuantCo 2024-2024
# SPDX-License-Identifier: BSD-3-Clause

import logging
import tempfile
from pathlib import Path

import pytest

from sqlcompyre.report import Report
from sqlcompyre.report.formatters import TerminalFormatter
from sqlcompyre.report.writers import FileWriter


def test_file_writer(monkeypatch: pytest.MonkeyPatch, reports: dict[str, Report]):
    formatter = TerminalFormatter()
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.chdir(tmpdir)

        writer = FileWriter(formatter)
        writer.write(reports)

        assert writer.path.parts[-1] == ".compyre"
        assert {"first.txt", "second.txt"}, set(writer.path.iterdir())
        for file in writer.path.iterdir():
            assert len(file.read_text()) > 0


def test_file_writer_init_file(monkeypatch: pytest.MonkeyPatch):
    formatter = TerminalFormatter()
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.chdir(tmpdir)

        path = Path(tmpdir)
        (path / ".compyre").write_text("")

        with pytest.raises(ValueError, match="is not a directory"):
            FileWriter(formatter)


def test_file_writer_init_directory_empty(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
):
    formatter = TerminalFormatter()
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.chdir(tmpdir)

        path = Path(tmpdir)
        (path / ".compyre").mkdir()

        with caplog.at_level(logging.WARNING):
            FileWriter(formatter)
        assert len(caplog.records) == 0


def test_file_writer_init_directory_not_empty(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
):
    formatter = TerminalFormatter()
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.chdir(tmpdir)

        path = Path(tmpdir)
        (path / ".compyre").mkdir()
        (path / ".compyre" / "file.txt").write_text("")

        with caplog.at_level(logging.WARNING):
            FileWriter(formatter)
        assert (
            len(caplog.records) == 1
            and "adding and possibly overwriting files" in caplog.records[0].msg
        )
