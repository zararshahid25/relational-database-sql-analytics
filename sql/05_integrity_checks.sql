-- These checks should return zero exception rows.

SELECT registration_no, COUNT(*)
FROM students
GROUP BY registration_no
HAVING COUNT(*) > 1;

SELECT job_id, student_id, COUNT(*)
FROM applications
GROUP BY job_id, student_id
HAVING COUNT(*) > 1;

SELECT a.application_id
FROM applications a
LEFT JOIN students s ON s.student_id = a.student_id
LEFT JOIN job_postings j ON j.job_id = a.job_id
WHERE s.student_id IS NULL OR j.job_id IS NULL;

SELECT interview_id, score
FROM interviews
WHERE score NOT BETWEEN 0 AND 100;

SELECT course_id, student_id, completion_status, final_score
FROM course_enrollments
WHERE completion_status = 'Completed' AND final_score IS NULL;

