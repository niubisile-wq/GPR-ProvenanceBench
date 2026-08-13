# Reproducibility Notes

This file describes how to interpret and rerun the repository materials.

## What Is Included

The repository includes the lightweight components needed to inspect the study logic:

- manuscript source, bibliography, journal template files, and compiled PDF;
- rendered figures and the figure-generation script;
- experiment scripts and PowerShell launchers;
- environment records from the execution workspace;
- sample manifests and split manifests;
- report summaries, source-data tables, JSON summaries, and CSV result records.

Large third-party data caches, raw GPR files, model/checkpoint caches, intermediate feature arrays, rendered raw-trace image dumps, local temporary files, and LaTeX build products are intentionally excluded from version control.

## Environment

The recorded execution environment is under `environment/`.

Key versions reported in the manuscript:

- Python 3.12.5
- NumPy 2.1.3
- scikit-learn 1.5.2
- Pillow 12.2.0
- PyTorch 2.8.0
- torchvision 0.23.0
- timm 1.0.27

The full recorded package list is in `environment/pip_freeze_20260810.txt`.

## Manuscript Build

From `manuscript/nte_submission_20260812/`, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\build.ps1
```

The build uses the local Taylor & Francis LaTeX template files included in the manuscript directory.

## Figure Generation

From `manuscript/nte_submission_20260812/`, run:

```powershell
py -3.12 .\scripts\make_manuscript_figures.py
```

This regenerates the manuscript figure PDFs, PNGs, and SVGs from the lightweight source tables in `reports/`.

Note: `fig1_workflow.pdf` was redrawn from the PowerPoint source at `manuscript/nte_submission_20260812/figures/fig1_workflow_source.pptx`.

## Experiment Reruns

The dated PowerShell wrappers in `experiments/` call the Python scripts in `scripts/`. They assume that the relevant third-party GPR assets have been obtained and placed where the manifests expect them.

Typical workflow:

1. Obtain the original third-party datasets from their providers.
2. Rebuild or verify the sample manifests in `data_manifests/`.
3. Verify frozen split assignments in `splits/`.
4. Run the relevant wrapper in `experiments/`.
5. Compare generated summaries against the corresponding files under `reports/`.
6. Rebuild manuscript figures and the manuscript PDF.

## Third-Party Data Boundary

Raw third-party GPR files are not redistributed in this repository. This includes downloaded public benchmark caches and any local external-blind cache. Reviewers or readers should obtain these files from the original providers under the applicable provider licences.

The repository retains derived metadata, file hashes, split assignments, result summaries, and figure source tables so that the evaluation logic can be audited without redistributing restricted source files.

## Repository Hygiene

The `.gitignore` intentionally excludes:

- `external_blind/`
- `tmp/`
- Python caches
- LaTeX build artifacts
- large intermediate arrays such as `.npz`, `.pt`, and `.pth`
- TIFF previews and ZIP bundles
- rendered raw-trace cache images under `reports/`

The exclusion rules are meant to keep the repository reviewable and within GitHub file-size limits while preserving the scientific audit trail.
