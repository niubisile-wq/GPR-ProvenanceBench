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
$OutDir = Join-Path $Bench "reports\ressam_transfer_bootstrap_ci_20260811"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

Invoke-Native py `
    (Join-Path $Bench "scripts\build_ressam_transfer_bootstrap_ci.py") `
    --five-model-summary (Join-Path $Bench "reports\five_model_synthesis_20260810\five_model_synthesis_summary.json") `
    --output-dir $OutDir

Invoke-Native py `
    (Join-Path $Bench "scripts\build_experiment_only_progress_20260811.py")
