# Mojahid Source-Direction Residualization Repair

Scope: train-only projection removal of `is_augmented`-discriminative HOG directions.
The source basis is learned on training folds only, then applied to test folds.

| protocol | removed dirs | target BA | target BA delta | source BA | source BA delta |
| --- | ---: | ---: | ---: | ---: | ---: |
| current_fold0_test_fold1_val | 0 | 0.7741 | +0.0000 | 0.5737 | +0.0000 |
| current_fold0_test_fold1_val | 1 | 0.6876 | -0.0865 | 0.5000 | -0.0737 |
| task_aware_fold0_test_fold3_val | 0 | 0.8210 | +0.0000 | 0.5812 | +0.0000 |
| task_aware_fold0_test_fold3_val | 1 | 0.6807 | -0.1403 | 0.5000 | -0.0812 |

## Best Tradeoff

- Protocol: `task_aware_fold0_test_fold3_val`
- Removed source directions: `1`
- Target BA delta: `-0.1403`
- Source probe BA delta: `-0.0812`

## Boundary

This is an internal representation-repair stress test. It can show whether
simple linear source residualization suppresses source information, but it
does not establish external repair benefit.
