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
$OutDir = Join-Path $Bench "reports\lbp_linear_svm_matrix_20260810"

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

Invoke-Native py `
    (Join-Path $Bench "scripts\run_lbp_linear_svm_matrix.py") `
    --mojahid-manifest (Join-Path $Bench "data_manifests\mojahid_unified_samples_20260810.csv") `
    --mojahid-data-root (Join-Path $Root "gpr_leakage_research\dataset_inspect\GPR_data") `
    --ressam-manifest (Join-Path $Bench "data_manifests\res_sam_unified_samples_20260810.csv") `
    --ressam-data-root (Join-Path $Root "external_assets\res_sam_data") `
    --output-dir $OutDir
