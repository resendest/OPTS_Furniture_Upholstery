from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

import os
import logging
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import RealDictCursor

# Initialize a module-level connection pool
_pool = SimpleConnectionPool(
    minconn=int(os.getenv("DB_MIN_CONN", 1)),
    maxconn=int(os.getenv("DB_MAX_CONN", 5)),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "127.0.0.1"),
    port=os.getenv("DB_PORT", "5432"),
    cursor_factory=RealDictCursor,
)


def execute(sql: str, params: tuple = ()):
    conn = _pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            # Fetch rows if any (SELECT or RETURNING)
            result = cur.fetchall() if cur.description else None
        # ----- ALWAYS commit, even on INSERT … RETURNING -----
        conn.commit()
        return result
    except Exception:
        conn.rollback()
        logging.exception("Database error executing SQL")
        raise
    finally:
        _pool.putconn(conn)

def query(sql: str, params: tuple = ()):
    """Alias for execute that always expects rows (SELECT)."""
    rows = execute(sql, params)
    return rows or []

