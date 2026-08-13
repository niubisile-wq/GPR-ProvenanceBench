$ErrorActionPreference = "Stop"
$Bench = Split-Path -Parent $PSScriptRoot
$OutDir = Join-Path $Bench "reports\mojahid_domain_adversarial_repair_20260811"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
& py (Join-Path $Bench "scripts\run_mojahid_domain_adversarial_repair.py") `
    --manifest (Join-Path $Bench "data_manifests\mojahid_unified_samples_20260810.csv") `
    --feature-cache (Join-Path $Bench "reports\unified_split_five_family_matrix_20260811\mojahid_five_family_features.npz") `
    --output-dir $OutDir
if ($LASTEXITCODE -ne 0) {
    throw "Mojahid domain-adversarial repair failed with exit code $LASTEXITCODE"
}
