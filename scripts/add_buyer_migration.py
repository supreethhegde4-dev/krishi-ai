import os
import sqlite3

target_file = "modules/buyer_connect_db.py"
with open(target_file, "r", encoding="utf-8") as f:
    code = f.read()

migration_code = """    # Database Migrations: Ensure production columns exist
    c.execute("PRAGMA table_info(buyers)")
    existing_cols = [r[1] for r in c.fetchall()]
    if "gstin" not in existing_cols:
        c.execute("ALTER TABLE buyers ADD COLUMN gstin TEXT")
    if "apmc_license" not in existing_cols:
        c.execute("ALTER TABLE buyers ADD COLUMN apmc_license TEXT")
    if "verified_by" not in existing_cols:
        c.execute("ALTER TABLE buyers ADD COLUMN verified_by INTEGER")
    if "verification_remarks" not in existing_cols:
        c.execute("ALTER TABLE buyers ADD COLUMN verification_remarks TEXT")
    conn.commit()
"""

# Insert migration right before conn.commit() in init_buyer_connect_tables
insert_idx = code.find("active_env = os.environ.get(\"KRISHI_ENV\", \"production\").lower()")
if "PRAGMA table_info(buyers)" not in code and insert_idx != -1:
    code = code[:insert_idx] + migration_code + "    " + code[insert_idx:]
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(code)
    print("SUCCESS: Added database migration to modules/buyer_connect_db.py")
else:
    print("Migration already present or insert_idx not found")
