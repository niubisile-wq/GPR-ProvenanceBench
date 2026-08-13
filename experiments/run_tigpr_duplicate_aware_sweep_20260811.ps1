$ErrorActionPreference = "Stop"

$Bench = Split-Path -Parent $PSScriptRoot
$Root = Split-Path -Parent $Bench

py (Join-Path $Bench "scripts\run_tigpr_duplicate_aware_sweep.py") `
  --manifest (Join-Path $Root "manifest\tigpr_sample_index_v1.csv") `
  --output-dir (Join-Path $Bench "reports\tigpr_duplicate_aware_sweep_20260811") `
  --image-size 64
