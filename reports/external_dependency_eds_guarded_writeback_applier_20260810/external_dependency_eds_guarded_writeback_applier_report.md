# External Dependency EDS Guarded Writeback Applier

Status: `external_dependency_eds_guarded_writeback_applier_ready_refusing_current_state`

Current result:

1. Candidate rows: 0
2. Complete candidate rows: 0
3. Writeback preflight allowed: false
4. Execute flag supplied: false
5. Writeback executed: false
6. Real EDS template modified: false
7. Portal upload allowed: false
8. Submission ready: false

Boundary: default mode is preflight only. Real writeback requires five complete
19.57 candidates, exact EDS-001 through EDS-005 coverage, intake approval and
the explicit `--execute-writeback` flag. This script never sends email, fills
FMR rows, runs recheck, uploads portal files or marks the manuscript submitted.
