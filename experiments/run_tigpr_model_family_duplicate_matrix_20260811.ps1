$ErrorActionPreference = "Stop"

$Bench = Split-Path -Parent $PSScriptRoot
$Root = Split-Path -Parent $Bench

py (Join-Path $Bench "scripts\run_tigpr_model_family_duplicate_matrix.py") `
  --manifest (Join-Path $Root "manifest\tigpr_sample_index_v1.csv") `
  --output-dir (Join-Path $Bench "reports\tigpr_model_family_duplicate_matrix_20260811") `
  --hog-image-size 64 `
  --pixel-image-size 32
