# SQL question guide

| Question | Main SQL concepts |
|---|---|
| Applications by stage | `GROUP BY`, `COUNT`, ordering |
| Employer offer rate | Multi-table view, conditional aggregation, `NULLIF` |
| Students above department average | Join plus correlated subquery |
| Jobs with no applications | `LEFT JOIN` and null filtering |
| Department placement rate | Distinct conditional counts and rate calculation |
| Mandatory skill gaps | Two CTEs, grouped counts, left join, `COALESCE` |
| Candidate rank within job | CTEs, weighted score, `DENSE_RANK` window function |
| Training vs interview reach | Multi-stage CTEs and conditional aggregation |
| Monthly application trend | Portable year-month key and grouped time analysis |
| Complete mandatory-skill matches | Bridge-table comparison using an analytical view |

## Practice method

1. Write down the output grain before running a query.
2. Identify which table owns each requested field.
3. Add joins one at a time and check the row count after each join.
4. For rates, write the numerator and denominator separately before dividing.
5. For bridge tables, check whether the same business entity can appear more than once.
6. Use `NULLIF(denominator, 0)` when a zero denominator is possible.
7. Validate one row manually from the seed CSVs.

