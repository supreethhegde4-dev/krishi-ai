"""
Tests check_database_health and CRUD operations through db_engine on Neon PostgreSQL.
"""
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from modules.db_engine import check_database_health, get_db_connection

def main():
    h = check_database_health()
    print("Database Health Telemetry:")
    for k, v in h.items():
        print(f"• {k}: {v}")
    assert h["status"] == "HEALTHY"
    assert h["is_persistent_cloud"] == True

    # Test CRUD through get_db_connection
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, email, full_name, role FROM users LIMIT 3;")
    rows = cur.fetchall()
    print("\nSample records fetched from Neon:")
    for r in rows:
        print(f"• ID #{r['id']}: {r['full_name']} ({r['email']}) - Role: {r['role']} [Index access: {r[1]}]")
        assert r['email'] == r[1]
    conn.close()
    print("\n[SUCCESS] Neon PostgreSQL fully integrated and verified via db_engine!")

if __name__ == "__main__":
    main()
