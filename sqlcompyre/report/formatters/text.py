# Copyright (c) QuantCo 2024-2024
# SPDX-License-Identifier: BSD-3-Clause

from ._factory import register
from .terminal import TerminalFormatter


@register("text")
class TextFormatter(TerminalFormatter):
    """Formatter for rendering reports as text (= non-colored terminal formatting)."""

    def __init__(self):
        super().__init__(colored=False)
