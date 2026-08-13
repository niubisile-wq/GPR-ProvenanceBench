# Res-SAM CORAL Mitigation Experiment

Run ID: `20260811_E01_ressam_hog_rbf_svm_coral_repair_seed_20260811`
Seed: `20260811`
Samples: `1050`

## Transfer Results

| train | test | train_n | test_n | baseline bal acc | mean/std bal acc | CORAL bal acc | mean/std delta | CORAL delta |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| synthetic | real_world | 450 | 300 | 0.4367 | 0.4633 | 0.4267 | +0.0267 | -0.0100 |
| real_world | synthetic | 300 | 450 | 0.3511 | 0.4778 | 0.4333 | +0.1267 | +0.0822 |

## Boundary

Mean/std alignment and CORAL use unlabeled target-environment images.
This is an internal mitigation stress test, not blind external validation
and not evidence that repair improves a locked external submission.
