# Copyright (c) QuantCo 2024-2025
# SPDX-License-Identifier: BSD-3-Clause

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.mssql import dialect as SqlAlchemyMssqlDialect  # noqa: N812

from ._base import DialectProtocol


class MssqlDialect(SqlAlchemyMssqlDialect, DialectProtocol):  # type: ignore
    """Dialect for Microsoft SQL Server."""

    name: str = "mssql"
    verbose_name: str = "Microsoft SQL Server"
    supports_schemas: bool = True
    supports_multi_part_schemas: bool = True
    case_sensitive_collation: str = "Latin1_General_CS_AS"
    case_insensitive_collation: str = "SQL_Latin1_General_CP1_CI_AS"
    views_support_notnull_columns: bool = True

    def get_table_creation_timestamps(
        self, engine: sa.Engine, tables: list[sa.Table]
    ) -> list[datetime]:
        # Potentially, we need to get the database from the tables
        db: str | None = None
        for table in tables:
            name = str(table)
            if name.count(".") > 1:
                table_db = name.split(".")[0]
                if db is not None and table_db != db:
                    raise ValueError(
                        "creation timestamps can only be queried from tables "
                        "within a single database"
                    )
                db = table_db
            elif db is not None:
                # Another table specified a database
                raise ValueError(
                    "all tables for which creation dates ought to be queried must "
                    "have the same number of schema parts"
                )

        # Then, we can define the structure of the tables we want to query...
        meta = sa.MetaData()
        sys_tables = sa.Table(
            "tables",
            meta,
            sa.Column("name", sa.String()),
            sa.Column("create_date", sa.TIMESTAMP()),
            sa.Column("schema_id", sa.Integer()),
            schema="sys" if db is None else f"{db}.sys",
        )
        sys_views = sa.Table(
            "views",
            meta,
            sa.Column("name", sa.String()),
            sa.Column("create_date", sa.TIMESTAMP()),
            sa.Column("schema_id", sa.Integer()),
            schema="sys" if db is None else f"{db}.sys",
        )
        sys_schemas = sa.Table(
            "schemas",
            meta,
            sa.Column("name", sa.String()),
            sa.Column("schema_id", sa.Integer()),
            schema="sys" if db is None else f"{db}.sys",
        )

        # ...and send the query eventually
        table_query = sa.select(
            (sys_schemas.c["name"] + "." + sys_tables.c["name"]),
            sys_tables.c["create_date"],
        ).join(sys_schemas, sys_tables.c["schema_id"] == sys_schemas.c["schema_id"])
        view_query = sa.select(
            (sys_schemas.c["name"] + "." + sys_views.c["name"]),
            sys_views.c["create_date"],
        ).join(sys_schemas, sys_views.c["schema_id"] == sys_schemas.c["schema_id"])
        query = table_query.union(view_query)

        with engine.connect() as conn:
            query_result = conn.execute(query)

            # Extract the creation dates
            mapping = {}
            for name, create_date in query_result:
                full_name = name if db is None else f"{db}.{name}"
                mapping[full_name] = create_date

        return [mapping[str(t)] for t in tables]
