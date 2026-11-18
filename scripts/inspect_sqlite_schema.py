"""
Inspects all tables, schemas, and row counts in data/krishi_ai.db
"""
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "krishi_ai.db")

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = cur.fetchall()

    print(f"Discovered {len(tables)} tables in SQLite:")
    for name, sql in tables:
        cur.execute(f"SELECT COUNT(*) FROM {name};")
        cnt = cur.fetchone()[0]
        print(f"\n--- Table: {name} ({cnt} rows) ---")
        print(sql)

if __name__ == "__main__":
    main()
