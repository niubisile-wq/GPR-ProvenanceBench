# FMR Evidence-to-Writeback Execution Order Audit

Status: `fmr_evidence_to_writeback_execution_order_audit_ready_all_current_commands_blocked`

Current result:

1. Ordered FMR rows: 6
2. Commands allowed now: 0
3. Writeback executed rows: 0
4. Real FMR template modified rows: 0
5. Receipt completion allowed: false
6. Guarded recheck allowed: false
7. Launcher execution allowed: false
8. Recheck executed: false
9. Portal upload allowed: false
10. Submission ready: false

Boundary: this audit locks execution order only. It does not execute evidence
validators, run `--execute-writeback`, execute guarded recheck, upload portal
files or mark the manuscript submitted.
