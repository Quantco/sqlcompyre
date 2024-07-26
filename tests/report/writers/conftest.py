# Copyright (c) QuantCo 2024-2024
# SPDX-License-Identifier: BSD-3-Clause

import pytest

from sqlcompyre.report import Report


@pytest.fixture()
def reports() -> dict[str, Report]:
    return {
        "first": Report("tables", "t1", "t2", None, {}),
        "second": Report("tables", "x1", "x2", None, {}),
    }
