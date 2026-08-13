# Figure 5 and Figure 6 Source Data 2026-08-10

Purpose: freeze remaining gate/failure-mode source data before plotting.

Boundary: Figure 5 is a 4TU feasibility/failure-mode map. Figure 6 is an external blind-validation gate map. Neither should be written as a completed confirmation result.

## Figure 5: 4TU Feasibility Map

| target | status | samples | projects | labels | feasible/attempted | feasible fraction | interpretation |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| Land type | usable_with_caution | 93 | 9 | 4 | 708/756 | 0.9365 | usable with caution; still not main confirmation alone |
| Land use | not_viable_for_group_holdout | 93 | 9 | 5 | 0/756 | 0.0000 | not viable for grouped holdout |
| Land cover | weak_due_to_single_project_labels | 93 | 9 | 4 | 420/756 | 0.5556 | weak because labels are concentrated in too few projects |
| Utility crossing | usable_with_caution | 84 | 9 | 2 | 360/756 | 0.4762 | usable with caution; still not main confirmation alone |
| Construction workers | not_viable_for_group_holdout | 69 | 8 | 3 | 0/420 | 0.0000 | not viable for grouped holdout |
| Relative groundwater level | weak_due_to_single_project_labels | 93 | 9 | 3 | 60/756 | 0.0794 | weak because labels are concentrated in too few projects |

## Figure 6: External Blind Gate Map

| component | type | status | boundary | main result? |
| --- | --- | --- | --- | --- |
| Track A: TIGPR restoration | external_asset_track | not_ready | local TIGPR sample index has 0 rows, not 7169; no local root contains the complete TIGPR five-class directory layout; available GPR_data.rar identity is mojahid_gpr_data, not verified TIGPR | no |
| Track B: New third-party blind GPR image set | external_asset_track | not_started | no advisor-held or third-party blind manifest exists locally; no encrypted label file or label-holder protocol exists; no one-shot submission package exists | no |
| Track C: 4TU-like raw-trace external asset | external_asset_track | not_ready | current 4TU metadata labels are not strong enough for main cross-model confirmation; existing 4TU group-aware evidence remains a stress test | no |
| Track D: Current Res-SAM as external-looking heldout | external_asset_track | already_used_in_model_matrix | Res-SAM has already been used for model-family synthesis; using it again as blind external validation would contaminate main claims | no |
| Blind intake template validation | protocol_template | PASS | PASS validates structure and blinding contract only; it does not mean a real blind external asset is available. | no |
| Locked evaluation dry run | evaluation_template | template_dry_run | This is a template dry run only; it does not constitute blind external validation. | no |
| External validation readiness gate | overall_gate | NO-GO | No current track satisfies blind external validation readiness. The next concrete step is acquisition or restoration, not additional internal modeling. | no |

## Plotting Notes

1. Figure 5 should use target-level feasibility fractions plus status colors.
2. Figure 6 should use a gate diagram, not a performance chart.
3. Mark all Figure 6 components as not main results until a real strict-SHA external asset is evaluated.
4. Keep the text explicit that protocol readiness does not equal blind external validation.
