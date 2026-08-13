# Mojahid Alignment Mitigation Sweep

Runs: `10`
Seeds: `20260811, 20260812, 20260813, 20260814, 20260815`

| protocol | baseline bal acc | mean/std bal acc | CORAL bal acc | mean/std delta | CORAL delta |
| --- | ---: | ---: | ---: | ---: | ---: |
| current_fold0_test_fold1_val | 0.8566 | 0.8690 | 0.8382 | +0.0124 | -0.0185 |
| task_aware_fold0_test_fold3_val | 0.8744 | 0.8828 | 0.8698 | +0.0084 | -0.0046 |

Boundary: this is an internal transductive mitigation stress test on
Mojahid grouped splits. It uses unlabeled test-fold images for feature
alignment and therefore cannot be used as blind external repair evidence.
