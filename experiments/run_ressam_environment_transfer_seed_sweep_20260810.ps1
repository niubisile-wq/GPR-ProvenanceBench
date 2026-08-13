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
$OutDir = Join-Path $Bench "reports\ressam_environment_transfer_seed_sweep_20260810"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$Seeds = @(20260810, 20260811, 20260812, 20260813, 20260814)

foreach ($Seed in $Seeds) {
    Invoke-Native py `
        (Join-Path $Bench "scripts\run_ressam_environment_transfer.py") `
        --manifest (Join-Path $Bench "data_manifests\res_sam_unified_samples_20260810.csv") `
        --data-root (Join-Path $Root "external_assets\res_sam_data") `
        --output-json (Join-Path $OutDir "result_seed_${Seed}.json") `
        --output-md (Join-Path $OutDir "summary_seed_${Seed}.md") `
        --seed $Seed
}

Invoke-Native py `
    (Join-Path $Bench "scripts\summarize_ressam_transfer_seed_sweep.py") `
    --result-dir $OutDir `
    --output-json (Join-Path $OutDir "seed_sweep_summary.json") `
    --output-md (Join-Path $OutDir "seed_sweep_summary.md")

