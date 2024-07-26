# Copyright (c) QuantCo 2024-2024
# SPDX-License-Identifier: BSD-3-Clause

from collections.abc import Callable
from typing import TypeVar

from ._base import Formatter

F = TypeVar("F", bound=Formatter)

_FORMATTERS = {}


def register(name: str) -> Callable[[type[F]], type[F]]:
    def decorator(cls: type[F]) -> type[F]:
        _FORMATTERS[name] = cls
        return cls

    return decorator


def get_formatter(name: str) -> Formatter:
    """Get the formatter for the specified identifier.

    Args:
        name: The identifier of the formatter.

    Returns:
        The initialized formatter.

    Raises:
        ValueError: If no formatter for the given identifier can be found.
    """
    if name not in _FORMATTERS:
        raise ValueError(f"Unknown formatter identifier '{name}'")
    return _FORMATTERS[name]()
