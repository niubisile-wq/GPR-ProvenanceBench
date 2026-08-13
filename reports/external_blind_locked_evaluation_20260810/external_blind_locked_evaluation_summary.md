# External Blind Locked Evaluation 2026-08-10

Status: **PASS**
Evaluation mode: **main_claim**

## Inputs

- manifest: `reports\external_blind_freeze_regression_20260811\synthetic_blind_manifest.csv`
- labels: `reports\external_blind_freeze_regression_20260811\synthetic_label_holdout.csv`
- predictions: `reports\external_blind_freeze_regression_20260811\synthetic_frozen_predictions.csv`

## Overall Metrics

- n: 240
- accuracy: 0.8166666666666667
- balanced_accuracy: 0.7094452540561547
- macro_f1: 0.7323625857182903
- labels: Crack, Interlayer_bonding_deficiency, Loose, No_damage, Void

## Issues

- none

## Boundary

This evaluation is eligible for main-claim reporting only if the prediction file was frozen before label unlock and the asset passed strict intake validation.
