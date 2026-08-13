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

function Convert-TargetName {
    param([string] $Target)
    return ($Target.ToLowerInvariant() -replace "[^a-z0-9]+", "_").Trim("_")
}

$Bench = Split-Path -Parent $PSScriptRoot
$Root = Split-Path -Parent $Bench
$OutDir = Join-Path $Bench "reports\4tu_p4v2_multitarget_20260810"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$TaskManifest = Join-Path $OutDir "4tu_p4v2_task_labels_20260810.csv"

Invoke-Native py `
    (Join-Path $Bench "scripts\build_4tu_task_label_join.py") `
    --package-manifest (Join-Path $Root "reports\4tu_split_packages_20260810\p4_graph_opt_v2\package_manifest.csv") `
    --activity-manifest (Join-Path $Root "manifest\4tu_project_activity_manifest.csv") `
    --output-csv $TaskManifest `
    --unmatched-csv (Join-Path $OutDir "4tu_p4v2_unmatched_rows_20260810.csv") `
    --summary-md (Join-Path $OutDir "4tu_p4v2_task_label_join_20260810.md")

$Targets = @(
    "Land type",
    "Land use",
    "Land cover",
    "Utility crossing",
    "Construction workers",
    "Relative groundwater level"
)

foreach ($Target in $Targets) {
    $Slug = Convert-TargetName $Target
    Invoke-Native py `
        (Join-Path $Bench "scripts\run_4tu_task_baseline.py") `
        --task-manifest $TaskManifest `
        --target-field $Target `
        --output-json (Join-Path $OutDir "${Slug}_result_seed_20260810.json") `
        --output-md (Join-Path $OutDir "${Slug}_summary_seed_20260810.md") `
        --seed 20260810
}

Invoke-Native py `
    (Join-Path $Bench "scripts\summarize_4tu_task_matrix.py") `
    --result-dir $OutDir `
    --output-json (Join-Path $OutDir "task_matrix_summary.json") `
    --output-md (Join-Path $OutDir "task_matrix_summary.md")

