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

$Manifest = Join-Path $Bench "data_manifests\mojahid_unified_samples_20260810.csv"
$DataRoot = Join-Path $Root "gpr_leakage_research\dataset_inspect\GPR_data"
$OutDir = Join-Path $Bench "reports\mojahid_hog_rbf_svm_20260810"

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

Invoke-Native py `
    (Join-Path $Bench "scripts\run_mojahid_hog_rbf_svm.py") `
    --manifest $Manifest `
    --data-root $DataRoot `
    --output-json (Join-Path $OutDir "result_seed_20260810.json") `
    --output-md (Join-Path $OutDir "summary_seed_20260810.md") `
    --seed 20260810

