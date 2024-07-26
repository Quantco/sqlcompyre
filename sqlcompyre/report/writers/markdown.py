# Copyright (c) QuantCo 2024-2024
# SPDX-License-Identifier: BSD-3-Clause

from .. import Report
from ._base import Writer
from ._factory import register


@register("markdown")
class MarkdownWriter(Writer):
    """Writer that outputs reports to standard output as Markdown.

    This writer is especially useful for printing comparisons to GitHub, e.g. as part of
    comments inside pull requests.
    """

    def write(
        self, reports: dict[str, Report], hide_matching_columns: bool = False
    ) -> None:
        for identifier, report in reports.items():
            fmt = report.format(
                self.formatter, hide_matching_columns=hide_matching_columns
            )
            print(
                f"<details><summary><b>{identifier}</b></summary>",
                f"```\n{fmt}\n```",
                "</details>",
                sep="\n\n",
            )
