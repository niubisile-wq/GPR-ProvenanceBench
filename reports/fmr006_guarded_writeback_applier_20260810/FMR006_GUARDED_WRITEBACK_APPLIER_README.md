# FMR-006 Guarded Writeback Applier

Status: `fmr006_guarded_writeback_applier_ready_refusing_current_state`

Current result:

1. Candidate rows: 0
2. Writeback preflight allowed: false
3. Execute flag supplied: false
4. Writeback executed: false
5. Real FMR template modified: false
6. Portal upload allowed: false
7. Submission ready: false

Boundary: default mode is preflight only. Real FMR-006 writeback requires a
complete 19.69 candidate and the explicit `--execute-writeback` flag. This
script does not complete prerequisite FMR rows, execute recheck, upload portal
files or mark the manuscript submitted.
