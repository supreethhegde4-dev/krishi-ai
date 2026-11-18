"""
Krishi AI – Production Neon PostgreSQL Migration Script
Applies complete relational schema and migrates non-demo application records.
Uses DATABASE_URL_UNPOOLED for direct schema migrations.
"""
import os
import sys
import sqlite3
import psycopg
from psycopg.rows import dict_row

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SQLITE_PATH = os.path.join(PROJECT_ROOT, "data", "krishi_ai.db")

POSTGRES_SCHEMA_DDL = """
-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    role VARCHAR(50) NOT NULL DEFAULT 'farmer',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMPTZ,
    is_active INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- 2. Farmer Profiles Table
CREATE TABLE IF NOT EXISTS farm_profiles (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    farm_name VARCHAR(255) NOT NULL,
    acreage DOUBLE PRECISION NOT NULL DEFAULT 2.5,
    village VARCHAR(255) NOT NULL,
    district VARCHAR(255) NOT NULL,
    state VARCHAR(255) NOT NULL,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    soil_type VARCHAR(255) NOT NULL DEFAULT 'Red Sandy Loam',
    primary_crops VARCHAR(255) NOT NULL DEFAULT 'Tomato, Maize',
    irrigation_source VARCHAR(255) NOT NULL DEFAULT 'Borewell / Drip'
);
CREATE INDEX IF NOT EXISTS idx_farm_profiles_district ON farm_profiles(district, state);

-- 3. Sessions Table
CREATE TABLE IF NOT EXISTS sessions (
    token VARCHAR(255) PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMPTZ NOT NULL,
    is_persistent INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);

-- 4. Login Attempts Table
CREATE TABLE IF NOT EXISTS login_attempts (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    attempt_time TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    success INTEGER NOT NULL,
    ip VARCHAR(100)
);
CREATE INDEX IF NOT EXISTS idx_login_attempts_email ON login_attempts(email, attempt_time);

-- 5. Password Resets Table
CREATE TABLE IF NOT EXISTS password_resets (
    token VARCHAR(255) PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMPTZ NOT NULL,
    used INTEGER NOT NULL DEFAULT 0
);

-- 6. User Predictions Table
CREATE TABLE IF NOT EXISTS user_predictions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    module_name VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    inputs_json TEXT NOT NULL,
    outputs_json TEXT NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_predictions_user ON user_predictions(user_id, module_name);

-- 7. Institutional Buyers Table
CREATE TABLE IF NOT EXISTS buyers (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    company_name VARCHAR(255) NOT NULL,
    business_type VARCHAR(100) NOT NULL,
    contact_person VARCHAR(255) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL,
    facility_address TEXT NOT NULL,
    district VARCHAR(255) NOT NULL,
    state VARCHAR(255) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    verified_status INTEGER NOT NULL DEFAULT 1,
    rating DOUBLE PRECISION NOT NULL DEFAULT 4.8,
    total_deals_completed INTEGER NOT NULL DEFAULT 10,
    payment_terms VARCHAR(255) NOT NULL DEFAULT 'Within 24 Hours of Delivery / Quality Check',
    gstin VARCHAR(100),
    apmc_license VARCHAR(100),
    verified_by INTEGER,
    verification_remarks TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_buyers_district ON buyers(district, state);

-- 8. Buyer Procurement Requirements Table
CREATE TABLE IF NOT EXISTS buyer_requirements (
    id SERIAL PRIMARY KEY,
    buyer_id INTEGER NOT NULL REFERENCES buyers(id) ON DELETE CASCADE,
    crop VARCHAR(100) NOT NULL,
    quantity_quintals DOUBLE PRECISION NOT NULL,
    min_quality_grade VARCHAR(100) NOT NULL,
    offered_price_per_quintal DOUBLE PRECISION NOT NULL,
    delivery_location VARCHAR(255) NOT NULL,
    delivery_district VARCHAR(255) NOT NULL,
    delivery_state VARCHAR(255) NOT NULL,
    delivery_lat DOUBLE PRECISION NOT NULL,
    delivery_lon DOUBLE PRECISION NOT NULL,
    required_by_date VARCHAR(50) NOT NULL,
    additional_specs TEXT,
    urgency_level VARCHAR(50) NOT NULL DEFAULT 'Standard',
    status VARCHAR(50) NOT NULL DEFAULT 'OPEN',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_buyer_requirements_crop ON buyer_requirements(crop, status);

-- 9. Farmer Produce Listings Table
CREATE TABLE IF NOT EXISTS farmer_produce_listings (
    id SERIAL PRIMARY KEY,
    farmer_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    farmer_name VARCHAR(255) NOT NULL,
    farmer_phone VARCHAR(50) NOT NULL,
    crop VARCHAR(100) NOT NULL,
    variety VARCHAR(100) NOT NULL,
    quantity_quintals DOUBLE PRECISION NOT NULL,
    expected_price_per_quintal DOUBLE PRECISION NOT NULL,
    quality_grade VARCHAR(50) NOT NULL,
    harvest_date VARCHAR(50) NOT NULL,
    village VARCHAR(255) NOT NULL,
    district VARCHAR(255) NOT NULL,
    state VARCHAR(255) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    notes TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_farmer_listings_crop ON farmer_produce_listings(crop, status);

-- 10. Farmer Quotations Table
CREATE TABLE IF NOT EXISTS farmer_quotations (
    id SERIAL PRIMARY KEY,
    requirement_id INTEGER NOT NULL REFERENCES buyer_requirements(id) ON DELETE CASCADE,
    farmer_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    farmer_name VARCHAR(255) NOT NULL,
    farmer_phone VARCHAR(50) NOT NULL,
    crop VARCHAR(100) NOT NULL,
    offered_quantity_quintals DOUBLE PRECISION NOT NULL,
    quoted_price_per_quintal DOUBLE PRECISION NOT NULL,
    offered_grade VARCHAR(50) NOT NULL,
    dispatch_location VARCHAR(255) NOT NULL,
    dispatch_district VARCHAR(255) NOT NULL,
    dispatch_state VARCHAR(255) NOT NULL,
    dispatch_lat DOUBLE PRECISION NOT NULL,
    dispatch_lon DOUBLE PRECISION NOT NULL,
    expected_delivery_date VARCHAR(50) NOT NULL,
    farmer_notes TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    counter_price_per_quintal DOUBLE PRECISION,
    buyer_feedback TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 11. Crop Inspections Table
CREATE TABLE IF NOT EXISTS crop_inspections (
    id SERIAL PRIMARY KEY,
    batch_ref VARCHAR(100) UNIQUE NOT NULL,
    farmer_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    farmer_name VARCHAR(255) NOT NULL,
    crop VARCHAR(100) NOT NULL,
    quantity_quintals DOUBLE PRECISION NOT NULL,
    ai_grade VARCHAR(50) NOT NULL,
    ai_confidence DOUBLE PRECISION NOT NULL,
    ai_damage_notes TEXT,
    inspector_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    inspector_name VARCHAR(255),
    inspector_grade VARCHAR(50),
    brix_reading DOUBLE PRECISION,
    size_caliper_mm DOUBLE PRECISION,
    defect_percent DOUBLE PRECISION,
    inspection_notes TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'AI_ASSESSED',
    certificate_hash VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    verified_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_inspections_batch ON crop_inspections(batch_ref);

-- 12. Trade Transactions Table
CREATE TABLE IF NOT EXISTS trade_transactions (
    id SERIAL PRIMARY KEY,
    quotation_id INTEGER,
    farmer_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    farmer_name VARCHAR(255) NOT NULL,
    buyer_id INTEGER NOT NULL REFERENCES buyers(id) ON DELETE CASCADE,
    buyer_name VARCHAR(255) NOT NULL,
    crop VARCHAR(100) NOT NULL,
    farmer_weight_kg DOUBLE PRECISION NOT NULL,
    weighbridge_weight_kg DOUBLE PRECISION NOT NULL,
    weight_discrepancy_kg DOUBLE PRECISION NOT NULL,
    agreed_rate_per_kg DOUBLE PRECISION NOT NULL,
    paid_rate_per_kg DOUBLE PRECISION NOT NULL,
    deductions_amount DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    deduction_reason TEXT,
    payment_received DOUBLE PRECISION NOT NULL,
    total_agreed_amount DOUBLE PRECISION NOT NULL,
    payment_status VARCHAR(50) NOT NULL DEFAULT 'PAID',
    risk_level VARCHAR(50) NOT NULL DEFAULT 'LOW',
    weighbridge_slip_ref VARCHAR(100),
    payment_slip_ref VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 13. Transaction Disputes Table
CREATE TABLE IF NOT EXISTS transaction_disputes (
    id SERIAL PRIMARY KEY,
    transaction_id INTEGER NOT NULL REFERENCES trade_transactions(id) ON DELETE CASCADE,
    farmer_id INTEGER NOT NULL,
    buyer_id INTEGER NOT NULL,
    dispute_type VARCHAR(100) NOT NULL,
    claimed_loss_amount DOUBLE PRECISION NOT NULL,
    dispute_statement TEXT NOT NULL,
    evidence_file TEXT,
    resolution_status VARCHAR(50) NOT NULL DEFAULT 'FILED',
    admin_notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 14. Audit Logs Table
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    action VARCHAR(255) NOT NULL,
    ip_address VARCHAR(100),
    details_json TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_id, created_at);
"""

def load_connection_url():
    for key in ["DATABASE_URL_UNPOOLED", "DATABASE_URL"]:
        if os.environ.get(key):
            return os.environ.get(key)
    for fname in [".env.local", ".env"]:
        fpath = os.path.join(PROJECT_ROOT, fname)
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("DATABASE_URL_UNPOOLED="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
            with open(fpath, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("DATABASE_URL="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None

def main():
    pg_url = load_connection_url()
    if not pg_url:
        print("[ERROR] Could not resolve Neon connection URL.")
        sys.exit(1)

    print("\n" + "="*60)
    print("KRISHI AI – NEON POSTGRESQL PRODUCTION MIGRATION")
    print("="*60)

    # 1. Connect and Apply Schema
    print("[Step 1] Applying complete PostgreSQL relational schema DDL to Neon...")
    with psycopg.connect(pg_url, row_factory=dict_row) as pg_conn:
        with pg_conn.cursor() as pg_cur:
            pg_cur.execute(POSTGRES_SCHEMA_DDL)
            pg_conn.commit()
            print("  [OK] Created 14 production tables and indexes.")

    # 2. Inspect SQLite Source
    print("\n[Step 2] Auditing SQLite local database tables & record counts...")
    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    sqlite_conn.row_factory = sqlite3.Row
    sq_cur = sqlite_conn.cursor()

    table_list = [
        "users", "farm_profiles", "buyers", "buyer_requirements",
        "farmer_produce_listings", "farmer_quotations", "crop_inspections",
        "trade_transactions", "transaction_disputes", "user_predictions"
    ]

    sqlite_counts = {}
    for tbl in table_list:
        try:
            sq_cur.execute(f"SELECT COUNT(*) FROM {tbl};")
            sqlite_counts[tbl] = sq_cur.fetchone()[0]
        except Exception:
            sqlite_counts[tbl] = 0

    for tbl, count in sqlite_counts.items():
        print(f"  • SQLite {tbl}: {count} records")

    # 3. Migrate Data
    print("\n[Step 3] Migrating verified application records into Neon PostgreSQL...")
    with psycopg.connect(pg_url, row_factory=dict_row) as pg_conn:
        with pg_conn.cursor() as pg_cur:
            # Users
            sq_cur.execute("SELECT * FROM users ORDER BY id;")
            users = sq_cur.fetchall()
            for u in users:
                pg_cur.execute("""
                    INSERT INTO users (id, email, password_hash, full_name, phone, role, created_at, last_login, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING;
                """, (u["id"], u["email"], u["password_hash"], u["full_name"], u["phone"], u["role"], u["created_at"], u["last_login"], u["is_active"]))
            
            # Farm Profiles
            sq_cur.execute("SELECT * FROM farm_profiles ORDER BY user_id;")
            fps = sq_cur.fetchall()
            for fp in fps:
                pg_cur.execute("""
                    INSERT INTO farm_profiles (user_id, farm_name, acreage, village, district, state, latitude, longitude, soil_type, primary_crops, irrigation_source)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (user_id) DO NOTHING;
                """, (fp["user_id"], fp["farm_name"], fp["acreage"], fp["village"], fp["district"], fp["state"], fp["latitude"], fp["longitude"], fp["soil_type"], fp["primary_crops"], fp["irrigation_source"]))

            # Buyers
            sq_cur.execute("SELECT * FROM buyers ORDER BY id;")
            buyers = [dict(b) for b in sq_cur.fetchall()]
            for b in buyers:
                pg_cur.execute("""
                    INSERT INTO buyers (id, user_id, company_name, business_type, contact_person, phone, email, facility_address, district, state, latitude, longitude, verified_status, rating, total_deals_completed, payment_terms, gstin, apmc_license, verified_by, verification_remarks, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING;
                """, (b["id"], b["user_id"], b["company_name"], b["business_type"], b["contact_person"], b["phone"], b["email"], b["facility_address"], b["district"], b["state"], b["latitude"], b["longitude"], b["verified_status"], b["rating"], b["total_deals_completed"], b["payment_terms"], b.get("gstin"), b.get("apmc_license"), b.get("verified_by"), b.get("verification_remarks"), b["created_at"]))

            # Buyer Requirements
            sq_cur.execute("SELECT * FROM buyer_requirements ORDER BY id;")
            reqs = [dict(r) for r in sq_cur.fetchall()]
            for r in reqs:
                pg_cur.execute("""
                    INSERT INTO buyer_requirements (id, buyer_id, crop, quantity_quintals, min_quality_grade, offered_price_per_quintal, delivery_location, delivery_district, delivery_state, delivery_lat, delivery_lon, required_by_date, additional_specs, urgency_level, status, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING;
                """, (r["id"], r["buyer_id"], r["crop"], r["quantity_quintals"], r["min_quality_grade"], r["offered_price_per_quintal"], r["delivery_location"], r["delivery_district"], r["delivery_state"], r["delivery_lat"], r["delivery_lon"], r["required_by_date"], r["additional_specs"], r["urgency_level"], r["status"], r["created_at"]))

            # Farmer Listings
            sq_cur.execute("SELECT * FROM farmer_produce_listings ORDER BY id;")
            listings = [dict(l) for l in sq_cur.fetchall()]
            for l in listings:
                pg_cur.execute("""
                    INSERT INTO farmer_produce_listings (id, farmer_id, farmer_name, farmer_phone, crop, variety, quantity_quintals, expected_price_per_quintal, quality_grade, harvest_date, village, district, state, latitude, longitude, notes, status, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING;
                """, (l["id"], l["farmer_id"], l["farmer_name"], l["farmer_phone"], l["crop"], l["variety"], l["quantity_quintals"], l["expected_price_per_quintal"], l["quality_grade"], l["harvest_date"], l["village"], l["district"], l["state"], l["latitude"], l["longitude"], l["notes"], l["status"], l["created_at"]))

            # Farmer Quotations
            sq_cur.execute("SELECT * FROM farmer_quotations ORDER BY id;")
            quots = [dict(q) for q in sq_cur.fetchall()]
            for q in quots:
                pg_cur.execute("""
                    INSERT INTO farmer_quotations (id, requirement_id, farmer_id, farmer_name, farmer_phone, crop, offered_quantity_quintals, quoted_price_per_quintal, offered_grade, dispatch_location, dispatch_district, dispatch_state, dispatch_lat, dispatch_lon, expected_delivery_date, farmer_notes, status, counter_price_per_quintal, buyer_feedback, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING;
                """, (q["id"], q["requirement_id"], q["farmer_id"], q["farmer_name"], q["farmer_phone"], q["crop"], q["offered_quantity_quintals"], q["quoted_price_per_quintal"], q["offered_grade"], q["dispatch_location"], q["dispatch_district"], q["dispatch_state"], q["dispatch_lat"], q["dispatch_lon"], q["expected_delivery_date"], q["farmer_notes"], q["status"], q["counter_price_per_quintal"], q["buyer_feedback"], q["created_at"], q["updated_at"]))

            # Crop Inspections
            sq_cur.execute("SELECT * FROM crop_inspections ORDER BY id;")
            insps = [dict(i) for i in sq_cur.fetchall()]
            for i in insps:
                pg_cur.execute("""
                    INSERT INTO crop_inspections (id, batch_ref, farmer_id, farmer_name, crop, quantity_quintals, ai_grade, ai_confidence, ai_damage_notes, inspector_id, inspector_name, inspector_grade, brix_reading, size_caliper_mm, defect_percent, inspection_notes, status, certificate_hash, created_at, verified_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING;
                """, (i["id"], i["batch_ref"], i["farmer_id"], i["farmer_name"], i["crop"], i["quantity_quintals"], i["ai_grade"], i["ai_confidence"], i["ai_damage_notes"], i["inspector_id"], i["inspector_name"], i["inspector_grade"], i["brix_reading"], i["size_caliper_mm"], i["defect_percent"], i["inspection_notes"], i["status"], i["certificate_hash"], i["created_at"], i["verified_at"]))

            # User Predictions
            sq_cur.execute("SELECT * FROM user_predictions ORDER BY id;")
            preds = [dict(p) for p in sq_cur.fetchall()]
            for p in preds:
                pg_cur.execute("""
                    INSERT INTO user_predictions (id, user_id, module_name, title, inputs_json, outputs_json, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING;
                """, (p["id"], p["user_id"], p["module_name"], p["title"], p["inputs_json"], p["outputs_json"], p["created_at"]))

            # Sessions
            sq_cur.execute("SELECT * FROM sessions;")
            sess = [dict(s) for s in sq_cur.fetchall()]
            for s in sess:
                pg_cur.execute("""
                    INSERT INTO sessions (token, user_id, created_at, expires_at, is_persistent)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (token) DO NOTHING;
                """, (s["token"], s["user_id"], s["created_at"], s["expires_at"], s["is_persistent"]))

            # Synchronize PostgreSQL Serial Sequences
            serial_tables = [
                ("users", "id"), ("buyers", "id"), ("buyer_requirements", "id"),
                ("farmer_produce_listings", "id"), ("farmer_quotations", "id"),
                ("crop_inspections", "id"), ("user_predictions", "id"),
                ("trade_transactions", "id"), ("transaction_disputes", "id"),
                ("login_attempts", "id"), ("audit_logs", "id")
            ]
            for tbl, pk in serial_tables:
                pg_cur.execute(f"""
                    SELECT setval(pg_get_serial_sequence('{tbl}', '{pk}'), COALESCE(MAX({pk}), 1))
                    FROM {tbl};
                """)

            pg_conn.commit()
            print("  [OK] Data migration and sequence synchronization complete.")

    # 4. Compare Row Counts
    print("\n[Step 4] Row Count Comparison (SQLite vs Neon PostgreSQL):")
    neon_counts = {}
    with psycopg.connect(pg_url, row_factory=dict_row) as pg_conn:
        with pg_conn.cursor() as pg_cur:
            for tbl in table_list:
                pg_cur.execute(f"SELECT COUNT(*) as cnt FROM {tbl};")
                neon_counts[tbl] = pg_cur.fetchone()["cnt"]

    print(f"{'Table Name':<28} | {'SQLite Rows':<12} | {'Neon Rows':<12} | {'Status'}")
    print("-" * 65)
    for tbl in table_list:
        sq_cnt = sqlite_counts.get(tbl, 0)
        ne_cnt = neon_counts.get(tbl, 0)
        match = "MATCHED" if sq_cnt == ne_cnt else "DIFF"
        print(f"{tbl:<28} | {sq_cnt:<12} | {ne_cnt:<12} | {match}")
    print("="*60)

if __name__ == "__main__":
    main()
