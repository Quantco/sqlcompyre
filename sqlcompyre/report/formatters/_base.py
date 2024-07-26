# Copyright (c) QuantCo 2024-2024
# SPDX-License-Identifier: BSD-3-Clause

from abc import ABC, abstractmethod
from typing import Any

from sqlcompyre.results import ColumnMatches, Counts, Names, RowMatches

from ..schema import Metadata, Section


class Formatter(ABC):
    """Abstract base class for formatters of reports."""

    @property
    @abstractmethod
    def file_extension(self) -> str:
        """The file extension to use when this formatter's output is written to a
        file."""

    @abstractmethod
    def format(
        self,
        metadata: Metadata,
        sections: list[Section],
        hide_matching_columns: bool = False,
    ) -> str:
        """Format the metadata and the sections from a report.

        Returns:
            The formatted string describing the metadata and all sections.
        """

    def _format_content(self, content: Any, hide_matching_columns: bool) -> str:
        if isinstance(content, Names):
            return self._format_names(content)
        if isinstance(content, Counts):
            return self._format_counts(content)
        if isinstance(content, RowMatches):
            return self._format_table_row_matches(content)
        if isinstance(content, ColumnMatches):
            return self._format_table_column_matches(content, hide_matching_columns)
        raise NotImplementedError

    @abstractmethod
    def _format_names(self, names: Names) -> str:
        pass

    @abstractmethod
    def _format_counts(self, counts: Counts) -> str:
        pass

    @abstractmethod
    def _format_table_row_matches(self, row_matches: RowMatches) -> str:
        pass

    @abstractmethod
    def _format_table_column_matches(
        self, column_matches: ColumnMatches, hide_matching_columns: bool
    ) -> str:
        pass
