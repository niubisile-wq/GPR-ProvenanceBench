$ErrorActionPreference = "Stop"
Set-Location -LiteralPath (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path))
Write-Host "RB-001 DIAGNOSTIC-ONLY RUNNER"
Write-Host "Running scanner, hash reconciliation and dry-run gate only."
py scripts/build_final_return_evidence_intake_scanner.py
py scripts/build_rb001_return_evidence_hash_reconciliation.py
py scripts/build_rb001_post_drop_dry_run_gate.py
Write-Host "RB-001 diagnostic-only runner completed. No writeback, transition, guarded runner or submission command was executed."
exit 0
