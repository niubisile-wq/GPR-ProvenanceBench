# Mojahid HOG + RBF-SVM Baseline 2026-08-10

This is the first frozen end-to-end model run under GPR-ProvenanceBench.

## Inputs

- Manifest: `data_manifests/mojahid_unified_samples_20260810.csv`
- Data root: `gpr_leakage_research/dataset_inspect/GPR_data`
- Samples: 2524
- Labels: {'cavity': 632, 'intact': 975, 'utility': 917}

## Split Results

| split | train_n | val_n | test_n | accuracy | balanced_accuracy | macro_f1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| random_stratified_80_20 | 2019 | 0 | 505 | 0.9644 | 0.9603 | 0.9614 |
| grouped_fold_0_test_fold_1_val | 1512 | 426 | 586 | 0.8669 | 0.8566 | 0.8579 |

## Interpretation Boundary

This is a G0 smoke baseline. It proves that one frozen model can run end to end,
but it is not a final manuscript claim and must be repeated across assets, seeds,
split protocols and model classes.
