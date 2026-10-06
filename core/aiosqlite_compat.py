"""
Lightweight aiosqlite compatibility wrapper around standard library sqlite3.
Falls back to asyncio.to_thread if aiosqlite is not installed in the environment.
Zero external dependency required. Supports both async with and await syntax.
"""
try:
    import aiosqlite as _real_aiosqlite
    aiosqlite = _real_aiosqlite
except ImportError:
    import asyncio
    import sqlite3

    class _CursorCompat:
        def __init__(self, cursor):
            self._cursor = cursor
            self.rowcount = getattr(cursor, "rowcount", -1)
            self.lastrowid = getattr(cursor, "lastrowid", None)

        async def fetchone(self):
            return await asyncio.to_thread(self._cursor.fetchone)

        async def fetchall(self):
            return await asyncio.to_thread(self._cursor.fetchall)

        def __aiter__(self):
            return self

        async def __anext__(self):
            row = await asyncio.to_thread(self._cursor.fetchone)
            if row is None:
                raise StopAsyncIteration
            return row

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    class _ExecuteContext:
        def __init__(self, conn, sql, parameters):
            self._conn = conn
            self._sql = sql
            self._parameters = parameters
            self._cursor_compat = None

        async def _run(self):
            if self._cursor_compat is None:
                cursor = await asyncio.to_thread(self._conn.execute, self._sql, self._parameters)
                self._cursor_compat = _CursorCompat(cursor)
            return self._cursor_compat

        def __await__(self):
            return self._run().__await__()

        async def __aenter__(self):
            return await self._run()

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    class _ExecuteManyContext:
        def __init__(self, conn, sql, parameters):
            self._conn = conn
            self._sql = sql
            self._parameters = parameters
            self._cursor_compat = None

        async def _run(self):
            if self._cursor_compat is None:
                cursor = await asyncio.to_thread(self._conn.executemany, self._sql, self._parameters)
                self._cursor_compat = _CursorCompat(cursor)
            return self._cursor_compat

        def __await__(self):
            return self._run().__await__()

        async def __aenter__(self):
            return await self._run()

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    class _ConnectionCompat:
        def __init__(self, conn):
            self._conn = conn
            self._row_factory = None

        @property
        def row_factory(self):
            return self._row_factory

        @row_factory.setter
        def row_factory(self, val):
            self._row_factory = val
            self._conn.row_factory = val

        def execute(self, sql, parameters=()):
            if self._row_factory:
                self._conn.row_factory = self._row_factory
            return _ExecuteContext(self._conn, sql, parameters)

        def executemany(self, sql, parameters):
            if self._row_factory:
                self._conn.row_factory = self._row_factory
            return _ExecuteManyContext(self._conn, sql, parameters)

        async def commit(self):
            await asyncio.to_thread(self._conn.commit)

        async def close(self):
            await asyncio.to_thread(self._conn.close)

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            await self.close()

    class _ConnectContext:
        def __init__(self, db_path, *args, **kwargs):
            self.db_path = db_path
            self.args = args
            self.kwargs = kwargs
            self._conn_compat = None

        def _get_conn(self):
            if self._conn_compat is None:
                conn = sqlite3.connect(self.db_path, check_same_thread=False)
                self._conn_compat = _ConnectionCompat(conn)
            return self._conn_compat

        def __await__(self):
            async def _connect_coro():
                return self._get_conn()
            return _connect_coro().__await__()

        async def __aenter__(self):
            return self._get_conn()

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            if self._conn_compat:
                await self._conn_compat.close()

    class _AioSqliteCompat:
        Row = sqlite3.Row

        def connect(self, db_path, *args, **kwargs):
            return _ConnectContext(db_path, *args, **kwargs)

    aiosqlite = _AioSqliteCompat()
