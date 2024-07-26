# Copyright (c) QuantCo 2024-2024
# SPDX-License-Identifier: BSD-3-Clause

import pytest

from sqlcompyre.report.formatters import (
    TerminalFormatter,
    TextFormatter,
    get_formatter,
)


def test_factory():
    assert isinstance(get_formatter("terminal"), TerminalFormatter)
    assert isinstance(get_formatter("text"), TextFormatter)
    with pytest.raises(ValueError, match="Unknown formatter"):
        get_formatter("unknown")
