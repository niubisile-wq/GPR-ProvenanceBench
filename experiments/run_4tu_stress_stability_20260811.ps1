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
$OutDir = Join-Path $Bench "reports\4tu_stress_stability_20260811"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

Invoke-Native py `
    (Join-Path $Bench "scripts\build_4tu_stress_stability_audit.py") `
    --fixed-metrics (Join-Path $Bench "reports\4tu_counterfactual_hog_seed_sweep_20260810\hog_seed_sweep_metrics.csv") `
    --group-metrics (Join-Path $Bench "reports\4tu_counterfactual_hog_group_splits_20260810\hog_group_split_metrics.csv") `
    --output-dir $OutDir

Invoke-Native py `
    (Join-Path $Bench "scripts\build_experiment_only_progress_20260811.py")
