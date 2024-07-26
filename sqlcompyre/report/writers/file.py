# Copyright (c) QuantCo 2024-2024
# SPDX-License-Identifier: BSD-3-Clause

import logging
from pathlib import Path

from .. import Report
from ..formatters import Formatter
from ._base import Writer
from ._factory import register


@register("file")
class FileWriter(Writer):
    """Writer that outputs reports to a set of files.

    The files are written to the ``.compyre`` directory which is created if it does not
    yet exist. Each report is then written to a dedicated file in that directory: the
    name of each file is the report's identifier and the extension is set to the
    formatter's configured file extension.
    """

    def __init__(self, formatter: Formatter):
        """
        Args:
            formatter: The formatter to use for rendering reports.
        """
        super().__init__(formatter)

        # Check path
        path = Path.cwd() / ".compyre"
        if path.exists():
            if path.is_file():
                raise ValueError("'%s' is not a directory")
            if any(path.iterdir()):
                logging.warning(
                    "'%s' is not empty, adding and possibly overwriting files.", path
                )
        else:
            path.mkdir()

        # Assign to instance attribute
        self.path = path

    def write(
        self, reports: dict[str, Report], hide_matching_columns: bool = False
    ) -> None:
        for identifier, report in reports.items():
            file_path = self.path / f"{identifier}.{self.formatter.file_extension}"
            file_path.write_text(
                report.format(
                    self.formatter, hide_matching_columns=hide_matching_columns
                ),
                encoding="utf-8",
            )
