"""
database.py — SQLite backend for Laboratory Sample Management System
=====================================================================
Handles all database operations: init, CRUD, and search.
"""

import sqlite3
import pandas as pd
from datetime import date, datetime
from pathlib import Path

# ── DB path: sits next to this file ─────────────────────────────────────────
DB_PATH = Path(__file__).parent / "lab_samples.db"


def _get_conn() -> sqlite3.Connection:
    """Return a connection with row_factory set for dict-like access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ── Schema ───────────────────────────────────────────────────────────────────
def init_db() -> None:
    """Create tables if they don't exist and seed demo data if empty."""
    with _get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS samples (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                sample_id       TEXT    NOT NULL UNIQUE,
                business_name   TEXT    NOT NULL,
                submitted_person TEXT   NOT NULL,
                lab_personnel   TEXT    NOT NULL,
                collection_date TEXT    NOT NULL,
                sample_type     TEXT    DEFAULT 'Unspecified',
                sample_stage    TEXT    DEFAULT 'Received',
                remarks         TEXT    DEFAULT '',
                created_at      TEXT    DEFAULT (datetime('now'))
            )
            """
        )
        conn.commit()

        # Seed with demo rows if table is empty
        count = conn.execute("SELECT COUNT(*) FROM samples").fetchone()[0]
        if count == 0:
            _seed_demo_data(conn)


def _seed_demo_data(conn: sqlite3.Connection) -> None:
    """Insert a handful of demo records for immediate dashboard visibility."""
    demo_rows = [
        ("LAB-2024-001", "Acme Pharma Ltd.", "Rajan Mehta",     "Dr. Priya Sharma",  "2024-11-05", "Pharmaceutical", "Analysis Complete", "Batch QC check"),
        ("LAB-2024-002", "AquaSure Testing", "Sunita Rao",       "Mr. Anil Nair",     "2024-11-12", "Water",          "Report Issued",     "Municipal supply sample"),
        ("LAB-2024-003", "GreenEarth Agro",  "Vikram Singh",     "Dr. Priya Sharma",  "2024-11-20", "Soil",           "In Progress",       "Pre-harvest nutrient check"),
        ("LAB-2024-004", "CityBlood Bank",   "Nisha Patel",      "Ms. Kavya Reddy",   "2024-12-01", "Blood",          "Received",          "Cross-match urgent"),
        ("LAB-2024-005", "Acme Pharma Ltd.", "Rajan Mehta",      "Ms. Kavya Reddy",   "2024-12-10", "Chemical",       "In Progress",       "API purity test"),
        ("LAB-2024-006", "FreshBite Foods",  "Arjun Kapoor",     "Mr. Anil Nair",     "2025-01-08", "Food",           "Analysis Complete", "Shelf-life validation"),
        ("LAB-2024-007", "AquaSure Testing", "Sunita Rao",       "Dr. Priya Sharma",  "2025-01-15", "Water",          "Report Issued",     "Industrial effluent"),
        ("LAB-2024-008", "BioLife Diagnostics","Meera Joshi",    "Ms. Kavya Reddy",   "2025-02-03", "Blood",          "Archived",          "Routine CBC panel"),
        ("LAB-2025-001", "GreenEarth Agro",  "Vikram Singh",     "Mr. Anil Nair",     "2025-03-10", "Soil",           "Received",          "New season baseline"),
        ("LAB-2025-002", "FreshBite Foods",  "Arjun Kapoor",     "Dr. Priya Sharma",  "2025-03-18", "Food",           "In Progress",       "Allergen screening"),
    ]
    conn.executemany(
        """
        INSERT OR IGNORE INTO samples
          (sample_id, business_name, submitted_person, lab_personnel,
           collection_date, sample_type, sample_stage, remarks)
        VALUES (?,?,?,?,?,?,?,?)
        """,
        demo_rows,
    )
    conn.commit()


# ── CREATE ───────────────────────────────────────────────────────────────────
def add_sample(
    sample_id: str,
    business_name: str,
    submitted_person: str,
    lab_personnel: str,
    collection_date: str,
    sample_type: str = "Unspecified",
    sample_stage: str = "Received",
    remarks: str = "",
) -> None:
    """Insert a new sample record. Raises sqlite3.IntegrityError on duplicate ID."""
    with _get_conn() as conn:
        conn.execute(
            """
            INSERT INTO samples
              (sample_id, business_name, submitted_person, lab_personnel,
               collection_date, sample_type, sample_stage, remarks)
            VALUES (?,?,?,?,?,?,?,?)
            """,
            (sample_id, business_name, submitted_person, lab_personnel,
             collection_date, sample_type, sample_stage, remarks),
        )
        conn.commit()


# ── READ ─────────────────────────────────────────────────────────────────────
def get_all_samples() -> pd.DataFrame:
    """Return all samples as a DataFrame."""
    with _get_conn() as conn:
        df = pd.read_sql_query(
            "SELECT sample_id, business_name, submitted_person, lab_personnel, "
            "collection_date, sample_type, sample_stage, remarks, created_at "
            "FROM samples ORDER BY collection_date DESC",
            conn,
        )
    return df


def get_sample_by_id(sample_id: str) -> dict | None:
    """Return a single record as a plain dict, or None if not found."""
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM samples WHERE sample_id = ?", (sample_id,)
        ).fetchone()
    return dict(row) if row else None


def sample_id_exists(sample_id: str) -> bool:
    """Check whether a sample_id is already taken."""
    with _get_conn() as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM samples WHERE sample_id = ?", (sample_id,)
        ).fetchone()[0]
    return count > 0


# ── SEARCH ───────────────────────────────────────────────────────────────────
def search_samples(
    sample_id: str = "",
    business_name: str = "",
    submitted_person: str = "",
    stage: str = "",
    date_from: str = "",
    date_to: str = "",
) -> pd.DataFrame:
    """
    Flexible search with optional LIKE filters and date range.
    All parameters are optional; empty string = no filter applied.
    """
    clauses = []
    params: list = []

    if sample_id.strip():
        clauses.append("sample_id LIKE ?")
        params.append(f"%{sample_id.strip()}%")

    if business_name.strip():
        clauses.append("LOWER(business_name) LIKE LOWER(?)")
        params.append(f"%{business_name.strip()}%")

    if submitted_person.strip():
        clauses.append("LOWER(submitted_person) LIKE LOWER(?)")
        params.append(f"%{submitted_person.strip()}%")

    if stage.strip():
        clauses.append("sample_stage = ?")
        params.append(stage.strip())

    if date_from.strip():
        clauses.append("collection_date >= ?")
        params.append(date_from.strip())

    if date_to.strip():
        clauses.append("collection_date <= ?")
        params.append(date_to.strip())

    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""

    query = (
        f"SELECT sample_id, business_name, submitted_person, lab_personnel, "
        f"collection_date, sample_type, sample_stage, remarks "
        f"FROM samples {where} ORDER BY collection_date DESC"
    )

    with _get_conn() as conn:
        df = pd.read_sql_query(query, conn, params=params)
    return df


# ── UPDATE ───────────────────────────────────────────────────────────────────
def update_sample(
    sample_id: str,
    business_name: str,
    submitted_person: str,
    lab_personnel: str,
    collection_date: str,
    sample_type: str,
    sample_stage: str,
    remarks: str,
) -> None:
    """Update mutable fields of an existing record."""
    with _get_conn() as conn:
        conn.execute(
            """
            UPDATE samples SET
                business_name    = ?,
                submitted_person = ?,
                lab_personnel    = ?,
                collection_date  = ?,
                sample_type      = ?,
                sample_stage     = ?,
                remarks          = ?
            WHERE sample_id = ?
            """,
            (business_name, submitted_person, lab_personnel,
             collection_date, sample_type, sample_stage, remarks, sample_id),
        )
        conn.commit()


# ── DELETE ───────────────────────────────────────────────────────────────────
def delete_sample(sample_id: str) -> None:
    """Permanently remove a record by sample_id."""
    with _get_conn() as conn:
        conn.execute("DELETE FROM samples WHERE sample_id = ?", (sample_id,))
        conn.commit()


# ── DASHBOARD STATS ──────────────────────────────────────────────────────────
def get_dashboard_stats() -> dict:
    """Return aggregated stats for the dashboard KPI cards."""
    today_str = date.today().isoformat()
    month_str = date.today().strftime("%Y-%m")

    with _get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) FROM samples").fetchone()[0]
        businesses = conn.execute(
            "SELECT COUNT(DISTINCT business_name) FROM samples"
        ).fetchone()[0]
        today_count = conn.execute(
            "SELECT COUNT(*) FROM samples WHERE collection_date = ?", (today_str,)
        ).fetchone()[0]
        month_count = conn.execute(
            "SELECT COUNT(*) FROM samples WHERE collection_date LIKE ?",
            (f"{month_str}%",),
        ).fetchone()[0]

    return {
        "total": total,
        "businesses": businesses,
        "today": today_count,
        "this_month": month_count,
    }
