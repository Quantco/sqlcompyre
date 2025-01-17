# Copyright (c) QuantCo 2024-2025
# SPDX-License-Identifier: BSD-3-Clause

import copy

import pytest
import sqlalchemy as sa

from tests._shared import TableFactory

STUDENT_DATA = [
    dict(id=1, name="Michael", age=22, gpa=2.57),
    dict(id=2, name="Emma", age=20, gpa=3.45),
    dict(id=3, name="Olivia", age=17, gpa=3.55),
    dict(id=4, name="James", age=51, gpa=3.88),
    dict(id=5, name="Charlotte", age=52, gpa=3.95),
]


def base_columns() -> list[sa.Column]:
    return [
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=False),
        sa.Column("name", sa.String(length=50)),
        sa.Column("age", sa.Integer()),
        sa.Column("gpa", sa.Float()),
    ]


def alt_columns() -> list[sa.Column]:
    return [
        sa.Column("id_v2", sa.Integer(), primary_key=True, autoincrement=False),
        sa.Column("name_v2", sa.String(length=50)),
        sa.Column("age_v2", sa.Integer()),
        sa.Column("gpa_v2", sa.Float()),
    ]


def alt_columns_small() -> list[sa.Column]:
    return [
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=False),
        sa.Column("name", sa.String(length=50)),
        sa.Column("age_v2", sa.Integer()),
        sa.Column("gpa_v2", sa.Float()),
    ]


def cased_columns() -> list[sa.Column]:
    return [
        sa.Column("Id", sa.Integer(), primary_key=True, autoincrement=False),
        sa.Column("Name", sa.String(length=50)),
        sa.Column("Age", sa.Integer()),
        sa.Column("Gpa", sa.Float()),
    ]


@pytest.fixture(scope="session")
def table_students(table_factory: TableFactory) -> sa.Table:
    return table_factory.create("students", base_columns(), STUDENT_DATA)


@pytest.fixture(scope="session")
def view_students(table_factory: TableFactory, table_students: sa.Table) -> sa.Table:
    return table_factory.create_view("students_view", sa.select(table_students))


@pytest.fixture(scope="session")
def table_students_small(table_factory: TableFactory) -> sa.Table:
    data = STUDENT_DATA[1:]
    return table_factory.create("students_small", base_columns(), data)


@pytest.fixture(scope="session")
def table_students_modified_1(table_factory: TableFactory) -> sa.Table:
    data = copy.deepcopy(STUDENT_DATA[1:])
    data[1]["age"] = 18
    return table_factory.create("students_modified_1", base_columns(), data)


@pytest.fixture(scope="session")
def table_students_modified_2(table_factory: TableFactory) -> sa.Table:
    data = STUDENT_DATA[:-1]
    return table_factory.create("students_modified_2", base_columns(), data)


@pytest.fixture(scope="session")
def table_students_modified_3(table_factory: TableFactory) -> sa.Table:
    data = [{**x, "gpa": x["gpa"] + 0.1} for x in STUDENT_DATA]  # type: ignore
    return table_factory.create("students_modified_3", base_columns(), data)


@pytest.fixture(scope="session")
def table_students_narrow(table_factory: TableFactory) -> sa.Table:
    return table_factory.create("students_narrow", base_columns()[:3], STUDENT_DATA)


@pytest.fixture(scope="session")
def table_students_renamed(table_factory: TableFactory) -> sa.Table:
    data = [
        {f"{key}_v2": value for key, value in student.items()}
        for student in STUDENT_DATA[:-1]
    ]
    return table_factory.create("students_renamed", alt_columns(), data)


@pytest.fixture(scope="session")
def table_students_partly_renamed(table_factory: TableFactory) -> sa.Table:
    data = [
        {
            (f"{key}_v2" if key in ("age", "gpa") else key): value
            for key, value in student.items()
        }
        for student in STUDENT_DATA[:-1]
    ]
    return table_factory.create("students_partly_renamed", alt_columns_small(), data)


@pytest.fixture(scope="session")
def table_students_cased(table_factory: TableFactory) -> sa.Table:
    data = [
        {key.capitalize(): value for key, value in student.items()}
        for student in STUDENT_DATA[:-1]
    ]
    return table_factory.create("students_cased", cased_columns(), data)


@pytest.fixture(scope="session")
def table_students_other_schema(table_factory_extra: TableFactory) -> sa.Table:
    return table_factory_extra.create("students", base_columns(), STUDENT_DATA)
