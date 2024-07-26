Development
===========

Thanks for deciding to work on ``sqlcompyre``! You clone the repository with the following steps:

.. code-block:: bash

    git clone https://github.com/quantco/sqlcompyre
    cd sqlcompyre

Next make sure to install the package locally and set up pre-commit hooks:

.. code-block:: bash

    pixi run pre-commit-install
    pixi run postinstall

All tests for this project currently require running an MSSQL server via Docker. You need to have `Docker <https://docs.docker.com/get-docker/>`_ installed to do this.

.. code-block:: bash

    docker compose up

Make sure you also have `msodbcsql18` installed, or install it `here <https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server>`_,
you might also need to set the environment variable `ODBCSYSINI` to the directory where `msodbcsql18` is installed.

Then, run the tests as below:

.. code-block:: bash

    pixi run test

When updating the documentation, you can compile a localized build of the documentation and then open it in your web browser using the commands below:

.. code-block:: bash

    pixi run docs

    # Open documentation
    open docs/_build/html/index.html
