# Copyright (c) QuantCo 2024-2024
# SPDX-License-Identifier: BSD-3-Clause

import pytest

from sqlcompyre.results import Counts


def test_equal():
    equal = Counts(left=5, right=5)
    not_equal = Counts(left=5, right=6)

    assert equal.equal
    assert not not_equal.equal


def test_diff():
    no_diff = Counts(left=5, right=5)
    left_diff = Counts(left=10, right=5)
    right_diff = Counts(left=5, right=8)

    assert no_diff.diff == 0
    assert left_diff.diff == 5
    assert right_diff.diff == 3


def test_fraction():
    no_diff = Counts(left=5, right=5)
    left_diff = Counts(left=10, right=5)
    right_diff = Counts(left=2, right=8)

    assert no_diff.fraction_left == pytest.approx(1)
    assert left_diff.fraction_left == pytest.approx(2)
    assert left_diff.fraction_right == pytest.approx(0.5)
    assert right_diff.fraction_left == pytest.approx(0.25)
    assert right_diff.fraction_right == pytest.approx(4)
