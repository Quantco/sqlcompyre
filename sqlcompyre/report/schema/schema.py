# Copyright (c) QuantCo 2024-2024
# SPDX-License-Identifier: BSD-3-Clause

from dataclasses import dataclass
from typing import Any


@dataclass
class Metadata:
    """Metadata available for a comparison."""

    #: The type of object being compared.
    object_type: str
    #: The name of the first object being compared.
    object_1: str
    #: The name of the second object being compared.
    object_2: str
    #: An optional description describing the comparison.
    description: str | None


@dataclass
class Section:
    """Information about a single section within a report."""

    #: The name of the section.
    name: str
    #: The content of the section.
    content: Any
