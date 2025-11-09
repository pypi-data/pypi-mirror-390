from sqlalchemy.ext.asyncio import AsyncConnection

from grammdb.contracts import DatabaseModule


def connection_ctx(db: DatabaseModule) -> AsyncConnection:
    """Returns a connection object suitable for use as an async context manager.

    Example:
        ```pycon
        >>> import sqlalchemy as sa
        >>> async def ex():
        ...     await grammdb.init_db(database(), "sqlite+aiosqlite://")
        ...     async with connection_ctx(database()) as conn:
        ...         stmt = grammdb.insert(into=schema.MyTable, num=1).returning(sa.column("num"))
        ...         result = await conn.execute(stmt)
        ...         await conn.commit()
        ...         return result.scalar_one()
        >>> asyncio.run(ex())
        1

        ```
    """

    return db.new_connection()


async def start_transaction(db: DatabaseModule) -> AsyncConnection:
    """Return an open transaction that can be passed around without a context block.

    Must be closed manually using one of the `{rollback|close|commit}_transaction` functions.

    Example:
        ```pycon
        >>> import sqlalchemy as sa
        >>> from sqlalchemy.exc import IntegrityError
        >>> async def ex():
        ...     tr = await start_transaction(database())
        ...     try:
        ...         stmt = grammdb.insert(into=schema.MyTable, num=1).returning(sa.column("num"))
        ...         result = await tr.execute(stmt)
        ...     except IntegrityError as e:
        ...         await rollback_transaction(tr)
        ...         raise e
        ...     else:
        ...         await commit_transaction(tr)
        ...         return result.scalar_one()
        >>> asyncio.run(ex())
        1

        ```
    """

    conn = db.new_connection()
    await conn.start()
    await conn.begin()
    return conn


async def rollback_transaction(tr: AsyncConnection) -> None:
    """Rollback a transaction manually.

    Intended to be used on the connection returned by `start_transaction`.
    """

    await tr.rollback()
    await tr.close()


async def close_transaction(tr: AsyncConnection) -> None:
    """Close a transaction manually.

    Intended to be used on the connection returned by `start_transaction`.
    """

    await tr.close()


async def commit_transaction(tr: AsyncConnection) -> None:
    """Commit a transaction manually.

    Intended to be used on the connection returned by `start_transaction`.
    """

    await tr.commit()
    await tr.close()
