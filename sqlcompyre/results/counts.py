# Copyright (c) QuantCo 2024-2024
# SPDX-License-Identifier: BSD-3-Clause

from dataclasses import dataclass


@dataclass
class Counts:
    """Investigate the counts of database objects."""

    #: The counts of the "left" database object.
    left: int
    #: The counts of the "right" database object.
    right: int

    @property
    def equal(self) -> bool:
        """Whether the counts are the same."""
        return self.left == self.right

    @property
    def diff(self) -> int:
        """The absolute difference in counts."""
        return abs(self.left - self.right)

    @property
    def gain_left(self) -> int:
        """The left count minus the right count."""
        return self.left - self.right

    @property
    def gain_right(self) -> int:
        """The right count minus the left count."""
        return self.right - self.left

    @property
    def fraction_left(self) -> float:
        """The left count divided by the right count."""
        try:
            return self.left / self.right
        except ZeroDivisionError:
            return float("nan")

    @property
    def fraction_right(self) -> float:
        """The right count divided by the left count."""
        try:
            return self.right / self.left
        except ZeroDivisionError:
            return float("nan")
