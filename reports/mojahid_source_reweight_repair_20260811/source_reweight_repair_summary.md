# Mojahid Source Reweighting Repair Sweep

Scope: train-only source/class reweighting on Mojahid grouped splits.
No target-fold images or labels are used to compute repair parameters.

Runs: `10`
Seeds: `20260811, 20260812, 20260813, 20260814, 20260815`

| protocol | uniform BA | class BA | source BA | label-source BA | best delta vs uniform |
| --- | ---: | ---: | ---: | ---: | ---: |
| current_fold0_test_fold1_val | 0.8566 | 0.8566 | 0.8424 | 0.8513 | +0.0000 |
| task_aware_fold0_test_fold3_val | 0.8744 | 0.8744 | 0.8501 | 0.8699 | +0.0000 |

## Boundary

This is a strict train-time internal repair experiment. It can bound whether
simple provenance-aware weighting helps on Mojahid, but it is not external
repair validation and cannot close the blind external gate.
