# Normalisation notes

The SkillBridge design targets third normal form (3NF).

## First normal form

- Every column stores one value.
- Repeating skills are not stored as `skill_1`, `skill_2`, and so on.
- Each table has a declared primary key.

## Second normal form

Bridge tables use complete composite keys:

- `student_skills(student_id, skill_id)`;
- `job_skills(job_id, skill_id)`;
- `course_enrollments(course_id, student_id)`.

Bridge attributes depend on the whole key. For example, a proficiency level belongs to one student's relationship with one skill, not to the student or skill alone.

## Third normal form

- Department name is stored once in `departments`, not repeated for every student.
- Employer details are stored in `employers`, not repeated in every job or application.
- Skill names and categories are stored in `skills`, not copied into the two skill bridge tables.
- Course provider and dates are stored in `training_courses`, not repeated in every enrolment.
- Interview results belong to interview rounds and are not stored on the student or job.

## Deliberate modelling choices

`order_id` does not exist in this domain; `application_id` is the central recruitment transaction. Application stage and final outcome are retained separately because one describes current process position while the other describes the final disposition.

The views are denormalised read surfaces. They do not change the normal form of the underlying tables.

