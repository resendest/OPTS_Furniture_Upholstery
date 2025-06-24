# backend/db.py

import os
import logging
from dotenv import load_dotenv
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import RealDictCursor

load_dotenv()

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
    """
    Execute any SQL:
      • If it’s a SELECT, returns a list of rows (each a dict).
      • If it’s an INSERT/UPDATE/DELETE with RETURNING, returns a single dict.
      • Otherwise returns None.
    """
    conn = _pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            result = None
            if cur.description:
                first_word = sql.lstrip().split()[0].upper()
                if first_word == "SELECT":
                    result = cur.fetchall()
                else:
                    result = cur.fetchone()
            conn.commit()
            return result
    except Exception:
        conn.rollback()
        logging.exception("Database error executing SQL")
        raise
    finally:
        _pool.putconn(conn)


def query(sql: str, params: tuple = ()):
    """
    Convenience for SELECTs when you always want a list back.
    """
    rows = execute(sql, params)
    return rows or []
