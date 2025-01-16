# Copyright (c) QuantCo 2024-2025
# SPDX-License-Identifier: BSD-3-Clause

import logging
import re
from functools import cached_property
from typing import Literal, cast

import sqlalchemy as sa
from tqdm.auto import tqdm

from sqlcompyre.report import Report
from sqlcompyre.results import Counts, Names

from .dialects import DialectProtocol
from .table_comparison import TableComparison


class SchemaComparison:
    """Compare the table metadata from two different SQL database schemas.

    Note:
        This class should never be initialized directly. Use the
        :meth:`~sqlcompyre.api.compare_schemas` function instead.
    """

    def __init__(
        self,
        engine: sa.Engine,
        left_schema: str,
        right_schema: str,
        left_tables: dict[str, sa.Table],
        right_tables: dict[str, sa.Table],
        float_precision: float,
        collation: str | None,
        ignore_casing: bool,
    ):
        """
        Args:
            engine: The engine to use for connecting to the database.
            left_schema: The name of the "left" schema. Purely informational.
            right_schema: The name of the "right" schema. Purely informational.
            left_tables: A mapping from fully-qualified table names to all tables in the "left"
                schema.
            right_tables: A mapping from fully-qualified table names to all tables in the "right"
                schema.
            float_precision: The precision of floating point comparisons.
            collation: An optional collation to use for comparing string columns.
            ignore_casing: Whether casing (e.g. capitalization) should be ignored when matching
                table names.
        """
        self.engine = engine
        self.left_schema = left_schema
        self.right_schema = right_schema
        self.left_tables = left_tables
        self.right_tables = right_tables
        self.float_precision = float_precision
        self.collation = collation
        self.ignore_casing = ignore_casing

    # ---------------------------------------------------------------------------------------------
    # COMPARISON
    # ---------------------------------------------------------------------------------------------

    @cached_property
    def table_counts(self) -> Counts:
        """A comparison between the number of tables in each schema."""
        return Counts(
            left=len(self.left_tables),
            right=len(self.right_tables),
        )

    @cached_property
    def table_names(self) -> Names:
        """A comparison between the table names of the two schemas."""
        return Names(
            left=set(self.left_tables.keys()),
            right=set(self.right_tables.keys()),
            name_mapping=None,
            ignore_casing=self.ignore_casing,
        )

    def compare_matched_table(
        self,
        name: str,
        join_columns: list[str] | None = None,
        ignore_columns: list[str] | None = None,
        column_name_mapping: dict[str, str] | None = None,
        infer_primary_keys: bool = False,
    ) -> TableComparison:
        """A full comparison between the tables in "left" and "right" schema with the
        specified name. The name must be available in ``table_names.in_common``.

        Args:
            name: The name of the table (possibly including a schema name if this schema comparison
                compares multi-part schemas).
            join_columns: The columns to join the tables on in order to compare column values. If
                not provided, defaults to the union of primary keys. The corresponding
                primary key(s) of the right table are determined via ``column_name_mapping``.
            ignore_columns: Columns to ignore to evaluate equality. These column names should
                reference the left table: corresponding columns in the right table are determined
                via ``column_name_mapping``. Primary key columns passed here are ignored.
            column_name_mapping: A mapping from column names in the left table to column names in
                the right table. If not provided, defaults to mapping columns with the same names.
            infer_primary_keys: Whether primary keys should be inferred if the tables do not have
                matching primary key(s).

        Returns:
            The full comparison between the tables.
        """
        if self.ignore_casing:
            # Find table names irrespective of casing
            if name.lower() not in self.table_names.in_common:
                raise ValueError(
                    "The table name is not available in at least one schema."
                )

            left_mapping = {
                name.lower(): table for name, table in self.left_tables.items()
            }
            left_table = left_mapping[name.lower()]

            right_mapping = {
                name.lower(): table for name, table in self.right_tables.items()
            }
            right_table = right_mapping[name.lower()]
        else:
            # Find table name with correct casing
            if name not in self.table_names.in_common:
                raise ValueError(
                    "The table name is not available in at least one schema."
                )

            left_table = self.left_tables[name]
            right_table = self.right_tables[name]

        return TableComparison(
            engine=self.engine,
            left_table=left_table,
            right_table=right_table,
            join_columns=join_columns,
            ignore_columns=ignore_columns,
            column_name_mapping=column_name_mapping,
            float_precision=self.float_precision,
            collation=self.collation,
            ignore_casing=self.ignore_casing,
            infer_primary_keys=infer_primary_keys,
        )

    # ---------------------------------------------------------------------------------------------
    # SUMMARY REPORT
    # ---------------------------------------------------------------------------------------------

    def summary_report(self) -> Report:
        """Generate a report that summarizes the schema comparison."""
        return Report(
            "schemas",
            self.left_schema,
            self.right_schema,
            description=None,
            sections={
                "Table Names": self.table_names,
                "Table Counts": self.table_counts,
            },
        )

    def table_reports(
        self,
        ignore_tables: list[str] | None = None,
        ignore_table_columns: dict[str, list[str]] | None = None,
        skip_equal: bool = False,
        infer_primary_keys: bool = False,
        sort_by: Literal["name", "creation_timestamp"] = "name",
        verbose: bool = True,
    ) -> dict[str, Report]:
        """Generate reports for all tables matched between the schemas.

        Args:
            ignore_tables: A list of regexes specifying tables to ignore completely. Consider
                using ``^`` and ``$`` to match full table names.
            ignore_table_columns: A mapping from table names to column names. The provided columns
                are ignored to evaluate equality and dropped from all reports. Different to the
                behavior for ``ignore_tables``, table names are not considered to be regular
                expressions.
            ignore: A mapping from table names to column names. Each table which provides no
                column names is ignored completely. If at least one column name is provided, the
                provided columns are ignored to evaluate equality.
            skip_equal: Whether to skip reports about tables which are equal in the two schemas.
                Tables that cannot be compared for equality (e.g. because they have no primary key)
                are still included.
            infer_primary_keys: Whether primary keys should be inferred if compared tables do not
                have matching primary key(s).
            sort_by: The strategy for sorting the table reports. Either alphabetically by the name
                of the tables (``name``) or chronologically by the creation timestamp of the tables
                in the "left" schema (``creation_timestamp``). Note that the latter option is not
                supported for all database systems.
            verbose: Whether to show a progress bar for the report generation.

        Returns:
            A mapping from matched table names to the reports of their comparisons, ordered by the
            sort strategy.
        """
        ignore_table_patterns = [
            re.compile(pattern) for pattern in (ignore_tables or [])
        ]
        ignore_table_columns = ignore_table_columns or {}

        result = {}
        pbar = tqdm(self.table_names.in_common, disable=not verbose)
        for table in pbar:
            if any(pattern.match(table) for pattern in ignore_table_patterns):
                logging.info("Ignoring table %s.", table)
                continue

            pbar.set_description(f"Processing '{table}'")
            comparison = self.compare_matched_table(
                table,
                ignore_columns=(
                    ignore_table_columns[table]
                    if table in ignore_table_columns
                    else None
                ),
                infer_primary_keys=infer_primary_keys,
            )
            if skip_equal and comparison.equal:
                continue
            result[table] = comparison.summary_report()

        match sort_by:
            case "name":
                return result
            case "creation_timestamp":
                timestamps = cast(
                    DialectProtocol, self.engine.dialect
                ).get_table_creation_timestamps(
                    self.engine, [self.left_tables[name] for name in result]
                )
                return {
                    name: result[name]
                    for name, _ in sorted(zip(result, timestamps), key=lambda x: x[1])
                }

    # ---------------------------------------------------------------------------------------------
    # STRING REPRESENTATION
    # ---------------------------------------------------------------------------------------------

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return (
            f"{self.__class__.__name__}"
            f'(left_schema="{self.left_schema}", right_schema="{self.right_schema}")'
        )
