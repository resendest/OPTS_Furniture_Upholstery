# backend/tests/test_db.py

import pytest
from backend.db import execute, query, transaction

def test_execute_and_query(tmp_path, monkeypatch):
    # Use a temporary table to avoid touching real data
    # 1) Create a temp table
    execute("CREATE TEMP TABLE t1 (id SERIAL PRIMARY KEY, name TEXT);", ())
    # 2) Insert a row and RETURNING id
    row = execute("INSERT INTO t1 (name) VALUES (%s) RETURNING id;", ("alice",))
    assert isinstance(row, dict)
    row_id = row["id"]
    assert isinstance(row_id, int)

    # 3) Query that same table
    results = query("SELECT name FROM t1 WHERE id = %s;", (row_id,))
    assert results == [{"name": "alice"}]

    # 4) Test transaction rollback
    with pytest.raises(Exception):
        with transaction():
            # Insert one more row, then force an error
            execute("INSERT INTO t1 (name) VALUES (%s);", ("bob",))
            raise Exception("force rollback")

    # After rollback, there should still be only one row ("alice")
    final = query("SELECT name FROM t1;")
    assert final == [{"name": "alice"}]
