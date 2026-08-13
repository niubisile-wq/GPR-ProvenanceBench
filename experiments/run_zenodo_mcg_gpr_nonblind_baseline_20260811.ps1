Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo
py scripts\run_zenodo_mcg_gpr_nonblind_baseline_20260811.py
