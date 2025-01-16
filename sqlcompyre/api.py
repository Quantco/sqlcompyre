# Copyright (c) QuantCo 2024-2025
# SPDX-License-Identifier: BSD-3-Clause

import sys

import sqlalchemy as sa

from .analysis import QueryInspection, SchemaComparison, TableComparison

# ---------------------------------------------------------------------------------------------
# INSPECTIONS
# ---------------------------------------------------------------------------------------------


def inspect(engine: sa.Engine, query: sa.Select | sa.FromClause) -> QueryInspection:
    """Inspect the results of a query in the database.

    Args:
        engine: The engine to use to access the database.
        query: The query whose results to inspect. This can either be a SQLAlchemy ``SELECT``
            statement or a ``FROM`` clause (which includes plain :class:`sqlalchemy.Table`
            objects).

    Returns:
        A query inspection object that can be used to easily gain insights into the query
        result.

    See also:
        :meth:`inspect_table` if you want to inspect the results of ``SELECT * FROM table`` and
        specify the table as a string.
    """
    if isinstance(query, sa.Select):
        return QueryInspection(engine, query.subquery())
    return QueryInspection(engine, query)


def inspect_table(engine: sa.Engine, table: sa.Table | str) -> QueryInspection:
    """Inspect a table in the database.

    Args:
        engine: The engine to use to access the database.
        table: The database table to inspect. When specified as string, the table can optionally
            be specified with schema (and database) name. For MSSQL, the table name can be
            specified as ``[[<database>.]<schema>.]<table>`` depending on the "default" database
            of the provided engine and the database's default schema.

    Returns:
        A query inspection object that can be used to easily gain insights into the table.

    See also:
        :meth:`inspect` if you want to inspect only a subset of a table or have a
        :class:`sqlalchemy.Table` object. This method should preferably only be used when
        specifying the table name as a string.
    """
    if isinstance(table, str):
        schema = _get_schema_name_from_table(table)
        meta = sa.MetaData()
        meta.reflect(bind=engine, schema=schema, views=True)
        sa_table = meta.tables[table]
    else:
        sa_table = table
    return inspect(engine, sa_table)


# ---------------------------------------------------------------------------------------------
# COMPARISONS
# ---------------------------------------------------------------------------------------------


def compare_tables(
    engine: sa.Engine,
    left: sa.Select | sa.FromClause | str,
    right: sa.Select | sa.FromClause | str,
    join_columns: list[str] | None = None,
    ignore_columns: list[str] | None = None,
    column_name_mapping: dict[str, str] | None = None,
    float_precision: float = sys.float_info.epsilon,
    collation: str | None = None,
    ignore_casing: bool = False,
    infer_primary_keys: bool = False,
) -> TableComparison:
    """Compare two tables in the database.

    Args:
        engine: The engine to use to access the database.
        left: The "left" database table for the comparison. The table can optionally be
            specified with schema (and database) name. For MSSQL, the table name can be
            specified as ``[[<database>.]<schema>.]<table>`` depending on the "default"
            database of the provided engine and the database's default schema. If provided as a
            SQLAlchemy table, the name is extracted automatically.
        right: The "right" database table to compare to the "left" table. The naming convention
            follows the convention for the "left" table.
        join_columns: The columns to join the tables on in order to compare column values. If
            not provided, defaults to the union of primary keys. The corresponding
            primary key(s) of the right table are determined via ``column_name_mapping``.
        ignore_columns: Columns to ignore to evaluate equality. These column names should
            reference the left table: corresponding columns in the right table are determined
            via ``column_name_mapping``. Primary key columns passed here are ignored.
        column_name_mapping: A mapping from column names in the left table to column names in
            the right table. If not provided, defaults to mapping columns with the same names.
        float_precision: The precision of floating point comparisons. Values with an absolute
            difference below the precision are considered equal.
        collation: An optional collation that is used to compare strings. Useful for making
            case-sensitive comparisons even if a table's column uses a case-insensitive
            collation.
        ignore_casing: Whether casing (e.g. capitalization) should be ignored when matching
            column names. This is valuable if only interacting with the database through
            case-insensitive tools (e.g. SQL).
        infer_primary_keys: Allows SQLCompyre to build a primary key from all matching columns
            automatically and use it to match tables even if they do not have a primary key.

    Returns:
        A table comparison object that can be used to explore the differences in the tables.
    """
    # Get the SQLAlchemy representation of the tables in the database
    left_table: sa.FromClause
    right_table: sa.FromClause
    if isinstance(left, str) or isinstance(right, str):
        meta = sa.MetaData()

        if isinstance(left, str):
            left_schema = _get_schema_name_from_table(left)
            meta.reflect(bind=engine, schema=left_schema, views=True)
            left_table = meta.tables[left]

        if isinstance(right, str):
            right_schema = _get_schema_name_from_table(right)
            meta.reflect(bind=engine, schema=right_schema, views=True)
            right_table = meta.tables[right]

    if not isinstance(left, str):
        left_table = left.subquery() if isinstance(left, sa.Select) else left
    if not isinstance(right, str):
        right_table = right.subquery() if isinstance(right, sa.Select) else right

    # Create a table comparison object
    return TableComparison(
        engine=engine,
        left_table=left_table,
        right_table=right_table,
        join_columns=join_columns,
        ignore_columns=ignore_columns,
        column_name_mapping=column_name_mapping,
        float_precision=float_precision,
        collation=collation,
        ignore_casing=ignore_casing,
        infer_primary_keys=infer_primary_keys,
    )


def compare_schemas(
    engine: sa.Engine,
    left: str,
    right: str,
    include_views: bool = False,
    float_precision: float = sys.float_info.epsilon,
    collation: str | None = None,
    ignore_casing: bool = False,
) -> SchemaComparison:
    """Compare all tables from two schemas in the database. For multi-part schemas (e.g.
    for MSSQL), it is possible to only specify the first part of the schema and compare
    tables from all schemas. In MSSQL, this allows comparing entire databases.

    Currently, the comparison only compares tables with the same name (and the same schema for
    multi-part schema comparisons).

    Args:
        engine: The engine to use to access the database.
        left: The name of the "left" schema from which to use tables. For multi-part schemas,
            the schema may be specified as ``<database>.*`` which then references all schemas
            (and tables) in ``<database>``. Note that this notation is merely a convention and
            general regex/glob notation is not supported.
        right: The name of the "right" schema whose tables to compare to those of the "left"
            one. The naming convention follows the convention for the "left" schema.
        include_views: Whether to include views in the comparison.
        float_precision: The precision of floating point comparisons. Values with an absolute
            difference below the precision are considered equal.
        collation: An optional collation that is used to compare strings. Useful for making
            case-sensitive comparisons even if a table's column uses a case-insensitive
            collation.
        ignore_casing: Whether casing (e.g. capitalization) should be ignored when matching
            table names. This is valuable if only interacting with the database through
            case-insensitive tools (e.g. SQL).

    Returns:
        A schema comparison object.
    """
    # Check that both "left" and "right" reference db or schema
    if left.endswith(".*") != right.endswith(".*"):
        raise ValueError(
            "Both `left` and `right` must either reference a schema or a database."
        )

    # Extract database names for multi-part schemas
    is_db_comparison = left.endswith(".*")
    left_name = left[:-2] if is_db_comparison else left
    right_name = right[:-2] if is_db_comparison else right

    # Find all tables in left and right schema/database
    left_tables = _get_tables_from_schema(
        engine,
        left_name,
        is_database=is_db_comparison,
        include_views=include_views,
    )
    right_tables = _get_tables_from_schema(
        engine,
        right_name,
        is_database=is_db_comparison,
        include_views=include_views,
    )

    # Create the schema comparison object. To obtain the table names, we split off the "prefix"
    # resulting from the `left` and `right` arguments.
    return SchemaComparison(
        engine=engine,
        left_schema=left,
        right_schema=right,
        left_tables={str(table)[len(left_name) + 1 :]: table for table in left_tables},
        right_tables={
            str(table)[len(right_name) + 1 :]: table for table in right_tables
        },
        float_precision=float_precision,
        collation=collation,
        ignore_casing=ignore_casing,
    )


# ---------------------------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------------------------


def _get_schema_name_from_table(table: str) -> str | None:
    splits = table.rsplit(".", maxsplit=1)
    if len(splits) == 1:
        return None
    return splits[0]


def _get_tables_from_schema(
    engine: sa.Engine,
    schema: str,
    is_database: bool,
    include_views: bool,
) -> list[sa.Table]:
    if is_database:
        engine = sa.create_engine(engine.url.set(database=schema))
        schemas = sa.inspect(engine).get_schema_names()
        nested_tables = [
            _get_tables_from_schema(
                engine, f"{schema}.{s}", is_database=False, include_views=include_views
            )
            for s in schemas
        ]
        return [table for schema in nested_tables for table in schema]
    meta = sa.MetaData()
    meta.reflect(bind=engine, schema=schema, views=include_views)
    return list(meta.tables.values())
