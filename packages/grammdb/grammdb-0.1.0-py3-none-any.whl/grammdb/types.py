from collections.abc import Callable

import sqlalchemy as sa

type WhereFunc[QUERY: (sa.Select, sa.Update, sa.Delete)] = Callable[[QUERY], QUERY]
"""Type alias used in the where clause arguments in the
`grammdb.select`, `grammdb.update`, and `grammdb.delete` functions.

The QUERY generic parameter is a tuple type (not a union) constrained to sqlalchemy's
Select, Update, or Delete constructs.

This means that this type alias represents a function that takes in a Select, Update, or Delete
statement and returns the same type of statement, and so is suitable for use in a reduction.
"""
