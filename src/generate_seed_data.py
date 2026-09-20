"""Generate deterministic SQL INSERT statements and CSV seed tables."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd


SEED = 2026
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = PROJECT_ROOT / "data" / "seed"
SQL_PATH = PROJECT_ROOT / "sql" / "02_seed_data.sql"


def sql_literal(value: object) -> str:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "NULL"
    if isinstance(value, (bool, np.bool_)):
        return "TRUE" if value else "FALSE"
    if isinstance(value, (int, np.integer)):
        return str(int(value))
    if isinstance(value, (float, np.floating)):
        return f"{float(value):.2f}"
    if isinstance(value, (pd.Timestamp, date)):
        return f"'{pd.Timestamp(value):%Y-%m-%d}'"
    return "'" + str(value).replace("'", "''") + "'"


def insert_statement(table: str, frame: pd.DataFrame) -> str:
    columns = ", ".join(frame.columns)
    rows = ["(" + ", ".join(sql_literal(value) for value in row) + ")" for row in frame.itertuples(index=False, name=None)]
    return f"INSERT INTO {table} ({columns}) VALUES\n  " + ",\n  ".join(rows) + ";\n"


def build_tables() -> dict[str, pd.DataFrame]:
    rng = np.random.default_rng(SEED)
    departments = pd.DataFrame(
        enumerate(
            ["Computer Engineering", "Software Engineering", "Electrical Engineering", "Mechanical Engineering", "Civil Engineering", "Business Analytics"],
            start=1,
        ),
        columns=["department_id", "department_name"],
    )
    skills_data = [
        (1, "Python", "Technical"), (2, "SQL", "Technical"), (3, "Excel", "Analytics"),
        (4, "Power BI", "Analytics"), (5, "Data Visualisation", "Analytics"),
        (6, "Machine Learning", "Technical"), (7, "REST APIs", "Technical"),
        (8, "PostgreSQL", "Technical"), (9, "Git", "Technical"), (10, "Docker", "Technical"),
        (11, "Project Management", "Professional"), (12, "Communication", "Professional"),
        (13, "Problem Solving", "Professional"), (14, "AutoCAD", "Engineering"),
        (15, "Circuit Design", "Engineering"), (16, "Embedded Systems", "Engineering"),
        (17, "Financial Analysis", "Business"), (18, "Market Research", "Business"),
        (19, "Cloud Fundamentals", "Technical"), (20, "Technical Writing", "Professional"),
    ]
    skills = pd.DataFrame(skills_data, columns=["skill_id", "skill_name", "skill_category"])
    employer_names = [
        "Nova Analytics", "ByteCraft Labs", "Axis Engineering", "Crescent Logistics",
        "Vertex Solutions", "Indus Retail", "Cloud Harbor", "Nexus Health Systems",
        "MetroBuild", "Orion Energy", "DataSpring", "TechBridge Consulting",
    ]
    employers = pd.DataFrame(
        {
            "employer_id": range(1, 13),
            "employer_name": employer_names,
            "sector": ["Technology", "Software", "Engineering", "Logistics", "Consulting", "Retail", "Cloud Services", "Healthcare IT", "Construction", "Energy", "Analytics", "Consulting"],
            "city": ["Islamabad", "Rawalpindi", "Taxila", "Islamabad", "Lahore", "Rawalpindi", "Islamabad", "Rawalpindi", "Islamabad", "Lahore", "Islamabad", "Rawalpindi"],
        }
    )

    first_names = ["Ali", "Ayesha", "Bilal", "Fatima", "Hassan", "Hira", "Omar", "Sara", "Zain", "Noor", "Hamza", "Maham"]
    last_names = ["Khan", "Ahmed", "Shah", "Malik", "Iqbal", "Raza", "Abbasi", "Siddiqui", "Hussain", "Mir"]
    student_rows = []
    for student_id in range(1, 151):
        department_id = int(rng.integers(1, 7))
        name = f"{rng.choice(first_names)} {rng.choice(last_names)} {student_id}"
        student_rows.append(
            (
                student_id,
                f"UET-{2021 + (student_id % 3)}-{student_id:04d}",
                name,
                f"student{student_id:03d}@skillbridge.example",
                department_id,
                int(rng.choice([2025, 2026], p=[0.46, 0.54])),
                round(float(np.clip(rng.normal(3.05, 0.42), 2.0, 3.95)), 2),
            )
        )
    students = pd.DataFrame(
        student_rows,
        columns=["student_id", "registration_no", "full_name", "email", "department_id", "graduation_year", "cgpa"],
    )

    student_skill_rows = []
    for student_id in students["student_id"]:
        chosen = rng.choice(skills["skill_id"], int(rng.integers(3, 8)), replace=False)
        for skill_id in chosen:
            student_skill_rows.append(
                (student_id, int(skill_id), int(rng.integers(2, 6)), date(2025, 1, 1) + timedelta(days=int(rng.integers(0, 330))))
            )
    student_skills = pd.DataFrame(student_skill_rows, columns=["student_id", "skill_id", "proficiency_level", "assessed_date"])

    title_pool = [
        "Junior Data Analyst", "Graduate Software Engineer", "MIS Reporting Associate",
        "Backend Engineering Intern", "Operations Analyst", "Embedded Systems Trainee",
        "Business Intelligence Intern", "Project Coordinator", "Cloud Support Associate",
        "Junior Design Engineer", "Research Assistant", "Quality Analyst",
    ]
    job_rows = []
    for job_id in range(1, 29):
        posted = date(2025, 1, 5) + timedelta(days=int(rng.integers(0, 170)))
        job_rows.append(
            (
                job_id,
                int(rng.integers(1, 13)),
                f"{rng.choice(title_pool)} {job_id}",
                rng.choice(["Internship", "Graduate Role", "Contract"], p=[0.36, 0.52, 0.12]),
                round(float(rng.uniform(2.3, 3.35)), 2),
                posted,
                posted + timedelta(days=int(rng.integers(20, 46))),
                int(rng.integers(1, 6)),
            )
        )
    jobs = pd.DataFrame(job_rows, columns=["job_id", "employer_id", "job_title", "employment_type", "min_cgpa", "posted_date", "closing_date", "openings"])

    job_skill_rows = []
    for job_id in jobs["job_id"]:
        chosen = rng.choice(skills["skill_id"], int(rng.integers(4, 8)), replace=False)
        for idx, skill_id in enumerate(chosen):
            job_skill_rows.append((job_id, int(skill_id), int(rng.integers(2, 5)), bool(idx < 3)))
    job_skills = pd.DataFrame(job_skill_rows, columns=["job_id", "skill_id", "required_level", "is_mandatory"])

    application_rows = []
    used: set[tuple[int, int]] = set()
    application_id = 1
    for student in students.itertuples(index=False):
        # Reserve the final two postings so the "jobs with no applications" query has a valid result.
        for job_id in rng.choice(jobs["job_id"].iloc[:-2], int(rng.integers(2, 6)), replace=False):
            key = (int(job_id), int(student.student_id))
            if key in used:
                continue
            used.add(key)
            job = jobs.loc[jobs["job_id"] == job_id].iloc[0]
            applied = pd.Timestamp(job["posted_date"]) + pd.Timedelta(days=int(rng.integers(0, 18)))
            outcome = rng.choice(["Pending", "Rejected", "Withdrawn", "Offered"], p=[0.25, 0.53, 0.08, 0.14])
            if outcome == "Offered":
                stage = "Offer"
            elif outcome == "Rejected":
                stage = rng.choice(["Screening", "Interview"], p=[0.65, 0.35])
            elif outcome == "Withdrawn":
                stage = rng.choice(["Applied", "Screening"])
            else:
                stage = rng.choice(["Applied", "Screening", "Interview"])
            application_rows.append((application_id, int(job_id), int(student.student_id), applied.date(), stage, outcome))
            application_id += 1
    applications = pd.DataFrame(application_rows, columns=["application_id", "job_id", "student_id", "applied_date", "application_stage", "final_outcome"])

    interview_rows = []
    interview_id = 1
    for application in applications[applications["application_stage"].isin(["Interview", "Offer"])].itertuples(index=False):
        rounds = 2 if application.application_stage == "Offer" else 1
        for round_number in range(1, rounds + 1):
            offered = application.final_outcome == "Offered"
            score = round(float(np.clip(rng.normal(78 if offered else 61, 10), 30, 98)), 1)
            result = "Pass" if (offered or score >= 70) else "Fail"
            interview_rows.append(
                (
                    interview_id, application.application_id, round_number,
                    "Technical" if round_number == 1 else "HR and Culture",
                    pd.Timestamp(application.applied_date).date() + timedelta(days=7 * round_number), score, result,
                )
            )
            interview_id += 1
    interviews = pd.DataFrame(interview_rows, columns=["interview_id", "application_id", "round_number", "interview_type", "interview_date", "score", "result"])

    course_titles = ["Applied SQL", "Python for Analytics", "Power BI Reporting", "Professional Communication", "Git and Collaboration", "Cloud Fundamentals", "Project Management Essentials", "Excel for Business"]
    course_skill_ids = [2, 1, 4, 12, 9, 19, 11, 3]
    courses = pd.DataFrame(
        {
            "course_id": range(1, 9),
            "course_title": course_titles,
            "provider": ["SkillBridge Academy"] * 8,
            "start_date": [date(2025, 2, 1) + timedelta(days=35 * i) for i in range(8)],
            "end_date": [date(2025, 2, 28) + timedelta(days=35 * i) for i in range(8)],
            "skill_id": course_skill_ids,
        }
    )
    enrollment_rows = []
    for student_id in students["student_id"]:
        for course_id in rng.choice(courses["course_id"], int(rng.integers(1, 4)), replace=False):
            status = rng.choice(["Completed", "In Progress", "Dropped"], p=[0.70, 0.22, 0.08])
            score = round(float(np.clip(rng.normal(78, 11), 45, 100)), 1) if status == "Completed" else None
            enrollment_rows.append((int(course_id), int(student_id), status, score))
    enrollments = pd.DataFrame(enrollment_rows, columns=["course_id", "student_id", "completion_status", "final_score"])

    return {
        "departments": departments,
        "students": students,
        "employers": employers,
        "skills": skills,
        "student_skills": student_skills,
        "job_postings": jobs,
        "job_skills": job_skills,
        "applications": applications,
        "interviews": interviews,
        "training_courses": courses,
        "course_enrollments": enrollments,
    }


def main() -> None:
    SEED_DIR.mkdir(parents=True, exist_ok=True)
    tables = build_tables()
    for name, frame in tables.items():
        frame.to_csv(SEED_DIR / f"{name}.csv", index=False)

    dependency_order = [
        "departments", "employers", "skills", "students", "student_skills",
        "job_postings", "job_skills", "applications", "interviews",
        "training_courses", "course_enrollments",
    ]
    sql = ["BEGIN;\n"]
    for table in reversed(dependency_order):
        sql.append(f"DELETE FROM {table};\n")
    for table in dependency_order:
        sql.append(insert_statement(table, tables[table]))
    sql.append("COMMIT;\n")
    SQL_PATH.write_text("\n".join(sql), encoding="utf-8")
    print(
        f"Generated seed data: {len(tables['students'])} students, "
        f"{len(tables['applications'])} applications, and {len(tables['interviews'])} interviews."
    )


if __name__ == "__main__":
    main()
