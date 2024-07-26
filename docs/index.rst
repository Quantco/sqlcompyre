SQLCompyre
==========

SQLCompyre is a simple Python package that allows you to find and explore the differences between
SQL tables, schemas, and entire databases. It provides both a Python interface and a CLI, allowing
it to be used for both ad-hoc comparisons as well as in-depth analyses.

SQLCompyre is designed to be dialect-agnostic and should, thus, work with most
database systems out-of-the-box. At the moment, is has been explicitly tested on the following
systems:

- `SQLite <https://en.wikipedia.org/wiki/SQLite>`_
- `Microsoft SQL Server <https://en.wikipedia.org/wiki/Microsoft_SQL_Server>`_


Contents
--------

.. toctree::
   :maxdepth: 2

   Installation <sites/installation.rst>
   Getting Started <sites/getting_started.rst>
   Example <sites/example/example.ipynb>
   Development <sites/development.rst>

API Reference
-------------

.. currentmodule:: sqlcompyre

.. autosummary::
    :toctree: _gen/public
    :nosignatures:
    :caption: Core API

    compare_tables
    compare_schemas
    inspect_query
    inspect_table

Analyses
^^^^^^^^

.. currentmodule:: sqlcompyre.analysis

.. autosummary::
    :caption: Analyses
    :toctree: _gen/comparisons
    :nosignatures:

    ~query_inspection.QueryInspection
    ~table_comparison.TableComparison
    ~schema_comparison.SchemaComparison

Results
^^^^^^^

.. currentmodule:: sqlcompyre.results

.. autosummary::
    :caption: Results
    :toctree: _gen/results
    :nosignatures:

    Counts
    Names
    RowMatches
    ColumnMatches


Report
^^^^^^

.. currentmodule:: sqlcompyre.report

.. autosummary::
    :caption: Report
    :toctree: _gen/report
    :nosignatures:

    ~report.Report

    :template: sites/formatters.rst
    formatters

    :template: sites/writers.rst
    writers
