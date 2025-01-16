# Copyright (c) QuantCo 2024-2025
# SPDX-License-Identifier: BSD-3-Clause

import sqlalchemy as sa
from sqlalchemy.schema import CreateSchema, DropSchema
from sqlalchemy_utils import create_database, database_exists, drop_database

from .dialects import dialect_from_connection_url


class SchemaFactory:
    """Simple utility class to create schemas for testing."""

    def __init__(self, connection_url: sa.URL):
        """
        Args:
            connection_url: The connection string to connect to the database.
        """
        self.connection_url = connection_url
        self.dialect = dialect_from_connection_url(connection_url)

    def create(self, name: str) -> str:
        """Create a new schema with the given name and drop a potentially existing
        one."""
        if not self.dialect.supports_schemas:
            raise ValueError(f"dialect '{self.dialect.name}' has no concept of schemas")

        if self.dialect.supports_multi_part_schemas:
            # For multi-part schemas, we create a new database
            target = self.connection_url.set(database=name)
            if database_exists(target):
                for attempt in range(3):
                    try:
                        drop_database(target)
                        break
                    except sa.exc.ProgrammingError as e:
                        print(f"Attempt {attempt}. Couldn't drop database:\n{e}")
                        pass
            create_database(target)
            return f"{name}.dbo"

        # For all other databases, we simply create a schema
        engine = sa.create_engine(self.connection_url)
        inspector = sa.inspect(engine)
        with engine.connect() as conn:
            if name in inspector.get_schema_names():
                conn.execute(DropSchema(name, cascade=True))
            conn.execute(CreateSchema(name))
        return name
