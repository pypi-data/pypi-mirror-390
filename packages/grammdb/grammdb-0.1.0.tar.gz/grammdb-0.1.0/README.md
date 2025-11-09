# grammdb
GrammAcc's Async Data Layer for Python Apps

**This project is still under development and may not be suitable for production applications**

This package provides a convenience layer over sqlalchemy core for async database setup and queries.

I frequently use the patterns in this package in my Quart projects, so I decided to package up the common pieces, so that I could pip install my data layer boilerplate instead of copying it from project to project.

The purpose of this package is to provide a foundation for building an isolated data layer in a traditional three-layer application. This makes maintenance easier since data access is isolated from the business logic of the service layer in the same way that display logic and user interactions are.

Most modern web frameworks do a good job of encouraging separation of display and business logic, but most examples you will find online mix the data and service layers together in ways that make it harder to test and modify the application.

Grammdb provides a few wrapper functions that simplify the process of connecting and querying a database through sqlalchemy's core, but it does not abstract away sqlalchemy's functionality or features. This is only a convenience wrapper to make some of the more error-prone parts of data abstraction easier to get right.

[API Docs](https://grammacc.github.io/grammdb)

## Installation

```bash
pip install grammdb
```

## Basic Usage

Assuming our data layer is in a sub-package named `dl`.

Define the database schema:

```python
# dl/schema.py

import sqlalchemy as sa
import grammdb

_metadata = sa.MetaData()

def get_metadata():
    return _metadata

MyTable = sa.Table(
    "my_table",
    get_metadata(),
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("my_relation_id", sa.Integer, sa.ForeignKey("my_relation.id"), nullable=True),
)

MyRelation = sa.Table(
    "my_relation",
    get_metadata(),
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("my_col", sa.Text),
)
```

Create and configure the database:

```python
# dl/__init__.py

import functools

import grammdb

from . import schema

database = grammdb.db_factory(schema)

async def init():
    await grammdb.init_db(database(), "sqlite+aiosqlite:///db.sqlite", echo=True, pool_size=15)
```

The `init_db` function configures the sqlalchemy async engine and makes it accessible via the database's `get_engine` function.
It also adds `created_at` and `updated_at` integer timestamp columns to every table in the database's schema, so that they do not need to be declared on every table in the schema manually.

Now we can call the init function in our application's startup routine:

```python
# app.py

import asyncio

from . import dl

async def run_app():
    await dl.init()

asyncio.run(run_app())
```

An alternative to declaring the init function is to use `functools.partial`:

```python
# dl/__init__.py

...

init = functools.partial(grammdb.init_db, database(), "sqlite+aiosqlite:///db.sqlite")
```

This has the advantage of allowing any caller to provide options to the underlying sqlalchemy engine:

```python
# app.py

...

async def run_app():
    await dl.init(poolclass=sa.pool.StaticPool)

...
```

The `db_factory` helper makes it easy to set up multiple databases as well:

```python
# dl/__init__.py

import functools

import grammdb

from . import app_schema, analytics_schema

app_database = grammdb.db_factory(app_schema)
analytics_database = grammdb.db_factory(analytics_schema)

init_app_db = functools.partial(grammdb.init_db, app_database(), "sqlite+aiosqlite:///app.db")
init_analytics_db = functools.partial(grammdb.init_db, analytics_database(), "postgresql+asyncpg://postgres:postgres@localhost:5432/usage")
```

With our database(s) now accessible by our application, we can start adding queries.

Grammdb provides wrapper functions for insert, update, delete, and select statements that read more like sql and avoid some of the pitfalls of sqlalchemy's query DSL as well as helpers for managing transactions both inside and out of a context manager.

Note: This example is stupidly contrived, but the point is to demonstrate the syntax, so bear with me. :)

```python
# service.py

import datetime
import asyncio

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncConnection

from grammdb import (
    select,
    insert,
    update,
    delete,
    start_transaction,
    commit_transaction,
    rollback_transaction,
    connection_ctx,
)
from grammdb.exceptions import constraint_error, ForeignKeyConstraintError
from grammdb.types import WhereFunc

import dl
from dl.schema import MyTable, MyRelation


def where_has_relation() -> WhereFunc:
    # Where functions are used in the select, update, and delete wrappers.
    # They take a single argument, which is a sqlalchemy statement that conforms
    # to the Selectable interface.
    def _(selectable):
        return selectable.where(sa.column("my_relation_id") != None)
    return _


def where_created_before(dt: datetime.datetime, table_name: str | None = None) -> WhereFunc:
    if table_name is None:
        def _(selectable):
            return selectable.where(sa.column("created_at") < dt.timestamp())
        return _
    else:
        def _(selectable):
            return selectable.where(sa.column(f"{table_name}_created_at") < dt.timestamp())
        return _


def from_my_data() -> sa.Select:
    # From functions return a valid Selectable that can be used
    # as the from clause in a query.
    aliases = {
        "my_table": [v.label("my_table_" + str(k)) for k, v in MyTable.c.items()],
        "my_relation": [v.label("my_relation_" + str(k)) for k, v in MyRelation.c.items()],
    }

    target = sa.outerjoin(MyTable, MyRelation, MyTable.c.my_relation_id == MyRelation.c.id)
    return sa.select(*[*aliases["my_relation"], *aliases["my_table"]]).select_from(target)


async def create_row(tr: AsyncConnection, relation_id: int | None = None) -> None:
    # The insert wrapper uses keyword-only arguments to read more like sql.
    stmt = insert(into=MyTable, my_relation_id=relation_id)
    await tr.execute(stmt)


async def create_relation(tr: AsyncConnection, col_val: str) -> int:
    stmt = insert(into=MyRelation, my_col=col_val).returning(MyRelation.c.id)
    res = await tr.execute(stmt)
    return res.scalar_one()


last_week = lambda: datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=7)


async def delete_old_relations(tr: AsyncConnection) -> list[str]:
    # The delete and update wrappers use the where functions to read more like sql.
    delete_relation = delete(MyRelation, where_created_before(last_week()))
    stmt = delete_relation.returning(MyRelation.c.my_col)
    try:
        with constraint_error():
            # The constraint_error() helper raises an error for the specific
            # constraint that was violated inside the context block if applicable.
            # Non-constraint violation errors are still propagated like normal, so this
            # won't interfere with other error handling logic.
            res = await tr.execute(stmt)
            return res.scalars()
    except ForeignKeyConstraintError:
        fk_stmt = delete(MyTable, where_created_before(last_week()), where_has_relation())
        await tr.execute(fk_stmt)
        res = await tr.execute(stmt)
        return res.scalars()


async def refresh_data():
    await dl.setup(echo=True)
    # We can manually start, rollback, and commit transactions
    # using the database that we created with our factory.
    tr = await start_transaction(dl.database())
    try:
        deleted_cols = await delete_old_relations(tr)
        for col_val in deleted_cols:
            rel_id = await create_relation(tr, col_val)
            await create_row(tr, rel_id)
    except Exception as e:
        await rollback_transaction(tr)
        raise e
    else:
        await commit_transaction(tr)

async def get_old_rows() -> list[sa.Row]:
    # We can also use connection_ctx() as an async context manager
    # instead of managing the transaction manually.
    async with connection_ctx(dl.database()) as conn:
        # The select wrapper uses the from and where functions to read more like sql.
        # It also accepts a string name of a column or a list of strings as the columns to select.
        # "*" is a special case that selects all columns from the from clause, but does not actually
        # do a select star in SQL. This is effectively the same as selecting an entire Model or Table
        # in regular SQLAlchemy.
        stmt = select("*", from_my_data(), where_created_before(last_week(), "my_table"))
        res = await conn.execute(stmt)
        return res.all()


asyncio.run(refresh_data())
```

The query wrappers give a more sql-like syntax for declaring common statements, and they also make the selected columns and from clause explicit. SQLalchemy's query DSL derives the from clause from the select clause, which can lead to unexpected problems like an unwanted cartesian product. It also makes complex queries harder to reason about because the semantics of the from clause are hidden.

The `from_*` and `where_*` functions can be called anything, but prefixing them with `from_` and `where_` causes the statements to read more like sql and makes it clearer what positional arguments are doing what in the resulting query.

I prefer declaring these functions in their own modules, so next to the `schema.py` module, I would also have a `from_.py` and `where.py`, and then the `from_my_data()` function would get called as `from_.my_data()`, and the `where_created_before()` would be `where.created_before()`. This promotes code reuse and modularity as well as composability of queries. The only part that bugs me is that `from` is a reserved word, so the module of from functions has to be suffixed with `_`.

See the [API Docs](https://grammacc.github.io/grammdb) for more details about the query and transaction functions.

## Other Examples

### Use In Alembic Migrations

```python
# env.py

import grammdb
from my_app import dl


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=dl.database().get_schema().get_metadata())

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    await dl.init(echo=True, poolclass=sa.pool.NullPool)

    async with grammdb.connection_ctx(dl.database()) as conn:
        await conn.run_sync(do_run_migrations)

    await dl.database().get_engine().dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())
```

### Standalone Python Script

```python
# prune_old_rows.py

import sqlalchemy as sa
import grammdb
import datetime
from my_app import dl
from my_app.dl import where

async def prune():
  await dl.init(poolclass=sa.pool.NullPool)
  async with grammdb.connection_ctx(dl.database()) as conn:
    last_week = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=7)
    stmt = grammdb.delete(dl.schema.MyTable, where.created_before(last_week.timestamp()))
    await conn.execute(stmt)
    await conn.commit()

asyncio.run(prune())
```

