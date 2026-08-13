# Res-SAM HOG + RBF-SVM Environment Transfer 2026-08-10

Samples: 1050
Seed: 20260810

## Overall Counts

| environment | label | count |
| --- | --- | ---: |
| real_world | cavity | 100 |
| real_world | crack | 100 |
| real_world | loose | 100 |
| real_world | manhole | 100 |
| real_world | normal | 100 |
| real_world | pipe | 100 |
| synthetic | cavity | 150 |
| synthetic | crack | 150 |
| synthetic | pipe | 150 |

## Within-Environment Random Baselines

| environment | train_n | test_n | balanced_accuracy | macro_f1 |
| --- | ---: | ---: | ---: | ---: |
| real_world | 480 | 120 | 0.8000 | 0.8017 |
| synthetic | 360 | 90 | 0.8889 | 0.8886 |

## Cross-Environment Transfer

Transfer uses only shared labels: `cavity`, `crack`, `pipe`.

| train | test | train_n | test_n | balanced_accuracy | macro_f1 |
| --- | --- | ---: | ---: | ---: | ---: |
| synthetic | real_world | 450 | 300 | 0.4367 | 0.3423 |
| real_world | synthetic | 300 | 450 | 0.3511 | 0.2034 |

## Boundary

This is a lightweight data-asset baseline, not a reproduction of the full
Res-SAM model. It tests environment transfer on published JPG exports with
a simple HOG+RBF-SVM model.
