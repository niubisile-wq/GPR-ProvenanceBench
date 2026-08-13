# 4TU Land Type Alignment Repair Sweep

Runs: `5`
Target: `Land type`

| method | balanced accuracy | delta vs raw | macro-F1 |
| --- | ---: | ---: | ---: |
| raw_source_only | 0.3857 | +0.0000 | 0.2792 |
| per_matrix_zscore_source_only | 0.3714 | -0.0143 | 0.3270 |
| mean_std_unlabeled_target | 0.2762 | -0.1095 | 0.1875 |
| coral_unlabeled_target | 0.3429 | -0.0429 | 0.3149 |

Boundary: Land type is usable with caution on the P4 v2 split. The
mean/std and CORAL variants use unlabeled test-split feature statistics,
so they are transductive internal repair tests. The per-matrix zscore
variant is non-transductive.
