# 4TU Raw-Trace Counterfactual Audit Protocol 2026-08-10

## Purpose

This protocol turns the existing 4TU raw-trace matrix renderer into an auditable
counterfactual workflow. It is still M0-M2 protocol work, not final causal evidence.

The goal is to verify that deterministic variants can be generated from the same
underlying matrix while measuring how much each variant changes the rendered signal.

## Input

Frozen input manifest:

`reports/4tu_baseline_package_v1/package_manifest.csv`

Matrix input field:

`package_npy_path`

Minimum smoke sample:

1. up to three samples from `train`;
2. up to three samples from `val`;
3. up to three samples from `test`.

## Variant Classes

### Intensity Re-Rendering

These preserve trace geometry and alter display scaling.

1. `original`
2. `log_clip`
3. `zscore_clip`
4. `amplitude_jitter`

### Nuisance Suppression

These alter likely export or border nuisances while preserving most matrix content.

1. `remove_top_band`
2. `remove_bottom_band`
3. `remove_border`

### Destructive Negative Control

This deliberately violates physical orientation and must not be treated as a
physically equivalent counterfactual.

1. `time_reverse`

## Metrics

Each variant is compared against the original matrix after min-max normalization.

1. Pearson correlation.
2. MAE.
3. RMSE.
4. Top-band mean absolute delta.
5. Bottom-band mean absolute delta.
6. Border mean absolute delta.
7. Center mean absolute delta.

## Interpretation Rules

1. `log_clip`, `zscore_clip` and `amplitude_jitter` are rendering counterfactuals.
2. `remove_top_band`, `remove_bottom_band` and `remove_border` are nuisance
   suppression tests.
3. `time_reverse` is a destructive negative control.
4. A classifier result can enter main evidence only after this audit is run on a
   frozen sample manifest, frozen split protocol and predeclared model pipeline.
5. This audit alone does not prove causal reliance; it only proves that the
   counterfactual generation layer is deterministic and measurable.

## Current Next Step

Run the smoke audit:

```powershell
& GPR-ProvenanceBench\experiments\run_4tu_counterfactual_audit_smoke_20260810.ps1
```

