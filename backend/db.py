# backend/db.py

import os, logging, psycopg2
from psycopg2 import OperationalError, InterfaceError
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import TRANSACTION_STATUS_IDLE
from dotenv import load_dotenv
from contextlib import contextmanager

load_dotenv()


class DBConnectionError(Exception):
    """Raised when the database connection cannot be established."""


class DBQueryError(Exception):
    """Raised when a SQL query fails after retrying."""


_conn: psycopg2.extensions.connection | None = None


def _connect():
    """Create a fresh connection using env vars (5-second timeout)."""
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            cursor_factory=RealDictCursor,
            connect_timeout=5
        )
        conn.autocommit = False  # turn off autocommit so we control commit/rollback
        return conn
    except (OperationalError, InterfaceError) as e:
        logging.exception("PostgreSQL connection failed")
        raise DBConnectionError(str(e)) from e


def get_db():
    """Return a *singleton* connection, (re)opening if necessary."""
    global _conn
    if _conn is None or _conn.closed != 0:
        _conn = _connect()
    return _conn


@contextmanager
def transaction():
    """
    Usage:
        with transaction():
            execute("INSERT ...", [...])
            execute("UPDATE ...", [...])
        # commits at block end if no exception, otherwise rolls back
    """
    conn = get_db()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def _retry(func, sql, params):
    """Attempt a reconnect + retry once; then raise DBQueryError."""
    global _conn
    try:
        _conn = _connect()
        return func(sql, params)
    except Exception as inner:
        raise DBQueryError(str(inner)) from inner


def query(sql: str, params: tuple = ()):
    """
    Return *list[dict]* result rows for a SELECT.
    Retries once on transient errors.
    """
    try:
        with get_db().cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()
    except (psycopg2.DatabaseError, psycopg2.OperationalError):
        logging.warning("Retrying failed SELECT…")
        return _retry(query, sql, params)


def execute(sql: str, params: tuple = ()):  # INSERT/UPDATE/DELETE
    """
    Execute a statement. If it returns rows (e.g. INSERT … RETURNING) → dict.
    Commits only if no transaction is already active.
    Retries once on transient errors.
    """
    conn = get_db()
    try:
        # Check current transaction status
        status_before = conn.get_transaction_status()

        with conn.cursor() as cur:
            cur.execute(sql, params)
            row = None
            if cur.description:      # e.g. INSERT … RETURNING
                row = cur.fetchone()

        # Only commit if we were idle before (not inside transaction())
        if status_before == TRANSACTION_STATUS_IDLE:
            conn.commit()

        return row

    except (psycopg2.DatabaseError, psycopg2.OperationalError):
        logging.warning("Retrying failed statement…")
        conn.rollback()
        return _retry(execute, sql, params)
