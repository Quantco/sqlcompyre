# Copyright (c) QuantCo 2024-2025
# SPDX-License-Identifier: BSD-3-Clause

import functools
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import click
import sqlalchemy as sa

import sqlcompyre as sc
from sqlcompyre import Config
from sqlcompyre.config.validation import read_config
from sqlcompyre.report.formatters import get_formatter
from sqlcompyre.report.writers import Writer, get_writer


@dataclass
class CliConfig:
    writer: Writer


def table_comparison_options(cli):
    @click.option(
        "-j",
        "--join-columns",
        type=str,
        default=None,
        help="The join column(s) to be used for matching rows, separated by comma.",
    )
    @click.option(
        "--hide-matching-columns/--no-hide-matching-columns",
        default=False,
        show_default=True,
        help="Whether to hide columns that show a 100% (i.e. perfect) match rate.",
    )
    @click.option(
        "--float-precision",
        default=sys.float_info.epsilon,
        show_default=f"{sys.float_info.epsilon=:.2e}",
        help="The precision to use for floating point comparisons.",
    )
    @click.option(
        "--collation",
        type=str,
        default=None,
        help="Optional collation to use for comparing strings.",
    )
    @click.option(
        "--ignore-casing/--no-ignore-casing",
        default=False,
        show_default=True,
        help="Whether column name casing should be ignored.",
    )
    @click.option(
        "--infer-primary-keys/--no-infer-primary-keys",
        default=False,
        show_default=True,
        help="Whether to infer primary keys for the table comparison.",
    )
    @functools.wraps(cli)
    def cli_wrapped(*args, **kwargs):
        return cli(*args, **kwargs)

    return cli_wrapped


@click.group()
@click.option(
    "-f",
    "--format",
    type=click.Choice(["terminal", "text"]),
    default=None,
    show_default="'terminal' if writer == 'stdout' else 'text'",
    help="The output format for reports.",
)
@click.option(
    "-w",
    "--writer",
    type=click.Choice(["stdout", "file", "markdown"]),
    default="stdout",
    show_default=True,
    help="A writer to output reports.",
)
@click.pass_context
def main(ctx: click.Context, format: str | None, writer: str):
    """Compare objects from a SQL database server."""
    # Set up logging
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(stream=sys.stderr)
    logfmt = "%(asctime)s - %(levelname)-8s - %(message)s"
    handler.setFormatter(logging.Formatter(logfmt, datefmt="%Y-%m-%d %H:%M:%S"))
    logger.addHandler(handler)

    # Get writer and formatter
    formatter = get_formatter(format or ("terminal" if writer == "stdout" else "text"))
    writer_cls = get_writer(writer, formatter)

    ctx.obj = CliConfig(writer_cls)


@main.command()
@click.argument("left_table")
@click.argument("right_table")
@click.option(
    "-s",
    "--database-connection-string",
    required=True,
    envvar="COMPYRE_DB_CONNECTION_STRING",
    show_default="$COMPYRE_DB_CONNECTION_STRING",
    help="The connection string to connect to a database.",
)
@table_comparison_options
@click.pass_obj
def tables(
    obj: CliConfig,
    left_table: str,
    right_table: str,
    database_connection_string: str,
    join_columns: str | None,
    hide_matching_columns: bool,
    float_precision: float,
    collation: str | None,
    ignore_casing: bool,
    infer_primary_keys: bool,
):
    """Compare two tables in a SQL database."""
    # Run the comparison and get the report
    engine = sa.create_engine(database_connection_string)
    comparison = sc.compare_tables(
        engine,
        left_table,
        right_table,
        join_columns=join_columns.split(",") if join_columns is not None else None,
        float_precision=float_precision,
        collation=collation,
        ignore_casing=ignore_casing,
        infer_primary_keys=infer_primary_keys,
    )
    report = comparison.summary_report()

    # Write the report
    obj.writer.write(
        {"comparison": report}, hide_matching_columns=hide_matching_columns
    )


@main.command()
@click.argument("left_schema")
@click.argument("right_schema")
@click.option(
    "-s",
    "--database-connection-string",
    required=True,
    envvar="COMPYRE_DB_CONNECTION_STRING",
    show_default="$COMPYRE_DB_CONNECTION_STRING",
    help="The connection string to connect to a database.",
)
@click.option(
    "--include-views/--no-include-views",
    default=False,
    show_default=True,
    help="Whether to include views into the comparison.",
)
@click.option(
    "--compare-tables/--no-compare-tables",
    default=False,
    show_default=True,
    help="Whether to also compare all tables matched between the schemas.",
)
@click.option(
    "--skip-equal/--no-skip-equal",
    default=False,
    show_default=True,
    help="Whether to skip outputting comparisons if tables are equal. "
    "Only applicable when --compare-tables is set.",
)
@click.option(
    "--hide-matching-columns/--no-hide-matching-columns",
    default=False,
    show_default=True,
    help="Whether to hide columns that show a 100% (i.e. perfect) match rate.",
)
@click.option(
    "--float-precision",
    default=sys.float_info.epsilon,
    show_default=f"{sys.float_info.epsilon=:.2e}",
    help="The precision to use for floating point comparisons in table comparison.",
)
@click.option(
    "--collation",
    type=str,
    default=None,
    help="Optional collation to use for comparing strings in table comparisons.",
)
@click.option(
    "--ignore-casing/--no-ignore-casing",
    default=False,
    show_default=True,
    help="Whether column name casing should be ignored in table comparisons.",
)
@click.option(
    "--infer-primary-keys/--no-infer-primary-keys",
    default=False,
    show_default=True,
    help="Whether to infer primary keys for table comparisons. "
    "Only applicable when --compare-tables is set.",
)
@click.option(
    "--sort-output-by",
    type=click.Choice(["name", "creation_timestamp"]),
    default="name",
    show_default=True,
    help="The order of the tables in the output.",
)
@click.option(
    "--config",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=None,
    help="A configuration file to read additional options for comparison.",
)
@click.pass_obj
def schemas(
    obj: CliConfig,
    left_schema: str,
    right_schema: str,
    database_connection_string: str,
    include_views: bool,
    compare_tables: bool,
    skip_equal: bool,
    hide_matching_columns: bool,
    float_precision: float,
    collation: str | None,
    ignore_casing: bool,
    infer_primary_keys: bool,
    sort_output_by: Literal["name", "creation_timestamp"],
    config: Path | None,
):
    """Compare two schemas/databases in a SQL database."""
    # Find tables/column that are ignored
    cfg: Config | None = None
    if config is not None:
        cfg = read_config(config)

    # Generate comparison and report for the schema
    engine = sa.create_engine(database_connection_string)
    comparison = sc.compare_schemas(
        engine,
        left_schema,
        right_schema,
        include_views=include_views,
        float_precision=float_precision,
        collation=collation,
        ignore_casing=ignore_casing,
    )
    report = comparison.summary_report()

    # Write the results
    if compare_tables:
        reports = comparison.table_reports(
            ignore_tables=cfg.ignore_tables if cfg else [],
            ignore_table_columns=cfg.ignore_table_columns if cfg else {},
            skip_equal=skip_equal,
            infer_primary_keys=infer_primary_keys,
            sort_by=sort_output_by,
            verbose=True,
        )
        obj.writer.write(
            {
                "__schema__": report,
                **reports,
            },
            hide_matching_columns=hide_matching_columns,
        )
    else:
        obj.writer.write(
            {"comparison": report}, hide_matching_columns=hide_matching_columns
        )
