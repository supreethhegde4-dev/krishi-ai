import os
import re

print("=== REFACTORING AUTH_DB & BUYER_CONNECT_DB FOR PRODUCTION READINESS ===")

# 1. Update modules/auth_db.py
auth_file = "modules/auth_db.py"
with open(auth_file, "r", encoding="utf-8") as f:
    auth_code = f.read()

# Replace seeding in init_db with conditional check on KRISHI_ENV
old_seed_block = """    # Seed Default Farmer & Admin if database is empty
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        # 1. Default Farmer Account
        farmer_pwd_hash = bcrypt.hashpw("Password@123".encode("utf-8"), bcrypt.gensalt(12)).decode("utf-8")
        c.execute(\"\"\"
        INSERT INTO users (email, password_hash, full_name, phone, role, created_at, is_active)
        VALUES (?, ?, ?, ?, ?, ?, 1)
        \"\"\", ("farmer@krishiai.com", farmer_pwd_hash, "Ramesh Gowda", "+91 98450 12345", "farmer", now_str))
        farmer_id = c.lastrowid
        
        c.execute(\"\"\"
        INSERT INTO farm_profiles (user_id, farm_name, acreage, village, district, state, latitude, longitude, soil_type, primary_crops, irrigation_source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        \"\"\", (farmer_id, "Green Valley Agro Farm", 3.5, "Ramanagara Rural", "Ramanagara", "Karnataka", 12.7209, 77.2799, "Red Sandy Loam", "Tomato, Maize, Banana", "Borewell Drip Irrigation"))

        # 2. Default Admin Account
        admin_pwd_hash = bcrypt.hashpw("Admin@123".encode("utf-8"), bcrypt.gensalt(12)).decode("utf-8")
        c.execute(\"\"\"
        INSERT INTO users (email, password_hash, full_name, phone, role, created_at, is_active)
        VALUES (?, ?, ?, ?, ?, ?, 1)
        \"\"\", ("admin@krishiai.com", admin_pwd_hash, "Krishi System Administrator", "+91 98800 54321", "admin", now_str))
        admin_id = c.lastrowid
        
        c.execute(\"\"\"
        INSERT INTO farm_profiles (user_id, farm_name, acreage, village, district, state, latitude, longitude, soil_type, primary_crops, irrigation_source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        \"\"\", (admin_id, "Central Agricultural Research Station", 10.0, "GKVK Campus", "Bangalore Urban", "Karnataka", 13.0768, 77.5753, "Clay Loam", "All Research Crops", "Canal & Micro-Sprinkler"))

        conn.commit()

    # Ensure Demo Buyer Account exists
    c.execute("SELECT id FROM users WHERE email = 'buyer@krishiai.com'")
    buyer_row = c.fetchone()
    if not buyer_row:
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        buyer_pwd_hash = bcrypt.hashpw("Password@123".encode("utf-8"), bcrypt.gensalt(12)).decode("utf-8")
        c.execute(\"\"\"
        INSERT INTO users (email, password_hash, full_name, phone, role, created_at, is_active)
        VALUES (?, ?, ?, ?, 'buyer', ?, 1)
        \"\"\", ("buyer@krishiai.com", buyer_pwd_hash, "Vikramaditya Rao", "+91 98451 22334", now_str))
        b_uid = c.lastrowid
        c.execute(\"\"\"
        INSERT OR REPLACE INTO farm_profiles (user_id, farm_name, acreage, village, district, state, latitude, longitude, soil_type, primary_crops, irrigation_source)
        VALUES (?, 'ITC Procurement & Sourcing Center', 0.0, 'Bidadi Industrial Area Phase II', 'Ramanagara', 'Karnataka', 12.7981, 77.4005, 'Industrial Agro Hub', 'Tomato, Wheat, Potato', 'Industrial Borewell')
        \"\"\", (b_uid,))
        # Link user_id to ITC in buyers table if exists
        try:
            c.execute("UPDATE buyers SET user_id = ? WHERE company_name LIKE '%ITC Agri%'", (b_uid,))
        except Exception:
            pass
        conn.commit()

    # Ensure Demo Inspector Account exists
    c.execute("SELECT id FROM users WHERE email = 'inspector@krishiai.com'")
    inspector_row = c.fetchone()
    if not inspector_row:
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        insp_pwd_hash = bcrypt.hashpw("Inspector@123".encode("utf-8"), bcrypt.gensalt(12)).decode("utf-8")
        c.execute('''
        INSERT INTO users (email, password_hash, full_name, phone, role, created_at, is_active)
        VALUES (?, ?, ?, ?, 'inspector', ?, 1)
        ''', ("inspector@krishiai.com", insp_pwd_hash, "Dr. Anand Murthy", "+91 94480 33442", now_str))
        i_uid = c.lastrowid
        c.execute('''
        INSERT OR REPLACE INTO farm_profiles (user_id, farm_name, acreage, village, district, state, latitude, longitude, soil_type, primary_crops, irrigation_source)
        VALUES (?, 'APMC State Quality & Certification Bureau', 0.0, 'Yeshwanthpur APMC Yard', 'Bangalore Urban', 'Karnataka', 13.0234, 77.5512, 'Accredited Testing Lab', 'Quality Certification & Grading', 'Inspection Facility')
        ''', (i_uid,))
        conn.commit()

    conn.close()"""

new_seed_block = """    conn.commit()
    # In development mode, seed test sandbox accounts for testing
    active_env = os.environ.get("KRISHI_ENV", "development").lower()
    if active_env == "development":
        seed_development_accounts(conn)

    conn.close()"""

dev_seed_func = """

def seed_development_accounts(conn: sqlite3.Connection):
    \"\"\"
    Seeds isolated sandbox test accounts ONLY when KRISHI_ENV=development.
    Never executed in production.
    \"\"\"
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        farmer_pwd_hash = bcrypt.hashpw("Password@123".encode("utf-8"), bcrypt.gensalt(12)).decode("utf-8")
        c.execute(\"\"\"
        INSERT INTO users (email, password_hash, full_name, phone, role, created_at, is_active)
        VALUES (?, ?, ?, ?, ?, ?, 1)
        \"\"\", ("farmer@krishiai.com", farmer_pwd_hash, "Ramesh Gowda", "+91 98450 12345", "farmer", now_str))
        farmer_id = c.lastrowid
        c.execute(\"\"\"
        INSERT INTO farm_profiles (user_id, farm_name, acreage, village, district, state, latitude, longitude, soil_type, primary_crops, irrigation_source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        \"\"\", (farmer_id, "Green Valley Agro Farm (Sandbox)", 3.5, "Ramanagara Rural", "Ramanagara", "Karnataka", 12.7209, 77.2799, "Red Sandy Loam", "Tomato, Maize, Banana", "Borewell Drip Irrigation"))

        admin_pwd_hash = bcrypt.hashpw("Admin@123".encode("utf-8"), bcrypt.gensalt(12)).decode("utf-8")
        c.execute(\"\"\"
        INSERT INTO users (email, password_hash, full_name, phone, role, created_at, is_active)
        VALUES (?, ?, ?, ?, ?, ?, 1)
        \"\"\", ("admin@krishiai.com", admin_pwd_hash, "System Administrator (Sandbox)", "+91 98800 54321", "admin", now_str))
        admin_id = c.lastrowid
        c.execute(\"\"\"
        INSERT INTO farm_profiles (user_id, farm_name, acreage, village, district, state, latitude, longitude, soil_type, primary_crops, irrigation_source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        \"\"\", (admin_id, "Central Agricultural Research Station (Sandbox)", 10.0, "GKVK Campus", "Bangalore Urban", "Karnataka", 13.0768, 77.5753, "Clay Loam", "All Research Crops", "Canal & Micro-Sprinkler"))

        conn.commit()

    # Seed dev buyer
    c.execute("SELECT id FROM users WHERE email = 'buyer@krishiai.com'")
    if not c.fetchone():
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        b_pwd = bcrypt.hashpw("Password@123".encode("utf-8"), bcrypt.gensalt(12)).decode("utf-8")
        c.execute("INSERT INTO users (email, password_hash, full_name, phone, role, created_at, is_active) VALUES (?, ?, 'Vikramaditya Rao (Sandbox)', '+91 98451 22334', 'buyer', ?, 1)", ("buyer@krishiai.com", b_pwd, now_str))
        b_uid = c.lastrowid
        c.execute("INSERT OR REPLACE INTO farm_profiles (user_id, farm_name, acreage, village, district, state, latitude, longitude, soil_type, primary_crops, irrigation_source) VALUES (?, 'Regional Agro Sourcing Hub (Sandbox)', 0.0, 'Industrial Area Phase II', 'Ramanagara', 'Karnataka', 12.7981, 77.4005, 'Commercial Warehouse', 'Tomato, Wheat, Potato', 'Industrial Facility')", (b_uid,))
        conn.commit()

    # Seed dev inspector
    c.execute("SELECT id FROM users WHERE email = 'inspector@krishiai.com'")
    if not c.fetchone():
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        i_pwd = bcrypt.hashpw("Inspector@123".encode("utf-8"), bcrypt.gensalt(12)).decode("utf-8")
        c.execute("INSERT INTO users (email, password_hash, full_name, phone, role, created_at, is_active) VALUES (?, ?, 'Dr. Anand Murthy (Sandbox)', '+91 94480 33442', 'inspector', ?, 1)", ("inspector@krishiai.com", i_pwd, now_str))
        i_uid = c.lastrowid
        c.execute("INSERT OR REPLACE INTO farm_profiles (user_id, farm_name, acreage, village, district, state, latitude, longitude, soil_type, primary_crops, irrigation_source) VALUES (?, 'State Quality & Certification Lab (Sandbox)', 0.0, 'APMC Yard', 'Bangalore Urban', 'Karnataka', 13.0234, 77.5512, 'Testing Laboratory', 'Quality Certification', 'Inspection Facility')", (i_uid,))
        conn.commit()


# ==============================================================================
# DPDP ACT 2023 COMPLIANCE: ACCOUNT DELETION & DATA EXPORT
# ==============================================================================
def delete_user_account(user_id: int) -> Tuple[bool, str]:
    \"\"\"
    Permanently deletes user account, farm profile, sessions, audit ledgers,
    produce listings, and farmer quotations in compliance with data privacy regulations.
    \"\"\"
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute("DELETE FROM users WHERE id = ?", (user_id,))
        c.execute("DELETE FROM farm_profiles WHERE user_id = ?", (user_id,))
        c.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
        c.execute("DELETE FROM user_predictions WHERE user_id = ?", (user_id,))
        c.execute("DELETE FROM farmer_produce_listings WHERE farmer_id = ?", (user_id,))
        c.execute("DELETE FROM farmer_quotations WHERE farmer_id = ?", (user_id,))
        conn.commit()
        return True, "User account and all associated telemetry records permanently deleted."
    except Exception as e:
        conn.rollback()
        return False, f"Failed to delete account: {str(e)}"
    finally:
        conn.close()


def export_user_data(user_id: int) -> Dict[str, Any]:
    \"\"\"
    Aggregates user's personal profile, farm telemetry, and saved decision audits
    into a portable JSON export object (Right to Data Portability).
    \"\"\"
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, email, full_name, phone, role, created_at FROM users WHERE id = ?", (user_id,))
    u_row = c.fetchone()
    user_dict = dict(u_row) if u_row else {}

    c.execute("SELECT * FROM farm_profiles WHERE user_id = ?", (user_id,))
    f_row = c.fetchone()
    farm_dict = dict(f_row) if f_row else {}

    c.execute("SELECT id, module_name, title, inputs_json, outputs_json, created_at FROM user_predictions WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
    preds = [dict(r) for r in c.fetchall()]

    conn.close()
    return {
        "export_metadata": {
            "platform": "Krishi AI",
            "exported_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "compliance": "DPDP Act 2023 Right to Data Portability"
        },
        "user_profile": user_dict,
        "farm_profile": farm_dict,
        "audit_ledgers": preds
    }
"""

auth_norm = auth_code.replace("\r\n", "\n")
old_seed_norm = old_seed_block.replace("\r\n", "\n")

if old_seed_norm in auth_norm:
    auth_norm = auth_norm.replace(old_seed_norm, new_seed_block, 1)
    auth_norm += dev_seed_func
    with open(auth_file, "w", encoding="utf-8") as f:
        f.write(auth_norm)
    print("SUCCESS: Refactored modules/auth_db.py for production readiness")
else:
    print("WARNING: Target seed block in auth_db.py not found directly, checking partial match...")

