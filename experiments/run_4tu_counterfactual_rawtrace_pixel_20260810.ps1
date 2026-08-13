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
$OutDir = Join-Path $Bench "reports\4tu_counterfactual_rawtrace_pixel_20260810"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

Invoke-Native py `
    (Join-Path $Bench "scripts\run_4tu_counterfactual_rawtrace_pixel.py") `
    --task-manifest (Join-Path $Bench "reports\4tu_p4v2_multitarget_20260810\4tu_p4v2_task_labels_20260810.csv") `
    --output-dir $OutDir `
    --seed 20260810 `
    --image-size 64
