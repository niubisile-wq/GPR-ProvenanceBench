# RB-001 manual execution receipt guide 2026-08-10

Fill `RB001_manual_execution_receipt_20260810.csv` only after real returned files have been copied into `final_return_evidence_inbox_20260810`.

Required sequence:

1. Copy real returned files into the matching route folder.
2. Compute SHA256 for each copied file.
3. Fill the receipt row for that route.
4. Run `reports/rb001_diagnostic_only_runner_20260810/run_rb001_diagnostic_only.ps1`.
5. Record the diagnostic runner return code.
6. Do not treat the receipt as writeback permission.

Current status: template only; no completed receipt rows exist.
