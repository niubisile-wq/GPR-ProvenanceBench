param(
    [switch]$FullM0M2
)

$ErrorActionPreference = "Stop"
$Bench = (Get-Item $PSScriptRoot).Parent.Parent.FullName
Set-Location $Bench

py scripts\build_final_manual_receipt_completion_validator.py
if ($LASTEXITCODE -ne 0) {
    throw "19.50 receipt completion validator failed"
}

$SummaryPath = Join-Path $Bench "reports\final_manual_receipt_completion_validator_20260810\final_manual_receipt_completion_validator_summary.json"
$Summary = Get-Content -LiteralPath $SummaryPath -Raw | ConvertFrom-Json

if (-not $Summary.guarded_recheck_allowed) {
    Write-Host "FINAL GUARDED RECHECK REFUSED"
    Write-Host "Reason: 19.50 guarded_recheck_allowed=false."
    Write-Host "Complete receipt rows:" $Summary.complete_receipt_rows
    Write-Host "Incomplete receipt rows:" $Summary.incomplete_receipt_rows
    Write-Host "No M0-M2, writeback, gate closure, portal upload or submission command was executed."
    exit 0
}

Write-Host "19.50 permits guarded recheck. Running status-only recheck runner."
powershell -ExecutionPolicy Bypass -File reports\manual_post_handoff_recheck_runner_20260810\run_after_manual_evidence_recheck.ps1
if ($LASTEXITCODE -ne 0) {
    throw "Guarded recheck runner failed"
}

if ($FullM0M2) {
    powershell -ExecutionPolicy Bypass -File scripts\run_m0_m2_checks.ps1
    if ($LASTEXITCODE -ne 0) {
        throw "Full M0-M2 failed"
    }
}

Write-Host "FINAL GUARDED RECHECK COMPLETE. Portal upload and submission still require 19.47 to pass."
