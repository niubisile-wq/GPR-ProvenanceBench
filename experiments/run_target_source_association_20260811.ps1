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
$OutDir = Join-Path $Bench "reports\target_source_association_20260811"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

Invoke-Native py `
    (Join-Path $Bench "scripts\build_target_source_association_audit.py") `
    --mojahid-manifest (Join-Path $Bench "data_manifests\mojahid_unified_samples_20260810.csv") `
    --ressam-manifest (Join-Path $Bench "data_manifests\res_sam_unified_samples_20260810.csv") `
    --four-tu-manifest (Join-Path $Bench "data_manifests\four_tu_unified_samples_20260810.csv") `
    --output-dir $OutDir

Invoke-Native py `
    (Join-Path $Bench "scripts\build_experiment_only_progress_20260811.py")
