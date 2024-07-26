# Copyright (c) QuantCo 2024-2024
# SPDX-License-Identifier: BSD-3-Clause

from functools import cached_property


class Names:
    """Investigate the names of database objects."""

    def __init__(self, left: set[str], right: set[str], ignore_casing: bool):
        """
        Args:
            left: Names from the "left" database object.
            right: Names from the "right" database object.
            ignore_casing: Whether to ignore casing for name equality.
        """
        if ignore_casing:
            self._set_left = {k.lower() for k in left}
            self._set_right = {k.lower() for k in right}
        else:
            self._set_left = left
            self._set_right = right

    @cached_property
    def left(self) -> list[str]:
        """Ordered names from the "left" database object."""
        return sorted(self._set_left)

    @cached_property
    def right(self) -> list[str]:
        """Ordered names from the "right" database object."""
        return sorted(self._set_right)

    @cached_property
    def in_common(self) -> list[str]:
        """Ordered list of names provided by both database objects."""
        return sorted(self._set_left.intersection(self._set_right))

    @cached_property
    def missing_left(self) -> list[str]:
        """Ordered list of names provided only by the "right" database object."""
        return sorted(self._set_right - self._set_left)

    @cached_property
    def missing_right(self) -> list[str]:
        """Ordered list of names provided only by the "left" database object."""
        return sorted(self._set_left - self._set_right)

    @cached_property
    def equal(self) -> bool:
        """Whether the names from both database objects overlap."""
        return self._set_left == self._set_right
