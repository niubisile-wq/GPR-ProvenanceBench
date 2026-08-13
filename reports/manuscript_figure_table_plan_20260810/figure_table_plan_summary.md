# Manuscript Figure/Table Plan 2026-08-10

Purpose: freeze the current claim-evidence-boundary map before making figures.

One-sentence argument: current evidence shows that GPR recognition performance is strongly affected by data source and environment transfer, with the strongest reproducible signal in Res-SAM cross-environment transfer; Mojahid and 4TU provide supporting or stress-test evidence, while blind external validation remains open.

## Main Figure Logic

1. Establish what assets are executable and what gates remain open.
2. Lead with the strongest cross-model result rather than the most convenient dataset.
3. Keep 4TU counterfactuals as stress-test evidence unless stronger grouped validation is added.
4. Report external blind validation as an open gate until a real asset passes the frozen protocol.

## Figure and Table Blueprint

| item | role | status | claim | boundary |
| --- | --- | --- | --- | --- |
| Figure 1 | Study design and evidence gates | ready_for_schematic | The project separates executable local evidence from unresolved confirmation gates. | This figure is a protocol/asset map, not a performance result. |
| Figure 2 | Five-model cross-model result matrix | ready_for_plot | Res-SAM environment transfer is the strongest current cross-model signal. | Scope is Mojahid and Res-SAM only; 4TU and blind external assets are not included in this matrix. |
| Figure 3 | Mojahid split inflation baseline | ready_with_caution | Mojahid random-minus-grouped performance inflation is directionally consistent but modest/model-dependent. | Do not frame as a universal leakage effect; only 1/5 model families reaches material support. |
| Figure 4 | 4TU raw-trace counterfactual stress test | ready_with_caution | 4TU multi-layer counterfactual stress-test evidence remains a feasibility-boundary layer rather than main confirmation. | This is stress-test and feasibility-boundary evidence, not final causal proof, main confirmation or blind external validation. |
| Figure 5 | 4TU feasibility and failure-mode map | ready_for_table_or_supplement | Current 4TU labels are insufficient for the main cross-model confirmation layer. | This is a gate/failure-mode result; it supports study design decisions, not model superiority. |
| Figure 6 | External blind validation gate | gate_open_not_result | Blind external validation remains unavailable under the frozen protocol. | The locked evaluation is template dry-run only; no manuscript claim can call it real blind external validation. |
| Table 1 | Dataset and asset audit | ready_for_table | Only Mojahid, 4TU and Res-SAM are executable local assets at this checkpoint; TIGPR is supporting-only. | Counts are local executable rows, not global dataset sizes. |
| Table 2 | Model-family support summary | ready_for_table | Cross-model material support is strong for Res-SAM transfer and weak for Mojahid split inflation. | Summary excludes 4TU and true blind external validation. |
| Table 3 | Gate status and remaining requirements | ready_for_internal_decision_table | The Nature Communications route remains conditional rather than submission-ready. | May be internal planning material unless the manuscript is framed as a benchmark/resource paper. |

## Claim-Evidence Details

### Figure 1: Study design and evidence gates

Claim: The project separates executable local evidence from unresolved confirmation gates.

Evidence: Asset inventory, unified manifests, TIGPR local NO-GO, Res-SAM local manifest, 4TU metadata/groupholdout feasibility, external validation readiness gate.

Source artifacts: `data_manifests/*_unified_samples_20260810.csv; reports/tigpr_local_asset_audit_20260810.md; reports/external_validation_readiness_20260810/external_validation_readiness_summary.md`

Status: `ready_for_schematic`

Boundary: This figure is a protocol/asset map, not a performance result.

Next action: Draw workflow schematic after finalizing visual style.

### Figure 2: Five-model cross-model result matrix

Claim: Res-SAM environment transfer is the strongest current cross-model signal.

Evidence: res_sam within_minus_transfer_real_world_to_synthetic: directional=5/5, material=5/5, mean_delta=0.4239, status=supported; res_sam within_minus_transfer_synthetic_to_real_world: directional=4/5, material=4/5, mean_delta=0.3743, status=supported; mojahid random_minus_grouped_balanced_accuracy: directional=5/5, material=1/5, mean_delta=0.0406, status=directional_only.

Source artifacts: `reports/five_model_synthesis_20260810/five_model_synthesis_summary.md; reports/five_model_synthesis_20260810/five_model_synthesis_model_rows.csv`

Status: `ready_for_plot`

Boundary: Scope is Mojahid and Res-SAM only; 4TU and blind external assets are not included in this matrix.

Next action: Plot model-family deltas and claim-level support counts.

### Figure 3: Mojahid split inflation baseline

Claim: Mojahid random-minus-grouped performance inflation is directionally consistent but modest/model-dependent.

Evidence: mojahid random_minus_grouped_balanced_accuracy: directional=5/5, material=1/5, mean_delta=0.0406, status=directional_only

Source artifacts: `reports/mojahid_hog_rbf_svm_seed_sweep_20260810/seed_sweep_summary.md; reports/five_model_synthesis_20260810/five_model_synthesis_claim_summary.csv`

Status: `ready_with_caution`

Boundary: Do not frame as a universal leakage effect; only 1/5 model families reaches material support.

Next action: Use as secondary panel or combine with Figure 2 rather than lead result.

### Figure 4: 4TU raw-trace counterfactual stress test

Claim: 4TU multi-layer counterfactual stress-test evidence remains a feasibility-boundary layer rather than main confirmation.

Evidence: HOG fixed-split Land type ExtraTrees log_clip BA_mean=0.0905, delta_mean=-0.3429, flip_mean=0.8583; group-aware selected ExtraTrees appears in 2/5 splits with log_clip delta_mean=-0.0422; the five-layer 4TU extension audit keeps all 4TU evidence as stress-test/feasibility-boundary evidence.

Source artifacts: `reports/4tu_counterfactual_hog_seed_sweep_20260810/hog_seed_sweep_summary.md; reports/4tu_counterfactual_hog_group_splits_20260810/hog_group_split_summary.md; reports/4tu_model_family_extension_audit_20260810/4tu_model_family_extension_audit.md`

Status: `ready_with_caution`

Boundary: This is stress-test and feasibility-boundary evidence, not final causal proof, main confirmation or blind external validation.

Next action: Plot fixed-split versus group-aware sensitivity side by side and add a five-layer evidence-boundary inset.

### Figure 5: 4TU feasibility and failure-mode map

Claim: Current 4TU labels are insufficient for the main cross-model confirmation layer.

Evidence: Land type=usable_with_caution; Land use=not_viable_for_group_holdout; Land cover=weak_due_to_single_project_labels; Utility crossing=usable_with_caution; Construction workers=not_viable_for_group_holdout; Relative groundwater level=weak_due_to_single_project_labels

Source artifacts: `reports/4tu_group_feasibility_20260810/4tu_group_feasibility_summary.md; reports/4tu_group_feasibility_20260810/4tu_group_feasibility_targets.csv`

Status: `ready_for_table_or_supplement`

Boundary: This is a gate/failure-mode result; it supports study design decisions, not model superiority.

Next action: Consider moving to Extended Data if main text is too crowded.

### Figure 6: External blind validation gate

Claim: Blind external validation remains unavailable under the frozen protocol.

Evidence: External readiness gate=NO-GO; tracks: A=not_ready; B=not_started; C=not_ready; D=already_used_in_model_matrix; locked evaluation mode=template_dry_run with status=PASS.

Source artifacts: `reports/external_validation_readiness_20260810/external_validation_readiness_summary.md; reports/external_blind_locked_evaluation_20260810/external_blind_locked_evaluation_summary.md`

Status: `gate_open_not_result`

Boundary: The locked evaluation is template dry-run only; no manuscript claim can call it real blind external validation.

Next action: Replace with real external result only after strict-sha manifest, frozen prediction and label unlock.

### Table 1: Dataset and asset audit

Claim: Only Mojahid, 4TU and Res-SAM are executable local assets at this checkpoint; TIGPR is supporting-only.

Evidence: Mojahid=2524 rows; 4TU=99 rows; Res-SAM=1050 rows; TIGPR=0 local executable rows.

Source artifacts: `data_manifests/*_unified_samples_20260810.csv; reports/tigpr_local_asset_audit_20260810.md`

Status: `ready_for_table`

Boundary: Counts are local executable rows, not global dataset sizes.

Next action: Render as dataset audit table.

### Table 2: Model-family support summary

Claim: Cross-model material support is strong for Res-SAM transfer and weak for Mojahid split inflation.

Evidence: mojahid random_minus_grouped_balanced_accuracy: directional=5/5, material=1/5, mean_delta=0.0406, status=directional_only; res_sam within_minus_transfer_real_world_to_synthetic: directional=5/5, material=5/5, mean_delta=0.4239, status=supported; res_sam within_minus_transfer_synthetic_to_real_world: directional=4/5, material=4/5, mean_delta=0.3743, status=supported

Source artifacts: `reports/five_model_synthesis_20260810/five_model_synthesis_claim_summary.csv`

Status: `ready_for_table`

Boundary: Summary excludes 4TU and true blind external validation.

Next action: Use as main or extended table depending on Figure 2 density.

### Table 3: Gate status and remaining requirements

Claim: The Nature Communications route remains conditional rather than submission-ready.

Evidence: External validation NO-GO; TIGPR NO-GO; 4TU not main confirmation; blind intake/evaluation template-ready only.

Source artifacts: `checkpoints/gate_status_20260810.md; checkpoints/checkpoint_20260810.md`

Status: `ready_for_internal_decision_table`

Boundary: May be internal planning material unless the manuscript is framed as a benchmark/resource paper.

Next action: Keep in checkpoint; decide later whether it becomes supplement.

## Manuscript Boundary

Do not write that the study has completed blind external validation. Do not present 4TU grouped results as a confirmed main-effect replication. Do not overstate Mojahid split inflation because material support is only 1/5 model families. The current main result should be framed around Res-SAM environment-transfer fragility, supported by secondary split and counterfactual stress-test evidence.
