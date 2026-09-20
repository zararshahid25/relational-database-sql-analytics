from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
import sqlglot


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = PROJECT_ROOT / "sql"


@pytest.fixture()
def database() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys = ON")
    for filename in ["01_schema.sql", "02_seed_data.sql", "03_views.sql"]:
        connection.executescript((SQL_DIR / filename).read_text(encoding="utf-8"))
    yield connection
    connection.close()


def test_all_sql_files_parse_in_postgres_dialect() -> None:
    for path in sorted(SQL_DIR.glob("*.sql")):
        statements = sqlglot.parse(path.read_text(encoding="utf-8"), read="postgres")
        assert statements
        assert all(statement is not None for statement in statements)


def test_seed_counts_and_orphan_checks(database: sqlite3.Connection) -> None:
    assert database.execute("SELECT COUNT(*) FROM students").fetchone()[0] == 150
    assert database.execute("SELECT COUNT(*) FROM employers").fetchone()[0] == 12
    assert database.execute("SELECT COUNT(*) FROM job_postings").fetchone()[0] == 28
    assert database.execute("SELECT COUNT(*) FROM applications").fetchone()[0] > 400
    assert database.execute(
        "SELECT COUNT(*) FROM applications a LEFT JOIN students s ON s.student_id=a.student_id WHERE s.student_id IS NULL"
    ).fetchone()[0] == 0


def test_constraints_reject_duplicate_bridge_and_invalid_cgpa(database: sqlite3.Connection) -> None:
    row = database.execute("SELECT student_id, skill_id, proficiency_level, assessed_date FROM student_skills LIMIT 1").fetchone()
    with pytest.raises(sqlite3.IntegrityError):
        database.execute("INSERT INTO student_skills VALUES (?, ?, ?, ?)", row)
    with pytest.raises(sqlite3.IntegrityError):
        database.execute(
            "INSERT INTO students VALUES (999, 'TEST-999', 'Invalid Student', 'invalid@example.com', 1, 2026, 4.5)"
        )


def test_required_views_return_valid_rates(database: sqlite3.Connection) -> None:
    departments = database.execute("SELECT COUNT(*) FROM vw_department_placement").fetchone()[0]
    offer_rates = [row[0] for row in database.execute("SELECT offer_rate_pct FROM vw_application_funnel WHERE applications > 0")]
    match_rates = [row[0] for row in database.execute("SELECT mandatory_skill_match_pct FROM vw_candidate_job_match")]
    assert departments == 6
    assert all(0 <= value <= 100 for value in offer_rates)
    assert all(0 <= value <= 100 for value in match_rates)


def test_question_set_executes_and_reserved_jobs_have_no_applications(database: sqlite3.Connection) -> None:
    statements = [
        statement.sql(dialect="sqlite")
        for statement in sqlglot.parse((SQL_DIR / "04_question_set.sql").read_text(encoding="utf-8"), read="postgres")
    ]
    for statement in statements:
        database.execute(statement).fetchmany(5)
    no_application_jobs = database.execute(
        "SELECT COUNT(*) FROM job_postings j LEFT JOIN applications a ON a.job_id=j.job_id WHERE a.application_id IS NULL"
    ).fetchone()[0]
    assert no_application_jobs == 2

