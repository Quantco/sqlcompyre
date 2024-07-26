# Copyright (c) QuantCo 2024-2024
# SPDX-License-Identifier: BSD-3-Clause

from collections.abc import Callable
from typing import TypeVar

from ..formatters import Formatter
from ._base import Writer

F = TypeVar("F", bound=Writer)

_WRITERS = {}


def register(name: str) -> Callable[[type[F]], type[F]]:
    def decorator(cls: type[F]) -> type[F]:
        _WRITERS[name] = cls
        return cls

    return decorator


def get_writer(name: str, formatter: Formatter) -> Writer:
    """Get the writer for the specified identifier.

    Args:
        name: The identifier of the writer.
        formatter: The formatter that the writer ought to use.

    Returns:
        The initialized writer.

    Raises:
        ValueError: If no writer for the given identifier can be found.
    """
    if name not in _WRITERS:
        raise ValueError(f"Unknown writer identifier '{name}'")
    return _WRITERS[name](formatter)
