# Copyright (c) QuantCo 2024-2024
# SPDX-License-Identifier: BSD-3-Clause

import shutil

from .. import Report
from ._base import Writer
from ._factory import register


@register("stdout")
class StdoutWriter(Writer):
    """Writer that outputs reports to standard output."""

    def write(
        self, reports: dict[str, Report], hide_matching_columns: bool = False
    ) -> None:
        size = shutil.get_terminal_size((80, 20))
        n_reports = len(reports)
        for i, (identifier, report) in enumerate(reports.items()):
            if i > 0:
                # Additional newline when printing n-th (n > 1) report
                print()
            if n_reports > 1:
                # Only print header if there is more than one report
                n_whitespace = max(0, size.columns - len(identifier) - 3)
                print(
                    "+" + "-" * (size.columns - 2) + "+",
                    "| " + identifier + " " * n_whitespace + "|",
                    "+" + "-" * (size.columns - 2) + "+",
                    sep="\n",
                    end="\n\n",
                )
            print(
                report.format(
                    self.formatter, hide_matching_columns=hide_matching_columns
                )
            )
