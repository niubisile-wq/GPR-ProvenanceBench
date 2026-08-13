Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo
py scripts\run_deepmask_gpr_augmentation_leakage_matrix_20260811.py
