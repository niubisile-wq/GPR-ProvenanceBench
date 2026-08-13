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
$OutDir = Join-Path $Bench "reports\4tu_counterfactual_hog_group_splits_20260810"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

Invoke-Native py `
    (Join-Path $Bench "scripts\run_4tu_counterfactual_hog_group_splits.py") `
    --task-manifest (Join-Path $Bench "reports\4tu_p4v2_multitarget_20260810\4tu_p4v2_task_labels_20260810.csv") `
    --output-dir $OutDir `
    --target "Land type" `
    --split-seeds 20260810 20260811 20260812 20260813 20260814 `
    --model-seed 20260810 `
    --image-size 64 `
    --val-projects 2 `
    --test-projects 2
