# Copyright (c) QuantCo 2024-2024
# SPDX-License-Identifier: BSD-3-Clause

"""Writers for outputting sets of reports to a destination."""

from ._base import Writer
from ._factory import get_writer
from .file import FileWriter
from .markdown import MarkdownWriter
from .stdout import StdoutWriter

__all__ = [
    "Writer",
    "get_writer",
    "FileWriter",
    "MarkdownWriter",
    "StdoutWriter",
]
