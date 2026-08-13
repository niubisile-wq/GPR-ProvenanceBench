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
$OutDir = Join-Path $Bench "reports\4tu_p4v2_land_type_20260810"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$TaskManifest = Join-Path $OutDir "4tu_p4v2_task_labels_20260810.csv"

Invoke-Native py `
    (Join-Path $Bench "scripts\build_4tu_task_label_join.py") `
    --package-manifest (Join-Path $Root "reports\4tu_split_packages_20260810\p4_graph_opt_v2\package_manifest.csv") `
    --activity-manifest (Join-Path $Root "manifest\4tu_project_activity_manifest.csv") `
    --output-csv $TaskManifest `
    --unmatched-csv (Join-Path $OutDir "4tu_p4v2_unmatched_rows_20260810.csv") `
    --summary-md (Join-Path $OutDir "4tu_p4v2_task_label_join_20260810.md")

Invoke-Native py `
    (Join-Path $Bench "scripts\run_4tu_task_baseline.py") `
    --task-manifest $TaskManifest `
    --target-field "Land type" `
    --output-json (Join-Path $OutDir "land_type_result_seed_20260810.json") `
    --output-md (Join-Path $OutDir "land_type_summary_seed_20260810.md") `
    --seed 20260810

