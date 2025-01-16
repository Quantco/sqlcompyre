# Copyright (c) QuantCo 2024-2025
# SPDX-License-Identifier: BSD-3-Clause

import math
from typing import Any

import tabulate

from sqlcompyre.results import ColumnMatches, Counts, Names, RowMatches

from ..schema import Metadata, Section
from ._base import Formatter
from ._factory import register


@register("terminal")
class TerminalFormatter(Formatter):
    """Formatter for printing reports to the terminal."""

    def __init__(self, colored: bool = True):
        """
        Args:
            colored: Whether the report should be colored.
        """
        self.colored = colored

    @property
    def file_extension(self) -> str:
        return "txt"

    def format(
        self,
        metadata: Metadata,
        sections: list[Section],
        hide_matching_columns: bool = False,
    ) -> str:
        # "Heading" with the metadata
        result = _colored(
            _underline(f"SQLCompyre Comparison of {metadata.object_type.capitalize()}"),
            context="title",
            enable=self.colored,
        )
        result += "\n" + _colored(
            f" -> '{metadata.object_1}' vs '{metadata.object_2}'",
            context="bold",
            enable=self.colored,
        )
        if metadata.description is not None:
            result += "\n\n" + "\n".join(
                " " * 2 + line for line in metadata.description.split("\n")
            )

        # Sections
        for section in sections:
            result += (
                "\n\n"
                + _colored(
                    _underline(section.name), context="heading", enable=self.colored
                )
                + self._format_content(
                    section.content, hide_matching_columns=hide_matching_columns
                )
            )

        return result

    # ---------------------------------------------------------------------------------------------

    def _format_names(self, names: Names) -> str:
        content = f" Number in common: {len(names.in_common):,}\n"
        content += f" Missing in left:  {names.missing_left}\n"
        content += f" Missing in right: {names.missing_right}"
        return content

    def _format_counts(self, counts: Counts) -> str:
        content = [
            ["Count", f"{counts.left:,}", f"{counts.right:,}"],
            ["Difference", f"{counts.gain_left:+,}", f"{counts.gain_right:+,}"],
            [
                "Fraction",
                f"{_safe_div(counts.left, counts.right):.3f}",
                f"{_safe_div(counts.right, counts.left):.3f}",
            ],
        ]
        return self._tabulate(content)

    def _format_table_row_matches(self, row_matches: RowMatches) -> str:
        # Additional calculations
        fraction_joined_equal = _safe_div(
            row_matches.n_joined_equal, row_matches.n_joined_total
        )
        fraction_joined_unequal = _safe_div(
            row_matches.n_joined_unequal, row_matches.n_joined_total
        )
        fraction_unjoined_left = _safe_div(
            row_matches.n_unjoined_left,
            row_matches.n_unjoined_left + row_matches.n_joined_total,
        )
        fraction_unjoined_right = _safe_div(
            row_matches.n_unjoined_right,
            row_matches.n_unjoined_right + row_matches.n_joined_total,
        )

        # Formatting
        str_joined_identical = f"[{fraction_joined_equal:.2%}]"
        str_joined_nonidentical = f"[{fraction_joined_unequal:.2%}]"
        str_unjoined_left = f"[{fraction_unjoined_left:.2%}]"
        str_unjoined_right = f"[{fraction_unjoined_right:.2%}]"
        lhs_len = max(len(str_joined_identical), len(str_unjoined_left))
        rhs_len = max(len(str_joined_nonidentical), len(str_unjoined_right))

        # Table definition
        content = [
            [
                "Joined (identical/non-identical)",
                f"{row_matches.n_joined_equal:,} {_pad(lhs_len - len(str_joined_identical))}"
                f"{str_joined_identical}",
                f"{row_matches.n_joined_unequal:,} {_pad(rhs_len - len(str_joined_nonidentical))}"
                f"{str_joined_nonidentical}",
            ],
            [
                "Unjoined (left/right)",
                f"{row_matches.n_unjoined_left:,} {_pad(lhs_len - len(str_unjoined_left))}"
                f"{str_unjoined_left}",
                f"{row_matches.n_unjoined_right:,} {_pad(rhs_len - len(str_unjoined_right))}"
                f"{str_unjoined_right}",
            ],
        ]
        return self._tabulate(content)

    def _format_table_column_matches(
        self, column_matches: ColumnMatches, hide_matching_columns: bool = False
    ) -> str:
        content = [
            [
                name,
                # We use math.floor here to make sure that we don't display 100.00% match
                # rate if the actual match rate is not exactly 100% (but e.g. 99.9999%).
                "n/a"
                if math.isnan(match)
                else f"{math.floor(match * 10000) / 10000:.2%}",
            ]
            for name, match in sorted(
                column_matches.fraction_same.items(), key=lambda x: x[0]
            )
            if not hide_matching_columns or match != 1.0
        ]
        return self._tabulate(content)

    # ---------------------------------------------------------------------------------------------

    def _tabulate(self, content: Any) -> str:
        if len(content) == 0:
            return ""
        return tabulate.tabulate(
            content,  # type: ignore
            tablefmt="presto",
            colalign=("left",) + ("right",) * (len(content[0]) - 1),
            disable_numparse=True,
        )


# -------------------------------------------------------------------------------------------------


def _safe_div(lhs: int, rhs: int) -> float:
    try:
        return lhs / rhs
    except ZeroDivisionError:
        return float("nan")


def _colored(text: str, context: str, enable: bool) -> str:
    if not enable:
        return text

    match context:
        case "title":
            code = "1;34"  # bold blue
        case "heading":
            code = "1;94"  # bold light blue
        case "bold":
            code = "1"  # bold
        case _:
            raise NotImplementedError

    return f"\033[{code}m{text}\033[0m"


def _underline(text: str) -> str:
    return text + "\n" + "=" * len(text) + "\n"


def _pad(n: int) -> str:
    return " " * n
