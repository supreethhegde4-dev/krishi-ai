import os

target_file = os.path.join(os.path.dirname(__file__), "..", "modules", "auth_db.py")

with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

target = "    conn.close()\n\n\ndef check_rate_limit"
addition = """    # Ensure Demo Inspector Account exists
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

    conn.close()


def check_rate_limit"""

content_norm = content.replace("\r\n", "\n")
if target in content_norm:
    content_norm = content_norm.replace(target, addition, 1)
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(content_norm)
    print("SUCCESSFULLY PATCHED auth_db.py")
else:
    print("TARGET NOT FOUND")
