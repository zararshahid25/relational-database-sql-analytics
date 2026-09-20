DROP VIEW IF EXISTS vw_application_funnel;
DROP VIEW IF EXISTS vw_candidate_job_match;
DROP VIEW IF EXISTS vw_department_placement;

CREATE VIEW vw_application_funnel AS
SELECT
    e.employer_id,
    e.employer_name,
    COUNT(DISTINCT j.job_id) AS jobs_posted,
    COUNT(a.application_id) AS applications,
    SUM(CASE WHEN a.application_stage IN ('Screening', 'Interview', 'Offer') THEN 1 ELSE 0 END) AS progressed_to_screening,
    SUM(CASE WHEN a.application_stage IN ('Interview', 'Offer') THEN 1 ELSE 0 END) AS reached_interview,
    SUM(CASE WHEN a.final_outcome = 'Offered' THEN 1 ELSE 0 END) AS offers,
    ROUND(
        100.0 * SUM(CASE WHEN a.final_outcome = 'Offered' THEN 1 ELSE 0 END)
        / NULLIF(COUNT(a.application_id), 0),
        1
    ) AS offer_rate_pct
FROM employers e
LEFT JOIN job_postings j ON j.employer_id = e.employer_id
LEFT JOIN applications a ON a.job_id = j.job_id
GROUP BY e.employer_id, e.employer_name;

CREATE VIEW vw_candidate_job_match AS
SELECT
    a.application_id,
    a.student_id,
    a.job_id,
    COUNT(js.skill_id) AS mandatory_skills_required,
    SUM(
        CASE
            WHEN ss.proficiency_level >= js.required_level THEN 1
            ELSE 0
        END
    ) AS mandatory_skills_met,
    ROUND(
        100.0 * SUM(
            CASE
                WHEN ss.proficiency_level >= js.required_level THEN 1
                ELSE 0
            END
        ) / NULLIF(COUNT(js.skill_id), 0),
        1
    ) AS mandatory_skill_match_pct
FROM applications a
JOIN job_skills js ON js.job_id = a.job_id AND js.is_mandatory = TRUE
LEFT JOIN student_skills ss
    ON ss.student_id = a.student_id
   AND ss.skill_id = js.skill_id
GROUP BY a.application_id, a.student_id, a.job_id;

CREATE VIEW vw_department_placement AS
SELECT
    d.department_id,
    d.department_name,
    COUNT(DISTINCT s.student_id) AS students,
    COUNT(DISTINCT CASE WHEN a.final_outcome = 'Offered' THEN s.student_id END) AS students_with_offer,
    ROUND(
        100.0 * COUNT(DISTINCT CASE WHEN a.final_outcome = 'Offered' THEN s.student_id END)
        / NULLIF(COUNT(DISTINCT s.student_id), 0),
        1
    ) AS placement_rate_pct
FROM departments d
JOIN students s ON s.department_id = d.department_id
LEFT JOIN applications a ON a.student_id = s.student_id
GROUP BY d.department_id, d.department_name;
