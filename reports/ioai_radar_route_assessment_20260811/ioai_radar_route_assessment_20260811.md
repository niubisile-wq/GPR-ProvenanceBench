# IOAI 2025 Radar route assessment 2026-08-11

## Decision

Status: public benchmark route is executable for experiment-only fallback use.

This route is not blind external validation. It is a public benchmark
evaluation path with public scoring assets in the official IOAI-2025 repo.

## Evidence

- Official repo tree exposes `Individual-Contest/Radar/training_set` with 1800
  `.mat.pt` samples.
- Official repo tree exposes `Individual-Contest/Radar/Solution/validation_set`
  and `test_set`, each with 501 `.mat.pt` files plus public scoring metadata.
- `Solution/Scoring` includes `ground_truth_val.csv`, `ground_truth_test.csv`
  and `metrics.py`.
- `Radar.ipynb` is a full baseline notebook: it defines the train/test data
  loader, a simple 3-layer CNN, training loop, inference export, and submission
  zip creation.
- A local smoke probe on 4 training samples and 2 public evaluation samples
  completed successfully.
- A larger cached probe on 35 training samples and 2 public evaluation samples
  completed successfully.

## Local probe results

### Smoke probe

- Training samples: 4
- Validation samples: 2
- Test samples: 2
- Epochs: 1
- Validation weighted score: 0.0779
- Test weighted score: 0.0880

### Cached probe

- Training samples: 35
- Validation samples: 2
- Test samples: 2
- Epochs: 2
- Validation weighted score: 0.0238
- Test weighted score: 0.0129

## Boundary

This route can strengthen experiment closure because it is executable and
reproducible. It cannot be promoted to blind external validation because the
public scoring assets expose the labels.

## Operational consequence

If the original blind external path remains unavailable, the Radar route can be
used as the public benchmark fallback for experiment-only closure. It should
remain labelled as public benchmark evaluation in the paper-facing material and
in the internal experiment ledger.
