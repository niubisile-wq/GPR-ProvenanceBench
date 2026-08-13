# External Validation Readiness 2026-08-10

Purpose: freeze what must be true before any result can be called blind external validation.

Gate status: **NO-GO**.

Decision: no current track satisfies blind external validation readiness. TIGPR restoration is now complete as local evidence, but it cannot be relabeled as blind external validation.

## Track Summary

| track | name | role | status | next action |
| --- | --- | --- | --- | --- |
| A | TIGPR restoration | restored public local image dataset; not blind external validation | ready_as_restored_local_not_blind | Use TIGPR only as restored-local duplicate-aware evidence; do not count it as blind external validation because labels and media are visible. |
| B | New third-party blind GPR image set | primary blind external validation | not_started | Create a blind intake template and ask the label holder to provide sample IDs, raw files or images, and sealed labels. |
| C | 4TU-like raw-trace external asset | external raw-trace counterfactual confirmation | not_ready | Search for or request a 4TU-like raw-trace dataset with better project and label balance before expanding the full five-model matrix. |
| D | Current Res-SAM as external-looking heldout | not acceptable as blind external validation | already_used_in_model_matrix | Use Res-SAM for cross-model evidence and methods development only; acquire a separate blind asset for final validation. |

## Hard Requirements

- external asset is not used in model development
- manifest includes stable sample_id, rel_path or abs_path, file_sha256, label field placeholder, and source_group
- labels are unavailable to the analyst until predictions are frozen
- one prediction submission is allowed for main claims
- evaluation script, model versions, seeds, preprocessing, and thresholds are frozen before labels are opened
- post-hoc reruns are excluded from main claims and reported as exploratory only

## Track Details

### Track A: TIGPR restoration

Status: `ready_as_restored_local_not_blind`

Blocking facts:

Minimum entry requirements:
- authorized source download
- local source image tree under external_assets/tigpr
- 7169-row sample index
- class counts verified against prior audit
- duplicate-aware grouped split with duplicate groups locked within folds

Next action: Use TIGPR only as restored-local duplicate-aware evidence; do not count it as blind external validation because labels and media are visible.

### Track B: New third-party blind GPR image set

Status: `not_started`

Blocking facts:
- no advisor-held or third-party blind manifest exists locally
- no encrypted label file or label-holder protocol exists
- no one-shot submission package exists

Minimum entry requirements:
- data not used in model selection or threshold tuning
- labels held by advisor or third party until predictions are frozen
- sample IDs and hashes frozen before prediction
- single allowed submission for main claims
- label space harmonized to a predeclared target before model execution

Next action: Create a blind intake template and ask the label holder to provide sample IDs, raw files or images, and sealed labels.

### Track C: 4TU-like raw-trace external asset

Status: `not_ready`

Blocking facts:
- current 4TU metadata labels are not strong enough for main cross-model confirmation
- existing 4TU group-aware evidence remains a stress test

Minimum entry requirements:
- at least 10 independent projects or collection groups
- at least 2 labels in every train/validation/test grouped split
- held-out labels covered by training labels
- raw traces available for deterministic counterfactual rendering
- project-level split frozen before model execution

Next action: Search for or request a 4TU-like raw-trace dataset with better project and label balance before expanding the full five-model matrix.

### Track D: Current Res-SAM as external-looking heldout

Status: `already_used_in_model_matrix`

Blocking facts:
- Res-SAM has already been used for model-family synthesis
- using it again as blind external validation would contaminate main claims

Minimum entry requirements:
- can remain a core local data asset
- cannot be relabeled as blind external after current analyses

Next action: Use Res-SAM for cross-model evidence and methods development only; acquire a separate blind asset for final validation.

## Protocol Consequence

1. Res-SAM remains the strongest current cross-model evidence but cannot be reused as blind external validation.
2. 4TU remains a raw-trace counterfactual stress-test asset, not the main confirmation layer.
3. TIGPR restoration is complete as local duplicate-aware evidence, but not as blind external validation.
4. Final Nature Communications-level claims still require a separate blind external asset or an equivalent advisor-held validation protocol.
