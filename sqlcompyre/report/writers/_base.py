# Copyright (c) QuantCo 2024-2024
# SPDX-License-Identifier: BSD-3-Clause

from abc import ABC, abstractmethod

from .. import Report
from ..formatters import Formatter


class Writer(ABC):
    """Abstract base class for writers of reports."""

    def __init__(self, formatter: Formatter):
        """
        Args:
            formatter: The formatter to use for rendering reports.
        """
        self.formatter = formatter

    @abstractmethod
    def write(
        self, reports: dict[str, Report], hide_matching_columns: bool = False
    ) -> None:
        """Write the provided reports to this writer's sink.

        Args:
            reports: A set of reports, mapped from an identifier to the report.
            hide_matching_columns: Whether to hide columns from the report which show a perfect
                (i.e. 100%) match rate.
        """
