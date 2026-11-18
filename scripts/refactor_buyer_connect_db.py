import os

target_file = "modules/buyer_connect_db.py"
with open(target_file, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update buyers table creation to include gstin and apmc_license if not present
old_create_buyers = """    # 1. Registered Buyers & Industries
    c.execute(\"\"\"
    CREATE TABLE IF NOT EXISTS buyers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        company_name TEXT NOT NULL,
        business_type TEXT NOT NULL,
        contact_person TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT NOT NULL,
        facility_address TEXT NOT NULL,
        district TEXT NOT NULL,
        state TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        verified_status INTEGER NOT NULL DEFAULT 1,
        rating REAL NOT NULL DEFAULT 4.8,
        total_deals_completed INTEGER NOT NULL DEFAULT 10,
        payment_terms TEXT NOT NULL DEFAULT 'Within 24 Hours of Delivery / Quality Check',
        created_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
    )
    \"\"\")"""

new_create_buyers = """    # 1. Registered Buyers & Industries (Production Schema)
    c.execute(\"\"\"
    CREATE TABLE IF NOT EXISTS buyers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        company_name TEXT NOT NULL,
        business_type TEXT NOT NULL,
        contact_person TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT NOT NULL,
        facility_address TEXT NOT NULL,
        district TEXT NOT NULL,
        state TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        gstin TEXT,
        apmc_license TEXT,
        verified_status INTEGER NOT NULL DEFAULT 0,
        verified_by INTEGER,
        verification_remarks TEXT,
        rating REAL NOT NULL DEFAULT 5.0,
        total_deals_completed INTEGER NOT NULL DEFAULT 0,
        payment_terms TEXT NOT NULL DEFAULT 'Within 24 Hours of Delivery / Gate Weighbridge Clearance',
        created_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL,
        FOREIGN KEY (verified_by) REFERENCES users (id) ON DELETE SET NULL
    )
    \"\"\")"""

code_norm = code.replace("\r\n", "\n")
old_buyers_norm = old_create_buyers.replace("\r\n", "\n")
new_buyers_norm = new_create_buyers.replace("\r\n", "\n")

if old_buyers_norm in code_norm:
    code_norm = code_norm.replace(old_buyers_norm, new_buyers_norm, 1)

# 2. Make seed_verified_buyers_and_requirements only run when KRISHI_ENV == 'development'
old_init_end = """    conn.commit()
    seed_verified_buyers_and_requirements(conn)
    conn.close()"""

new_init_end = """    conn.commit()
    active_env = os.environ.get("KRISHI_ENV", "production").lower()
    if active_env == "development":
        seed_development_sandbox_buyers(conn)
    conn.close()"""

old_init_end_norm = old_init_end.replace("\r\n", "\n")
new_init_end_norm = new_init_end.replace("\r\n", "\n")

if old_init_end_norm in code_norm:
    code_norm = code_norm.replace(old_init_end_norm, new_init_end_norm, 1)

# Replace the brand names in seed function with generic sandbox entities
old_seed_fn_header = "def seed_verified_buyers_and_requirements(conn: sqlite3.Connection):"
new_seed_fn = """def seed_development_sandbox_buyers(conn: sqlite3.Connection):
    \"\"\"
    Seeds generic demonstration buyer profiles ONLY in development mode.
    Does NOT use unauthorized real commercial brand names.
    \"\"\"
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM buyers")
    if c.fetchone()[0] > 0:
        return

    now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
    sample_buyers = [
        (
            1, "Apex Agro-Processing Hub (Sandbox)", "Food Processing & Milling",
            "S. Kulkarni (Test)", "+91 98451 00001", "procure@apexagro-test.in",
            "Bidadi Industrial Complex Phase II",
            "Ramanagara", "Karnataka", 12.7981, 77.4005, "29AABCU9603R1ZM", "APMC-KAR-9821", 1, 4.9, 12,
            "100% Direct Bank Transfer within 24h of Gate Inspection", now_str
        ),
        (
            None, "Southern Wholesale Cold Chain (Sandbox)", "Wholesale & Aggregator Chain",
            "P. Nair (Test)", "+91 97410 00002", "procure@southerncold-test.in",
            "Mysore Road Agro Hub, Kengeri",
            "Bangalore Urban", "Karnataka", 12.9121, 77.4833, "29AABCS1234F1ZX", "APMC-BLR-4512", 1, 4.8, 8,
            "Immediate payment on weighbridge receipt + quality clearance", now_str
        ),
        (
            None, "Deccan Organic Millers (Sandbox)", "Organic Cereals & Pulses",
            "R. Kumar (Test)", "+91 99002 00003", "sourcing@deccanorganic-test.in",
            "Tiptur Highway Industrial Park",
            "Tumakuru", "Karnataka", 13.2584, 76.4789, "29AABCO5566G1ZQ", "APMC-TUM-3310", 1, 4.9, 5,
            "Weekly settlement with premium organic certification bonus", now_str
        )
    ]
    for b in sample_buyers:
        c.execute(\"\"\"
        INSERT INTO buyers (
            user_id, company_name, business_type, contact_person, phone, email,
            facility_address, district, state, latitude, longitude, gstin, apmc_license,
            verified_status, rating, total_deals_completed, payment_terms, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        \"\"\", b)
    conn.commit()"""

if old_seed_fn_header in code_norm:
    # Find end of old seed function
    idx = code_norm.find(old_seed_fn_header)
    end_idx = code_norm.find("# ==============================================================================", idx)
    if end_idx != -1:
        code_norm = code_norm[:idx] + new_seed_fn + "\n\n" + code_norm[end_idx:]

# Add buyer registration and verification functions
new_buyer_methods = """

# ==============================================================================
# REAL PRODUCTION BUYER REGISTRATION & VERIFICATION WORKFLOW
# ==============================================================================
def register_buyer_profile(
    user_id: int,
    company_name: str,
    business_type: str,
    contact_person: str,
    phone: str,
    email: str,
    facility_address: str,
    district: str,
    state: str,
    latitude: float,
    longitude: float,
    gstin: str,
    apmc_license: Optional[str] = None,
    payment_terms: str = "Immediate Bank Transfer on Weighbridge Clearance"
) -> Tuple[bool, str, Optional[int]]:
    \"\"\"
    Registers a genuine commercial buyer profile in pending verification state (0).
    Requires valid GSTIN / APMC License for compliance auditing.
    \"\"\"
    clean_gst = gstin.strip().upper()
    if len(clean_gst) < 10:
        return False, "A valid GSTIN or Business Identification Number is required for buyer registration.", None

    conn = get_db_connection()
    c = conn.cursor()
    now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        c.execute(\"\"\"
        INSERT INTO buyers (
            user_id, company_name, business_type, contact_person, phone, email,
            facility_address, district, state, latitude, longitude, gstin, apmc_license,
            verified_status, rating, total_deals_completed, payment_terms, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 5.0, 0, ?, ?)
        \"\"\", (
            user_id, company_name.strip(), business_type, contact_person.strip(),
            phone.strip(), email.strip().lower(), facility_address.strip(),
            district.strip(), state.strip(), latitude, longitude, clean_gst,
            apmc_license.strip() if apmc_license else None, payment_terms, now_str
        ))
        conn.commit()
        return True, "Buyer profile registered successfully. Awaiting administrative license verification.", c.lastrowid
    except Exception as e:
        conn.rollback()
        return False, f"Failed to register buyer profile: {str(e)}", None
    finally:
        conn.close()


def verify_buyer_account(
    buyer_id: int,
    admin_id: int,
    remarks: str = "Verified official GSTIN and APMC market license."
) -> Tuple[bool, str]:
    \"\"\"
    Grants official verified status (1) to a registered buyer after regulatory due diligence.
    \"\"\"
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute(\"\"\"
        UPDATE buyers
        SET verified_status = 1,
            verified_by = ?,
            verification_remarks = ?
        WHERE id = ?
        \"\"\", (admin_id, remarks, buyer_id))
        conn.commit()
        return True, f"Buyer #{buyer_id} verified successfully."
    except Exception as e:
        conn.rollback()
        return False, f"Verification failed: {str(e)}"
    finally:
        conn.close()
"""

if "def register_buyer_profile" not in code_norm:
    code_norm += new_buyer_methods

with open(target_file, "w", encoding="utf-8") as f:
    f.write(code_norm)

print("SUCCESS: Refactored modules/buyer_connect_db.py for production readiness")
