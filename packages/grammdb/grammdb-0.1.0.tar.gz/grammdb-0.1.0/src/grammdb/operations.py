__all__ = [
    "delete",
    "insert",
    "select",
    "update",
]

import functools
import math
import time
from typing import Any

import sqlalchemy as sa

from grammdb.types import WhereFunc

_reducer = lambda stmt, where_func: where_func(stmt)
_timestamp = lambda: math.floor(time.time())


def select(
    columns: str | tuple[str, ...], from_clause: sa.Select, *where_clauses: WhereFunc
) -> sa.Select:
    """Wrapper for generating sqlalchemy select statements with a more sql-like DSL.

    Note:
        Using "*" as the first argument is a special case that does not actually do a select star
        in SQL. It is simply syntax sugar around SQLAlchemy's regular behavior of selecting the
        full set of columns in the from clause by name.
        In other words, `sa.select(MyTable)` and `grammdb.select("*", sa.select(MyTable))` are
        effectively equivalent.

    Args:
        columns:
            One of the following:
                A single string representing the name of the column to select.
                A literal "*" meaning select all columns in the from clause.
                A list of strings representing the column names to select from the from clause.
        from_clause:
            A selectable object. Usually, this would be provided using a from function to create
            a statement that reads more like sql.
        *where_clauses:
            Arbitrary number of where functions to apply as the where clause in the built query.
    """

    # Explanation for Any:
    # SQLAlchemy's core is too dynamic, and it's type annotations don't match the documented
    # inputs. E.g. a tuple of string column names doesn't satisfy the type annotations for
    # with_only_columns below, but this works at runtime.
    select_columns: Any = (
        from_clause.selected_columns if columns == "*" else from_clause.selected_columns[columns]
    )
    return functools.reduce(
        _reducer,
        where_clauses,
        from_clause.with_only_columns(select_columns),
    )


def update(table_: sa.Table, *where_clauses: WhereFunc, **set_clause: Any) -> sa.Update:
    """Wrapper for generating sqlalchemy update statements with a more sql-like DSL."""

    return functools.reduce(
        _reducer,
        where_clauses,
        sa.update(table_),
    ).values(**set_clause, updated_at=_timestamp())


def delete(from_: sa.Table, *where_clauses: WhereFunc) -> sa.Delete:
    """Wrapper for generating sqlalchemy delete statements with a more sql-like DSL."""

    return functools.reduce(
        _reducer,
        where_clauses,
        sa.delete(from_),
    )


def insert(*, into: sa.Table, **values: Any) -> sa.Insert:
    """Wrapper for generating sqlalchemy insert statements with a more sql-like DSL.

    The `into` argument is enforced as keyword-only to make the statements read more like sql.
    """

    return sa.insert(into).values(**values)


def insert_many(*, into: sa.Table, values: list[dict[str, Any]]) -> sa.Insert:
    """Wrapper for generating sqlalchemy bulk insert statements with a more sql-like DSL.

    The `into` argument is enforced as keyword-only to make the statements read more like sql.
    """

    return sa.insert(into).values(values)
