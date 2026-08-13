$ErrorActionPreference = 'Stop'

$sourceDir = $PSScriptRoot
$buildDir = 'D:\codex_texbuild\gnte_manuscript'

New-Item -ItemType Directory -Path $buildDir -Force | Out-Null
Copy-Item -Path (Join-Path $sourceDir '*') -Destination $buildDir -Recurse -Force

Push-Location $buildDir
try {
    latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
} finally {
    Pop-Location
}

Copy-Item -LiteralPath (Join-Path $buildDir 'main.pdf') -Destination (Join-Path $sourceDir 'main.pdf') -Force
Write-Output (Join-Path $sourceDir 'main.pdf')

