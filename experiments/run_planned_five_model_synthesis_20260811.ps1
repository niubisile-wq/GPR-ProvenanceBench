$ErrorActionPreference = "Stop"
$Bench = Split-Path -Parent $PSScriptRoot
& py (Join-Path $Bench "scripts\synthesize_planned_five_model_matrix_20260811.py")
if ($LASTEXITCODE -ne 0) {
    throw "Planned five-model synthesis failed with exit code $LASTEXITCODE"
}
