"""
Database Production Integrity, Backup & Disaster Recovery Module for Krishi AI.
Provides:
1. SQLite PRAGMA integrity and foreign key validation
2. Automated hot backups to disk or cloud volume
3. Disaster recovery restore workflows
4. PostgreSQL / Remote Database migration schema export
"""
import os
import shutil
import sqlite3
import datetime
from typing import Dict, Any, Tuple, List

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "krishi_ai.db")
BACKUP_DIR = os.path.join(PROJECT_ROOT, "data", "backups")


def verify_database_integrity() -> Dict[str, Any]:
    """
    Executes SQLite internal integrity checks, foreign key constraint checks,
    and returns database file size and index coverage.
    """
    if not os.path.exists(DB_PATH):
        return {"status": "ERROR", "message": f"Database file {DB_PATH} not found."}

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 1. Integrity check
    c.execute("PRAGMA integrity_check")
    integrity_rows = c.fetchall()
    is_healthy = len(integrity_rows) == 1 and integrity_rows[0][0] == "ok"

    # 2. Foreign key check
    c.execute("PRAGMA foreign_key_check")
    fk_violations = c.fetchall()

    # 3. Table counts
    tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    table_stats = {}
    for t in tables:
        cnt = c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        table_stats[t] = cnt

    # 4. Indexes
    indexes = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='index'").fetchall()]

    conn.close()

    db_size_kb = os.path.getsize(DB_PATH) / 1024.0

    return {
        "status": "HEALTHY" if is_healthy and len(fk_violations) == 0 else "WARNING",
        "integrity_check": "ok" if is_healthy else str(integrity_rows),
        "foreign_key_violations": len(fk_violations),
        "db_size_kb": round(db_size_kb, 1),
        "table_count": len(tables),
        "index_count": len(indexes),
        "tables": table_stats
    }


def backup_database() -> Tuple[bool, str, Optional[str]]:
    """
    Performs an atomic online backup of SQLite database using sqlite3 backup API.
    Saves snapshot to data/backups/krishi_ai_backup_YYYYMMDD_HHMMSS.db.
    """
    if not os.path.exists(DB_PATH):
        return False, "Database file does not exist.", None

    os.makedirs(BACKUP_DIR, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"krishi_ai_backup_{ts}.db")

    try:
        source_conn = sqlite3.connect(DB_PATH)
        dest_conn = sqlite3.connect(backup_file)
        with dest_conn:
            source_conn.backup(dest_conn, pages=100)
        dest_conn.close()
        source_conn.close()
        return True, f"Online backup successfully created at {backup_file}", backup_file
    except Exception as e:
        return False, f"Backup failed: {str(e)}", None


def restore_database(backup_path: str) -> Tuple[bool, str]:
    """
    Restores the database from a verified backup file after validating its integrity.
    """
    if not os.path.exists(backup_path):
        return False, f"Backup file {backup_path} not found."

    # Validate backup file integrity first
    try:
        test_conn = sqlite3.connect(backup_path)
        c = test_conn.cursor()
        c.execute("PRAGMA integrity_check")
        res = c.fetchone()[0]
        test_conn.close()
        if res != "ok":
            return False, "Target backup file failed SQLite integrity check. Restore aborted."
    except Exception as e:
        return False, f"Cannot read backup file: {str(e)}"

    try:
        shutil.copy2(backup_path, DB_PATH)
        return True, f"Database restored successfully from {backup_path}."
    except Exception as e:
        return False, f"Restore failed: {str(e)}"
