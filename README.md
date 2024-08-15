# SQLCompyre

[![CI](https://img.shields.io/github/actions/workflow/status/quantco/sqlcompyre/ci.yml?style=flat-square&branch=main)](https://github.com/quantco/sqlcompyre/actions/workflows/ci.yml)
[![conda-forge](https://img.shields.io/conda/vn/conda-forge/sqlcompyre?logoColor=white&logo=conda-forge&style=flat-square)](https://prefix.dev/channels/conda-forge/packages/sqlcompyre)
[![Documentation](https://img.shields.io/badge/docs-latest-success?branch=main&style=flat-square)](https://sqlcompyre.readthedocs.io/en/latest/)
[![pypi-version](https://img.shields.io/pypi/v/sqlcompyre.svg?logo=pypi&logoColor=white&style=flat-square)](https://pypi.org/project/sqlcompyre)
[![python-version](https://img.shields.io/pypi/pyversions/sqlcompyre?logoColor=white&logo=python&style=flat-square)](https://pypi.org/project/sqlcompyre)

SQLCompyre is a simple Python package that allows you to find and explore the differences between SQL tables, schemas, and entire databases. It provides both a Python interface and a CLI, allowing it to be used for both ad-hoc comparisons as well as in-depth analyses.

SQLCompyre is designed to be dialect-agnostic and should, thus, work with most database systems out-of-the-box.

## Usage example

Given a connection to a database, this snippet will print a report of the differences between two tables:

```python
import sqlalchemy as sa
import sqlcompyre as sc

engine = sa.create_engine("<your_connection_string>")
comparison = sc.compare_tables(engine, "<left table name>", "<right table name>")

report = comparison.summary_report()
print(report)
```

To find more examples and get started, please visit the [documentation](https://sqlcompyre.readthedocs.io/en/latest/).

## Installation

SQLCompyre can be installed via `pip` or `conda`:

```bash
pip install sqlcompyre
# or
micromamba install sqlcompyre
# or
conda install sqlcompyre
```

Details on its usage can be found in the [documentation](https://sqlcompyre.readthedocs.io/en/latest/).

## Development

This project is managed by [pixi](https://pixi.sh).
You can install the package in development mode using:

```bash
git clone https://github.com/quantco/sqlcompyre
cd sqlcompyre

pixi run pre-commit-install
pixi run postinstall
```

### Running Tests Locally

1. Make sure you have `msodbcsql18` installed, or install it [here](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

2. Make sure you have `Docker` installed, or install it [here](https://docs.docker.com/get-docker/)

3. Create a local test database with the following command:

```bash
docker compose up
```

4. Set environment variable

```bash
export DB_CONNECTION_STRING="mssql+pyodbc://sa:Passw0rd@localhost:1435/master?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=no"
```

5. Navigate to the main directory of this repository and run pytest.

```bash
pixi run test
```
