DROP VIEW IF EXISTS vw_application_funnel;
DROP VIEW IF EXISTS vw_candidate_job_match;
DROP VIEW IF EXISTS vw_department_placement;

DROP TABLE IF EXISTS course_enrollments;
DROP TABLE IF EXISTS training_courses;
DROP TABLE IF EXISTS interviews;
DROP TABLE IF EXISTS applications;
DROP TABLE IF EXISTS job_skills;
DROP TABLE IF EXISTS job_postings;
DROP TABLE IF EXISTS student_skills;
DROP TABLE IF EXISTS skills;
DROP TABLE IF EXISTS employers;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS departments;

CREATE TABLE departments (
    department_id      INTEGER PRIMARY KEY,
    department_name    VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE students (
    student_id         INTEGER PRIMARY KEY,
    registration_no   VARCHAR(30) NOT NULL UNIQUE,
    full_name          VARCHAR(120) NOT NULL,
    email              VARCHAR(160) NOT NULL UNIQUE,
    department_id      INTEGER NOT NULL REFERENCES departments(department_id),
    graduation_year    INTEGER NOT NULL CHECK (graduation_year BETWEEN 2024 AND 2030),
    cgpa               NUMERIC(3,2) NOT NULL CHECK (cgpa BETWEEN 0 AND 4)
);

CREATE TABLE employers (
    employer_id        INTEGER PRIMARY KEY,
    employer_name      VARCHAR(140) NOT NULL UNIQUE,
    sector             VARCHAR(80) NOT NULL,
    city               VARCHAR(80) NOT NULL
);

CREATE TABLE skills (
    skill_id           INTEGER PRIMARY KEY,
    skill_name         VARCHAR(80) NOT NULL UNIQUE,
    skill_category     VARCHAR(60) NOT NULL
);

CREATE TABLE student_skills (
    student_id         INTEGER NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    skill_id           INTEGER NOT NULL REFERENCES skills(skill_id),
    proficiency_level  INTEGER NOT NULL CHECK (proficiency_level BETWEEN 1 AND 5),
    assessed_date      DATE NOT NULL,
    PRIMARY KEY (student_id, skill_id)
);

CREATE TABLE job_postings (
    job_id             INTEGER PRIMARY KEY,
    employer_id        INTEGER NOT NULL REFERENCES employers(employer_id),
    job_title          VARCHAR(140) NOT NULL,
    employment_type    VARCHAR(30) NOT NULL CHECK (employment_type IN ('Internship', 'Graduate Role', 'Contract')),
    min_cgpa           NUMERIC(3,2) NOT NULL CHECK (min_cgpa BETWEEN 0 AND 4),
    posted_date        DATE NOT NULL,
    closing_date       DATE NOT NULL,
    openings           INTEGER NOT NULL CHECK (openings > 0),
    CHECK (closing_date >= posted_date)
);

CREATE TABLE job_skills (
    job_id             INTEGER NOT NULL REFERENCES job_postings(job_id) ON DELETE CASCADE,
    skill_id           INTEGER NOT NULL REFERENCES skills(skill_id),
    required_level     INTEGER NOT NULL CHECK (required_level BETWEEN 1 AND 5),
    is_mandatory       BOOLEAN NOT NULL DEFAULT TRUE,
    PRIMARY KEY (job_id, skill_id)
);

CREATE TABLE applications (
    application_id     INTEGER PRIMARY KEY,
    job_id             INTEGER NOT NULL REFERENCES job_postings(job_id),
    student_id         INTEGER NOT NULL REFERENCES students(student_id),
    applied_date       DATE NOT NULL,
    application_stage  VARCHAR(30) NOT NULL CHECK (application_stage IN ('Applied', 'Screening', 'Interview', 'Offer')),
    final_outcome      VARCHAR(30) NOT NULL CHECK (final_outcome IN ('Pending', 'Rejected', 'Withdrawn', 'Offered')),
    UNIQUE (job_id, student_id)
);

CREATE TABLE interviews (
    interview_id       INTEGER PRIMARY KEY,
    application_id     INTEGER NOT NULL REFERENCES applications(application_id) ON DELETE CASCADE,
    round_number       INTEGER NOT NULL CHECK (round_number BETWEEN 1 AND 5),
    interview_type     VARCHAR(40) NOT NULL,
    interview_date     DATE NOT NULL,
    score              NUMERIC(5,2) NOT NULL CHECK (score BETWEEN 0 AND 100),
    result             VARCHAR(20) NOT NULL CHECK (result IN ('Pass', 'Fail', 'Pending')),
    UNIQUE (application_id, round_number)
);

CREATE TABLE training_courses (
    course_id          INTEGER PRIMARY KEY,
    course_title       VARCHAR(140) NOT NULL UNIQUE,
    provider           VARCHAR(100) NOT NULL,
    start_date         DATE NOT NULL,
    end_date           DATE NOT NULL,
    skill_id           INTEGER NOT NULL REFERENCES skills(skill_id),
    CHECK (end_date >= start_date)
);

CREATE TABLE course_enrollments (
    course_id          INTEGER NOT NULL REFERENCES training_courses(course_id) ON DELETE CASCADE,
    student_id         INTEGER NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    completion_status  VARCHAR(20) NOT NULL CHECK (completion_status IN ('Completed', 'In Progress', 'Dropped')),
    final_score        NUMERIC(5,2) CHECK (final_score BETWEEN 0 AND 100),
    PRIMARY KEY (course_id, student_id),
    CHECK (
        (completion_status = 'Completed' AND final_score IS NOT NULL)
        OR (completion_status <> 'Completed')
    )
);

CREATE INDEX idx_students_department ON students(department_id);
CREATE INDEX idx_jobs_employer ON job_postings(employer_id);
CREATE INDEX idx_applications_job ON applications(job_id);
CREATE INDEX idx_applications_student ON applications(student_id);
CREATE INDEX idx_applications_stage ON applications(application_stage);
CREATE INDEX idx_interviews_application ON interviews(application_id);
