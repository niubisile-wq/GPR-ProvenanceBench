# FMR-001 Sendout Completion Writeback Preflight

Status: `fmr001_sendout_completion_writeback_preflight_ready_blocked_waiting_verified_eds`

Current result:

1. FMR-001 rows: 1
2. EDS sent receipt rows: 0
3. EDS missing send receipts: 5
4. FMR-001 candidate rows: 0
5. FMR-001 writeback allowed: false
6. Real FMR template modified: false
7. Guarded recheck allowed: false
8. Portal upload allowed: false
9. Submission ready: false

Boundary: this preflight only proposes the FMR-001 completion value after EDS
sendout evidence has been verified and post-writeback revalidation confirms the
unlock. It does not write the FMR intake template, run validators, upload portal
files or mark the manuscript submitted.
