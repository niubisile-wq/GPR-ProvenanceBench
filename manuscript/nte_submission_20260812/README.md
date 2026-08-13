# Nondestructive Testing and Evaluation manuscript package

## Entry files

- `main.tex`: manuscript source
- `references.bib`: verified BibTeX records
- `build.ps1`: ASCII-path compilation wrapper for the local TeX Live setup

## Build

Run from PowerShell:

```powershell
.\build.ps1
```

The script stages the project in `D:\codex_texbuild\gnte_manuscript`, runs
`latexmk`, and copies `main.pdf` back into this directory.

## Required files

The Taylor & Francis class and NLM bibliography style are copied into this
directory from the archived official bundle. Keep them beside `main.tex`.

## Status

- Journal layout: single-column Interact
- Reference style: numbered NLM
- Scientific text: scaffold only
- Author metadata: placeholder
- References: not yet populated
- Submission ready: no

