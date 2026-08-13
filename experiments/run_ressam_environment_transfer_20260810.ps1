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
$OutDir = Join-Path $Bench "reports\ressam_environment_transfer_20260810"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

Invoke-Native py `
    (Join-Path $Bench "scripts\run_ressam_environment_transfer.py") `
    --manifest (Join-Path $Bench "data_manifests\res_sam_unified_samples_20260810.csv") `
    --data-root (Join-Path $Root "external_assets\res_sam_data") `
    --output-json (Join-Path $OutDir "result_seed_20260810.json") `
    --output-md (Join-Path $OutDir "summary_seed_20260810.md") `
    --seed 20260810

