-- Q1. How many applications reached each stage?
SELECT
    application_stage,
    COUNT(*) AS applications
FROM applications
GROUP BY application_stage
ORDER BY applications DESC;

-- Q2. Which employers have the highest offer rate, with at least 20 applications?
SELECT
    employer_name,
    applications,
    offers,
    offer_rate_pct
FROM vw_application_funnel
WHERE applications >= 20
ORDER BY offer_rate_pct DESC, applications DESC;

-- Q3. Which students have a CGPA above their own department average?
SELECT
    s.registration_no,
    s.full_name,
    d.department_name,
    s.cgpa
FROM students s
JOIN departments d ON d.department_id = s.department_id
WHERE s.cgpa > (
    SELECT AVG(peer.cgpa)
    FROM students peer
    WHERE peer.department_id = s.department_id
)
ORDER BY d.department_name, s.cgpa DESC;

-- Q4. Which advertised jobs have no applications?
SELECT
    j.job_id,
    j.job_title,
    e.employer_name,
    j.closing_date
FROM job_postings j
JOIN employers e ON e.employer_id = j.employer_id
LEFT JOIN applications a ON a.job_id = j.job_id
WHERE a.application_id IS NULL
ORDER BY j.closing_date;

-- Q5. What is each department's placement rate?
SELECT
    department_name,
    students,
    students_with_offer,
    placement_rate_pct
FROM vw_department_placement
ORDER BY placement_rate_pct DESC, department_name;

-- Q6. Which mandatory skills have the largest student proficiency gap?
WITH required AS (
    SELECT js.skill_id, COUNT(DISTINCT js.job_id) AS jobs_requiring_skill
    FROM job_skills js
    WHERE js.is_mandatory = TRUE
    GROUP BY js.skill_id
), qualified_students AS (
    SELECT ss.skill_id, COUNT(DISTINCT ss.student_id) AS qualified_students
    FROM student_skills ss
    WHERE ss.proficiency_level >= 3
    GROUP BY ss.skill_id
)
SELECT
    sk.skill_name,
    r.jobs_requiring_skill,
    COALESCE(q.qualified_students, 0) AS qualified_students
FROM required r
JOIN skills sk ON sk.skill_id = r.skill_id
LEFT JOIN qualified_students q ON q.skill_id = r.skill_id
ORDER BY r.jobs_requiring_skill DESC, qualified_students ASC;

-- Q7. Rank candidates within each job using skill match and interview score.
WITH interview_scores AS (
    SELECT application_id, AVG(score) AS average_interview_score
    FROM interviews
    GROUP BY application_id
), candidate_scores AS (
    SELECT
        a.job_id,
        a.application_id,
        s.full_name,
        m.mandatory_skill_match_pct,
        COALESCE(i.average_interview_score, 0) AS average_interview_score,
        0.6 * m.mandatory_skill_match_pct + 0.4 * COALESCE(i.average_interview_score, 0) AS composite_score
    FROM applications a
    JOIN students s ON s.student_id = a.student_id
    JOIN vw_candidate_job_match m ON m.application_id = a.application_id
    LEFT JOIN interview_scores i ON i.application_id = a.application_id
)
SELECT
    job_id,
    application_id,
    full_name,
    ROUND(mandatory_skill_match_pct, 1) AS skill_match_pct,
    ROUND(average_interview_score, 1) AS interview_score,
    ROUND(composite_score, 1) AS composite_score,
    DENSE_RANK() OVER (PARTITION BY job_id ORDER BY composite_score DESC) AS candidate_rank
FROM candidate_scores
ORDER BY job_id, candidate_rank, application_id;

-- Q8. Do students who completed training reach interviews more often?
WITH student_training AS (
    SELECT
        s.student_id,
        CASE
            WHEN SUM(CASE WHEN ce.completion_status = 'Completed' THEN 1 ELSE 0 END) > 0 THEN 'Completed training'
            ELSE 'No completed training'
        END AS training_group
    FROM students s
    LEFT JOIN course_enrollments ce ON ce.student_id = s.student_id
    GROUP BY s.student_id
), student_outcomes AS (
    SELECT
        st.student_id,
        st.training_group,
        MAX(CASE WHEN a.application_stage IN ('Interview', 'Offer') THEN 1 ELSE 0 END) AS reached_interview
    FROM student_training st
    LEFT JOIN applications a ON a.student_id = st.student_id
    GROUP BY st.student_id, st.training_group
)
SELECT
    training_group,
    COUNT(*) AS students,
    SUM(reached_interview) AS students_reaching_interview,
    ROUND(100.0 * SUM(reached_interview) / NULLIF(COUNT(*), 0), 1) AS interview_reach_pct
FROM student_outcomes
GROUP BY training_group;

-- Q9. Monthly application trend using a portable YYYY-MM key.
SELECT
    SUBSTR(CAST(applied_date AS VARCHAR), 1, 7) AS application_month,
    COUNT(*) AS applications,
    SUM(CASE WHEN final_outcome = 'Offered' THEN 1 ELSE 0 END) AS offers
FROM applications
GROUP BY SUBSTR(CAST(applied_date AS VARCHAR), 1, 7)
ORDER BY application_month;

-- Q10. Which students satisfy every mandatory skill for an applied job?
SELECT
    a.application_id,
    s.full_name,
    j.job_title,
    m.mandatory_skills_required,
    m.mandatory_skills_met
FROM applications a
JOIN students s ON s.student_id = a.student_id
JOIN job_postings j ON j.job_id = a.job_id
JOIN vw_candidate_job_match m ON m.application_id = a.application_id
WHERE m.mandatory_skills_required = m.mandatory_skills_met
ORDER BY j.job_title, s.full_name;

