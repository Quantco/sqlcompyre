# Copyright (c) QuantCo 2024-2025
# SPDX-License-Identifier: BSD-3-Clause

from typing import Any

import sqlalchemy as sa
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.schema import DropTable
from sqlalchemy.sql import compiler


class TableFactory:
    """Simple utility class to create tables for testing."""

    def __init__(self, engine: sa.Engine, schema: str | None):
        """
        Args:
            engine: The engine to interact with the database.
            schema: The schema to create tables in or None if tables should be created in the
                default schema.
        """
        self.engine = engine
        self.schema = schema
        self.metadata = sa.MetaData()

    def create(
        self,
        name: str,
        columns: list[sa.Column],
        data: list[dict[str, Any]],
    ) -> sa.Table:
        """Creates a new table in the database with the given metadata and values."""
        table = sa.Table(name, self.metadata, *columns, schema=self.schema)
        with self.engine.begin() as trans:
            trans.execute(DropTable(table, if_exists=True))
        with self.engine.begin() as trans:
            table.create(trans)
            if len(data) > 0:
                trans.execute(table.insert().values(), data)
            return table

    def create_view(self, name: str, query: sa.Select) -> sa.Table:
        """Creates a new view in the database using the given query."""
        schema: str | None
        if self.schema is not None and len(self.schema.split(".")) > 1:
            # Multi-part schema
            database, schema = self.schema.split(".")
            engine = sa.create_engine(self.engine.url.set(database=database))
        else:
            engine = self.engine
            schema = self.schema

        fullname = name if schema is None else f"[{schema}].[{name}]"
        with engine.begin() as trans:
            trans.execute(_DropView(fullname))
        with engine.begin() as trans:
            trans.execute(_CreateView(fullname, query))

        # Return with self.schema instead of schema here to keep multi-part schemas
        columns = [
            sa.Column(name, col.type) for name, col in query.selected_columns.items()
        ]
        return sa.Table(name, self.metadata, *columns, schema=self.schema)


# -------------------------------------------------------------------------------------------------
# DROP VIEW
# -------------------------------------------------------------------------------------------------


class _DropView(sa.DDLElement):
    def __init__(self, name: str):
        self.name = name


@compiles(_DropView)
def visit_drop_view(  # noqa
    element: _DropView, compiler: compiler.SQLCompiler, **kw: Any
):
    return f"DROP VIEW IF EXISTS {element.name}"


# -------------------------------------------------------------------------------------------------
# CREATE VIEW
# -------------------------------------------------------------------------------------------------


class _CreateView(sa.DDLElement):
    def __init__(self, name: str, select: sa.Select):
        self.name = name
        self.select = select


@compiles(_CreateView)
def visit_create_view(  # noqa
    element: _CreateView, compiler: compiler.SQLCompiler, **kw: Any
):
    return (
        f"CREATE VIEW {element.name} "
        f"AS {compiler.sql_compiler.process(element.select, literal_binds=True)}"
    )
