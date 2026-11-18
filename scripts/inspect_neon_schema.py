"""
Inspects public schema tables in the connected Neon PostgreSQL database.
"""
import os
import sys
import psycopg
from psycopg.rows import dict_row

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def get_url():
    for fname in [".env.local", ".env"]:
        fpath = os.path.join(PROJECT_ROOT, fname)
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("DATABASE_URL="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None

def main():
    url = get_url()
    if not url:
        print("[ERROR] DATABASE_URL not found.")
        sys.exit(1)

    with psycopg.connect(url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """)
            tables = cur.fetchall()
            tbl_names = [t["table_name"] for t in tables]
            print(f"Existing tables in Neon public schema ({len(tbl_names)} tables):")
            print(tbl_names)

if __name__ == "__main__":
    main()
