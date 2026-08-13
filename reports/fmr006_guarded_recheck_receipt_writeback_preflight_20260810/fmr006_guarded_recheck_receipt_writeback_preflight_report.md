# FMR-006 Guarded Recheck Receipt Writeback Preflight

Status: `fmr006_guarded_recheck_receipt_writeback_preflight_ready_blocked_waiting_fmr001_to_fmr005`

Current result:

1. FMR-006 rows: 1
2. Prerequisite complete receipts: 0/5
3. Missing prerequisite receipts: FMR-001;FMR-002;FMR-003;FMR-004;FMR-005
4. Receipt completion allowed: false
5. Guarded recheck allowed: false
6. Launcher execution allowed: false
7. Recheck executed: false
8. M0-M2 log exists: true
9. M0-M2 pass detected: false
10. FMR-006 candidate rows: 0
11. FMR-006 writeback allowed: false
12. Real FMR template modified: false
13. Portal upload allowed: false
14. Submission ready: false

Boundary: FMR-006 remains blocked until FMR-001 through FMR-005 are complete and
a guarded post-evidence M0-M2 recheck is actually allowed and executed. A PASS
log from a routine local run is retained as evidence but is not sufficient by
itself. This preflight does not write the FMR intake template, execute recheck,
upload portal files or mark the manuscript submitted.
