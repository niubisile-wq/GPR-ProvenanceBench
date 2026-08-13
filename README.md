# GPR-ProvenanceBench

This repository contains manuscript and reproducibility materials for:

**Provenance-aware evaluation of ground-penetrating-radar recognition reveals fragile cross-environment generalization**

The study evaluates how ground-penetrating radar (GPR) recognition results change when public assets are audited and interpreted through provenance-aware splits, cross-environment transfer, duplicate and augmentation lineage checks, raw-trace stress tests, and repair or calibration controls.

## Repository Scope

This repository is intended to support manuscript review and reproducibility. It includes:

- manuscript source and compiled submission PDF;
- figure source files and rendered manuscript figures;
- experiment scripts and PowerShell run wrappers;
- environment records;
- protocol descriptions;
- sample manifests and split definitions;
- lightweight result summaries, source-data tables, and audit artifacts.

Raw third-party GPR files are not redistributed here. They should be obtained from their original providers under the applicable provider licences. Source-data tables, sample manifests, split definitions, protocol records, audit artifacts, figure source tables, and analysis code are available from the corresponding author upon reasonable request.

## Main Files

- `manuscript/nte_submission_20260812/main.tex`: manuscript source.
- `manuscript/nte_submission_20260812/main.pdf`: compiled manuscript PDF.
- `manuscript/nte_submission_20260812/figures/`: manuscript figures in PDF/PNG/SVG form.
- `manuscript/nte_submission_20260812/scripts/make_manuscript_figures.py`: script used to render the current manuscript figure set.
- `scripts/`: experiment, audit, manifest, split, and reporting scripts.
- `experiments/`: PowerShell wrappers for dated experiment runs.
- `data_manifests/`: sample-level manifests used by the experiments.
- `splits/`: frozen split assignments.
- `reports/`: lightweight result records and audit summaries.
- `environment/`: Python and package environment records.
- `protocols/`: protocol notes for raw-trace and external-validation components.

See `REPRODUCIBILITY.md` for a practical rerun guide.

## Data and Code Availability

Raw third-party GPR data are not redistributed by the authors. Derived metadata, file hashes, split assignments, result summaries, source-data tables, and audit records are retained to support reproducibility without redistributing restricted source files.

The analysis code and additional protocol records are available from the corresponding author upon reasonable request.

## Citation

If using these materials, please cite the associated manuscript once available.
