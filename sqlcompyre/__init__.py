# Copyright (c) QuantCo 2024-2024
# SPDX-License-Identifier: BSD-3-Clause

import warnings as _warnings
from importlib import metadata as _metadata

try:
    __version__ = _metadata.version(__name__)
except _metadata.PackageNotFoundError as e:  # pragma: no cover
    _warnings.warn(f"Could not determine version of {__name__}\n{e!s}", stacklevel=2)
    __version__ = "unknown"

from .api import compare_schemas, compare_tables, inspect, inspect_table
from .config import Config

__all__ = [
    "compare_schemas",
    "compare_tables",
    "inspect",
    "inspect_table",
    "Config",
]
