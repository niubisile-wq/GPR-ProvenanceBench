# Mojahid HOG + RBF-SVM Seed Sweep 2026-08-10

Runs: 5
Seeds: [20260810, 20260811, 20260812, 20260813, 20260814]

## Split Summary

| split | metric | mean | std | min | max |
| --- | --- | ---: | ---: | ---: | ---: |
| random_stratified_80_20 | accuracy | 0.9580 | 0.0051 | 0.9525 | 0.9644 |
| random_stratified_80_20 | balanced_accuracy | 0.9543 | 0.0049 | 0.9489 | 0.9603 |
| random_stratified_80_20 | macro_f1 | 0.9546 | 0.0051 | 0.9492 | 0.9614 |
| grouped_fold_0_test_fold_1_val | accuracy | 0.8669 | 0.0000 | 0.8669 | 0.8669 |
| grouped_fold_0_test_fold_1_val | balanced_accuracy | 0.8566 | 0.0000 | 0.8566 | 0.8566 |
| grouped_fold_0_test_fold_1_val | macro_f1 | 0.8579 | 0.0000 | 0.8579 | 0.8579 |

## Random Minus Grouped

| metric | mean_delta | std | min | max |
| --- | ---: | ---: | ---: | ---: |
| accuracy | 0.0911 | 0.0051 | 0.0856 | 0.0975 |
| balanced_accuracy | 0.0976 | 0.0049 | 0.0923 | 0.1037 |
| macro_f1 | 0.0967 | 0.0051 | 0.0913 | 0.1035 |

## Interpretation Boundary

This seed sweep is still a Mojahid-only smoke/stability result. It supports
the split-sensitivity direction but cannot serve as final manuscript evidence
until repeated across independent assets and frozen split protocols.
