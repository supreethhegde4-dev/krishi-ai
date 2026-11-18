"""
Patches modules/auth_db.py and modules/buyer_connect_db.py to use db_engine.get_db_connection.
Ensures seamless compatibility with both Neon PostgreSQL and local SQLite.
"""
import os

auth_db_path = os.path.join(os.path.dirname(__file__), "..", "modules", "auth_db.py")
buyer_db_path = os.path.join(os.path.dirname(__file__), "..", "modules", "buyer_connect_db.py")

# 1. Patch modules/auth_db.py
with open(auth_db_path, "r", encoding="utf-8") as f:
    auth_content = f.read()

old_get_conn_auth = """def get_db_connection() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn"""

new_get_conn_auth = """from modules.db_engine import get_db_connection, is_postgres_configured"""

auth_content = auth_content.replace(old_get_conn_auth.replace("\r\n", "\n"), new_get_conn_auth)
auth_content = auth_content.replace(old_get_conn_auth.replace("\n", "\r\n"), new_get_conn_auth)

old_init_db = """def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")"""

new_init_db = """def init_db():
    if is_postgres_configured():
        return
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")"""

auth_content = auth_content.replace(old_init_db.replace("\r\n", "\n"), new_init_db)
auth_content = auth_content.replace(old_init_db.replace("\n", "\r\n"), new_init_db)

with open(auth_db_path, "w", encoding="utf-8") as f:
    f.write(auth_content)
print("[OK] Patched modules/auth_db.py")

# 2. Patch modules/buyer_connect_db.py
with open(buyer_db_path, "r", encoding="utf-8") as f:
    buyer_content = f.read()

old_get_conn_buyer = """def get_db_connection() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn"""

new_get_conn_buyer = """from modules.db_engine import get_db_connection, is_postgres_configured"""

buyer_content = buyer_content.replace(old_get_conn_buyer.replace("\r\n", "\n"), new_get_conn_buyer)
buyer_content = buyer_content.replace(old_get_conn_buyer.replace("\n", "\r\n"), new_get_conn_buyer)

old_init_buyer = """def init_buyer_connect_tables():
    \"\"\"Initializes tables for buyers, industry requirements, and quotations.\"\"\"
    conn = get_db_connection()"""

new_init_buyer = """def init_buyer_connect_tables():
    \"\"\"Initializes tables for buyers, industry requirements, and quotations.\"\"\"
    if is_postgres_configured():
        return
    conn = get_db_connection()"""

buyer_content = buyer_content.replace(old_init_buyer.replace("\r\n", "\n"), new_init_buyer)
buyer_content = buyer_content.replace(old_init_buyer.replace("\n", "\r\n"), new_init_buyer)

with open(buyer_db_path, "w", encoding="utf-8") as f:
    f.write(buyer_content)
print("[OK] Patched modules/buyer_connect_db.py")
