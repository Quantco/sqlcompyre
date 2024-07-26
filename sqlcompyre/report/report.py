# Copyright (c) QuantCo 2024-2024
# SPDX-License-Identifier: BSD-3-Clause

from typing import Any, Literal

from .formatters import Formatter, TerminalFormatter
from .schema import Metadata, Section


class Report:
    """Summary of the comparison of two SQL database objects."""

    def __init__(
        self,
        object_type: Literal["tables", "schemas"],
        object_1: str,
        object_2: str,
        description: str | None,
        sections: dict[str, Any],
    ):
        """
        Args:
            object_type: The type of object that the report summarizes the comparison for.
            object_1: The name of the first object from the comparison.
            object_2: The name of the second object from the comparison.
            description: An optional description to add before any sections.
            sections: The sections that this report contains.
        """
        self.meta = Metadata(
            object_type=object_type,
            object_1=object_1,
            object_2=object_2,
            description=description,
        )
        self.sections = [Section(name, content) for name, content in sections.items()]

    def format(self, formatter: Formatter, hide_matching_columns: bool = False) -> str:
        """Format this report with the provided formatter.

        Args:
            formatter: The formatter to use for converting this report into a string.
            hide_matching_columns: Whether to hide columns where the values are the same.

        Returns:
            The report, formatted with the provided formatter.
        """
        return formatter.format(
            self.meta,
            self.sections,
            hide_matching_columns=hide_matching_columns,
        )

    def __str__(self) -> str:
        formatter = TerminalFormatter(colored=False)
        return formatter.format(self.meta, self.sections)

    def __repr__(self) -> str:
        formatter = TerminalFormatter(colored=True)
        return formatter.format(self.meta, self.sections)
