"""
Authentication, User Isolation, and Database Management for Krishi AI.
Uses SQLite (data/krishi_ai.db) with bcrypt password hashing,
session management, brute force throttling, and farmer data isolation.
"""
import os
import sqlite3
import bcrypt
import secrets
import datetime
from typing import Optional, Dict, Any, List, Tuple

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "krishi_ai.db")


def get_db_connection() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes tables and seeds default accounts if not present."""
    conn = get_db_connection()
    c = conn.cursor()

    # Users Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        phone TEXT,
        role TEXT NOT NULL DEFAULT 'farmer',
        created_at TEXT NOT NULL,
        last_login TEXT,
        is_active INTEGER NOT NULL DEFAULT 1
    )
    """)

    # Farm Profiles (Data Isolation per User)
    c.execute("""
    CREATE TABLE IF NOT EXISTS farm_profiles (
        user_id INTEGER PRIMARY KEY,
        farm_name TEXT NOT NULL,
        acreage REAL NOT NULL DEFAULT 2.5,
        village TEXT NOT NULL,
        district TEXT NOT NULL,
        state TEXT NOT NULL,
        latitude REAL,
        longitude REAL,
        soil_type TEXT NOT NULL DEFAULT 'Red Sandy Loam',
        primary_crops TEXT NOT NULL DEFAULT 'Tomato, Maize',
        irrigation_source TEXT NOT NULL DEFAULT 'Borewell / Drip',
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    """)

    # Sessions Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        token TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        created_at TEXT NOT NULL,
        expires_at TEXT NOT NULL,
        is_persistent INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    """)

    # Login Attempts (Rate Limiting)
    c.execute("""
    CREATE TABLE IF NOT EXISTS login_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        attempt_time TEXT NOT NULL,
        success INTEGER NOT NULL,
        ip TEXT
    )
    """)

    # Password Reset Tokens
    c.execute("""
    CREATE TABLE IF NOT EXISTS password_resets (
        token TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        created_at TEXT NOT NULL,
        expires_at TEXT NOT NULL,
        used INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    """)

    # User Saved Predictions & Reports (Isolated per user)
    c.execute("""
    CREATE TABLE IF NOT EXISTS user_predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        module_name TEXT NOT NULL,
        title TEXT NOT NULL,
        inputs_json TEXT NOT NULL,
        outputs_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    """)

    conn.commit()

    # Seed Default Farmer & Admin if database is empty
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        # 1. Default Farmer Account
        farmer_pwd_hash = bcrypt.hashpw("Password@123".encode("utf-8"), bcrypt.gensalt(12)).decode("utf-8")
        c.execute("""
        INSERT INTO users (email, password_hash, full_name, phone, role, created_at, is_active)
        VALUES (?, ?, ?, ?, ?, ?, 1)
        """, ("farmer@krishiai.com", farmer_pwd_hash, "Ramesh Gowda", "+91 98450 12345", "farmer", now_str))
        farmer_id = c.lastrowid
        
        c.execute("""
        INSERT INTO farm_profiles (user_id, farm_name, acreage, village, district, state, latitude, longitude, soil_type, primary_crops, irrigation_source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (farmer_id, "Green Valley Agro Farm", 3.5, "Ramanagara Rural", "Ramanagara", "Karnataka", 12.7209, 77.2799, "Red Sandy Loam", "Tomato, Maize, Banana", "Borewell Drip Irrigation"))

        # 2. Default Admin Account
        admin_pwd_hash = bcrypt.hashpw("Admin@123".encode("utf-8"), bcrypt.gensalt(12)).decode("utf-8")
        c.execute("""
        INSERT INTO users (email, password_hash, full_name, phone, role, created_at, is_active)
        VALUES (?, ?, ?, ?, ?, ?, 1)
        """, ("admin@krishiai.com", admin_pwd_hash, "Krishi System Administrator", "+91 98800 54321", "admin", now_str))
        admin_id = c.lastrowid
        
        c.execute("""
        INSERT INTO farm_profiles (user_id, farm_name, acreage, village, district, state, latitude, longitude, soil_type, primary_crops, irrigation_source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (admin_id, "Central Agricultural Research Station", 10.0, "GKVK Campus", "Bangalore Urban", "Karnataka", 13.0768, 77.5753, "Clay Loam", "All Research Crops", "Canal & Micro-Sprinkler"))

        conn.commit()

    # Ensure Demo Buyer Account exists
    c.execute("SELECT id FROM users WHERE email = 'buyer@krishiai.com'")
    buyer_row = c.fetchone()
    if not buyer_row:
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        buyer_pwd_hash = bcrypt.hashpw("Password@123".encode("utf-8"), bcrypt.gensalt(12)).decode("utf-8")
        c.execute("""
        INSERT INTO users (email, password_hash, full_name, phone, role, created_at, is_active)
        VALUES (?, ?, ?, ?, 'buyer', ?, 1)
        """, ("buyer@krishiai.com", buyer_pwd_hash, "Vikramaditya Rao", "+91 98451 22334", now_str))
        b_uid = c.lastrowid
        c.execute("""
        INSERT OR REPLACE INTO farm_profiles (user_id, farm_name, acreage, village, district, state, latitude, longitude, soil_type, primary_crops, irrigation_source)
        VALUES (?, 'ITC Procurement & Sourcing Center', 0.0, 'Bidadi Industrial Area Phase II', 'Ramanagara', 'Karnataka', 12.7981, 77.4005, 'Industrial Agro Hub', 'Tomato, Wheat, Potato', 'Industrial Borewell')
        """, (b_uid,))
        # Link user_id to ITC in buyers table if exists
        try:
            c.execute("UPDATE buyers SET user_id = ? WHERE company_name LIKE '%ITC Agri%'", (b_uid,))
        except Exception:
            pass
        conn.commit()

    conn.close()


def check_rate_limit(email: str, max_failures: int = 5, window_minutes: int = 10) -> Tuple[bool, int]:
    """
    Checks if login attempts for this email exceed failure threshold within time window.
    Returns (is_throttled, seconds_remaining).
    """
    conn = get_db_connection()
    c = conn.cursor()
    cutoff = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=window_minutes)).isoformat()
    
    c.execute("""
    SELECT attempt_time FROM login_attempts
    WHERE email = ? AND success = 0 AND attempt_time > ?
    ORDER BY attempt_time DESC
    """, (email.lower().strip(), cutoff))
    failures = c.fetchall()
    conn.close()
    
    if len(failures) >= max_failures:
        oldest_failure = datetime.datetime.fromisoformat(failures[-1][0])
        elapsed = (datetime.datetime.now(datetime.timezone.utc) - oldest_failure).total_seconds()
        remaining = max(1, int(window_minutes * 60 - elapsed))
        return True, remaining
    return False, 0


def log_login_attempt(email: str, success: bool, ip: str = "127.0.0.1"):
    conn = get_db_connection()
    c = conn.cursor()
    now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
    c.execute("INSERT INTO login_attempts (email, attempt_time, success, ip) VALUES (?, ?, ?, ?)",
              (email.lower().strip(), now_str, 1 if success else 0, ip))
    conn.commit()
    conn.close()


def register_user(full_name: str, email: str, password: str, phone: Optional[str] = None, role: str = "farmer") -> Tuple[bool, str]:
    """Registers a new user after validation."""
    clean_email = email.lower().strip()
    clean_name = full_name.strip()
    
    if not clean_name:
        return False, "Full Name is required."
    if "@" not in clean_email or "." not in clean_email.split("@")[-1]:
        return False, "Please provide a valid email address."
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not any(c.isupper() for c in password) or not any(c.isdigit() for c in password):
        return False, "Password must include at least one uppercase letter and one number."

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE email = ?", (clean_email,))
    if c.fetchone():
        conn.close()
        return False, "An account with this email already exists."

    pwd_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(12)).decode("utf-8")
    now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()

    try:
        c.execute("""
        INSERT INTO users (email, password_hash, full_name, phone, role, created_at, is_active)
        VALUES (?, ?, ?, ?, ?, ?, 1)
        """, (clean_email, pwd_hash, clean_name, phone.strip() if phone else None, role, now_str))
        user_id = c.lastrowid

        # Create initial farm profile
        c.execute("""
        INSERT INTO farm_profiles (user_id, farm_name, acreage, village, district, state, latitude, longitude, soil_type, primary_crops, irrigation_source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, f"{clean_name}'s Farm", 2.0, "Ramanagara", "Ramanagara", "Karnataka", 12.7209, 77.2799, "Red Loam", "Tomato", "Borewell"))
        conn.commit()
        conn.close()
        return True, "Account created successfully! You can now sign in."
    except Exception as e:
        conn.close()
        return False, "Registration failed due to a system error. Please try again."


def authenticate_user(email: str, password: str, remember_me: bool = False, ip: str = "127.0.0.1") -> Tuple[bool, str, Optional[str], Optional[Dict[str, Any]]]:
    """
    Authenticates user, checks rate limiting, and issues a session token.
    Returns (success, message, token, user_dict).
    """
    clean_email = email.lower().strip()
    is_throttled, rem_sec = check_rate_limit(clean_email)
    if is_throttled:
        return False, f"Too many failed login attempts. Please wait {rem_sec} seconds before retrying.", None, None

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (clean_email,))
    user = c.fetchone()

    if not user or not user["is_active"]:
        log_login_attempt(clean_email, success=False, ip=ip)
        conn.close()
        return False, "Invalid email or password.", None, None

    # Verify password with bcrypt
    try:
        is_valid = bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8"))
    except Exception:
        is_valid = False

    if not is_valid:
        log_login_attempt(clean_email, success=False, ip=ip)
        conn.close()
        return False, "Invalid email or password.", None, None

    # Success: log attempt & create session token
    log_login_attempt(clean_email, success=True, ip=ip)
    now_dt = datetime.datetime.now(datetime.timezone.utc)
    now_str = now_dt.isoformat()
    c.execute("UPDATE users SET last_login = ? WHERE id = ?", (now_str, user["id"]))

    duration_days = 30 if remember_me else 1
    expires_dt = now_dt + datetime.timedelta(days=duration_days)
    token = secrets.token_hex(32)

    c.execute("""
    INSERT INTO sessions (token, user_id, created_at, expires_at, is_persistent)
    VALUES (?, ?, ?, ?, ?)
    """, (token, user["id"], now_str, expires_dt.isoformat(), 1 if remember_me else 0))
    conn.commit()

    # Get farm profile
    c.execute("SELECT * FROM farm_profiles WHERE user_id = ?", (user["id"],))
    farm = c.fetchone()
    conn.close()

    user_dict = {
        "id": user["id"],
        "email": user["email"],
        "full_name": user["full_name"],
        "phone": user["phone"],
        "role": user["role"],
        "farm": dict(farm) if farm else {}
    }
    return True, "Authentication successful.", token, user_dict


def get_user_by_session_token(token: str) -> Optional[Dict[str, Any]]:
    """Validates session token and returns isolated user profile."""
    if not token:
        return None
    conn = get_db_connection()
    c = conn.cursor()
    now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()

    c.execute("""
    SELECT s.user_id, s.expires_at, u.email, u.full_name, u.phone, u.role, u.is_active
    FROM sessions s
    JOIN users u ON s.user_id = u.id
    WHERE s.token = ? AND s.expires_at > ? AND u.is_active = 1
    """, (token, now_str))
    res = c.fetchone()
    if not res:
        conn.close()
        return None

    # Fetch farm profile
    c.execute("SELECT * FROM farm_profiles WHERE user_id = ?", (res["user_id"],))
    farm = c.fetchone()
    conn.close()

    return {
        "id": res["user_id"],
        "email": res["email"],
        "full_name": res["full_name"],
        "phone": res["phone"],
        "role": res["role"],
        "farm": dict(farm) if farm else {}
    }


def invalidate_session(token: str):
    """Logs out by removing session token."""
    if not token:
        return
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM sessions WHERE token = ?", (token,))
    conn.commit()
    conn.close()


def create_password_reset_token(email: str) -> Tuple[bool, str, Optional[str]]:
    """Creates a 30-minute single-use password reset token."""
    clean_email = email.lower().strip()
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE email = ? AND is_active = 1", (clean_email,))
    user = c.fetchone()
    if not user:
        conn.close()
        return False, "If this email exists in our records, a reset link has been generated.", None

    token = secrets.token_urlsafe(32)
    now_dt = datetime.datetime.now(datetime.timezone.utc)
    expires_dt = now_dt + datetime.timedelta(minutes=30)

    c.execute("""
    INSERT INTO password_resets (token, user_id, created_at, expires_at, used)
    VALUES (?, ?, ?, ?, 0)
    """, (token, user["id"], now_dt.isoformat(), expires_dt.isoformat()))
    conn.commit()
    conn.close()
    return True, "Password reset token generated.", token


def reset_password_with_token(token: str, new_password: str) -> Tuple[bool, str]:
    if len(new_password) < 8:
        return False, "Password must be at least 8 characters long."
    if not any(c.isupper() for c in new_password) or not any(c.isdigit() for c in new_password):
        return False, "Password must include at least one uppercase letter and one number."

    conn = get_db_connection()
    c = conn.cursor()
    now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()

    c.execute("""
    SELECT user_id FROM password_resets
    WHERE token = ? AND used = 0 AND expires_at > ?
    """, (token, now_str))
    res = c.fetchone()
    if not res:
        conn.close()
        return False, "This password reset token is invalid or has expired."

    user_id = res["user_id"]
    new_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt(12)).decode("utf-8")

    c.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user_id))
    c.execute("UPDATE password_resets SET used = 1 WHERE token = ?", (token,))
    c.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))  # Log out all sessions
    conn.commit()
    conn.close()
    return True, "Password reset successful! You can now log in with your new password."


def change_user_password(user_id: int, current_password: str, new_password: str) -> Tuple[bool, str]:
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return False, "User not found."

    if not bcrypt.checkpw(current_password.encode("utf-8"), row["password_hash"].encode("utf-8")):
        conn.close()
        return False, "Current password is incorrect."

    if len(new_password) < 8 or not any(c.isupper() for c in new_password) or not any(c.isdigit() for c in new_password):
        conn.close()
        return False, "New password must be at least 8 chars with an uppercase letter and a number."

    new_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt(12)).decode("utf-8")
    c.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user_id))
    conn.commit()
    conn.close()
    return True, "Password changed successfully."


def update_farm_profile(user_id: int, farm_data: Dict[str, Any]) -> Tuple[bool, str]:
    """Updates farm details for the isolated user."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
    UPDATE farm_profiles
    SET farm_name = ?, acreage = ?, village = ?, district = ?, state = ?,
        latitude = ?, longitude = ?, soil_type = ?, primary_crops = ?, irrigation_source = ?
    WHERE user_id = ?
    """, (
        farm_data.get("farm_name", "My Farm"),
        float(farm_data.get("acreage", 2.5)),
        farm_data.get("village", "Ramanagara"),
        farm_data.get("district", "Ramanagara"),
        farm_data.get("state", "Karnataka"),
        float(farm_data.get("latitude", 12.7209)),
        float(farm_data.get("longitude", 77.2799)),
        farm_data.get("soil_type", "Red Loam"),
        farm_data.get("primary_crops", "Tomato"),
        farm_data.get("irrigation_source", "Borewell Drip"),
        user_id
    ))
    conn.commit()
    conn.close()
    return True, "Farm profile updated successfully."


def save_user_prediction(user_id: int, module_name: str, title: str, inputs_json: str, outputs_json: str) -> int:
    """Saves a prediction/report isolated strictly to the authenticated user."""
    conn = get_db_connection()
    c = conn.cursor()
    now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
    c.execute("""
    INSERT INTO user_predictions (user_id, module_name, title, inputs_json, outputs_json, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, module_name, title, inputs_json, outputs_json, now_str))
    pred_id = c.lastrowid
    conn.commit()
    conn.close()
    return pred_id


def get_user_predictions(user_id: int, module_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """Returns only predictions belonging to this user (Data Isolation)."""
    conn = get_db_connection()
    c = conn.cursor()
    if module_name:
        c.execute("""
        SELECT * FROM user_predictions
        WHERE user_id = ? AND module_name = ?
        ORDER BY id DESC
        """, (user_id, module_name))
    else:
        c.execute("""
        SELECT * FROM user_predictions
        WHERE user_id = ?
        ORDER BY id DESC
        """, (user_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


# Ensure database initialized on import
init_db()
