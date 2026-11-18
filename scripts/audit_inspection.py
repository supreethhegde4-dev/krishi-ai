import os
import sqlite3
import glob

DB_PATH = "data/krishi_ai.db"
print("=== DATABASE AUDIT ===")
if os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    print(f"Total tables: {len(tables)}")
    for t in tables:
        cnt = c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  Table: {t:28} | Rows: {cnt}")
        
    print("\n--- Users Table Breakdown ---")
    users = c.execute("SELECT id, email, full_name, role, created_at FROM users").fetchall()
    for u in users:
        print(f"  User #{u[0]}: {u[1]} ({u[2]}) - Role: {u[3]}")

    print("\n--- Buyers Table Breakdown ---")
    buyers = c.execute("SELECT id, company_name, business_type, contact_person, email, verified_status FROM buyers").fetchall()
    for b in buyers:
        print(f"  Buyer #{b[0]}: {b[1]} ({b[2]}) - Contact: {b[3]} ({b[4]}) - Verified: {b[5]}")

    print("\n--- Buyer Requirements Breakdown ---")
    reqs = c.execute("SELECT id, buyer_id, crop, quantity_quintals, offered_price_per_quintal, status FROM buyer_requirements").fetchall()
    for r in reqs:
        print(f"  Req #{r[0]}: Buyer #{r[1]} - {r[2]} ({r[3]} Q) @ Rs.{r[4]}/Q - Status: {r[5]}")

    conn.close()
else:
    print(f"Database {DB_PATH} not found!")

print("\n=== PARQUET & DUCKDB DATA AUDIT ===")
parquet_files = glob.glob("data/historical_parquet/parquet/*.parquet")
print(f"Parquet files found: {len(parquet_files)}")
total_size_mb = sum(os.path.getsize(f) for f in parquet_files) / (1024 * 1024)
print(f"Total Parquet size: {total_size_mb:.2f} MB")

print("\n=== MODELS AUDIT ===")
model_files = glob.glob("models/*.pkl")
for m in model_files:
    print(f"  Model: {m} ({os.path.getsize(m)/1024:.1f} KB)")
