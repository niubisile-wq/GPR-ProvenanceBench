# FMR-002 Author Decision Writeback Preflight

Status: `fmr002_author_decision_writeback_preflight_ready_blocked_waiting_author_decisions`

Current result:

1. FMR-002 rows: 1
2. Decision rows: 4
3. Resolved decision rows: 0
4. FMR-002 candidate rows: 0
5. FMR-002 writeback allowed: false
6. Real FMR template modified: false
7. Guarded recheck allowed: false
8. Portal upload allowed: false
9. Submission ready: false

Boundary: recommended defaults in `author_decision_closure_form_v2.csv` are not
accepted as author decisions. This preflight only proposes FMR-002 completion
after explicit author/advisor responses, backend/scope selection and manual
evidence intake approval. It does not write the FMR intake template, render
figures, close gates, upload portal files or mark the manuscript submitted.
