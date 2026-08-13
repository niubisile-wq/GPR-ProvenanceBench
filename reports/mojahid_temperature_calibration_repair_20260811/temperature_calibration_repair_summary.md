# Mojahid Temperature Calibration Repair

Scope: train/validation-only post-hoc calibration on Mojahid grouped splits.
The test fold is used once for final evaluation after temperature selection on the validation fold.

| protocol | T | uncal BA | cal BA | delta BA | uncal ECE | cal ECE | delta ECE |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| current_fold0_test_fold1_val | 3.700 | 0.7741 | 0.7741 | +0.0000 | 0.1651 | 0.0296 | -0.1355 |
| task_aware_fold0_test_fold3_val | 3.750 | 0.8210 | 0.8210 | +0.0000 | 0.1208 | 0.0297 | -0.0910 |

## Boundary

Temperature calibration can change confidence and ECE without changing
predicted classes. This is an internal grouped-split repair/calibration
test, not external repair validation.
