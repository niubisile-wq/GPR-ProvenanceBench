$ErrorActionPreference = "Stop"

function Invoke-Native {
    param(
        [Parameter(Mandatory = $true)]
        [string] $FilePath,
        [Parameter(ValueFromRemainingArguments = $true)]
        [string[]] $Arguments
    )

    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code ${LASTEXITCODE}: $FilePath $($Arguments -join ' ')"
    }
}

$Bench = Split-Path -Parent $PSScriptRoot
$Root = Split-Path -Parent $Bench
$OutDir = Join-Path $Bench "reports\mojahid_alignment_repair_20260811"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

Invoke-Native py `
    (Join-Path $Bench "scripts\run_mojahid_alignment_repair_sweep.py") `
    --manifest (Join-Path $Bench "data_manifests\mojahid_unified_samples_20260810.csv") `
    --data-root (Join-Path $Root "gpr_leakage_research\dataset_inspect\GPR_data") `
    --output-dir $OutDir

Invoke-Native py `
    (Join-Path $Bench "scripts\build_experiment_only_progress_20260811.py")
