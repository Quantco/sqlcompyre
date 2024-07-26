# Copyright (c) QuantCo 2024-2024
# SPDX-License-Identifier: BSD-3-Clause

import pytest

from sqlcompyre.report.formatters import TextFormatter
from sqlcompyre.report.writers import (
    FileWriter,
    MarkdownWriter,
    StdoutWriter,
    get_writer,
)


def test_factory():
    formatter = TextFormatter()
    assert isinstance(get_writer("file", formatter), FileWriter)
    assert isinstance(get_writer("markdown", formatter), MarkdownWriter)
    assert isinstance(get_writer("stdout", formatter), StdoutWriter)
    with pytest.raises(ValueError, match="Unknown writer"):
        get_writer("unknown", formatter)
