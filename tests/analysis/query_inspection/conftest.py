# Copyright (c) QuantCo 2024-2024
# SPDX-License-Identifier: BSD-3-Clause


import pytest
import sqlalchemy as sa
from sqlalchemy import Column, Integer, String

from tests._shared import TableFactory

CHARACTER_DATA = [
    dict(first_name="Donald", last_name="Duck", age=27),
    dict(first_name="Donald", last_name="Duck", age=27),
    dict(first_name="Daisy", last_name="Duck", age=26),
    dict(first_name="Huey", last_name="Duck", age=6),
    dict(first_name="Dewey", last_name="Duck", age=6),
    dict(first_name="Louie", last_name="Duck", age=6),
    dict(first_name="Scrooge", last_name="McDuck", age=65),
    dict(first_name="Gladstone", last_name="Gander", age=35),
]


def columns() -> list[Column]:
    return [
        Column("first_name", String(length=20)),
        Column("last_name", String(length=20)),
        Column("age", Integer()),
    ]


@pytest.fixture(scope="session")
def table_characters(table_factory: TableFactory) -> sa.Table:
    return table_factory.create("characters", columns(), CHARACTER_DATA)
