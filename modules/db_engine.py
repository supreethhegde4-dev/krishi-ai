"""
Krishi AI – Multi-Database Persistent Production Engine
Supports:
1. Cloud PostgreSQL (Neon, Supabase, AWS RDS) via DATABASE_URL
2. Local High-Performance SQLite (with WAL journaling and foreign keys) as development/offline fallback

Provides unified connection pooling, schema migrations, health monitoring,
and transaction safety for all platform modules.
"""
import os
import sys
import time
import json
import sqlite3
import datetime
from typing import Dict, Any, List, Optional, Tuple
from contextlib import contextmanager

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_SQLITE_PATH = os.path.join(PROJECT_ROOT, "data", "krishi_ai.db")

def get_database_url() -> Optional[str]:
    """Retrieves DATABASE_URL from environment or .env file."""
    val = os.environ.get("DATABASE_URL")
    if val and val.strip():
        return val.strip()

    env_path = os.path.join(PROJECT_ROOT, ".env")
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("DATABASE_URL="):
                        v = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if v:
                            return v
        except Exception:
            pass
    return None


def is_postgres_configured() -> bool:
    db_url = get_database_url()
    return bool(db_url and (db_url.startswith("postgres://") or db_url.startswith("postgresql://")))


# Initialize Global SQLAlchemy Engine if PostgreSQL is configured
_PG_ENGINE = None

if is_postgres_configured():
    try:
        from sqlalchemy import create_engine
        raw_url = get_database_url()
        # SQLAlchemy requires postgresql:// instead of postgres://
        if raw_url.startswith("postgres://"):
            raw_url = "postgresql://" + raw_url[len("postgres://"):]
        _PG_ENGINE = create_engine(
            raw_url,
            pool_size=5,
            max_overflow=10,
            pool_recycle=1800,
            pool_pre_ping=True
        )
    except Exception as e:
        print(f"[Warning] Failed to initialize PostgreSQL engine: {e}. Falling back to SQLite.")
        _PG_ENGINE = None


class DictRow(dict):
    """Provides both dictionary and index-based access to mimic sqlite3.Row."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._keys = list(self.keys())

    def __getitem__(self, key):
        if isinstance(key, int):
            return super().__getitem__(self._keys[key])
        return super().__getitem__(key)


@contextmanager
def get_db_cursor():
    """
    Context manager that yields a cursor and connection, automatically committing transactions.
    Works transparently across PostgreSQL and SQLite.
    """
    if _PG_ENGINE is not None:
        import psycopg2
        import psycopg2.extras
        conn = _PG_ENGINE.raw_connection()
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            yield cursor, conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()
    else:
        os.makedirs(os.path.dirname(DEFAULT_SQLITE_PATH), exist_ok=True)
        conn = sqlite3.connect(DEFAULT_SQLITE_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        try:
            cursor = conn.cursor()
            yield cursor, conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()


def execute_query(query: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
    """
    Executes a SELECT query and returns rows as dictionaries.
    Translates '?' parameter syntax to '%s' when running on PostgreSQL.
    """
    if params is None:
        params = ()

    with get_db_cursor() as (cur, conn):
        if _PG_ENGINE is not None:
            # PostgreSQL uses %s
            pg_query = query.replace("?", "%s")
            cur.execute(pg_query, params)
            rows = cur.fetchall()
            return [dict(r) for r in rows]
        else:
            cur.execute(query, params)
            rows = cur.fetchall()
            return [dict(r) for r in rows]


def execute_update(query: str, params: Optional[Tuple] = None) -> int:
    """
    Executes an INSERT, UPDATE, or DELETE query and returns lastrowid or affected rows.
    """
    if params is None:
        params = ()

    with get_db_cursor() as (cur, conn):
        if _PG_ENGINE is not None:
            pg_query = query.replace("?", "%s")
            cur.execute(pg_query, params)
            return cur.rowcount
        else:
            cur.execute(query, params)
            return cur.lastrowid or cur.rowcount


def check_database_health() -> Dict[str, Any]:
    """
    Comprehensive Database Health & Persistence Telemetry.
    """
    t0 = time.time()
    db_type = "PostgreSQL (Cloud Persistent - Neon/Supabase)" if _PG_ENGINE is not None else "SQLite (Local Embedded)"
    try:
        with get_db_cursor() as (cur, conn):
            if _PG_ENGINE is not None:
                cur.execute("SELECT 1;")
            else:
                cur.execute("PRAGMA integrity_check;")
                res = cur.fetchone()
                if res and res[0] != "ok":
                    raise RuntimeError(f"SQLite PRAGMA integrity check failed: {res[0]}")

        latency_ms = round((time.time() - t0) * 1000.0, 2)
        
        # Get table row counts
        counts = {}
        for tbl in ["users", "farmer_profiles", "buyers", "crop_inspections", "buyer_requirements", "quotations", "transactions"]:
            try:
                rows = execute_query(f"SELECT COUNT(*) as cnt FROM {tbl};")
                counts[tbl] = rows[0]["cnt"] if rows else 0
            except Exception:
                counts[tbl] = 0

        return {
            "status": "HEALTHY",
            "database_type": db_type,
            "is_persistent_cloud": _PG_ENGINE is not None,
            "latency_ms": latency_ms,
            "storage_path": get_database_url() if _PG_ENGINE else DEFAULT_SQLITE_PATH,
            "table_record_counts": counts,
            "ephemeral_warning": (_PG_ENGINE is None)
        }
    except Exception as e:
        return {
            "status": "UNHEALTHY",
            "database_type": db_type,
            "is_persistent_cloud": _PG_ENGINE is not None,
            "error": str(e),
            "ephemeral_warning": True
        }
