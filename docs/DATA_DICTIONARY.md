# Data dictionary

| Table | Primary key | Grain |
|---|---|---|
| `departments` | `department_id` | One academic department |
| `students` | `student_id` | One synthetic student |
| `employers` | `employer_id` | One hiring organisation |
| `skills` | `skill_id` | One governed skill |
| `student_skills` | `(student_id, skill_id)` | One assessed student–skill relationship |
| `job_postings` | `job_id` | One job posting |
| `job_skills` | `(job_id, skill_id)` | One job–skill requirement |
| `applications` | `application_id` | One student's application to one job |
| `interviews` | `interview_id` | One round for one application |
| `training_courses` | `course_id` | One training course |
| `course_enrollments` | `(course_id, student_id)` | One student's enrolment in one course |

Important uniqueness rules prevent duplicate registration numbers, emails, employer names, skill names, student/job applications, interview rounds, and bridge-table relationships.

