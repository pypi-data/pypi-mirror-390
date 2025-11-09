import math
import time
from collections.abc import Callable

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    create_async_engine,
)

from grammdb.contracts import (
    DatabaseModule,
    SchemaModule,
)

_timestamp = lambda: math.floor(time.time())


async def init_db(
    db_mod: DatabaseModule,
    db_uri: str,
    *,
    drop_tables: bool = False,
    hook: Callable[[AsyncEngine], None] = lambda x: None,
    **engine_options,
) -> None:
    """Setup the sqlalchemy AsyncEngine for the provided database module to connect to the server at
    `db_uri`.


    Args:
        db_mod: The database module to setup.
            This stateful module will hold the newly configured engine.
        db_uri: The connection string for the target backend.
        drop_tables: Keyword-only argument.
            If True, drop and recreate all tables in the `db_mod.schema`.
            If False, only create tables that don't already exist.
            Default: False
        hook: Keyword-only argument.
            Callback function to invoke after creating the engine, but before creating tables
            and assigning it to the database module. Default is a no-op.
            Accepts a single argument, which is the newly created engine.
            This can be used to apply custom setup code on the engine. For example, to enable
            sqlite foreign key support:
            ```pycon
            >>> import sqlalchemy as sa
            >>> def setup_hook(engine: sa.ext.asyncio.AsyncEngine) -> None:
            ...     def _(async_conn, dbapi_conn, conn = None):
            ...         async_conn.cursor().execute("PRAGMA foreign_keys = ON;")
            ...     sa.event.listen(engine.sync_engine, "connect", _)
            >>> async def ex():
            ...     await init_db(database(), "sqlite+aiosqlite://", hook=setup_hook)
            >>> asyncio.run(ex())

            ```
        **engine_options:
            Any additional keyword arguments are passed to `create_async_engine` as-is.
            Default:

                echo: False
                poolclass: `sqlalchemy.pool.AsyncAdaptedQueuePool`
                pool_size: 10

            Example:
                ```pycon
                >>> async def ex():
                ...     await init_db(database(), "sqlite+aiosqlite://", pool_size=1)
                ...     return database().get_engine().pool.size()
                >>> asyncio.run(ex())
                1

                ```

    """

    default_options = {"echo": False, "poolclass": sa.pool.AsyncAdaptedQueuePool, "pool_size": 10}

    engine = create_async_engine(db_uri, **{**default_options, **engine_options})

    for table in db_mod.get_schema().get_metadata().tables.values():
        table.append_column(
            sa.Column("created_at", sa.Integer, default=_timestamp), replace_existing=True
        )
        table.append_column(
            sa.Column("updated_at", sa.Integer, nullable=True), replace_existing=True
        )

    hook(engine)
    db_mod.set_engine(engine)
    async with engine.begin() as conn:
        if drop_tables:
            await conn.run_sync(db_mod.get_schema().get_metadata().drop_all)
        await conn.run_sync(db_mod.get_schema().get_metadata().create_all)


class _DatabaseFacade:
    """Concrete implementation of the `grammdb.contracts.DatabaseModule` Protocol."""

    _ENGINE: AsyncEngine | None = None
    _SCHEMA: SchemaModule

    def __init__(self, schema_mod: SchemaModule) -> None:
        """
        Args:
            schema_mod: The `grammdb.contracts.DatabaseModule.schema`.
        """

        self._SCHEMA = schema_mod

    def get_schema(self) -> SchemaModule:
        return self._SCHEMA

    def get_engine(self) -> AsyncEngine:
        assert (
            self._ENGINE is not None
        ), "No engine found. Did you forget to call init_db() on this database?"
        return self._ENGINE

    def set_engine(self, value: AsyncEngine) -> None:
        self._ENGINE = value

    def new_connection(self) -> AsyncConnection:
        return self.get_engine().connect()


def db_factory(schema_mod: SchemaModule) -> Callable[[], DatabaseModule]:
    """Returns a closure that provides a valid `grammdb.contracts.DatabaseModule`.

    The closure caches the database module, so subsequent calls to the returned function
    will return the same object.

    In other words, the following invariants hold:
        ```pycon
        >>> db1 = db_factory(schema)
        >>> db2 = db_factory(schema)
        >>> db1() is db1()
        True
        >>> db2() is db2()
        True
        >>> db1() is not db2()
        True

        ```

    Note:
        The concrete type of the object returned by the closure can be any valid implementation
        of the `grammdb.contracts.DatabaseModule` protocol, including arbitrary classes or modules.
        The only guarantee about this object is that it implements that protocol correctly, so the
        concrete type and any fields on that object that are not part of the DatabaseModule protocol
        should be treated as implementation details that could change at any time. This is true even
        for public members of the concrete type that are not part of the DatabaseModule interface.
        Red flags for client code are `isinstance` checks and any usage of a field not specified
        in the protocol.
    """

    db = _DatabaseFacade(schema_mod)

    def _() -> DatabaseModule:
        return db

    return _
