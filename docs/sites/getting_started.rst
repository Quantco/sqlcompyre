Getting Started
===============


Prerequisites
-------------

This documentation assumes some programming experience with Python and a beginner's understanding
of SQLAlchemy Engines and Tables. If you haven't used SQLAlchemy to connect to databases in the
past, try looking at the SQLAlchemy Documentation first:

- `Forming connection strings and connecting to databases <https://docs.sqlalchemy.org/en/14/core/engines.html>`_

- `Using an engine to access pre-existing tables <https://docs.sqlalchemy.org/en/14/core/metadata.html>`_


Creating a :class:`~sqlcompyre.analysis.table_comparison.TableComparison` Object
---------------------------------------------------------------------------------

To compare two tables, you simply need to call the top-level :meth:`~sqlcompyre.compare_tables` function:

.. code-block:: python

    import sqlalchemy as sa
    import sqlcompyre as sc

    engine = sa.create_engine("<your_connection_string>")
    comparison = sc.compare_tables(engine, "<left table name>", "<right table name>")

Importantly, the tables passed to this method may belong to different schemas. In the case of
MSSQL, tables may even belong to different databases. The user simply has to take care to pass the fully-qualified name of the table.

There are a few optional arguments when calling :meth:`~sqlcompyre.compare_tables` that often
need to be set when comparing tables.


Generating a Report
-------------------

Perhaps the first thing you would do with a :class:`~sqlcompyre.analysis.table_comparison.TableComparison` is to print a report summarizing the changes. This is done through the :func:`~sqlcompyre.analysis.table_comparison.TableComparison.summary_report` method:

.. code-block:: python

    report = comparison.summary_report()
    print(report)


Accessing Comparison Metrics
----------------------------

After viewing a report, you may wish to explore some sections in more detail. Most comparison information is contained within the attributes of a :class:`~sqlcompyre.analysis.table_comparison.TableComparison`, split into four categories:

- ``row_counts``: A :class:`~sqlcompyre.results.RowCounts` object
- ``column_names``: A :class:`~sqlcompyre.results.ColumnNames` object
- ``row_matches``: A :class:`~sqlcompyre.results.RowMatches` object
- ``column_matches``: A :class:`~sqlcompyre.results.ColumnMatches` object

You can access attributes using dot notation as in the below:

.. code-block:: python

    # Find number of rows in left table
    num_rows_left = comparison.row_counts.left

    # Find number of rows in the inner join
    num_joined_columns = comparison.row_matches.n_joined_total


Additionally, you can find the top changes in any column using the :func:`~sqlcompyre.analysis.table_comparison.TableComparison.get_top_changes` function.


Using Query Results
-------------------

Some attributes contained within a :class:`~sqlcompyre.analysis.table_comparison.TableComparison` object are `SQLAlchemy Select <https://docs.sqlalchemy.org/en/14/core/selectable.html#sqlalchemy.sql.expression.Select>`_ objects that you can use to further explore your data.

.. code-block:: python

    # Querying for all rows in the right table that could not be joined with rows in the left table
    unjoined_right = comparison.row_matches.unjoined_right

    # editing the query to only give 10 rows
    first_10 = unjoined_right.limit(10)

    # executing the query and printing results
    with left_engine.connect() as conn:
        res = conn.execute(first_10)
    for row in res:
        print(row)

    # Alternatively, storing query results as a dataframe
    df = pandas.read_sql(first_10, left_engine)
