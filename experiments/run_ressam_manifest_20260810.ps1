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
$Repo = Join-Path $Root "external_assets\res_sam_repo"
$DataRoot = Join-Path $Root "external_assets\res_sam_data"

Invoke-Native py `
    (Join-Path $Bench "scripts\build_ressam_unified_manifest.py") `
    --zip-path (Join-Path $Repo "gpr_data.zip") `
    --extract-dir $DataRoot `
    --output-csv (Join-Path $Bench "data_manifests\res_sam_unified_samples_20260810.csv") `
    --summary-md (Join-Path $Bench "data_manifests\res_sam_unified_samples_20260810.md")

