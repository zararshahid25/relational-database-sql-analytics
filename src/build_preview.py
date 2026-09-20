"""Execute the SQL project in SQLite and build a portfolio summary image."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import pandas as pd
import seaborn as sns


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = PROJECT_ROOT / "sql"
ASSETS_DIR = PROJECT_ROOT / "assets"
REPORTS_DIR = PROJECT_ROOT / "reports"

NAVY, PURPLE, BLUE, GREEN, GOLD, MUTED = "#25324A", "#6750A4", "#4C78A8", "#4C9A74", "#D6A542", "#667085"


def build_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys = ON")
    for filename in ["01_schema.sql", "02_seed_data.sql", "03_views.sql"]:
        connection.executescript((SQL_DIR / filename).read_text(encoding="utf-8"))
    return connection


def card(fig: plt.Figure, x: float, title: str, value: str) -> None:
    fig.patches.append(
        FancyBboxPatch(
            (x, 0.80), 0.17, 0.085,
            boxstyle="round,pad=0.008,rounding_size=0.01",
            transform=fig.transFigure, facecolor="white", edgecolor="#DFE3EA", linewidth=1,
        )
    )
    fig.text(x + 0.013, 0.852, title, color=MUTED, fontsize=9)
    fig.text(x + 0.013, 0.817, value, color=NAVY, fontsize=16, weight="bold")


def main() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    connection = build_connection()

    students = connection.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    applications = connection.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
    employers = connection.execute("SELECT COUNT(*) FROM employers").fetchone()[0]
    placed = connection.execute("SELECT COUNT(DISTINCT student_id) FROM applications WHERE final_outcome='Offered'").fetchone()[0]
    placement_rate = 100 * placed / students
    avg_match = connection.execute("SELECT AVG(mandatory_skill_match_pct) FROM vw_candidate_job_match").fetchone()[0]

    department = pd.read_sql_query(
        "SELECT department_name, placement_rate_pct FROM vw_department_placement ORDER BY placement_rate_pct DESC",
        connection,
    )
    funnel = pd.read_sql_query(
        "SELECT application_stage, COUNT(*) AS applications FROM applications GROUP BY application_stage",
        connection,
    )
    employer = pd.read_sql_query(
        "SELECT employer_name, applications, offer_rate_pct FROM vw_application_funnel WHERE applications > 0 ORDER BY offer_rate_pct DESC LIMIT 8",
        connection,
    )
    skill = pd.read_sql_query(
        """
        SELECT s.skill_name, COUNT(*) AS mandatory_job_requirements
        FROM job_skills js
        JOIN skills s ON s.skill_id = js.skill_id
        WHERE js.is_mandatory = TRUE
        GROUP BY s.skill_name
        ORDER BY mandatory_job_requirements DESC, s.skill_name
        LIMIT 10
        """,
        connection,
    )
    department.to_csv(REPORTS_DIR / "department_placement.csv", index=False)
    funnel.to_csv(REPORTS_DIR / "application_funnel.csv", index=False)
    employer.to_csv(REPORTS_DIR / "employer_offer_rates.csv", index=False)
    skill.to_csv(REPORTS_DIR / "mandatory_skill_demand.csv", index=False)

    sns.set_theme(style="whitegrid")
    fig = plt.figure(figsize=(16, 11), facecolor="#F5F6F9")
    grid = fig.add_gridspec(3, 2, left=0.06, right=0.96, bottom=0.07, top=0.71, hspace=0.78, wspace=0.28)
    fig.text(0.06, 0.95, "SkillBridge Relational Database & SQL Analytics", color=NAVY, fontsize=24, weight="bold")
    fig.text(0.06, 0.918, "Normalised training and placement system · PostgreSQL · synthetic academic data", color=MUTED, fontsize=11)
    for i, (title, value) in enumerate(
        [
            ("Students", f"{students:,}"),
            ("Applications", f"{applications:,}"),
            ("Employers", f"{employers:,}"),
            ("Students with offer", f"{placed:,}"),
            ("Placement rate", f"{placement_rate:.1f}%"),
        ]
    ):
        card(fig, 0.06 + i * 0.182, title, value)

    ax1 = fig.add_subplot(grid[0, 0])
    d = department.sort_values("placement_rate_pct")
    ax1.barh(d["department_name"], d["placement_rate_pct"], color=PURPLE)
    ax1.set_title("Placement rate by department", loc="left", color=NAVY, weight="bold")
    ax1.set_xlabel("Students with offer (%)")
    ax1.set_ylabel("")

    ax2 = fig.add_subplot(grid[0, 1])
    funnel_order = ["Applied", "Screening", "Interview", "Offer"]
    f = funnel.set_index("application_stage").reindex(funnel_order).fillna(0)
    ax2.bar(f.index, f["applications"], color=[BLUE, PURPLE, GOLD, GREEN])
    ax2.set_title("Applications by current stage", loc="left", color=NAVY, weight="bold")
    ax2.set_ylabel("Applications")

    ax3 = fig.add_subplot(grid[1, 0])
    e = employer.sort_values("offer_rate_pct")
    ax3.barh(e["employer_name"], e["offer_rate_pct"], color=GREEN)
    ax3.set_title("Top employer offer rates", loc="left", color=NAVY, weight="bold")
    ax3.set_xlabel("Offer rate (%)")
    ax3.set_ylabel("")

    ax4 = fig.add_subplot(grid[1, 1])
    s = skill.sort_values("mandatory_job_requirements")
    ax4.barh(s["skill_name"], s["mandatory_job_requirements"], color=GOLD)
    ax4.set_title("Most requested mandatory skills", loc="left", color=NAVY, weight="bold")
    ax4.set_xlabel("Job requirements")
    ax4.set_ylabel("")

    ax5 = fig.add_subplot(grid[2, :])
    ax5.axis("off")
    ax5.set_title("Normalised database model", loc="left", color=NAVY, weight="bold", pad=14)
    groups = [
        (0.02, "Academic", "departments → students"),
        (0.22, "Skills", "skills ↔ student_skills\nskills ↔ job_skills"),
        (0.46, "Recruitment", "employers → jobs → applications → interviews"),
        (0.73, "Training", "training_courses ↔ course_enrollments"),
    ]
    for x, heading, detail in groups:
        width = 0.23 if heading == "Recruitment" else 0.18
        ax5.add_patch(FancyBboxPatch((x, 0.25), width, 0.50, boxstyle="round,pad=0.02,rounding_size=0.03", facecolor="white", edgecolor="#D9DFE8", linewidth=1.2))
        ax5.text(x + 0.015, 0.61, heading, color=PURPLE, fontsize=12, weight="bold")
        ax5.text(x + 0.015, 0.42, detail, color=MUTED, fontsize=10, va="center")
    ax5.text(0.02, 0.08, f"11 tables · 12 foreign keys · 3 many-to-many bridge tables · average mandatory-skill match {avg_match:.1f}%", color=MUTED, fontsize=10)

    for axis in [ax1, ax2, ax3, ax4]:
        axis.set_facecolor("white")
        axis.grid(axis="x" if axis in [ax1, ax3, ax4] else "y", color="#E7EAF0", linewidth=0.8)
        axis.spines[["top", "right", "left"]].set_visible(False)
        axis.tick_params(colors=MUTED)

    fig.text(0.06, 0.018, "Analytics use joins, grouped aggregations, correlated subqueries, CTEs, and window functions. All records are synthetic.", color=MUTED, fontsize=9)
    fig.savefig(ASSETS_DIR / "skillbridge_sql_analytics.jpg", dpi=110, bbox_inches="tight", facecolor=fig.get_facecolor(), pil_kwargs={"quality": 92})
    plt.close(fig)
    connection.close()
    print("Executed the schema and built the SQL analytics preview.")


if __name__ == "__main__":
    main()

