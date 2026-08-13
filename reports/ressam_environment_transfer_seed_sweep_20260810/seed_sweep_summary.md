# Res-SAM Environment-Transfer Seed Sweep 2026-08-10

Runs: 5
Seeds: [20260810, 20260811, 20260812, 20260813, 20260814]

## Within-Environment Baselines

| environment | metric | mean | std | min | max |
| --- | --- | ---: | ---: | ---: | ---: |
| real_world | accuracy | 0.8483 | 0.0308 | 0.8000 | 0.8750 |
| real_world | balanced_accuracy | 0.8483 | 0.0308 | 0.8000 | 0.8750 |
| real_world | macro_f1 | 0.8486 | 0.0303 | 0.8017 | 0.8753 |
| synthetic | accuracy | 0.9067 | 0.0279 | 0.8667 | 0.9333 |
| synthetic | balanced_accuracy | 0.9067 | 0.0279 | 0.8667 | 0.9333 |
| synthetic | macro_f1 | 0.9066 | 0.0275 | 0.8678 | 0.9338 |

## Cross-Environment Transfer

| direction | metric | mean | std | min | max |
| --- | --- | ---: | ---: | ---: | ---: |
| synthetic_to_real_world | accuracy | 0.4367 | 0.0000 | 0.4367 | 0.4367 |
| synthetic_to_real_world | balanced_accuracy | 0.4367 | 0.0000 | 0.4367 | 0.4367 |
| synthetic_to_real_world | macro_f1 | 0.3423 | 0.0000 | 0.3423 | 0.3423 |
| real_world_to_synthetic | accuracy | 0.3511 | 0.0000 | 0.3511 | 0.3511 |
| real_world_to_synthetic | balanced_accuracy | 0.3511 | 0.0000 | 0.3511 | 0.3511 |
| real_world_to_synthetic | macro_f1 | 0.2034 | 0.0000 | 0.2034 | 0.2034 |

## Within Minus Transfer

For each transfer direction, the within-environment baseline on the test
environment is subtracted by the corresponding transfer performance.

| direction | metric | mean_delta | std | min | max |
| --- | --- | ---: | ---: | ---: | ---: |
| synthetic_to_real_world | accuracy | 0.4117 | 0.0308 | 0.3633 | 0.4383 |
| synthetic_to_real_world | balanced_accuracy | 0.4117 | 0.0308 | 0.3633 | 0.4383 |
| synthetic_to_real_world | macro_f1 | 0.5063 | 0.0303 | 0.4594 | 0.5329 |
| real_world_to_synthetic | accuracy | 0.5556 | 0.0279 | 0.5156 | 0.5822 |
| real_world_to_synthetic | balanced_accuracy | 0.5556 | 0.0279 | 0.5156 | 0.5822 |
| real_world_to_synthetic | macro_f1 | 0.7033 | 0.0275 | 0.6644 | 0.7304 |

## Boundary

This is a lightweight HOG+RBF-SVM seed sweep on Res-SAM JPG exports.
It supports environment-shift auditing but is not a reproduction of the
full Res-SAM model.
