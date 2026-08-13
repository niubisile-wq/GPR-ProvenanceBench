# Figure rendering preflight 2026-08-10

This package checks whether the planned figure set can move into formal rendering after the author chooses one backend.

Current state: no final figures are rendered.

## Required author decision

Choose exactly one backend: Python or R. The current default recommendation is Python because the analysis pipeline and source-data files are already Python-oriented.

## Stop rules

1. Do not start formal figure rendering before backend choice.
2. Do not treat any planned figure as final without PDF, SVG, 600-dpi PNG preview and visual QA.
3. Do not upgrade Figure 6 into an external-validation result.
4. Do not use final figure captions until references, manuscript branch and Source Data are locked.
