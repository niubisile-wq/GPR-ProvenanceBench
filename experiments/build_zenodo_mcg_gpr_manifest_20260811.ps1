Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo
py scripts\build_zenodo_mcg_gpr_manifest_20260811.py
