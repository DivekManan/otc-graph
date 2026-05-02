import sqlite3
from contextlib import contextmanager

DB_PATH = "otc.db"

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def execute_query(sql: str, params=None):
    with get_db() as conn:
        cur = conn.cursor()
        if params:
            cur.execute(sql, params)
        else:
            cur.execute(sql)
        rows = cur.fetchall()
        return [dict(row) for row in rows]

def get_schema():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cur.fetchall()]
        schema = {}
        for table in tables:
            cur.execute(f"PRAGMA table_info({table})")
            cols = cur.fetchall()
            schema[table] = [{"name": c[1], "type": c[2]} for c in cols]
        return schema