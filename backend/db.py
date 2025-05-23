"""Database helper with robust exception handling and automatic reconnection."""
import os, logging
import psycopg2
from psycopg2 import OperationalError, InterfaceError, DatabaseError
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

class DBConnectionError(Exception):
    """Raised when the database connection cannot be established."""

class DBQueryError(Exception):
    """Raised when a SQL query fails after retrying."""

_conn: psycopg2.extensions.connection | None = None

# ---------------------------------------------------------------------------
# Low‑level connector
# ---------------------------------------------------------------------------

def _connect():
    """Create a fresh connection using env vars (5‑second timeout)."""
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
        conn.autocommit = True
        return conn
    except (OperationalError, InterfaceError) as e:
        logging.exception("❌  PostgreSQL connection failed")
        raise DBConnectionError(str(e)) from e

# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def get_db():
    """Return a *singleton* connection, (re)opening if necessary."""
    global _conn
    if _conn is None or _conn.closed != 0:
        _conn = _connect()
    return _conn


def _retry(func, sql, params):
    """Attempt a reconnect + retry once; then raise DBQueryError."""
    global _conn
    try:
        _conn = _connect()
        return func(sql, params)
    except Exception as inner:
        raise DBQueryError(str(inner)) from inner


def query(sql: str, params: tuple = ()):  # SELECT …
    """Return *list[dict]* result rows."""
    try:
        with get_db().cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()
    except (DatabaseError, OperationalError):
        logging.warning("Retrying failed SELECT…")
        return _retry(query, sql, params)


def execute(sql: str, params: tuple = ()):  # INSERT/UPDATE/DELETE
    """Execute a statement. If it returns rows (e.g. INSERT … RETURNING) → dict."""
    try:
        with get_db().cursor() as cur:
            cur.execute(sql, params)
            if cur.description:  # RETURNING …
                return cur.fetchone()
    except (DatabaseError, OperationalError):
        logging.warning("Retrying failed statement…")
        return _retry(execute, sql, params)

