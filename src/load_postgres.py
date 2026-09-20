"""Create and populate the SkillBridge PostgreSQL database."""

from __future__ import annotations

import os
from pathlib import Path

import psycopg


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = PROJECT_ROOT / "sql"


def main() -> None:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("Set DATABASE_URL before loading PostgreSQL.")
    scripts = ["01_schema.sql", "02_seed_data.sql", "03_views.sql"]
    with psycopg.connect(database_url, autocommit=True) as connection:
        with connection.cursor() as cursor:
            for filename in scripts:
                cursor.execute((SQL_DIR / filename).read_text(encoding="utf-8"))
    print("Created and populated the SkillBridge PostgreSQL database.")


if __name__ == "__main__":
    main()

