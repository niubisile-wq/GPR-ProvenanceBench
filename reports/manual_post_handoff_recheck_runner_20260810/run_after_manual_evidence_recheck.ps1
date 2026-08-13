param(
    [switch]$FullM0M2
)

$ErrorActionPreference = "Stop"
$Bench = (Get-Item $PSScriptRoot).Parent.Parent.FullName
Set-Location $Bench

function Invoke-SafeStep {
    param([string]$Label, [string[]]$Command)
    Write-Host "SAFE RECHECK: $Label"
    & $Command[0] $Command[1..($Command.Length - 1)]
    if ($LASTEXITCODE -ne 0) {
        throw "Step failed: $Label"
    }
}

Invoke-SafeStep "audit manual evidence inbox" @("py", "scripts\build_manual_evidence_inbox_audit.py")
Invoke-SafeStep "refresh inbox-to-tracker writeback queue" @("py", "scripts\build_inbox_to_tracker_writeback_queue.py")
Invoke-SafeStep "validate post-dispatch evidence intake" @("py", "scripts\build_post_dispatch_evidence_intake_validator.py")
Invoke-SafeStep "preflight manual evidence entry" @("py", "scripts\build_manual_evidence_entry_preflight.py")
Invoke-SafeStep "refresh manual evidence lifecycle dashboard" @("py", "scripts\build_manual_evidence_lifecycle_dashboard.py")
Invoke-SafeStep "refresh gate closure execution board" @("py", "scripts\build_gate_closure_execution_board.py")
Invoke-SafeStep "refresh submission completion ledger" @("py", "scripts\build_submission_completion_ledger.py")
Invoke-SafeStep "refresh portal submission file preflight" @("py", "scripts\build_portal_submission_file_preflight.py")
Invoke-SafeStep "check text encoding" @("py", "scripts\check_manuscript_text_encoding.py")

if ($FullM0M2) {
    powershell -ExecutionPolicy Bypass -File scripts\run_m0_m2_checks.ps1
    if ($LASTEXITCODE -ne 0) {
        throw "Full M0-M2 check failed"
    }
}

Write-Host "SAFE RECHECK COMPLETE. This runner did not write manual evidence, close gates, or upload files."
