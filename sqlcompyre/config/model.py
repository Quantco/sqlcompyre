# Copyright (c) QuantCo 2024-2024
# SPDX-License-Identifier: BSD-3-Clause


from pydantic import BaseModel, Field


class Config(BaseModel):
    ignore_tables: list[str] = Field(default_factory=lambda: [])
    ignore_table_columns: dict[str, list[str]] = Field(default_factory=lambda: {})
