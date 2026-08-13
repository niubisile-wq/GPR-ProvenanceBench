# Zenodo MCG GPR Split Stress

| split | train n | test n | mean shift | MAE | R2 | tertile BA |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| official_train_to_val | 630 | 168 | -0.0107 | 0.0404 | 0.3165 | 0.5466 |
| official_train_to_test | 630 | 168 | +0.0421 | 0.0454 | -0.1512 | 0.5305 |
| random_stratified_70_15 | 676 | 145 | -0.0011 | 0.0468 | 0.3257 | 0.5371 |
| random_stratified_70_15 | 676 | 145 | -0.0008 | 0.0428 | 0.3722 | 0.5393 |
| random_stratified_70_15 | 676 | 145 | +0.0035 | 0.0453 | 0.2735 | 0.5101 |
| random_stratified_70_15 | 676 | 145 | -0.0048 | 0.0493 | 0.1539 | 0.4341 |
| random_stratified_70_15 | 676 | 145 | -0.0020 | 0.0461 | 0.3305 | 0.5099 |

## Boundary

This is a public non-blind split-stress audit over a segmentation-derived
foreground-ratio task. It cannot close blind external validation.
