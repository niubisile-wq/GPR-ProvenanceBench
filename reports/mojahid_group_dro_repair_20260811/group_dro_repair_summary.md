# Mojahid Group-DRO Repair

Scope: train-only source-robust optimization on Mojahid HOG features.
No test-fold labels or target-fold statistics are used to choose repair parameters.

| protocol | strategy | BA | BA delta | worst-source acc | worst-source delta | ECE | ECE delta |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| current_fold0_test_fold1_val | erm | 0.7810 | +0.0000 | 0.0000 | +0.0000 | 0.1182 | +0.0000 |
| current_fold0_test_fold1_val | source_group_dro | 0.7632 | -0.0178 | 0.0000 | +0.0000 | 0.1393 | +0.0211 |
| current_fold0_test_fold1_val | label_source_group_dro | 0.7680 | -0.0130 | 0.0000 | +0.0000 | 0.1367 | +0.0185 |
| current_fold0_test_fold1_val | processing_role_dro | 0.7829 | +0.0018 | 0.0000 | +0.0000 | 0.1169 | -0.0013 |
| task_aware_fold0_test_fold3_val | erm | 0.8095 | +0.0000 | 0.0000 | +0.0000 | 0.0843 | +0.0000 |
| task_aware_fold0_test_fold3_val | source_group_dro | 0.8029 | -0.0066 | 0.1429 | +0.1429 | 0.0962 | +0.0119 |
| task_aware_fold0_test_fold3_val | label_source_group_dro | 0.8019 | -0.0075 | 0.1429 | +0.1429 | 0.0972 | +0.0129 |
| task_aware_fold0_test_fold3_val | processing_role_dro | 0.8119 | +0.0025 | 0.0000 | +0.0000 | 0.0821 | -0.0022 |

## Boundary

This is an internal train-time repair stress test. It can indicate whether
source-robust optimization helps the Mojahid grouped protocols, but it
does not establish blind external repair benefit.
