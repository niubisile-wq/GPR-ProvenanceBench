# 4TU Small-CNN Counterfactual Reliance 2026-08-10

Protocol: normalize raw matrix, resize to 64x64 grayscale, train a small CPU CNN on original train matrices, select best epoch by validation balanced accuracy, then evaluate original and variant test matrices.

## Target Status

| target | records | viable | best_epoch | val_BA |
| --- | ---: | --- | ---: | ---: |
| Land type | 93 | True | 39 | 0.3750 |
| Land cover | 93 | True | 23 | 0.4167 |
| Utility crossing | 84 | True | 1 | 0.5000 |
| Construction workers | 93 | True | 1 | 0.5000 |

## Largest Drops

| target | variant | test_BA | delta_BA | flip_rate |
| --- | --- | ---: | ---: | ---: |
| Land type | log_clip | 0.0238 | -0.4000 | 1.0000 |
| Land type | zscore_clip | 0.2000 | -0.2238 | 0.9167 |
| Land type | time_reverse | 0.3333 | -0.0905 | 0.1667 |
| Land cover | remove_border | 0.2485 | -0.0242 | 0.1667 |
| Land type | amplitude_jitter | 0.4238 | 0.0000 | 0.0000 |
| Land type | remove_bottom_band | 0.4238 | 0.0000 | 0.0000 |
| Land cover | amplitude_jitter | 0.2727 | 0.0000 | 0.0000 |
| Land cover | remove_bottom_band | 0.2727 | 0.0000 | 0.0000 |
| Utility crossing | log_clip | 0.5000 | 0.0000 | 0.0000 |
| Utility crossing | zscore_clip | 0.5000 | 0.0000 | 0.0000 |
| Utility crossing | amplitude_jitter | 0.5000 | 0.0000 | 0.0000 |
| Utility crossing | remove_top_band | 0.5000 | 0.0000 | 0.0000 |

## Boundary

This is a CPU proof-of-execution CNN. It establishes that the counterfactual pipeline can run with a learned image model, but it is single-seed and underpowered; final claims require repeated seeds, stronger tuning and external validation.
