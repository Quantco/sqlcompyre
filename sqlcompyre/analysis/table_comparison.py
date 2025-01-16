# Copyright (c) QuantCo 2024-2025
# SPDX-License-Identifier: BSD-3-Clause

import functools
import logging
from functools import cached_property

import sqlalchemy as sa

from sqlcompyre.report import Report
from sqlcompyre.results import ColumnMatches, Counts, Names, RowMatches


class TableComparison:
    """Compare the content of two SQL database tables.

    Note:
        This class should never be initialized directly. Use the
        :meth:`~sqlcompyre.api.compare_tables` function instead.
    """

    def __init__(
        self,
        engine: sa.Engine,
        left_table: sa.FromClause,
        right_table: sa.FromClause,
        join_columns: list[str] | None,
        column_name_mapping: dict[str, str] | None,
        ignore_columns: list[str] | None,
        float_precision: float,
        collation: str | None,
        ignore_casing: bool,
        infer_primary_keys: bool,
    ):
        """
        Args:
            engine: The engine to use for connecting to the database.
            left_table: The "left" table of the comparison.
            right_table: The "right" table of the comparison to compare to ``left_table``.
            join_columns: The columns to join the tables on in order to compare column values. If
                not provided, defaults to the union of primary keys. The corresponding
                primary key(s) of the right table are determined via ``column_name_mapping``.
            column_name_mapping: A mapping from column names in the left table to column names in
                the right table. If not provided, defaults to mapping columns with the same names.
            ignore_columns: Columns to ignore to evaluate equality.
            float_precision: The precision of floating point comparisons.
            collation: An optional collation to use for comparing string columns.
            ignore_casing: Whether casing (e.g. capitalization) should be ignored when matching
                column names.
            infer_primary_keys: Whether to infer primary keys if none are available.
        """
        self.engine = engine
        self.left_table = left_table.alias("left")
        self.right_table = right_table.alias("right")
        self.column_name_mapping = _identity_column_mapping_if_needed(
            left_table,
            right_table,
            column_name_mapping or {},
            ignore_columns or [],
            ignore_casing=ignore_casing,
        )
        self.float_precision = float_precision
        self.collation = collation
        self.ignore_casing = ignore_casing

        self._user_join_columns = join_columns or []
        self._infer_primary_keys = infer_primary_keys

    # ---------------------------------------------------------------------------------------------
    # COMPUTED PROPERTIES
    # ---------------------------------------------------------------------------------------------

    @cached_property
    def join_columns(self) -> list[str]:
        """The columns used for joining the two tables."""
        pks = _join_columns_from_pk_if_needed(
            self.engine,
            self.left_table,
            self.right_table,
            self._user_join_columns,
            ignore_casing=self.ignore_casing,
            column_name_mapping=self.column_name_mapping,
            infer_primary_keys=self._infer_primary_keys,
        )
        return sorted(pks)

    # ---------------------------------------------------------------------------------------------
    # COMPARISON
    # ---------------------------------------------------------------------------------------------

    @cached_property
    def equal(self) -> bool:
        """Whether the compared tables are equal."""
        try:
            return (
                len(self.column_names.missing_left) == 0
                and len(self.column_names.missing_right) == 0
                and self.row_matches.n_joined_equal == self.row_matches.n_joined_total
                and self.row_matches.n_unjoined_left == 0
                and self.row_matches.n_unjoined_right == 0
            )
        except ValueError:
            # There are no join columns (or they can't be inferred). We can still compare for
            # equality via "EXCEPT ALL" statements. Since they are not supported by most database
            # systems, we resort to EXCEPT + GROUP BY though...
            left_columns = [
                self.left_table.c[c] for c in self.column_name_mapping.keys()
            ]
            left_with_counts = (
                sa.select(*left_columns, sa.func.count().label("num"))
                .select_from(self.left_table)
                .group_by(*left_columns)
                .cte("left_with_counts")
            )

            right_columns = [
                self.right_table.c[c] for c in self.column_name_mapping.values()
            ]
            right_with_counts = (
                sa.select(*right_columns, sa.func.count().label("num"))
                .select_from(self.right_table)
                .group_by(*right_columns)
                .cte("right_with_counts")
            )

            only_left = (
                sa.select(left_with_counts)
                .except_(sa.select(right_with_counts))
                .cte("only_left")
            )
            only_right = (
                sa.select(right_with_counts)
                .except_(sa.select(left_with_counts))
                .cte("only_right")
            )
            union = sa.union(sa.select(only_left), sa.select(only_right))
            count = sa.select(sa.func.count()).select_from(union.subquery())
            with self.engine.connect() as conn:
                return conn.execute(count).scalar_one() == 0

    @cached_property
    def row_counts(self) -> Counts:
        """A comparison between the number of rows in each table."""
        return Counts(
            left=self._count_rows(self.left_table),
            right=self._count_rows(self.right_table),
        )

    @cached_property
    def column_names(self) -> Names:
        """A comparison between the column names of the two tables."""
        return Names(
            left={col.name for col in self.left_table.columns},
            right={col.name for col in self.right_table.columns},
            name_mapping=self.column_name_mapping,
            ignore_casing=self.ignore_casing,
        )

    @cached_property
    def row_matches(self) -> RowMatches:
        """A comparison between the contents of the individual rows in the two
        tables."""
        # Get conditions for (non-)equal columns
        equality_conditions = [
            self._is_equal(colname_1, colname_2)
            for colname_1, colname_2 in self.column_name_mapping.items()
            if colname_1 not in self.join_columns
        ]
        inequality_conditions: list[sa.ColumnElement[bool]] = [
            sa.not_(c) for c in equality_conditions
        ]

        # If there are no conditions, equality is always true, inequality is always false
        if not equality_conditions:
            equality_conditions = [sa.true()]
            inequality_conditions = [sa.false()]

        # -- Create queries
        # Query for rows ONLY in left table
        left_columns = [self.left_table.c[c] for c in self.join_columns] + [
            self.left_table.c[c]
            for c in self.column_name_mapping
            if c not in self.join_columns
        ]
        unjoined_left = (
            sa.select(*left_columns)
            .select_from(self._outer_join(left=True))
            .where(
                self.right_table.c[self.column_name_mapping[self.join_columns[0]]].is_(
                    None
                )
            )
        )

        # Query for rows ONLY in right table
        right_columns = [
            self.right_table.c[self.column_name_mapping[c]] for c in self.join_columns
        ] + [
            self.right_table.c[v]
            for k, v in self.column_name_mapping.items()
            if k not in self.join_columns
        ]
        unjoined_right = (
            sa.select(*right_columns)
            .select_from(self._outer_join(left=False))
            .where(self.left_table.c[self.join_columns[0]].is_(None))
        )

        # For the remaining queries, we need to build a set of column names
        join_columns = [
            self.left_table.c[c].label(f"joined_{c}") for c in self.join_columns
        ]
        left_columns = [
            self.left_table.c[c].label(f"left_{c}")
            for c in self.column_name_mapping.keys()
            if c not in self.join_columns
        ]
        right_columns = [
            self.right_table.c[c].label(f"right_{c}")
            for k, c in self.column_name_mapping.items()
            if k not in self.join_columns
        ]
        # Interleave left and right columns here
        columns = join_columns + [
            c for cols in zip(left_columns, right_columns) for c in cols
        ]

        # The remaining queries
        joined_total = sa.select(*columns).select_from(self._inner_join())
        joined_unequal = joined_total.where(sa.or_(*inequality_conditions))
        joined_equal = joined_total.where(sa.and_(*equality_conditions))
        joined_row_count = self._count_rows(self._inner_join())
        different_row_count = self._count_rows(joined_unequal.subquery())

        # Return row machts
        return RowMatches(
            n_unjoined_left=self.row_counts.left - joined_row_count,
            n_unjoined_right=self.row_counts.right - joined_row_count,
            n_joined_equal=joined_row_count - different_row_count,
            n_joined_unequal=different_row_count,
            n_joined_total=joined_row_count,
            unjoined_left=unjoined_left,
            unjoined_right=unjoined_right,
            joined_equal=joined_equal,
            joined_unequal=joined_unequal,
            joined_total=joined_total,
        )

    @cached_property
    def column_matches(self) -> ColumnMatches:
        """A comparison between the column values of the two tables."""
        MATCH_SUFFIX = "_zzz_match"
        inner_join = self._inner_join()

        # Query for testing equality of column values in matching rows
        cases = [
            sa.case((self._is_equal(left_column, right_column), 1.0), else_=0.0).label(
                f"{left_column}_{MATCH_SUFFIX}"
            )
            for left_column, right_column in self.column_name_mapping.items()
            if left_column not in self.join_columns
        ]
        if len(cases) == 0:
            return ColumnMatches(fraction_same={}, mismatch_selects={})

        case_stmt = sa.select(*cases).select_from(inner_join).subquery()

        # Compute fraction of matching values
        cols_to_avg = [col for col in case_stmt.c if f"_{MATCH_SUFFIX}" in col.name]
        avgs = sa.select(
            *[
                sa.func.avg(col).label(f"{col.name.replace(f'_{MATCH_SUFFIX}', '')}")
                for col in cols_to_avg
            ]
        )
        with self.engine.connect() as conn:
            avgs_results = {
                column: (match if match is not None else float("nan"))
                for column, match in conn.execute(avgs).all()[0]._asdict().items()
            }

        # Find column mismatches
        mismatch_selects = {
            left_column: sa.select(inner_join).where(
                sa.not_(self._is_equal(left_column, right_column))
            )
            for left_column, right_column in self.column_name_mapping.items()
            if left_column not in self.join_columns
        }
        return ColumnMatches(
            fraction_same=avgs_results,
            mismatch_selects=mismatch_selects,
        )

    @functools.lru_cache
    def get_top_changes(self, column_name: str, n: int = 5) -> dict[str, int]:
        """Gets the most common changes in a single column.

        Args:
            column_name: The name of the column in the "left" table.
            n: The number of changes to get.

        Returns:
            A dictionary where the key is a change in string form (maybe "true -> false") and the
            value is the number of times the change occurs.
        """
        aggregate_query = self._get_aggregate_changes(column_name)
        with self.engine.connect() as conn:
            res = conn.execute(aggregate_query.limit(n))
            return {change: count for change, count in res}

    # ---------------------------------------------------------------------------------------------
    # SUMMARY REPORT
    # ---------------------------------------------------------------------------------------------

    def summary_report(self) -> Report:
        """Generate a report that summarizes the table comparison.

        Returns:
            A report summarizing the comparison of the two tables.
        """
        description = None
        sections = {
            "Column Names": self.column_names,
            "Row Counts": self.row_counts,
        }

        # Optionally add additional information if `join_columns` can be constructed
        try:
            description = "Joining on columns:"
            for column in self.join_columns:
                description += (
                    f"\n  - '{column}' = '{self.column_name_mapping[column]}'"
                )
            sections.update(
                {
                    "Row Matches": self.row_matches,
                    "Column Matches": self.column_matches,
                }
            )
        except ValueError as exc:
            logging.warning(
                "'%s' and '%s' cannot be matched (%s): dropping row and column matches "
                "from the report",
                self._left_table_name,
                self._right_table_name,
                exc,
            )

        return Report(
            "tables",
            self._left_table_name,
            self._right_table_name,
            description,
            sections,
        )

    # ---------------------------------------------------------------------------------------------
    # UTILITY METHODS
    # ---------------------------------------------------------------------------------------------

    @property
    def _left_table_name(self) -> str:
        if isinstance(self.left_table, sa.Alias):
            return str(self.left_table.element)
        return "<left query>"

    @property
    def _right_table_name(self) -> str:
        if isinstance(self.right_table, sa.Alias):
            return str(self.right_table.element)
        return "<right query>"

    def _is_equal(self, left_column: str, right_column: str) -> sa.ColumnElement[bool]:
        """Forms a condition for comparing two columns.

        Args:
            left_column: Column in "left" table being compared.
            right_column: Column in "right" table being compared.

        Returns:
            A condition for comparing two columns of the "left" and "right" table.
        """
        lhs = self.left_table.c[left_column]
        rhs = self.right_table.c[right_column]

        # Create the condition that is used
        if not isinstance(lhs.type, sa.Float):
            if isinstance(lhs.type, sa.String) and self.collation is not None:
                condition = lhs.collate(self.collation) == rhs.collate(self.collation)
            else:
                condition = lhs == rhs
        else:
            condition = sa.func.abs(lhs - rhs) < self.float_precision

        # Ensure that NULLs are considered equal...
        # We have to take care that the equality is invertible (e.g. NULL = NULL is `unknown`
        # and inverting this is still `unknown`). For more discussion, see
        # https://stackoverflow.com/questions/1075142/how-to-compare-values-which-may-both-be-null-in-t-sql
        # The following is a more robust formulation of `A = B OR (A IS NULL AND B IS NULL)`.
        return sa.func.coalesce(
            sa.case((condition, None), else_=lhs),
            sa.case((condition, None), else_=rhs),
        ).is_(None)

    @cached_property
    def _join_conditions(self) -> list[sa.ColumnElement[bool]]:
        """Forms a list of join conditions."""
        return [
            (
                self.left_table.c[join_col]
                == self.right_table.c[self.column_name_mapping[join_col]]
            )
            for join_col in self.join_columns
        ]

    def _inner_join(self) -> sa.Join:
        """Specifies an inner join on the left and right tables."""
        return self.left_table.join(self.right_table, sa.and_(*self._join_conditions))

    def _outer_join(self, left: bool) -> sa.Join:
        """Specifies an outer join between the two tables.

        Args:
            left: ``True`` for a left outer join and ``False`` for a right outer join

        Returns:
            A left or right outer join
        """
        left_table = self.left_table
        right_table = self.right_table
        if left:
            return left_table.outerjoin(right_table, sa.and_(*self._join_conditions))
        return right_table.outerjoin(left_table, sa.and_(*self._join_conditions))

    def _get_aggregate_changes(self, left_col_name: str) -> sa.Select:
        """Counts the number of different ways each column changes from one table to
        another.

        Args:
            left_col_name: The column name in the left table.

        Returns:
            A select statement counting the number of each unique change, ordering by most common
            to least common.
        """
        right_col_name = self.column_name_mapping[left_col_name]
        left_col = self.left_table.c[left_col_name]
        right_col = self.right_table.c[right_col_name]

        change = (
            sa.case((left_col.is_(None), "NULL"), else_=sa.cast(left_col, sa.String))
            + " -> "
            + sa.case(
                (right_col.is_(None), "NULL"), else_=sa.cast(right_col, sa.String)
            )
        )

        return (
            sa.select(change, sa.func.count())
            .select_from(self._inner_join())
            .where(sa.not_(self._is_equal(left_col_name, right_col_name)))
            .group_by(left_col, right_col)
            .order_by(sa.func.count().desc())
        )

    def _count_rows(self, table: sa.FromClause) -> int:
        """Counts the number of rows in a table-like object.

        Args:
            table: A table-like object.

        Returns:
            The number of rows.
        """
        with self.engine.connect() as conn:
            return conn.execute(
                sa.select(sa.func.count()).select_from(table)
            ).scalar_one()

    # ---------------------------------------------------------------------------------------------
    # STRING REPRESENTATION
    # ---------------------------------------------------------------------------------------------

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return (
            f"{self.__class__.__name__}("
            f'left_table="{self._left_table_name}", '
            f'right_table="{self._right_table_name}")'
        )


# -------------------------------------------------------------------------------------------------
# UTILITIES
# -------------------------------------------------------------------------------------------------


def _join_columns_from_pk_if_needed(
    engine: sa.Engine,
    left: sa.FromClause,
    right: sa.FromClause,
    join_columns: list[str],
    ignore_casing: bool,
    column_name_mapping: dict[str, str],
    infer_primary_keys: bool,
) -> list[str]:
    if join_columns and ignore_casing:
        # If we already have join columns and do not case about casing being passed, we need to
        # fix the casing for Python to work correctly
        lowercase_map = {c.name.lower(): c.name for c in left.columns}
        join_columns = [lowercase_map[c.lower()] for c in join_columns]

    if not join_columns:
        left_pks = {col.name for col in left.columns if col.primary_key}
        right_pks = {col.name for col in right.columns if col.primary_key}
        reverse_mapping = {v: k for k, v in column_name_mapping.items()}
        if not (left_pks - set(column_name_mapping) | right_pks - set(reverse_mapping)):
            # All primary keys can be matched
            join_columns = list(left_pks | {reverse_mapping[pk] for pk in right_pks})

    if not join_columns:
        if not infer_primary_keys:
            raise ValueError(
                "No matching primary keys found and no join columns specified. Consider "
                "specifying `ignore_casing` if your column names are case-sensitive or "
                "`infer_primary_keys` if your table does not have a primary key."
            )

        # Here we want to infer the primary key. For this, we need to check whether all columns
        # that are being matched provide a useful primary key. We do not make any effort to
        # calculate a small primary key to reduce computational complexity. However, we need to
        # get rid of all columns that can be NULL.
        non_null_column_mapping = {
            k: v
            for k, v in column_name_mapping.items()
            if _is_valid_primary_key_column(engine, left, right, k, v)
        }
        if len(non_null_column_mapping) == 0:
            raise ValueError(
                "Automatically inferring primary keys failed as there are no non-null columns "
                "that can be matched."
            )

        left_keys = list(non_null_column_mapping.keys())
        right_keys = list(non_null_column_mapping.values())
        if (not _is_valid_primary_key(engine, left, left_keys)) or (
            not _is_valid_primary_key(engine, right, right_keys)
        ):
            raise ValueError(
                "Automatically inferring primary keys failed as the mapped column names "
                "would cause duplicates."
            )

        # When we reach this point, we are okay to use all columns
        join_columns = left_keys

    return join_columns


def _is_valid_primary_key_column(
    engine: sa.Engine,
    left_table: sa.FromClause,
    right_table: sa.FromClause,
    left_column: str,
    right_column: str,
) -> bool:
    # If both columns are non-nullable, it is a valid column.
    if (
        not left_table.c[left_column].nullable
        and not right_table.c[right_column].nullable
    ):
        return True

    # If not, let's check if there are actually any nulls in the column.
    with engine.connect() as conn:
        left_nulls = conn.execute(
            sa.select(sa.func.count())
            .select_from(left_table)
            .where(left_table.c[left_column].is_(None))
        ).scalar_one()
        right_nulls = conn.execute(
            sa.select(sa.func.count())
            .select_from(right_table)
            .where(right_table.c[right_column].is_(None))
        ).scalar_one()
    return left_nulls == 0 and right_nulls == 0


def _is_valid_primary_key(
    engine: sa.Engine, table: sa.FromClause, columns: list[str]
) -> bool:
    with engine.connect() as conn:
        result = conn.execute(
            sa.select(*[table.c[c] for c in columns])
            .select_from(table)
            .group_by(*columns)
            .having(sa.func.count() > 1)
        )
        return result.fetchone() is None


def _identity_column_mapping_if_needed(
    left: sa.FromClause,
    right: sa.FromClause,
    mapping: dict[str, str],
    ignore_columns: list[str],
    ignore_casing: bool,
) -> dict[str, str]:
    left_columns = {col.name for col in left.columns}
    right_columns = {col.name for col in right.columns}

    # In the following we proceed as follows: if `ignore_casing` is set, we want to _match_ on the
    # lowercased column names but eventually _output_ the cased column names. This is required for
    # SQLAlchemy to work correctly.
    lowercase_left_columns = {c.lower(): c for c in left_columns}
    lowercase_right_columns = {c.lower(): c for c in right_columns}

    # Ensure that mapped columns have the correct casing
    if mapping and ignore_casing:
        try:
            mapping = {
                lowercase_left_columns[lhs.lower()]: (
                    lowercase_right_columns[rhs.lower()]
                )
                for lhs, rhs in mapping.items()
            }
        except KeyError:
            # An error occurred! Check which column mappings are invalid and return them
            left_not_available = {k.lower() for k in mapping.keys()}.difference(
                lowercase_left_columns.keys()
            )
            if len(left_not_available) > 0:
                raise ValueError(
                    f"{len(left_not_available)} column(s) could not be found in the left table: "
                    f"{sorted(left_not_available)}."
                )

            right_not_available = {v.lower() for v in mapping.values()}.difference(
                lowercase_right_columns.keys()
            )
            if len(right_not_available) > 0:
                raise ValueError(
                    f"{len(right_not_available)} column(s) could not be found in the right table: "
                    f"{sorted(right_not_available)}."
                )
    elif mapping:
        # If we don't ignore casing, we still want to check whether the mapping is valid
        left_not_available = set(mapping.keys()).difference(left_columns)
        if len(left_not_available) > 0:
            raise ValueError(
                f"{len(left_not_available)} column(s) could not be found in the left table: "
                f"{sorted(left_not_available)}."
            )

        right_not_available = set(mapping.values()).difference(right_columns)
        if len(right_not_available) > 0:
            raise ValueError(
                f"{len(right_not_available)} column(s) could not be found in the right table: "
                f"{sorted(right_not_available)}."
            )

    # Add additional "identity" mappings... possibly while ignoring the casing
    if ignore_casing:
        overlapping_columns = set(lowercase_left_columns).intersection(
            lowercase_right_columns
        )
        missing_mapped_columns = {
            lowercase_left_columns[col] for col in overlapping_columns
        }.difference(mapping.keys())
        mapping.update(
            {
                lowercase_left_columns[col.lower()]: lowercase_right_columns[
                    col.lower()
                ]
                for col in missing_mapped_columns
            }
        )
    else:
        missing_mapped_columns = left_columns.intersection(right_columns).difference(
            mapping.keys()
        )
        mapping.update({col: col for col in missing_mapped_columns})

    # Eventually, ignore columns
    if ignore_casing:
        lowered_ignore = {c.lower() for c in ignore_columns}
        mapping = {k: v for k, v in mapping.items() if k.lower() not in lowered_ignore}
    else:
        mapping = {k: v for k, v in mapping.items() if k not in ignore_columns}

    # Sanity checks
    if len(mapping) == 0:
        raise ValueError(
            "No columns could be matched between tables. Consider setting "
            "`column_name_mapping` or `ignore_casing` if your column names are "
            "case-sensitive."
        )
    return mapping
