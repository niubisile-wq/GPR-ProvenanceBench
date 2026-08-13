# Blind External Validation Protocol 2026-08-10

## Purpose

This protocol defines the only route by which a result can be called blind
external validation in the CNS GPR provenance project. It is designed to prevent
data reuse, label leakage, repeated submissions, and post-hoc model selection.

Current gate status: **NO-GO**.

Reason: no external asset currently satisfies the acquisition, label-holdout,
hashing, prediction-freeze, and unlock-evaluation requirements.

## One-Sentence Argument

In GPR B-scan recognition, we will test whether provenance-aware evaluation
better predicts external performance by applying frozen models to a previously
unused, label-hidden external asset, with the boundary that post-hoc reruns are
exploratory only.

## Roles

1. Data holder: prepares files and keeps labels inaccessible to the analyst.
2. Analyst: receives unlabeled samples, freezes preprocessing and predictions.
3. Auditor: verifies hashes, timestamps, scripts, model versions, and the single
   prediction submission.
4. Unlocker: releases labels only after the frozen prediction package is stored.

The same person must not both optimize the models and reveal labels before the
main prediction package is frozen.

## Required Files

Unlabeled intake manifest:

`data_manifests/external_blind_manifest_template_20260810.csv`

Label holdout template, held by the data holder:

`data_manifests/external_blind_label_holdout_template_20260810.csv`

Prediction submission template:

`data_manifests/external_blind_prediction_submission_template_20260810.csv`

Readiness validator:

`scripts/validate_external_blind_intake.py`

Locked evaluation script, used only after label unlock:

`scripts/evaluate_external_blind_submission.py`

## Intake Manifest Contract

The analyst-facing manifest must contain these columns:

1. `sample_id`: stable, unique ID assigned before prediction.
2. `rel_path`: path relative to the external asset root, if files are local.
3. `abs_path`: absolute path, if relative paths are not possible.
4. `file_sha256`: SHA256 of the raw file or exported image used for prediction.
5. `label_placeholder`: must be empty, `NA`, `HELD_OUT`, or `BLINDED`.
6. `source_group`: independent source, project, site, collection, or device group.
7. `asset_track`: one of `tigpr_restoration`, `third_party_blind`,
   `4tu_like_raw_trace`, or `other_external`.
8. `modality`: `image`, `raw_trace`, or `mixed`.
9. `target_task`: predeclared prediction target.
10. `notes`: optional non-label metadata.

Hard rule: the analyst-facing manifest must not contain real class labels,
diagnostic labels, split labels derived from the hidden outcome, or informal
label hints in `notes`.

## Label Holdout Contract

The label file must be stored outside the analyst workflow until unlock. It must
contain:

1. `sample_id`
2. `sealed_label`
3. `label_space_version`
4. `label_holder`
5. `sealed_timestamp`
6. `unlock_timestamp`
7. `unlock_authorized_by`

The label holder may provide a cryptographic hash of the sealed label file
before prediction, but not the label values.

## Prediction Submission Contract

The one-shot prediction file must contain:

1. `sample_id`
2. `predicted_label`
3. `prediction_score`
4. `model_family`
5. `model_version`
6. `preprocessing_version`
7. `seed`
8. `submission_id`
9. `prediction_timestamp`

Only one `submission_id` can be used for main-claim external validation. Any
later submission is exploratory and must be separated from the main claim.

## Freeze Sequence

1. Data holder prepares the external asset and sample list.
2. Analyst receives only the unlabeled intake manifest and raw files/images.
3. Analyst runs `validate_external_blind_intake.py` on the manifest.
4. Analyst freezes model family, model checkpoint or parameters, preprocessing,
   seeds, thresholds, evaluation script, and prediction format.
5. Analyst writes the prediction submission file once.
6. Auditor records file hashes for the manifest, model config, scripts, and
   prediction submission.
7. Unlocker releases the label holdout file.
8. Evaluation is run exactly once for the main claim with
   `evaluate_external_blind_submission.py --main-claim`.
9. Any rerun after unlock is marked exploratory and cannot replace the main
   external result.

## Minimum GO Criteria

A blind external track can move from NO-GO to GO only if all conditions below
are true:

1. The asset has not been used for model development, model selection, threshold
   tuning, prompt/protocol debugging, or figure selection.
2. The analyst-facing manifest has no labels or label hints.
3. Every sample has a unique `sample_id`.
4. Every available file has a stable SHA256.
5. `source_group` is present for grouped error analysis.
6. The label space is declared before prediction.
7. The prediction submission is frozen before labels are opened.
8. The label unlock event has a timestamp and authorization record.
9. The final report distinguishes main one-shot results from exploratory reruns.
10. The locked evaluation report is generated from the frozen manifest, unlocked
    label file and frozen prediction submission without changing any model output.

## Current Tracks

Track A, TIGPR restoration: not ready. Local sample index has zero rows and the
available `GPR_data.rar` has been identified as Mojahid rather than TIGPR.

Track B, third-party blind GPR image set: not started. This is the preferred
primary external validation route once an advisor or collaborator can hold labels.

Track C, 4TU-like raw-trace external asset: not ready. Current 4TU evidence is
valuable for counterfactual stress testing but is too label/project-limited for
main confirmation.

Track D, current Res-SAM heldout: not acceptable as blind external validation.
Res-SAM has already been used in the model matrix and cannot be reused as a
label-hidden external asset.

## Reporting Rules

The manuscript may state "blind external validation" only for results generated
under this protocol. Until then, current external-looking results must be named
more narrowly, such as "environment-transfer evaluation", "cross-source
transfer", or "held-out external-style stress test".

## Next Action

Use the templates and validator to prepare an empty but auditable intake package.
Once a new external asset is available, fill the manifest, run the validator,
freeze models and predictions, request label unlock, then run the locked
evaluation script once for the main claim.
