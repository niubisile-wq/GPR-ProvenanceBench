# FMR Guarded Writeback Coverage Audit

Status: `fmr_guarded_writeback_coverage_audit_passed_all_layers_guarded`

Current result:

1. FMR rows: 6
2. Coverage complete rows: 6
3. Regression pass rows: 6
4. Writeback allowed rows: 0
5. Writeback executed rows: 0
6. Real FMR template modified rows: 0
7. Submission ready rows: 0
8. Portal upload allowed: false
9. Submission ready: false

Boundary: this audit verifies that FMR-001 through FMR-006 each have a
preflight, guarded applier and regression layer, and that the current state has
not executed real writeback. It does not complete receipts, write any FMR row,
execute recheck, upload portal files or mark the manuscript submitted.
