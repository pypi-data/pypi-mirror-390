from typing import Protocol

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
)


class SchemaModule(Protocol):
    """Protocol defining a database schema.

    This protocol is intended to be implemented as a python module and not
    a class, but a class that satisfies the protocol will work as well.
    """

    def get_metadata(self) -> sa.MetaData:
        """The sqlalchemy metadata object that contains the tables in this schema."""

        pass


class DatabaseModule(Protocol):
    """Protocol defining a database wrapper.

    For convenience, a class or module satisfying this protocol is returned
    by the closure created by the `grammdb.db_factory` function, but
    any class or module that correctly implements this protocol can be used.
    """

    def get_schema(self) -> SchemaModule:
        """The schema defining the tables in this database."""

        pass

    def get_engine(self) -> AsyncEngine:
        """The underlying engine that gets set up by the
        `grammdb.init_db` function."""

        pass

    def set_engine(self, engine: AsyncEngine):
        """Assigns the underlying engine that will be returned by `get_engine`.

        This function is used by the `grammdb.init_db` function and generally
        should not be called by client code.
        """

        pass

    def new_connection(self) -> AsyncConnection:
        """Factory for creating new connections in the underlying engine's connection
        pool.

        This function is used by the transaction management helper functions, and
        is not intended to be called directly by client code.
        """

        pass
