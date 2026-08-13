# Mojahid Source-Confusion Feature Repair

Scope: train-only HOG feature selection penalizing source-predictive dimensions.

| protocol | best strategy | target BA delta | source-probe BA delta | tradeoff score |
| --- | --- | ---: | ---: | ---: |
| current_fold0_test_fold1_val | target_over_source_alpha_0_top_256 | +0.0000 | +0.0000 | +0.0000 |
| task_aware_fold0_test_fold3_val | target_over_source_alpha_0_top_256 | +0.0000 | +0.0000 | +0.0000 |

## Boundary

Feature selection scores are learned on train folds only. This is an
internal source-confusion repair stress test, not blind external repair
evidence and not a final mitigation claim.
