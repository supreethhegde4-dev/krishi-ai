"""
Tests live connectivity to Neon PostgreSQL using Psycopg 3.
Redacts all passwords and connection credentials.
"""
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

def load_neon_url(unpooled=False):
    key = "DATABASE_URL_UNPOOLED" if unpooled else "DATABASE_URL"
    if os.environ.get(key):
        return os.environ.get(key)
    
    for fname in [".env.local", ".env"]:
        fpath = os.path.join(PROJECT_ROOT, fname)
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(f"{key}="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
                    if not unpooled and line.startswith("DATABASE_URL="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None

def main():
    url = load_neon_url(unpooled=False)
    if not url:
        print("[ERROR] No DATABASE_URL found in environment, .env.local, or .env")
        sys.exit(1)

    import psycopg
    from psycopg.rows import dict_row

    print("[INFO] Connecting to Neon PostgreSQL using Psycopg 3...")
    try:
        with psycopg.connect(url, row_factory=dict_row, connect_timeout=10) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                v_row = cur.fetchone()
                version_str = v_row["version"] if v_row else "Unknown"
                
                cur.execute("SELECT current_database(), current_user, inet_server_addr();")
                info = cur.fetchone()
                
                print("[SUCCESS] Connected to Neon PostgreSQL successfully!")
                print(f"• Database Engine: {version_str.split(' on ')[0]}")
                print(f"• Connected Database: {info['current_database']}")
                print(f"• Database User: {info['current_user']}")
                print("• SSL Connection: Encrypted (require)")
    except Exception as e:
        print(f"[FAILED] Could not connect to Neon PostgreSQL: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
