# 4TU Counterfactual Variant Audit 2026-08-10

Samples: 99
Variants: original, log_clip, zscore_clip, amplitude_jitter, remove_top_band, remove_bottom_band, remove_border, time_reverse

## Aggregate Metrics

| variant | pearson_r_mean | mae_mean | rmse_mean | border_mae_mean | center_mae_mean |
| --- | ---: | ---: | ---: | ---: | ---: |
| original | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| log_clip | 0.5790 | 0.2036 | 0.2230 | 0.1821 | 0.2074 |
| zscore_clip | 0.9573 | 0.0378 | 0.0644 | 0.0333 | 0.0385 |
| amplitude_jitter | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| remove_top_band | 0.9307 | 0.0072 | 0.0226 | 0.0220 | 0.0043 |
| remove_bottom_band | 1.0000 | 0.0000 | 0.0001 | 0.0001 | 0.0000 |
| remove_border | 0.9249 | 0.0065 | 0.0259 | 0.0200 | 0.0029 |
| time_reverse | -0.0006 | 0.0478 | 0.1005 | 0.0353 | 0.0498 |

## Boundary

This audit verifies deterministic counterfactual generation and
measurable variant deltas on the selected frozen package rows. It is
not yet a classifier-level causal reliance test.
