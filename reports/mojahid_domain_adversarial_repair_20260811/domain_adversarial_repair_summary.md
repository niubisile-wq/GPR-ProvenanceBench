# Mojahid Train-Only Domain-Adversarial Repair

A gradient-reversal network suppresses the binary original/augmented processing-role signal using training folds only. Checkpoint selection uses validation target balanced accuracy; test folds are never used for selection.

| protocol | lambda | target BA | delta vs ERM | domain BA | delta vs ERM |
| --- | ---: | ---: | ---: | ---: | ---: |
| current_fold0_test_fold1_val | 0.0 | 0.7425 | +0.0000 | 0.6605 | +0.0000 |
| current_fold0_test_fold1_val | 0.1 | 0.7351 | -0.0074 | 0.6479 | -0.0126 |
| current_fold0_test_fold1_val | 0.5 | 0.7388 | -0.0038 | 0.6418 | -0.0187 |
| current_fold0_test_fold1_val | 1.0 | 0.7421 | -0.0004 | 0.6039 | -0.0567 |
| task_aware_fold0_test_fold3_val | 0.0 | 0.7655 | +0.0000 | 0.6384 | +0.0000 |
| task_aware_fold0_test_fold3_val | 0.1 | 0.7684 | +0.0029 | 0.6455 | +0.0071 |
| task_aware_fold0_test_fold3_val | 0.5 | 0.7644 | -0.0011 | 0.6266 | -0.0118 |
| task_aware_fold0_test_fold3_val | 1.0 | 0.7601 | -0.0053 | 0.5876 | -0.0508 |

## Boundary

This is an internal train-only representation-invariance stress test over a processing-role proxy. It is not a real blind external repair result, and a lower domain probe is useful only if target generalization is retained.
