import contextlib

from sqlalchemy.exc import IntegrityError


class ConstraintError(Exception):
    """Base class for constraint violation exceptions."""

    pass


class UniqueConstraintError(ConstraintError):
    """Represents a unique constraint violation."""

    pass


class ForeignKeyConstraintError(ConstraintError):
    """Represents a foreign key constraint violation."""

    pass


class CheckConstraintError(ConstraintError):
    """Represents a check constraint violation."""

    pass


class NotNullConstraintError(ConstraintError):
    """Represents a not null constraint violation."""

    pass


@contextlib.contextmanager
def constraint_error():
    """Context manager that will catch and parse a `sqlalchemy.exc.IntegrityError`
    and raise one of the specific constraint errors from this module in its place.

    SQLAlchemy raises `IntegrityError` on any constraint violation, but sometimes it's
    helpful to know exactly which constraint was violated in application code and handle
    only that specific error.

    Note:
        This is only tested on sqlite3 and postgresql. This function relies on the
        string message provided in the sqlalchemy error to determine which constraint
        was violated, and this may not be reliable on all backends.

    Example:
        ```pycon
        >>> from grammdb.exceptions import constraint_error, UniqueConstraintError
        >>> def generate_xkcd_random_number():
        ...     # Chosen by fair dice roll.
        ...     # Guaranteed to be random.
        ...     return 4
        >>> async def try_insert(rand_num):
        ...     try:
        ...         async with grammdb.connection_ctx(database()) as conn:
        ...             with constraint_error():
        ...                 await conn.execute(grammdb.insert(into=schema.MyTable, num=rand_num))
        ...                 await conn.commit()
        ...     except UniqueConstraintError:
        ...         print("Random number collision encountered. Trying a new random number...")
        ...         await try_insert(generate_xkcd_random_number())
        ...     except Exception as e:
        ...         print(f"Unknown error occurred: {e}")
        >>> async def ex():
        ...     await grammdb.init_db(database(), "sqlite+aiosqlite://")
        ...     await try_insert(generate_xkcd_random_number())
        >>> asyncio.run(ex())

        ```
    """

    try:
        yield None
    except IntegrityError as e:
        err_str = str(e)
        comp_str = err_str.lower()
        if "unique constraint" in comp_str:
            raise UniqueConstraintError(err_str) from e
        elif "check constraint" in comp_str:
            raise CheckConstraintError(err_str) from e
        elif "foreign key constraint" in comp_str:
            raise ForeignKeyConstraintError(err_str) from e
        elif "not null constraint" in comp_str or "not-null constraint" in comp_str:
            raise NotNullConstraintError(err_str) from e
        else:
            raise e
