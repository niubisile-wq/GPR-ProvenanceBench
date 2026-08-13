#!/usr/bin/env python3
"""Build an experiment-only progress audit for GPR-ProvenanceBench."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "experiment_only_progress_20260811"


def read_json(rel_path: str) -> dict:
    return json.loads((BENCH_ROOT / rel_path).read_text(encoding="utf-8-sig"))


def exists(rel_path: str) -> bool:
    return (BENCH_ROOT / rel_path).exists()


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    five_model = read_json("reports/five_model_synthesis_20260810/five_model_synthesis_summary.json")
    planned_five_model = read_json(
        "reports/planned_five_model_synthesis_20260811/planned_five_model_synthesis_summary.json"
    )
    deit_tiny = read_json(
        "reports/deit_tiny_embedding_svm_matrix_20260811/deit_tiny_embedding_svm_summary.json"
    )
    external = read_json("reports/external_validation_readiness_20260810/external_validation_readiness_summary.json")
    tigpr_audit = read_json("reports/tigpr_local_asset_audit_20260810.json")
    res_sam_repair = read_json("reports/ressam_coral_repair_20260811/seed_sweep_summary.json")
    mojahid_repair = read_json("reports/mojahid_alignment_repair_20260811/seed_sweep_summary.json")
    nontransductive_repair = read_json("reports/ressam_nontransductive_repair_20260811/seed_sweep_summary.json")
    source_aug_repair = read_json("reports/ressam_source_style_aug_repair_20260811/seed_sweep_summary.json")
    four_tu_repair = read_json("reports/4tu_alignment_repair_20260811/seed_sweep_summary.json")
    mojahid_reweight_repair = read_json(
        "reports/mojahid_source_reweight_repair_20260811/source_reweight_repair_summary.json"
    )
    mojahid_reweight_protocols = mojahid_reweight_repair["protocols"]
    mojahid_calibration_repair = read_json(
        "reports/mojahid_temperature_calibration_repair_20260811/temperature_calibration_repair_summary.json"
    )
    mojahid_calibration_protocols = mojahid_calibration_repair["protocols"]
    mojahid_residualization_repair = read_json(
        "reports/mojahid_source_residualization_repair_20260811/source_residualization_repair_summary.json"
    )
    mojahid_residualization_protocols = mojahid_residualization_repair["protocols"]
    mojahid_group_dro_repair = read_json(
        "reports/mojahid_group_dro_repair_20260811/group_dro_repair_summary.json"
    )
    mojahid_group_dro_protocols = mojahid_group_dro_repair["protocols"]
    mojahid_domain_adversarial_repair = read_json(
        "reports/mojahid_domain_adversarial_repair_20260811/domain_adversarial_repair_summary.json"
    )
    mojahid_domain_adversarial_rows = {
        (row["protocol"], float(row["grl_lambda"])): row
        for row in mojahid_domain_adversarial_repair["aggregate_rows"]
    }
    leakage_dose = read_json("reports/mojahid_leakage_dose_20260811/dose_sweep_summary.json")
    tigpr_leakage_dose = read_json(
        "reports/tigpr_duplicate_leakage_dose_20260811/tigpr_duplicate_leakage_dose_summary.json"
    )
    source_predictability = read_json("reports/source_predictability_20260811/source_predictability_summary.json")
    source_tasks = {row["task"]: row for row in source_predictability["tasks"]}
    ressam_bootstrap = read_json("reports/ressam_transfer_bootstrap_ci_20260811/ressam_transfer_bootstrap_ci_summary.json")
    ressam_bootstrap_rows = {row["contrast"]: row for row in ressam_bootstrap["contrast_rows"]}
    association = read_json("reports/target_source_association_20260811/target_source_association_summary.json")
    association_rows = {row["task_id"]: row for row in association["task_rows"]}
    four_tu_task_association = read_json("reports/4tu_task_source_association_20260811/4tu_task_source_association_summary.json")
    four_tu_strongest_association = four_tu_task_association["strongest_project_association"]
    four_tu_stability = read_json("reports/4tu_stress_stability_20260811/4tu_stress_stability_summary.json")
    four_tu_stability_layers = {row["layer"]: row for row in four_tu_stability["layers"]}
    tigpr_restored = tigpr_audit.get("status") == "GO" and tigpr_audit.get("sample_index_rows") == 7169
    tigpr_duplicate = read_json("reports/tigpr_duplicate_aware_sweep_20260811/tigpr_duplicate_aware_summary.json")
    tigpr_model_matrix = read_json(
        "reports/tigpr_model_family_duplicate_matrix_20260811/tigpr_model_family_duplicate_summary.json"
    )
    raw_gpr_candidate = read_json(
        "reports/external_raw_gpr_candidate_probe_20260811/external_raw_gpr_candidate_probe_summary.json"
    )
    external_freeze_regression = read_json(
        "reports/external_blind_freeze_regression_20260811/external_blind_freeze_regression_summary.json"
    )
    external_intake_validation = read_json(
        "reports/external_blind_intake_20260810/external_blind_intake_validation_summary.json"
    )
    external_locked_evaluation = read_json(
        "reports/external_blind_locked_evaluation_20260810/external_blind_locked_evaluation_summary.json"
    )
    frozen_registry = read_json(
        "reports/frozen_experiment_registry_20260811/frozen_experiment_registry_summary.json"
    )
    zenodo_raw_audit = read_json(
        "reports/zenodo_gpr_raw_asset_audit_20260811/zenodo_gpr_raw_asset_audit_summary.json"
    )
    zenodo_trackc = read_json(
        "reports/zenodo_gpr_trackc_metadata_baseline_20260811/zenodo_gpr_trackc_metadata_baseline_summary.json"
    )
    zenodo_trackc_models = {row["model"]: row for row in zenodo_trackc["model_contrasts"]}
    zenodo_mcg_download = read_json(
        "reports/zenodo_mcg_gpr_download_20260811/zenodo_mcg_gpr_download_summary.json"
    )
    zenodo_mcg_manifest = read_json(
        "reports/zenodo_mcg_gpr_manifest_20260811/zenodo_mcg_gpr_manifest_summary.json"
    )
    zenodo_mcg_baseline = read_json(
        "reports/zenodo_mcg_gpr_nonblind_baseline_20260811/zenodo_mcg_gpr_nonblind_baseline_summary.json"
    )
    zenodo_mcg_split_stress = read_json(
        "reports/zenodo_mcg_gpr_split_stress_20260811/zenodo_mcg_gpr_split_stress_summary.json"
    )
    deepmask_audit = read_json(
        "reports/deepmask_gpr_asset_audit_20260811/deepmask_gpr_asset_audit_summary.json"
    )
    deepmask_matrix = read_json(
        "reports/deepmask_gpr_augmentation_leakage_matrix_20260811/deepmask_gpr_augmentation_leakage_summary.json"
    )
    cross_asset_collision = read_json(
        "reports/cross_asset_collision_audit_20260811/cross_asset_collision_audit_summary.json"
    )
    hidden_eval_candidate_audit = read_json(
        "reports/hidden_eval_candidate_audit_20260811/hidden_eval_candidate_audit_summary.json"
    )
    gate_consistency = read_json(
        "reports/experiment_gate_consistency_20260811/experiment_gate_consistency_summary.json"
    )
    split_audit = read_json(
        "reports/unified_split_manifest_audit_20260811/unified_split_manifest_audit_summary.json"
    )
    split_baseline = read_json(
        "reports/unified_split_baseline_20260811/unified_split_baseline_summary.json"
    )
    split_ranking = read_json(
        "reports/unified_split_model_ranking_audit_20260811/unified_split_model_ranking_audit_summary.json"
    )
    split_effect_stats = read_json(
        "reports/unified_split_effect_statistics_20260811/unified_split_effect_statistics_summary.json"
    )
    split_seed_stability = read_json(
        "reports/unified_split_seed_stability_20260811/unified_split_seed_stability_summary.json"
    )
    split_five_family = read_json(
        "reports/unified_split_five_family_matrix_20260811/unified_split_five_family_matrix_summary.json"
    )
    signflip_audit = read_json(
        "reports/local_signflip_permutation_audit_20260811/local_signflip_permutation_audit_summary.json"
    )
    signflip_rows = {
        f"{row['audit_family']}::{row['unit']}": row
        for row in signflip_audit["unified_rows"] + signflip_audit["four_tu_rows"]
    }

    modules = [
        {
            "module": "Asset inventory and unified sample manifests",
            "weight_percent": 8,
            "earned_percent": 8 if tigpr_restored else 7,
            "status": "complete_with_tigpr_sample_level_restored_deepmask_duplicate_mirror_audited_local_split_manifests_baseline_ranking_effect_stats_seed_stability_five_family_matrix_and_signflip_stats"
            if tigpr_restored
            else "mostly_complete_tigpr_sample_level_gap",
            "evidence": "data_manifests; splits; reports/tigpr_local_asset_audit_20260810.json; reports/deepmask_gpr_asset_audit_20260811/deepmask_gpr_asset_audit_summary.json; reports/deepmask_gpr_augmentation_leakage_matrix_20260811/deepmask_gpr_augmentation_leakage_summary.json; reports/cross_asset_collision_audit_20260811/cross_asset_collision_audit_summary.json; reports/unified_split_manifest_audit_20260811/unified_split_manifest_audit_summary.json; reports/unified_split_baseline_20260811/unified_split_baseline_summary.json; reports/unified_split_model_ranking_audit_20260811/unified_split_model_ranking_audit_summary.json; reports/unified_split_effect_statistics_20260811/unified_split_effect_statistics_summary.json; reports/unified_split_seed_stability_20260811/unified_split_seed_stability_summary.json; reports/unified_split_five_family_matrix_20260811/unified_split_five_family_matrix_summary.json; reports/local_signflip_permutation_audit_20260811/local_signflip_permutation_audit_summary.json",
            "basis": (
                "Mojahid, 4TU, Res-SAM, TIGPR and DeepMask/GPR_data unified sample manifests exist. "
                f"Latest TIGPR local audit status={tigpr_audit['status']}; "
                f"sample_index_rows={tigpr_audit.get('sample_index_rows')}. "
                f"DeepMask/GPR_data adds {deepmask_audit['rows']} labelled image rows, "
                f"{deepmask_audit['base_source_groups']} base source groups and a 60-run augmentation/source-group matrix; "
                f"best random-minus-group-holdout BA={deepmask_matrix['best_random_minus_best_group_holdout_ba']:+.4f}. "
                "Cross-asset collision audit shows DeepMask/GPR_data is a complete SHA duplicate of Mojahid, "
                f"leaving {cross_asset_collision['independent_asset_clusters_by_hash']} independent hash clusters, "
                "so DeepMask is counted only as a duplicate mirror/stress asset, not an independent external asset. "
                "Local executable split manifests now cover "
                f"{split_audit['split_manifest_rows']} dataset/protocol pairs across "
                f"{len(split_audit['datasets'])} dataset ids, and unified split baselines show largest random-minus-protocol BA gaps of "
                f"{split_baseline['dataset_summaries']['mojahid']['largest_random_minus_protocol_ba']:+.4f} for Mojahid, "
                f"{split_baseline['dataset_summaries']['tigpr']['largest_random_minus_protocol_ba']:+.4f} for TIGPR and "
                f"{split_baseline['dataset_summaries']['zenodo_14637589']['largest_random_minus_protocol_ba']:+.4f} for Zenodo. "
                "Two-model ranking audit shows top-model flips versus random split in "
                f"{split_ranking['dataset_summaries']['mojahid']['top_model_flip_count_vs_random']} Mojahid protocols, "
                f"{split_ranking['dataset_summaries']['tigpr']['top_model_flip_count_vs_random']} TIGPR protocols and "
                f"{split_ranking['dataset_summaries']['zenodo_14637589']['top_model_flip_count_vs_random']} Zenodo protocols. "
                f"Bootstrap split-effect statistics add {len(split_effect_stats['contrasts'])} random-minus-protocol contrasts "
                f"and {split_effect_stats['prediction_rows']} per-sample prediction rows. "
                f"Five-seed split-stability audit adds {len(split_seed_stability['runs'])} local runs with largest mean "
                "random-minus-protocol BA gaps of "
                f"{split_seed_stability['dataset_summaries']['mojahid']['largest_mean_random_minus_protocol_ba']:+.4f} for Mojahid, "
                f"{split_seed_stability['dataset_summaries']['tigpr']['largest_mean_random_minus_protocol_ba']:+.4f} for TIGPR and "
                f"{split_seed_stability['dataset_summaries']['zenodo_14637589']['largest_mean_random_minus_protocol_ba']:+.4f} for Zenodo and "
                f"{split_seed_stability['dataset_summaries']['deepmask_gpr']['largest_mean_random_minus_protocol_ba']:+.4f} for DeepMask/GPR_data. "
                f"Five-family split matrix adds {len(split_five_family['runs'])} local model/protocol runs and top-model flip counts of "
                f"{split_five_family['dataset_summaries']['mojahid']['top_model_flip_count_vs_random']} for Mojahid, "
                f"{split_five_family['dataset_summaries']['tigpr']['top_model_flip_count_vs_random']} for TIGPR and "
                f"{split_five_family['dataset_summaries']['zenodo_14637589']['top_model_flip_count_vs_random']} for Zenodo and "
                f"{split_five_family['dataset_summaries']['deepmask_gpr']['top_model_flip_count_vs_random']} for DeepMask/GPR_data. "
                "Exact sign/sign-flip statistics over unified split contrasts show "
                f"{signflip_rows['unified_split_random_minus_protocol::all_assets']['positive_count']}/"
                f"{signflip_rows['unified_split_random_minus_protocol::all_assets']['n_contrasts']} positive contrasts, "
                f"sign p={signflip_rows['unified_split_random_minus_protocol::all_assets']['exact_sign_positive_tail_p']:.4f} "
                f"and mean sign-flip p={signflip_rows['unified_split_random_minus_protocol::all_assets']['exact_signflip_mean_positive_p']:.4f}. "
                "TIGPR duplicate-aware sweep confirms hash-group split has zero shared duplicate groups and "
                f"random-minus-group HOG balanced-accuracy delta="
                f"{tigpr_duplicate['random_minus_group']['random_minus_group_hog_balanced_accuracy']['mean']:+.4f}. "
                "The TIGPR duplicate model-family matrix shows "
                f"{tigpr_model_matrix['claim_summary']['directional_support_count']}/"
                f"{tigpr_model_matrix['claim_summary']['n_model_families']} directional support and "
                f"{tigpr_model_matrix['claim_summary']['material_support_count']}/"
                f"{tigpr_model_matrix['claim_summary']['n_model_families']} material support."
                if tigpr_restored
                else (
                    "Mojahid, 4TU and Res-SAM unified sample manifests exist; TIGPR remains sample-level incomplete. "
                    f"Latest TIGPR local audit status={tigpr_audit['status']} with {len(tigpr_audit.get('blockers', []))} blockers."
                )
            ),
            "remaining_gap": "None for local sample-level asset inventory; blind external validation remains separate."
            if tigpr_restored
            else "TIGPR has no usable local sample-level image tree; third asset lock remains conditional.",
        },
        {
            "module": "Mojahid split-sensitivity experiments",
            "weight_percent": 8,
            "earned_percent": 8,
            "status": "complete_as_secondary_directional_evidence",
            "evidence": "reports/mojahid_hog_rbf_svm_seed_sweep_20260810/seed_sweep_summary.json",
            "basis": "Five-model synthesis reports 5/5 directional support but only 1/5 material support for random-minus-grouped inflation.",
            "remaining_gap": "Use as secondary directional evidence, not the main universal claim.",
        },
        {
            "module": "Res-SAM environment-transfer experiments",
            "weight_percent": 15,
            "earned_percent": 15,
            "status": "complete_as_current_lead_internal_result_with_cross_model_ci",
            "evidence": "reports/five_model_synthesis_20260810/five_model_synthesis_summary.json; reports/ressam_transfer_bootstrap_ci_20260811/ressam_transfer_bootstrap_ci_summary.json",
            "basis": (
                "Both transfer directions are supported in five-model synthesis; material support is 5/5 and 4/5 across model families. "
                f"Cross-model bootstrap CIs are "
                f"[{ressam_bootstrap_rows['within_minus_transfer_real_world_to_synthetic']['ci95_low']:.4f}, "
                f"{ressam_bootstrap_rows['within_minus_transfer_real_world_to_synthetic']['ci95_high']:.4f}] "
                "for real_world->synthetic and "
                f"[{ressam_bootstrap_rows['within_minus_transfer_synthetic_to_real_world']['ci95_low']:.4f}, "
                f"{ressam_bootstrap_rows['within_minus_transfer_synthetic_to_real_world']['ci95_high']:.4f}] "
                "for synthetic->real_world."
            ),
            "remaining_gap": "This is not blind external validation because Res-SAM is already used in model development.",
        },
        {
            "module": "Source predictability / provenance signal experiments",
            "weight_percent": 9,
            "earned_percent": 9,
            "status": "complete_for_internal_h1_signal_and_association_metrics",
            "evidence": "reports/source_predictability_20260811/source_predictability_summary.json; reports/target_source_association_20260811/target_source_association_summary.json",
            "basis": (
                "Internal source-signal probes show learnable provenance: "
                f"Res-SAM environment balanced accuracy={source_tasks['ressam_environment_source_group']['metrics']['balanced_accuracy']['mean']:.4f} "
                f"versus chance={source_tasks['ressam_environment_source_group']['chance_balanced_accuracy']:.4f}; "
                f"Mojahid lineage balanced accuracy={source_tasks['mojahid_augmentation_lineage_source_group']['metrics']['balanced_accuracy']['mean']:.4f} "
                f"versus chance={source_tasks['mojahid_augmentation_lineage_source_group']['chance_balanced_accuracy']:.4f}. "
                f"Manifest association audit reports Mojahid label-source_group NMI={association_rows['mojahid_label_vs_source_group']['normalized_mutual_information']:.4f} "
                f"and Res-SAM label-environment NMI={association_rows['ressam_label_vs_environment']['normalized_mutual_information']:.4f}."
            ),
            "remaining_gap": "This proves internal provenance signal recoverability, not external generalization.",
        },
        {
            "module": "Cross-model synthesis",
            "weight_percent": 9,
            "earned_percent": 9,
            "status": "complete_for_current_internal_claim_boundary",
            "evidence": "reports/planned_five_model_synthesis_20260811/planned_five_model_synthesis_summary.json; reports/deit_tiny_embedding_svm_matrix_20260811/deit_tiny_embedding_svm_summary.json; reports/unified_split_five_family_matrix_20260811/unified_split_five_family_matrix_summary.json; reports/frozen_experiment_registry_20260811/frozen_experiment_registry_summary.json",
            "basis": (
                f"Legacy model rows={len(five_model.get('model_rows', []))}; "
                f"planned-family model rows={len(planned_five_model.get('model_rows', []))}; "
                f"planned-family claim summaries={len(planned_five_model.get('claim_summary', []))}. "
                f"The explicitly planned DeiT-Tiny slot now uses {deit_tiny['architecture']} with "
                f"{len(deit_tiny['seeds'])} seeds, {deit_tiny['embedding_dim']}-dimensional embeddings and "
                f"weight status={deit_tiny['weights']['loaded']}. "
                f"Unified split five-family matrix adds {len(split_five_family['runs'])} runs across "
                f"{len(split_five_family['datasets'])} assets, {len(split_five_family['protocols'])} protocols and five lightweight families per asset. "
                f"Frozen experiment registry records {frozen_registry['registry_rows']} artifacts with "
                f"{frozen_registry['missing_required_rows']} missing required rows and {frozen_registry['hashed_file_rows']} hashed files."
            ),
            "remaining_gap": "The named architecture slots are now present for Mojahid/Res-SAM directional evidence, but ResNet18, EfficientNetB0 and DeiT-Tiny are frozen-embedding baselines rather than end-to-end fine-tuned models, and no real blind external matrix exists.",
        },
        {
            "module": "4TU raw-trace counterfactual and stress-test experiments",
            "weight_percent": 12,
            "earned_percent": 12,
            "status": "complete_as_feasibility_and_boundary_evidence_with_task_source_and_stability_audits",
            "evidence": "reports/4tu_model_family_extension_audit_20260810/4tu_model_family_extension_audit_summary.json; reports/4tu_task_source_association_20260811/4tu_task_source_association_summary.json; reports/4tu_stress_stability_20260811/4tu_stress_stability_summary.json; reports/zenodo_gpr_raw_asset_audit_20260811/zenodo_gpr_raw_asset_audit_summary.json; reports/zenodo_gpr_trackc_metadata_baseline_20260811/zenodo_gpr_trackc_metadata_baseline_summary.json",
            "basis": (
                "Raw-trace-derived HOG, pixel and small-CNN stress tests exist, but current 4TU labels do not support full main confirmation. "
                f"Task-level label/source audit shows strongest project association for {four_tu_strongest_association['target_field']} "
                f"with NMI={four_tu_strongest_association['normalized_mutual_information']:.4f} "
                f"and Cramer's V={four_tu_strongest_association['cramers_v']:.4f}. "
                f"Stress stability audit shows log_clip fixed-split mean delta "
                f"{four_tu_stability_layers['fixed_split_seed_sweep']['delta']['mean']:.4f} versus group-aware mean delta "
                f"{four_tu_stability_layers['group_aware_project_splits']['delta']['mean']:.4f}, reinforcing the feasibility-boundary interpretation. "
                "The sign-flip audit gives fixed-split log_clip negative-tail sign p="
                f"{signflip_rows['4tu_log_clip_stress_delta::fixed_split_seed_sweep']['exact_sign_negative_tail_p']:.4f} "
                "and group-aware negative-tail sign p="
                f"{signflip_rows['4tu_log_clip_stress_delta::group_aware_project_splits']['exact_sign_negative_tail_p']:.4f}. "
                "Zenodo public raw-GPR Track C is downloaded, MD5-verified, extracted and manifested with "
                f"{zenodo_raw_audit['manifest_rows']} raw-trace rows; its metadata/byte-signature baseline shows "
                f"ExtraTrees random BA={zenodo_trackc_models['extra_trees']['random_balanced_accuracy']['mean']:.4f} "
                f"versus project-group BA={zenodo_trackc_models['extra_trees']['group_balanced_accuracy']['mean']:.4f}."
            ),
            "remaining_gap": "Zenodo strengthens non-blind raw-GPR stress evidence but remains public/non-blind; main external confirmation still needs label-held validation.",
        },
        {
            "module": "Leakage-dose experiments",
            "weight_percent": 10,
            "earned_percent": 10,
            "status": "mojahid_lineage_dose_plus_tigpr_duplicate_dose_complete_for_local_cross_asset_boundary",
            "evidence": "reports/mojahid_leakage_dose_20260811/dose_sweep_summary.json; reports/tigpr_duplicate_leakage_dose_20260811/tigpr_duplicate_leakage_dose_summary.json",
            "basis": (
                "Controlled lineage leakage doses 0/5/10/20/40% were run across five seeds. "
                f"Balanced accuracy changed from {leakage_dose['dose_summary']['0.00']['balanced_accuracy']['mean']:.4f} "
                f"at dose 0 to {leakage_dose['dose_summary']['0.40']['balanced_accuracy']['mean']:.4f} "
                "at dose 0.40; confidence, ECE and class-level error-structure metrics are recorded for the same dose curve. "
                "TIGPR duplicate leakage doses add a restored-local second-asset dose stress test: "
                f"hash-group baseline BA={tigpr_leakage_dose['dose_summary']['0.00']['balanced_accuracy']['mean']:.4f}, "
                f"dose 0.20 delta={tigpr_leakage_dose['dose_summary']['0.20']['delta_vs_dose0_balanced_accuracy']['mean']:+.4f}, "
                f"and dose 0.40 delta={tigpr_leakage_dose['dose_summary']['0.40']['delta_vs_dose0_balanced_accuracy']['mean']:+.4f}."
            ),
            "remaining_gap": "Dose-response is now local cross-asset evidence, but TIGPR uses duplicate-group leakage rather than the Mojahid lineage mechanism and remains non-blind.",
        },
        {
            "module": "Repair / mitigation experiments",
            "weight_percent": 9,
            "earned_percent": 9,
            "status": "three_asset_repair_boundary_plus_train_only_reweighting_calibration_residualization_group_dro_and_domain_adversarial_repair_established",
            "evidence": "reports/ressam_coral_repair_20260811/seed_sweep_summary.json; reports/mojahid_alignment_repair_20260811/seed_sweep_summary.json; reports/ressam_nontransductive_repair_20260811/seed_sweep_summary.json; reports/ressam_source_style_aug_repair_20260811/seed_sweep_summary.json; reports/4tu_alignment_repair_20260811/seed_sweep_summary.json; reports/mojahid_source_reweight_repair_20260811/source_reweight_repair_summary.json; reports/mojahid_temperature_calibration_repair_20260811/temperature_calibration_repair_summary.json; reports/mojahid_source_residualization_repair_20260811/source_residualization_repair_summary.json; reports/mojahid_group_dro_repair_20260811/group_dro_repair_summary.json; reports/mojahid_domain_adversarial_repair_20260811/domain_adversarial_repair_summary.json",
            "basis": (
                "Res-SAM mean/std alignment improved balanced accuracy in both transfer directions "
                f"({res_sam_repair['transfer']['synthetic_to_real_world']['delta_mean_std_minus_baseline']['balanced_accuracy']['mean']:+.4f}, "
                f"{res_sam_repair['transfer']['real_world_to_synthetic']['delta_mean_std_minus_baseline']['balanced_accuracy']['mean']:+.4f}). "
                "Mojahid mean/std alignment also improved balanced accuracy under both grouped protocols "
                f"({mojahid_repair['protocols']['current_fold0_test_fold1_val']['delta_mean_std_minus_baseline']['balanced_accuracy']['mean']:+.4f}, "
                f"{mojahid_repair['protocols']['task_aware_fold0_test_fold3_val']['delta_mean_std_minus_baseline']['balanced_accuracy']['mean']:+.4f}). "
                "Train-only gradient-reversal repair at lambda=1.0 reduced processing-role domain BA by "
                f"{mojahid_domain_adversarial_rows[('current_fold0_test_fold1_val', 1.0)]['domain_ba_delta_vs_erm']:+.4f} "
                "with target BA change "
                f"{mojahid_domain_adversarial_rows[('current_fold0_test_fold1_val', 1.0)]['target_ba_delta_vs_erm']:+.4f}; "
                "under the task-aware protocol the domain BA change was "
                f"{mojahid_domain_adversarial_rows[('task_aware_fold0_test_fold3_val', 1.0)]['domain_ba_delta_vs_erm']:+.4f} "
                "with target BA change "
                f"{mojahid_domain_adversarial_rows[('task_aware_fold0_test_fold3_val', 1.0)]['target_ba_delta_vs_erm']:+.4f}. "
                "Non-transductive per-image zscore was nearly neutral "
                f"({nontransductive_repair['transfer']['synthetic_to_real_world']['per_image_zscore']['balanced_accuracy']['mean'] - nontransductive_repair['transfer']['synthetic_to_real_world']['raw']['balanced_accuracy']['mean']:+.4f}, "
                f"{nontransductive_repair['transfer']['real_world_to_synthetic']['per_image_zscore']['balanced_accuracy']['mean'] - nontransductive_repair['transfer']['real_world_to_synthetic']['raw']['balanced_accuracy']['mean']:+.4f}); "
                "source-side style augmentation was negative in both transfer directions "
                f"({max(value['balanced_accuracy']['mean'] for key, value in source_aug_repair['transfer']['synthetic_to_real_world'].items() if key.startswith('source_style_aug_to_')) - source_aug_repair['transfer']['synthetic_to_real_world']['raw_source_to_raw_target']['balanced_accuracy']['mean']:+.4f}, "
                f"{max(value['balanced_accuracy']['mean'] for key, value in source_aug_repair['transfer']['real_world_to_synthetic'].items() if key.startswith('source_style_aug_to_')) - source_aug_repair['transfer']['real_world_to_synthetic']['raw_source_to_raw_target']['balanced_accuracy']['mean']:+.4f}); "
                "4TU Land type alignment was negative on balanced accuracy for mean/std and CORAL "
                f"({four_tu_repair['split']['delta_mean_std_minus_raw']['balanced_accuracy']['mean']:+.4f}, "
                f"{four_tu_repair['split']['delta_coral_minus_raw']['balanced_accuracy']['mean']:+.4f}). "
                "Mojahid train-only source reweighting did not improve balanced accuracy; "
                f"source-balanced deltas were {mojahid_reweight_protocols['current_fold0_test_fold1_val']['delta_source_balanced_minus_uniform']['balanced_accuracy']['mean']:+.4f} "
                f"and {mojahid_reweight_protocols['task_aware_fold0_test_fold3_val']['delta_source_balanced_minus_uniform']['balanced_accuracy']['mean']:+.4f}. "
                "Mojahid validation-only temperature calibration reduced ECE "
                f"({mojahid_calibration_protocols['current_fold0_test_fold1_val']['delta_temperature_calibrated_minus_uncalibrated']['ece_10bin']['mean']:+.4f}, "
                f"{mojahid_calibration_protocols['task_aware_fold0_test_fold3_val']['delta_temperature_calibrated_minus_uncalibrated']['ece_10bin']['mean']:+.4f}) "
                "without changing balanced accuracy. Mojahid train-only source-direction residualization using is_augmented source signal reduced source-probe BA "
                f"({mojahid_residualization_protocols['current_fold0_test_fold1_val']['1']['delta_source_probe_minus_k0']['balanced_accuracy']['mean']:+.4f}, "
                f"{mojahid_residualization_protocols['task_aware_fold0_test_fold3_val']['1']['delta_source_probe_minus_k0']['balanced_accuracy']['mean']:+.4f}) "
                "but also reduced target BA "
                f"({mojahid_residualization_protocols['current_fold0_test_fold1_val']['1']['delta_target_minus_k0']['balanced_accuracy']['mean']:+.4f}, "
                f"{mojahid_residualization_protocols['task_aware_fold0_test_fold3_val']['1']['delta_target_minus_k0']['balanced_accuracy']['mean']:+.4f}). "
                "Mojahid group-DRO repair adds source_group, label-source_group and processing-role robust optimization; "
                "source_group DRO target BA deltas were "
                f"{mojahid_group_dro_protocols['current_fold0_test_fold1_val']['delta_source_group_dro_minus_erm']['balanced_accuracy']['mean']:+.4f} "
                f"and {mojahid_group_dro_protocols['task_aware_fold0_test_fold3_val']['delta_source_group_dro_minus_erm']['balanced_accuracy']['mean']:+.4f}, "
                "while processing-role DRO deltas were "
                f"{mojahid_group_dro_protocols['current_fold0_test_fold1_val']['delta_processing_role_dro_minus_erm']['balanced_accuracy']['mean']:+.4f} "
                f"and {mojahid_group_dro_protocols['task_aware_fold0_test_fold3_val']['delta_processing_role_dro_minus_erm']['balanced_accuracy']['mean']:+.4f}. "
                "CORAL remains mixed, simple train-time reweighting should not be treated as a repair winner, calibration only fixes confidence, "
                "naive source residualization shows a source-performance trade-off, and group-DRO gives only tiny processing-role gains."
            ),
            "remaining_gap": "Repair is not a universal positive result: target-statistic alignment helps on Res-SAM/Mojahid, but strict non-transductive variants, 4TU alignment, Mojahid train-only reweighting, source-group DRO and naive source residualization do not show stable target gains; calibration improves ECE only.",
        },
        {
            "module": "Blind external validation",
            "weight_percent": 20,
            "earned_percent": 0,
            "status": "no_go_real_blind_asset_missing_synthetic_freeze_regression_passed_hidden_eval_candidates_audited",
            "evidence": "reports/external_validation_readiness_20260810/external_validation_readiness_summary.json; reports/external_blind_freeze_regression_20260811/external_blind_freeze_regression_summary.json; reports/external_blind_intake_20260810/external_blind_intake_validation_summary.json; reports/external_blind_locked_evaluation_20260810/external_blind_locked_evaluation_summary.json; reports/hidden_eval_candidate_audit_20260811/hidden_eval_candidate_audit_summary.json; reports/experiment_gate_consistency_20260811/experiment_gate_consistency_summary.json",
            "basis": (
                f"External gate status={external.get('gate', {}).get('status')}; "
                f"ready tracks={len(external.get('gate', {}).get('current_ready_tracks', []))}. "
                "Synthetic blind-freeze regression passed with "
                f"{external_freeze_regression['n_synthetic_blind']} held-out TIGPR fixture rows, "
                f"strict intake status={external_intake_validation['status']} and locked evaluation status="
                f"{external_locked_evaluation['status']}; prediction precedes synthetic unlock="
                f"{external_freeze_regression['prediction_precedes_unlock']}. "
                f"Hidden-evaluation candidate audit screened {hidden_eval_candidate_audit['candidate_count']} current GPR-related candidates "
                f"and found {hidden_eval_candidate_audit['eligible_candidate_count']} candidates satisfying all blind-gate criteria. "
                f"Gate consistency validator status={gate_consistency['status']} with {gate_consistency['pass_count']} pass checks."
            ),
            "remaining_gap": "Requires a real held-out external asset with labels unavailable before one-shot prediction.",
        },
    ]

    total_weight = sum(int(row["weight_percent"]) for row in modules)
    earned = sum(int(row["earned_percent"]) for row in modules)
    completion = round(earned / total_weight * 100, 1)

    qa_rows = [
        {
            "check": "weights sum to 100",
            "result": "PASS" if total_weight == 100 else "FAIL",
            "detail": f"total_weight={total_weight}",
        },
        {
            "check": "module evidence exists",
            "result": "PASS"
            if all(all(exists(part.strip()) for part in str(row["evidence"]).split(";")) for row in modules)
            else "FAIL",
            "detail": "all listed evidence paths checked, including semicolon-separated paths",
        },
        {
            "check": "planned five-model architecture matrix included",
            "result": "PASS"
            if planned_five_model.get("planned_model_families") == [
                "hog_rbf_svm",
                "lightweight_cnn",
                "resnet18_embedding_linear_svm",
                "efficientnet_b0_embedding_linear_svm",
                "deit_tiny_embedding_linear_svm",
            ]
            and len(planned_five_model.get("model_rows", [])) == 15
            and len(planned_five_model.get("claim_summary", [])) == 3
            and deit_tiny.get("weights", {}).get("loaded") == "imagenet_default"
            and len(deit_tiny.get("seeds", [])) == 5
            else "FAIL",
            "detail": "The exact five architecture families named in the frozen plan must have a Mojahid/Res-SAM directional matrix, including five-seed DeiT-Tiny evidence",
        },
        {
            "check": "unified local split manifests included",
            "result": "PASS"
            if exists("reports/unified_split_manifest_audit_20260811/unified_split_manifest_audit_summary.json")
            and split_audit.get("status") == "complete_local_unified_split_manifests"
            and split_audit.get("split_manifest_rows") == 20
            and split_audit.get("all_split_files_exist")
            else "FAIL",
            "detail": "Mojahid, TIGPR, Zenodo and DeepMask/GPR_data should each have five local split protocol manifests",
        },
        {
            "check": "group-disjoint split protocols leakage-audited",
            "result": "PASS"
            if all(
                row["audit"]["group_leakage_free_train_test"]
                for row in split_audit["split_rows"]
                if row["protocol"] in split_audit["group_disjoint_protocols"]
            )
            else "FAIL",
            "detail": "Source-group holdout, P4-style and DataSAIL-like local protocols must have zero train-test group overlap",
        },
        {
            "check": "unified split baseline included",
            "result": "PASS"
            if exists("reports/unified_split_baseline_20260811/unified_split_baseline_summary.json")
            and split_baseline.get("status") == "complete_local_unified_split_baseline"
            and len(split_baseline.get("runs", [])) == 20
            and not split_baseline.get("blind_external_eligible", True)
            else "FAIL",
            "detail": "Every generated split manifest should have one local lightweight baseline run",
        },
        {
            "check": "unified split model-ranking audit included",
            "result": "PASS"
            if exists("reports/unified_split_model_ranking_audit_20260811/unified_split_model_ranking_audit_summary.json")
            and split_ranking.get("status") == "complete_local_unified_split_model_ranking_audit"
            and len(split_ranking.get("runs", [])) == 40
            and not split_ranking.get("blind_external_eligible", True)
            else "FAIL",
            "detail": "Every generated split manifest should have two local model-family runs for ranking sensitivity",
        },
        {
            "check": "unified split effect statistics included",
            "result": "PASS"
            if exists("reports/unified_split_effect_statistics_20260811/unified_split_effect_statistics_summary.json")
            and split_effect_stats.get("status") == "complete_local_unified_split_effect_statistics"
            and len(split_effect_stats.get("contrasts", [])) == 16
            and split_effect_stats.get("prediction_rows", 0) > 0
            and not split_effect_stats.get("blind_external_eligible", True)
            else "FAIL",
            "detail": "Random-minus-protocol split effects should have bootstrap intervals and per-sample prediction rows",
        },
        {
            "check": "unified split seed stability included",
            "result": "PASS"
            if exists("reports/unified_split_seed_stability_20260811/unified_split_seed_stability_summary.json")
            and split_seed_stability.get("status") == "complete_local_unified_split_seed_stability"
            and len(split_seed_stability.get("runs", [])) == 100
            and len(split_seed_stability.get("seeds", [])) == 5
            and not split_seed_stability.get("blind_external_eligible", True)
            else "FAIL",
            "detail": "Every generated split manifest should have five local SGD seeds for stability auditing",
        },
        {
            "check": "unified split five-family matrix included",
            "result": "PASS"
            if exists("reports/unified_split_five_family_matrix_20260811/unified_split_five_family_matrix_summary.json")
            and split_five_family.get("status") == "complete_local_unified_split_five_family_matrix"
            and len(split_five_family.get("runs", [])) == 100
            and len(split_five_family.get("datasets", [])) == 4
            and len(split_five_family.get("protocols", [])) == 5
            and not split_five_family.get("blind_external_eligible", True)
            else "FAIL",
            "detail": "Three assets should each have five local families over five unified split protocols",
        },
        {
            "check": "local signflip permutation audit included",
            "result": "PASS"
            if exists("reports/local_signflip_permutation_audit_20260811/local_signflip_permutation_audit_summary.json")
            and signflip_audit.get("status") == "complete_local_signflip_permutation_audit"
            and len(signflip_audit.get("unified_rows", [])) == 5
            and len(signflip_audit.get("four_tu_rows", [])) == 2
            and not signflip_audit.get("blind_external_eligible", True)
            else "FAIL",
            "detail": "Unified split and 4TU stress contrasts should have exact sign/sign-flip statistics",
        },
        {
            "check": "frozen experiment registry included",
            "result": "PASS"
            if exists("reports/frozen_experiment_registry_20260811/frozen_experiment_registry_summary.json")
            and frozen_registry.get("status") == "complete_local_frozen_experiment_registry"
            and frozen_registry.get("missing_required_rows") == 0
            and frozen_registry.get("registry_rows", 0) >= 100
            and frozen_registry.get("experiment_entrypoint_rows", 0) >= 40
            and frozen_registry.get("hashed_file_rows", 0) >= 100
            and not frozen_registry.get("blind_external_eligible", True)
            else "FAIL",
            "detail": "Frozen local experiment registry must hash current evidence, scripts, environment and entrypoints",
        },
        {
            "check": "zenodo mcg gpr public asset included",
            "result": "PASS"
            if exists("reports/zenodo_mcg_gpr_download_20260811/zenodo_mcg_gpr_download_summary.json")
            and exists("reports/zenodo_mcg_gpr_manifest_20260811/zenodo_mcg_gpr_manifest_summary.json")
            and exists("reports/zenodo_mcg_gpr_nonblind_baseline_20260811/zenodo_mcg_gpr_nonblind_baseline_summary.json")
            and zenodo_mcg_download.get("status") == "complete_public_mcg_gpr_download_verified_extracted"
            and zenodo_mcg_download.get("md5_verified") is True
            and zenodo_mcg_manifest.get("status") == "complete_public_mcg_gpr_manifest"
            and zenodo_mcg_manifest.get("rows") == 8100
            and zenodo_mcg_manifest.get("annotated_rows") == 966
            and zenodo_mcg_baseline.get("status") == "complete_public_mcg_gpr_nonblind_baseline"
            and len(zenodo_mcg_baseline.get("runs", [])) == 3
            and zenodo_mcg_split_stress.get("status") == "complete_public_mcg_gpr_split_stress"
            and len(zenodo_mcg_split_stress.get("runs", [])) == 7
            and not zenodo_mcg_baseline.get("blind_external_eligible", True)
            and not zenodo_mcg_split_stress.get("blind_external_eligible", True)
            else "FAIL",
            "detail": "Zenodo MCG GPR must be downloaded, MD5-verified, manifested and evaluated only as non-blind public stress evidence",
        },
        {
            "check": "cross-asset collision audit included",
            "result": "PASS"
            if exists("reports/cross_asset_collision_audit_20260811/cross_asset_collision_audit_summary.json")
            and cross_asset_collision.get("status") == "complete_local_cross_asset_collision_audit"
            and cross_asset_collision.get("independent_asset_clusters_by_hash") == 4
            and cross_asset_collision.get("mojahid_deepmask_complete_sha_overlap") is True
            and not cross_asset_collision.get("deepmask_independent_external_evidence_eligible", True)
            and not cross_asset_collision.get("blind_external_eligible", True)
            else "FAIL",
            "detail": "DeepMask/GPR_data must be prevented from being counted as an independent external/cross-asset dataset",
        },
        {
            "check": "deepmask gpr duplicate mirror asset included",
            "result": "PASS"
            if exists("reports/deepmask_gpr_asset_audit_20260811/deepmask_gpr_asset_audit_summary.json")
            and exists("reports/deepmask_gpr_augmentation_leakage_matrix_20260811/deepmask_gpr_augmentation_leakage_summary.json")
            and deepmask_audit.get("status") == "complete_local_public_asset_manifest"
            and deepmask_audit.get("rows") == 2524
            and deepmask_audit.get("base_source_groups") == 285
            and deepmask_matrix.get("status") == "complete_local_public_augmentation_leakage_matrix"
            and deepmask_matrix.get("runs") == 60
            and deepmask_matrix["best_group_holdout_balanced_accuracy"]["shared_train_test_base_groups"]["mean"] == 0.0
            and not deepmask_matrix.get("blind_external_eligible", True)
            else "FAIL",
            "detail": "DeepMask/GPR_data is retained as a local/public duplicate mirror stress asset, not independent external evidence",
        },
        {
            "check": "repair experiments included",
            "result": "PASS"
            if exists("reports/ressam_coral_repair_20260811/seed_sweep_summary.json")
            and exists("reports/mojahid_alignment_repair_20260811/seed_sweep_summary.json")
            and exists("reports/ressam_nontransductive_repair_20260811/seed_sweep_summary.json")
            and exists("reports/ressam_source_style_aug_repair_20260811/seed_sweep_summary.json")
            and exists("reports/4tu_alignment_repair_20260811/seed_sweep_summary.json")
            and exists("reports/mojahid_source_reweight_repair_20260811/source_reweight_repair_summary.json")
            and exists("reports/mojahid_temperature_calibration_repair_20260811/temperature_calibration_repair_summary.json")
            and exists("reports/mojahid_source_residualization_repair_20260811/source_residualization_repair_summary.json")
            and exists("reports/mojahid_group_dro_repair_20260811/group_dro_repair_summary.json")
            else "FAIL",
            "detail": "Transductive, non-transductive and train-only mitigation sweeps required",
        },
        {
            "check": "mojahid train-only source reweighting repair included",
            "result": "PASS"
            if mojahid_reweight_repair.get("status") == "complete_internal_train_only_reweighting_repair"
            and not mojahid_reweight_repair.get("repair_uses_unlabeled_target_statistics", True)
            and not mojahid_reweight_repair.get("blind_external_eligible", True)
            else "FAIL",
            "detail": "Train-only repair must be separated from target-statistic and blind-external repair evidence",
        },
        {
            "check": "mojahid validation-only temperature calibration repair included",
            "result": "PASS"
            if mojahid_calibration_repair.get("status") == "complete_internal_temperature_calibration_repair"
            and not mojahid_calibration_repair.get("repair_uses_test_fold_for_parameter_selection", True)
            and not mojahid_calibration_repair.get("blind_external_eligible", True)
            else "FAIL",
            "detail": "Calibration repair must tune on validation fold only and stay separated from blind-external repair evidence",
        },
        {
            "check": "mojahid train-only source residualization repair included",
            "result": "PASS"
            if mojahid_residualization_repair.get("status") == "complete_internal_source_residualization_repair"
            and mojahid_residualization_repair.get("source_field") == "is_augmented"
            and not mojahid_residualization_repair.get("source_basis_uses_test_fold", True)
            and not mojahid_residualization_repair.get("blind_external_eligible", True)
            else "FAIL",
            "detail": "Residualization repair must learn source basis on train folds and use a source signal shared across test folds",
        },
        {
            "check": "mojahid train-only group dro repair included",
            "result": "PASS"
            if mojahid_group_dro_repair.get("status") == "complete_internal_group_dro_repair"
            and len(mojahid_group_dro_repair.get("detailed_runs", [])) == 10
            and "source_group_dro" in mojahid_group_dro_repair.get("strategies", [])
            and "processing_role_dro" in mojahid_group_dro_repair.get("strategies", [])
            and not mojahid_group_dro_repair.get("repair_uses_unlabeled_target_statistics", True)
            and not mojahid_group_dro_repair.get("repair_uses_test_fold_for_parameter_selection", True)
            and not mojahid_group_dro_repair.get("blind_external_eligible", True)
            else "FAIL",
            "detail": "Group-DRO repair must remain train-only and report source-group plus processing-role robust optimization",
        },
        {
            "check": "mojahid train-only domain adversarial repair included",
            "result": "PASS"
            if mojahid_domain_adversarial_repair.get("status") == "complete_internal_train_only_domain_adversarial_repair"
            and len(mojahid_domain_adversarial_repair.get("detailed_rows", [])) == 40
            and not mojahid_domain_adversarial_repair.get("repair_uses_unlabeled_target_statistics", True)
            and not mojahid_domain_adversarial_repair.get("repair_uses_test_fold_for_parameter_selection", True)
            and not mojahid_domain_adversarial_repair.get("blind_external_eligible", True)
            else "FAIL",
            "detail": "Gradient-reversal repair must run two grouped protocols, four strengths and five seeds using train folds only",
        },
        {
            "check": "leakage dose experiment included",
            "result": "PASS"
            if exists("reports/mojahid_leakage_dose_20260811/dose_sweep_summary.json")
            and exists("reports/tigpr_duplicate_leakage_dose_20260811/tigpr_duplicate_leakage_dose_summary.json")
            else "FAIL",
            "detail": "Mojahid lineage and TIGPR duplicate leakage-dose sweeps required",
        },
        {
            "check": "tigpr duplicate leakage dose included",
            "result": "PASS"
            if tigpr_leakage_dose.get("status") == "complete_local_tigpr_duplicate_leakage_dose"
            and len(tigpr_leakage_dose.get("detailed_runs", [])) == 25
            and tigpr_leakage_dose.get("duplicate_group_count", 0) > 0
            and not tigpr_leakage_dose.get("blind_external_eligible", True)
            else "FAIL",
            "detail": "TIGPR duplicate dose should run five doses across five seeds while staying non-blind",
        },
        {
            "check": "leakage confidence metrics included",
            "result": "PASS"
            if "ece_10bin" in leakage_dose["dose_summary"]["0.00"]
            and "mean_confidence" in leakage_dose["dose_summary"]["0.40"]
            else "FAIL",
            "detail": "Leakage dose sweep must include confidence and ECE metrics",
        },
        {
            "check": "leakage error-structure metrics included",
            "result": "PASS"
            if "worst_class_recall" in leakage_dose["dose_summary"]["0.00"]
            and "class_recall_spread" in leakage_dose["dose_summary"]["0.40"]
            and "per_class_recall" in leakage_dose["detailed_runs"][0]
            else "FAIL",
            "detail": "Leakage dose sweep must include class recall and prediction-distribution error structure",
        },
        {
            "check": "source predictability experiment included",
            "result": "PASS"
            if exists("reports/source_predictability_20260811/source_predictability_summary.json")
            else "FAIL",
            "detail": "Mojahid and Res-SAM internal source-signal probes required",
        },
        {
            "check": "target-source association audit included",
            "result": "PASS"
            if exists("reports/target_source_association_20260811/target_source_association_summary.json")
            and association.get("complete_tasks", 0) >= 3
            else "FAIL",
            "detail": "Manifest-level target/source coupling metrics required",
        },
        {
            "check": "ressam transfer bootstrap ci included",
            "result": "PASS"
            if exists("reports/ressam_transfer_bootstrap_ci_20260811/ressam_transfer_bootstrap_ci_summary.json")
            and len(ressam_bootstrap.get("contrast_rows", [])) == 2
            else "FAIL",
            "detail": "Res-SAM lead transfer contrast needs cross-model uncertainty",
        },
        {
            "check": "4tu task-source association audit included",
            "result": "PASS"
            if exists("reports/4tu_task_source_association_20260811/4tu_task_source_association_summary.json")
            and four_tu_task_association.get("complete_pairs", 0) >= 6
            else "FAIL",
            "detail": "4TU task-level metadata labels need project/split association audit",
        },
        {
            "check": "4tu stress stability audit included",
            "result": "PASS"
            if exists("reports/4tu_stress_stability_20260811/4tu_stress_stability_summary.json")
            and len(four_tu_stability.get("layers", [])) == 2
            else "FAIL",
            "detail": "4TU fixed versus group-aware stress boundary needs stability audit",
        },
        {
            "check": "tigpr local asset audit refreshed",
            "result": "PASS"
            if exists("reports/tigpr_local_asset_audit_20260810.json")
            and tigpr_audit.get("status") in {"GO", "NO-GO"}
            else "FAIL",
            "detail": "TIGPR audit must explicitly record GO or NO-GO state",
        },
        {
            "check": "tigpr restored sample-level media verified",
            "result": "PASS"
            if tigpr_restored
            and exists("data_manifests/tigpr_unified_samples_20260810.csv")
            else "FAIL",
            "detail": f"status={tigpr_audit.get('status')}; rows={tigpr_audit.get('sample_index_rows')}",
        },
        {
            "check": "tigpr duplicate-aware sweep included",
            "result": "PASS"
            if exists("reports/tigpr_duplicate_aware_sweep_20260811/tigpr_duplicate_aware_summary.json")
            and tigpr_duplicate["split_summary"]["hash_group_stratified_80_20"]["shared_groups"]["mean"] == 0.0
            else "FAIL",
            "detail": "TIGPR restored asset needs duplicate-aware random-vs-group split evidence",
        },
        {
            "check": "tigpr model-family duplicate matrix included",
            "result": "PASS"
            if exists("reports/tigpr_model_family_duplicate_matrix_20260811/tigpr_model_family_duplicate_summary.json")
            and tigpr_model_matrix["claim_summary"]["n_model_families"] == 5
            else "FAIL",
            "detail": "TIGPR duplicate effect should be checked beyond one HOG model",
        },
        {
            "check": "external raw-gpr candidate downloaded and manifested",
            "result": "PASS"
            if exists("reports/external_raw_gpr_candidate_probe_20260811/external_raw_gpr_candidate_probe_summary.json")
            and raw_gpr_candidate["candidates"][0]["current_status"] == "downloaded_verified_extracted_manifested"
            and raw_gpr_candidate["candidates"][0]["local_archive_md5_verified"]
            and raw_gpr_candidate["candidates"][0]["local_manifest_rows"] == 914
            else "FAIL",
            "detail": "Track C public raw-GPR candidate should be recorded separately from blind validation",
        },
        {
            "check": "synthetic external blind freeze regression passed",
            "result": "PASS"
            if exists("reports/external_blind_freeze_regression_20260811/external_blind_freeze_regression_summary.json")
            and external_freeze_regression.get("status") == "complete_synthetic_blind_freeze_regression"
            and external_freeze_regression.get("n_synthetic_blind") == 240
            and external_freeze_regression.get("prediction_precedes_unlock") is True
            and external_intake_validation.get("status") == "PASS"
            and external_intake_validation.get("manifest_summary", {}).get("hash_verified_rows") == 240
            and external_locked_evaluation.get("status") == "PASS"
            and external_locked_evaluation.get("metrics", {}).get("overall", {}).get("n") == 240
            and not external_freeze_regression.get("blind_external_eligible", True)
            else "FAIL",
            "detail": "Synthetic fixture must pass strict intake and locked evaluation while remaining non-eligible for real blind claims",
        },
        {
            "check": "zenodo trackc nonblind baseline included",
            "result": "PASS"
            if exists("reports/zenodo_gpr_trackc_metadata_baseline_20260811/zenodo_gpr_trackc_metadata_baseline_summary.json")
            and zenodo_trackc.get("status") == "complete_nonblind_trackc_baseline"
            and not zenodo_trackc.get("blind_external_eligible", True)
            else "FAIL",
            "detail": "Zenodo raw-GPR stress test must remain marked non-blind",
        },
        {
            "check": "hidden evaluation candidate audit included",
            "result": "PASS"
            if exists("reports/hidden_eval_candidate_audit_20260811/hidden_eval_candidate_audit_summary.json")
            and hidden_eval_candidate_audit.get("status") == "complete_hidden_eval_candidate_audit_no_eligible_candidate"
            and hidden_eval_candidate_audit.get("candidate_count") >= 6
            and hidden_eval_candidate_audit.get("eligible_candidate_count") == 0
            and hidden_eval_candidate_audit.get("gate_decision") == "NO-GO"
            and hidden_eval_candidate_audit.get("hidden_eval_candidate_exists_but_not_usable") is True
            and not hidden_eval_candidate_audit.get("blind_external_eligible", True)
            else "FAIL",
            "detail": "Current hidden-test/challenge candidates must be audited before the blind external gate can remain closed",
        },
        {
            "check": "experiment gate consistency validator passed",
            "result": "PASS"
            if exists("reports/experiment_gate_consistency_20260811/experiment_gate_consistency_summary.json")
            and gate_consistency.get("status") == "PASS"
            and gate_consistency.get("fail_count") == 0
            and gate_consistency.get("blind_external_gate_consistent_no_go") is True
            and gate_consistency.get("submission_ready") is False
            and not gate_consistency.get("blind_external_eligible", True)
            else "FAIL",
            "detail": "Readiness, hidden-eval candidates, synthetic freeze regression, collision audit and progress summary must agree on NO-GO",
        },
        {
            "check": "blind external gate remains protected",
            "result": "PASS" if external.get("gate", {}).get("status") == "NO-GO" else "FAIL",
            "detail": f"external_gate={external.get('gate', {}).get('status')}",
        },
    ]

    next_actions = [
        {
            "priority": 1,
            "action": "Acquire a true blind external asset.",
            "can_run_locally": "no",
            "reason": "This is the only route to closing the 20% blind external validation block.",
        },
        {
            "priority": 2,
            "action": "Treat strict non-transductive repair as currently unsupported unless a stronger method is added later.",
            "can_run_locally": "partly",
            "reason": "Per-image preprocessing and source-style augmentation both failed to provide stable non-transductive gains.",
        },
        {
            "priority": 3,
            "action": "Treat Zenodo raw-GPR results as non-blind Track C stress evidence and avoid promoting them to blind external validation.",
            "can_run_locally": "done_for_current_baseline",
            "reason": (
                f"Candidate {raw_gpr_candidate['candidates'][0]['doi']} is "
                f"{raw_gpr_candidate['candidates'][0]['size_bytes']} bytes and now has "
                f"{raw_gpr_candidate['candidates'][0]['local_manifest_rows']} manifested raw-trace rows, "
                "but its labels/provenance are public."
            ),
        },
        {
            "priority": 4,
            "action": "If continuing local-only work, explore a stronger train-time repair family rather than more feature-statistic alignment.",
            "can_run_locally": "partly",
            "reason": "Three local assets now bound the simple alignment result; more of the same is unlikely to close the experimental gate.",
        },
    ]

    summary = {
        "package": "experiment_only_progress_20260811",
        "experiment_only_completion_percent": completion,
        "module_rows": len(modules),
        "earned_percent_total": earned,
        "weight_percent_total": total_weight,
        "planned_five_model_matrix_added": True,
        "planned_five_model_families": planned_five_model.get("planned_model_families"),
        "planned_five_model_rows": len(planned_five_model.get("model_rows", [])),
        "planned_five_model_claim_summaries": len(planned_five_model.get("claim_summary", [])),
        "deit_tiny_matrix_added": True,
        "deit_tiny_seeds": len(deit_tiny.get("seeds", [])),
        "deit_tiny_weight_status": deit_tiny.get("weights", {}).get("loaded"),
        "unified_local_split_manifests_added": True,
        "unified_local_split_manifest_rows": split_audit.get("split_manifest_rows"),
        "unified_local_split_baseline_added": True,
        "unified_local_split_baseline_runs": len(split_baseline.get("runs", [])),
        "unified_local_split_model_ranking_audit_added": True,
        "unified_local_split_model_ranking_runs": len(split_ranking.get("runs", [])),
        "unified_local_split_effect_statistics_added": True,
        "unified_local_split_effect_contrasts": len(split_effect_stats.get("contrasts", [])),
        "unified_local_split_effect_prediction_rows": split_effect_stats.get("prediction_rows"),
        "unified_local_split_seed_stability_added": True,
        "unified_local_split_seed_stability_runs": len(split_seed_stability.get("runs", [])),
        "unified_local_split_five_family_matrix_added": True,
        "unified_local_split_five_family_matrix_runs": len(split_five_family.get("runs", [])),
        "local_signflip_permutation_audit_added": True,
        "local_signflip_permutation_audit_rows": len(signflip_audit.get("unified_rows", [])) + len(signflip_audit.get("four_tu_rows", [])),
        "frozen_experiment_registry_added": True,
        "frozen_experiment_registry_rows": frozen_registry.get("registry_rows"),
        "frozen_experiment_registry_missing_required_rows": frozen_registry.get("missing_required_rows"),
        "frozen_experiment_registry_hashed_file_rows": frozen_registry.get("hashed_file_rows"),
        "deepmask_gpr_public_asset_added": True,
        "deepmask_gpr_rows": deepmask_audit.get("rows"),
        "deepmask_gpr_base_source_groups": deepmask_audit.get("base_source_groups"),
        "deepmask_gpr_augmentation_matrix_runs": deepmask_matrix.get("runs"),
        "deepmask_gpr_best_random_minus_group_holdout_ba": deepmask_matrix.get("best_random_minus_best_group_holdout_ba"),
        "cross_asset_collision_audit_added": True,
        "independent_asset_clusters_by_hash": cross_asset_collision.get("independent_asset_clusters_by_hash"),
        "mojahid_deepmask_complete_sha_overlap": cross_asset_collision.get("mojahid_deepmask_complete_sha_overlap"),
        "deepmask_independent_external_evidence_eligible": cross_asset_collision.get("deepmask_independent_external_evidence_eligible"),
        "hidden_eval_candidate_audit_added": True,
        "hidden_eval_candidate_count": hidden_eval_candidate_audit.get("candidate_count"),
        "hidden_eval_eligible_candidate_count": hidden_eval_candidate_audit.get("eligible_candidate_count"),
        "hidden_eval_gate_decision": hidden_eval_candidate_audit.get("gate_decision"),
        "experiment_gate_consistency_added": True,
        "experiment_gate_consistency_status": gate_consistency.get("status"),
        "experiment_gate_consistency_pass_count": gate_consistency.get("pass_count"),
        "repair_experiment_added": True,
        "repair_assets_with_alignment_sweeps": 2,
        "nontransductive_repair_sweep_added": True,
        "source_style_aug_repair_sweep_added": True,
        "four_tu_repair_sweep_added": True,
        "mojahid_train_only_source_reweight_repair_added": True,
        "mojahid_validation_only_temperature_calibration_repair_added": True,
        "mojahid_train_only_source_residualization_repair_added": True,
        "mojahid_train_only_group_dro_repair_added": True,
        "mojahid_train_only_domain_adversarial_repair_added": True,
        "mojahid_domain_adversarial_repair_runs": len(mojahid_domain_adversarial_repair.get("detailed_rows", [])),
        "mojahid_leakage_dose_sweep_added": True,
        "tigpr_duplicate_leakage_dose_sweep_added": True,
        "tigpr_duplicate_leakage_dose_runs": len(tigpr_leakage_dose.get("detailed_runs", [])),
        "mojahid_leakage_confidence_metrics_added": True,
        "mojahid_leakage_error_structure_metrics_added": True,
        "source_predictability_sweep_added": True,
        "target_source_association_audit_added": True,
        "ressam_transfer_bootstrap_ci_added": True,
        "four_tu_task_source_association_audit_added": True,
        "four_tu_stress_stability_audit_added": True,
        "tigpr_local_asset_audit_refreshed": True,
        "tigpr_sample_level_asset_restored": tigpr_restored,
        "tigpr_duplicate_aware_sweep_added": True,
        "tigpr_model_family_duplicate_matrix_added": True,
        "external_raw_gpr_candidate_probe_added": True,
        "synthetic_external_blind_freeze_regression_added": True,
        "synthetic_external_blind_freeze_regression_rows": external_freeze_regression.get("n_synthetic_blind"),
        "synthetic_external_blind_freeze_regression_intake_status": external_intake_validation.get("status"),
        "synthetic_external_blind_freeze_regression_locked_eval_status": external_locked_evaluation.get("status"),
        "zenodo_raw_gpr_download_verified_manifested": True,
        "zenodo_trackc_nonblind_baseline_added": True,
        "zenodo_mcg_gpr_download_manifest_baseline_added": True,
        "zenodo_mcg_gpr_rows": zenodo_mcg_manifest.get("rows"),
        "zenodo_mcg_gpr_annotated_rows": zenodo_mcg_manifest.get("annotated_rows"),
        "zenodo_mcg_gpr_baseline_runs": len(zenodo_mcg_baseline.get("runs", [])),
        "zenodo_mcg_gpr_split_stress_runs": len(zenodo_mcg_split_stress.get("runs", [])),
        "zenodo_mcg_gpr_official_minus_random_mae": zenodo_mcg_split_stress.get("official_minus_random_mae"),
        "zenodo_mcg_gpr_official_minus_random_tertile_ba": zenodo_mcg_split_stress.get("official_minus_random_tertile_ba"),
        "blind_external_status": external.get("gate", {}).get("status"),
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "submission_ready": False,
        "status": "experiment_only_progress_updated_not_complete",
    }

    report = [
        "# Experiment-Only Progress Audit",
        "",
        f"Experiment-only completion: {completion}%.",
        "",
        "This audit excludes manuscript prose, cover letters, administrative",
        "declarations, portal upload files and citation work. It only counts data",
        "assets, split/provenance experiments, model experiments, counterfactual",
        "experiments, mitigation experiments and blind external validation.",
        "",
        "## Module Scores",
        "",
        "| Module | Weight | Earned | Status |",
        "| --- | ---: | ---: | --- |",
    ]
    for row in modules:
        report.append(f"| {row['module']} | {row['weight_percent']} | {row['earned_percent']} | {row['status']} |")

    report.extend(
        [
            "",
            "## New 2026-08-11 Experimental Increment",
            "",
            "Added repair, leakage-dose and source-predictability experimental increments:",
            "",
            f"- Unified local split manifests added: {split_audit['split_manifest_rows']} dataset/protocol rows across {len(split_audit['datasets'])} dataset ids",
            f"- Cross-asset SHA collision audit independent hash clusters: {cross_asset_collision['independent_asset_clusters_by_hash']}",
            f"- Cross-asset SHA collision audit full duplicate pairs: {cross_asset_collision['fully_duplicate_pairs']}",
            f"- Split protocols per dataset: {split_audit['protocols_per_dataset']}; group-disjoint protocols: {', '.join(split_audit['group_disjoint_protocols'])}",
            f"- Unified split baseline runs added: {len(split_baseline['runs'])} local runs across {len(split_baseline['datasets'])} dataset ids",
            f"- Mojahid largest random-minus-protocol split BA gap: {split_baseline['dataset_summaries']['mojahid']['largest_random_minus_protocol_ba']:+.4f}",
            f"- TIGPR largest random-minus-protocol split BA gap: {split_baseline['dataset_summaries']['tigpr']['largest_random_minus_protocol_ba']:+.4f}",
            f"- Zenodo largest random-minus-protocol split BA gap: {split_baseline['dataset_summaries']['zenodo_14637589']['largest_random_minus_protocol_ba']:+.4f}",
            f"- Unified split model-ranking audit runs added: {len(split_ranking['runs'])} local model/protocol runs",
            f"- Mojahid top-model flips versus random split: {split_ranking['dataset_summaries']['mojahid']['top_model_flip_count_vs_random']}",
            f"- TIGPR top-model flips versus random split: {split_ranking['dataset_summaries']['tigpr']['top_model_flip_count_vs_random']}",
            f"- Zenodo top-model flips versus random split: {split_ranking['dataset_summaries']['zenodo_14637589']['top_model_flip_count_vs_random']}",
            f"- Unified split effect bootstrap contrasts added: {len(split_effect_stats['contrasts'])}",
            f"- Unified split effect per-sample prediction rows: {split_effect_stats['prediction_rows']}",
            f"- Unified split seed-stability runs added: {len(split_seed_stability['runs'])} local runs across {len(split_seed_stability['datasets'])} assets, {len(split_seed_stability['protocols'])} protocols and {len(split_seed_stability['seeds'])} seeds",
            f"- Mojahid five-seed largest mean random-minus-protocol split BA gap: {split_seed_stability['dataset_summaries']['mojahid']['largest_mean_random_minus_protocol_ba']:+.4f}",
            f"- TIGPR five-seed largest mean random-minus-protocol split BA gap: {split_seed_stability['dataset_summaries']['tigpr']['largest_mean_random_minus_protocol_ba']:+.4f}",
            f"- Zenodo five-seed largest mean random-minus-protocol split BA gap: {split_seed_stability['dataset_summaries']['zenodo_14637589']['largest_mean_random_minus_protocol_ba']:+.4f}",
            f"- DeepMask/GPR_data five-seed largest mean random-minus-protocol split BA gap: {split_seed_stability['dataset_summaries']['deepmask_gpr']['largest_mean_random_minus_protocol_ba']:+.4f}",
            f"- Unified split five-family matrix runs added: {len(split_five_family['runs'])}",
            f"- Unified five-family random top models: Mojahid {split_five_family['dataset_summaries']['mojahid']['random_rank'][0]}, TIGPR {split_five_family['dataset_summaries']['tigpr']['random_rank'][0]}, Zenodo {split_five_family['dataset_summaries']['zenodo_14637589']['random_rank'][0]}, DeepMask/GPR_data {split_five_family['dataset_summaries']['deepmask_gpr']['random_rank'][0]}",
            f"- Unified five-family top-model flips versus random split: Mojahid {split_five_family['dataset_summaries']['mojahid']['top_model_flip_count_vs_random']}, TIGPR {split_five_family['dataset_summaries']['tigpr']['top_model_flip_count_vs_random']}, Zenodo {split_five_family['dataset_summaries']['zenodo_14637589']['top_model_flip_count_vs_random']}, DeepMask/GPR_data {split_five_family['dataset_summaries']['deepmask_gpr']['top_model_flip_count_vs_random']}",
            f"- Unified split exact sign audit all-assets positives: {signflip_rows['unified_split_random_minus_protocol::all_assets']['positive_count']}/{signflip_rows['unified_split_random_minus_protocol::all_assets']['n_contrasts']}",
            f"- Unified split all-assets sign p / mean sign-flip p: {signflip_rows['unified_split_random_minus_protocol::all_assets']['exact_sign_positive_tail_p']:.4f} / {signflip_rows['unified_split_random_minus_protocol::all_assets']['exact_signflip_mean_positive_p']:.4f}",
            f"- Frozen experiment registry rows / missing required / hashed files: {frozen_registry['registry_rows']} / {frozen_registry['missing_required_rows']} / {frozen_registry['hashed_file_rows']}",
            f"- Frozen experiment entrypoints / script sources: {frozen_registry['experiment_entrypoint_rows']} / {frozen_registry['script_source_rows']}",
            f"- DeepMask/GPR_data duplicate mirror rows / base source groups: {deepmask_audit['rows']} / {deepmask_audit['base_source_groups']}",
            f"- DeepMask/GPR_data augmentation matrix runs: {deepmask_matrix['runs']}",
            f"- DeepMask/GPR_data best random/group-holdout balanced accuracy: {deepmask_matrix['best_random_balanced_accuracy']['balanced_accuracy']['mean']:.4f} / {deepmask_matrix['best_group_holdout_balanced_accuracy']['balanced_accuracy']['mean']:.4f}",
            f"- DeepMask/GPR_data best random-minus-group-holdout balanced accuracy delta: {deepmask_matrix['best_random_minus_best_group_holdout_ba']:+.4f}",
            f"- TIGPR local asset audit status: {tigpr_audit['status']} with {tigpr_audit.get('sample_index_rows')} sample-index rows",
            f"- TIGPR random stratified HOG balanced accuracy: {tigpr_duplicate['split_summary']['random_stratified_80_20']['hog_balanced_accuracy']['mean']:.4f}",
            f"- TIGPR hash-group HOG balanced accuracy: {tigpr_duplicate['split_summary']['hash_group_stratified_80_20']['hog_balanced_accuracy']['mean']:.4f}",
            f"- TIGPR random-minus-group HOG balanced accuracy delta: {tigpr_duplicate['random_minus_group']['random_minus_group_hog_balanced_accuracy']['mean']:+.4f}",
            f"- TIGPR random split shared duplicate hash groups: {tigpr_duplicate['split_summary']['random_stratified_80_20']['shared_groups']['mean']:.1f}",
            f"- TIGPR group split shared duplicate hash groups: {tigpr_duplicate['split_summary']['hash_group_stratified_80_20']['shared_groups']['mean']:.1f}",
            f"- TIGPR metadata-only group-split balanced accuracy: {tigpr_duplicate['split_summary']['hash_group_stratified_80_20']['metadata_balanced_accuracy']['mean']:.4f}",
            f"- TIGPR duplicate model-family support: {tigpr_model_matrix['claim_summary']['directional_support_count']}/{tigpr_model_matrix['claim_summary']['n_model_families']} directional and {tigpr_model_matrix['claim_summary']['material_support_count']}/{tigpr_model_matrix['claim_summary']['n_model_families']} material",
            f"- TIGPR duplicate model-family mean random-minus-group balanced accuracy delta: {tigpr_model_matrix['claim_summary']['delta_mean_across_models']:+.4f}",
            f"- TIGPR duplicate leakage dose runs: {len(tigpr_leakage_dose['detailed_runs'])} across {len(tigpr_leakage_dose['doses'])} doses and {len(tigpr_leakage_dose['seeds'])} seeds",
            f"- TIGPR duplicate leakage dose 0.00 balanced accuracy: {tigpr_leakage_dose['dose_summary']['0.00']['balanced_accuracy']['mean']:.4f}",
            f"- TIGPR duplicate leakage dose 0.20 delta vs 0.00: {tigpr_leakage_dose['dose_summary']['0.20']['delta_vs_dose0_balanced_accuracy']['mean']:+.4f}",
            f"- TIGPR duplicate leakage dose 0.40 delta vs 0.00: {tigpr_leakage_dose['dose_summary']['0.40']['delta_vs_dose0_balanced_accuracy']['mean']:+.4f}",
            f"- External raw-GPR candidate recorded: {raw_gpr_candidate['candidates'][0]['doi']} ({raw_gpr_candidate['candidates'][0]['size_bytes']} bytes), not blind-eligible",
            f"- Hidden-evaluation candidate audit candidates / eligible / gate: {hidden_eval_candidate_audit['candidate_count']} / {hidden_eval_candidate_audit['eligible_candidate_count']} / {hidden_eval_candidate_audit['gate_decision']}",
            f"- Experiment gate consistency status / pass checks / fail checks: {gate_consistency['status']} / {gate_consistency['pass_count']} / {gate_consistency['fail_count']}",
            f"- Synthetic blind-freeze regression rows / intake status / locked-eval status: {external_freeze_regression['n_synthetic_blind']} / {external_intake_validation['status']} / {external_locked_evaluation['status']}",
            f"- Synthetic blind-freeze prediction SHA-256: {external_freeze_regression['prediction_sha256_at_freeze']}",
            f"- Synthetic blind-freeze locked evaluation balanced accuracy: {external_locked_evaluation['metrics']['overall']['balanced_accuracy']:.4f}",
            f"- Zenodo raw-GPR archive MD5 verified: {zenodo_raw_audit['archive']['md5_verified']} with {zenodo_raw_audit['manifest_rows']} raw-trace manifest rows",
            f"- Zenodo raw-GPR raw rows by top category: {zenodo_raw_audit['category_summary']}",
            f"- Zenodo Track C SGD random/group balanced accuracy: {zenodo_trackc_models['sgd_logistic']['random_balanced_accuracy']['mean']:.4f} / {zenodo_trackc_models['sgd_logistic']['group_balanced_accuracy']['mean']:.4f}",
            f"- Zenodo Track C ExtraTrees random/group balanced accuracy: {zenodo_trackc_models['extra_trees']['random_balanced_accuracy']['mean']:.4f} / {zenodo_trackc_models['extra_trees']['group_balanced_accuracy']['mean']:.4f}",
            f"- Zenodo Track C random split shared project groups: {zenodo_trackc_models['extra_trees']['random_shared_groups']['mean']:.1f}; group split shared project groups: {zenodo_trackc_models['extra_trees']['group_shared_groups']['mean']:.1f}",
            f"- Zenodo MCG GPR archive MD5 verified: {zenodo_mcg_download['md5_verified']} with {zenodo_mcg_manifest['rows']} image rows and {zenodo_mcg_manifest['annotated_rows']} annotated downstream rows",
            f"- Zenodo MCG GPR non-blind baseline runs: {len(zenodo_mcg_baseline['runs'])}",
            f"- Zenodo MCG GPR split-stress runs: {len(zenodo_mcg_split_stress['runs'])}; official-minus-random MAE / tertile BA: {zenodo_mcg_split_stress['official_minus_random_mae']:+.4f} / {zenodo_mcg_split_stress['official_minus_random_tertile_ba']:+.4f}",
            f"- Res-SAM mean/std synthetic -> real_world balanced accuracy delta: {res_sam_repair['transfer']['synthetic_to_real_world']['delta_mean_std_minus_baseline']['balanced_accuracy']['mean']:+.4f}",
            f"- Res-SAM mean/std real_world -> synthetic balanced accuracy delta: {res_sam_repair['transfer']['real_world_to_synthetic']['delta_mean_std_minus_baseline']['balanced_accuracy']['mean']:+.4f}",
            f"- Mojahid mean/std current grouped balanced accuracy delta: {mojahid_repair['protocols']['current_fold0_test_fold1_val']['delta_mean_std_minus_baseline']['balanced_accuracy']['mean']:+.4f}",
            f"- Mojahid mean/std task-aware grouped balanced accuracy delta: {mojahid_repair['protocols']['task_aware_fold0_test_fold3_val']['delta_mean_std_minus_baseline']['balanced_accuracy']['mean']:+.4f}",
            f"- Res-SAM non-transductive per-image zscore synthetic -> real_world balanced accuracy delta: {nontransductive_repair['transfer']['synthetic_to_real_world']['per_image_zscore']['balanced_accuracy']['mean'] - nontransductive_repair['transfer']['synthetic_to_real_world']['raw']['balanced_accuracy']['mean']:+.4f}",
            f"- Res-SAM non-transductive per-image zscore real_world -> synthetic balanced accuracy delta: {nontransductive_repair['transfer']['real_world_to_synthetic']['per_image_zscore']['balanced_accuracy']['mean'] - nontransductive_repair['transfer']['real_world_to_synthetic']['raw']['balanced_accuracy']['mean']:+.4f}",
            f"- Res-SAM source-style augmentation best synthetic -> real_world balanced accuracy delta: {max(value['balanced_accuracy']['mean'] for key, value in source_aug_repair['transfer']['synthetic_to_real_world'].items() if key.startswith('source_style_aug_to_')) - source_aug_repair['transfer']['synthetic_to_real_world']['raw_source_to_raw_target']['balanced_accuracy']['mean']:+.4f}",
            f"- Res-SAM source-style augmentation best real_world -> synthetic balanced accuracy delta: {max(value['balanced_accuracy']['mean'] for key, value in source_aug_repair['transfer']['real_world_to_synthetic'].items() if key.startswith('source_style_aug_to_')) - source_aug_repair['transfer']['real_world_to_synthetic']['raw_source_to_raw_target']['balanced_accuracy']['mean']:+.4f}",
            f"- Mojahid train-only source-balanced repair current grouped balanced accuracy delta: {mojahid_reweight_protocols['current_fold0_test_fold1_val']['delta_source_balanced_minus_uniform']['balanced_accuracy']['mean']:+.4f}",
            f"- Mojahid train-only label-source-balanced repair current grouped balanced accuracy delta: {mojahid_reweight_protocols['current_fold0_test_fold1_val']['delta_label_source_balanced_minus_uniform']['balanced_accuracy']['mean']:+.4f}",
            f"- Mojahid train-only source-balanced repair task-aware grouped balanced accuracy delta: {mojahid_reweight_protocols['task_aware_fold0_test_fold3_val']['delta_source_balanced_minus_uniform']['balanced_accuracy']['mean']:+.4f}",
            f"- Mojahid train-only label-source-balanced repair task-aware grouped balanced accuracy delta: {mojahid_reweight_protocols['task_aware_fold0_test_fold3_val']['delta_label_source_balanced_minus_uniform']['balanced_accuracy']['mean']:+.4f}",
            f"- Mojahid validation-only temperature calibration current grouped ECE delta / balanced accuracy delta: {mojahid_calibration_protocols['current_fold0_test_fold1_val']['delta_temperature_calibrated_minus_uncalibrated']['ece_10bin']['mean']:+.4f} / {mojahid_calibration_protocols['current_fold0_test_fold1_val']['delta_temperature_calibrated_minus_uncalibrated']['balanced_accuracy']['mean']:+.4f}",
            f"- Mojahid validation-only temperature calibration task-aware grouped ECE delta / balanced accuracy delta: {mojahid_calibration_protocols['task_aware_fold0_test_fold3_val']['delta_temperature_calibrated_minus_uncalibrated']['ece_10bin']['mean']:+.4f} / {mojahid_calibration_protocols['task_aware_fold0_test_fold3_val']['delta_temperature_calibrated_minus_uncalibrated']['balanced_accuracy']['mean']:+.4f}",
            f"- Mojahid source residualization current grouped source-probe BA delta / target BA delta: {mojahid_residualization_protocols['current_fold0_test_fold1_val']['1']['delta_source_probe_minus_k0']['balanced_accuracy']['mean']:+.4f} / {mojahid_residualization_protocols['current_fold0_test_fold1_val']['1']['delta_target_minus_k0']['balanced_accuracy']['mean']:+.4f}",
            f"- Mojahid source residualization task-aware grouped source-probe BA delta / target BA delta: {mojahid_residualization_protocols['task_aware_fold0_test_fold3_val']['1']['delta_source_probe_minus_k0']['balanced_accuracy']['mean']:+.4f} / {mojahid_residualization_protocols['task_aware_fold0_test_fold3_val']['1']['delta_target_minus_k0']['balanced_accuracy']['mean']:+.4f}",
            f"- Mojahid source-group DRO current/task-aware balanced accuracy deltas: {mojahid_group_dro_protocols['current_fold0_test_fold1_val']['delta_source_group_dro_minus_erm']['balanced_accuracy']['mean']:+.4f} / {mojahid_group_dro_protocols['task_aware_fold0_test_fold3_val']['delta_source_group_dro_minus_erm']['balanced_accuracy']['mean']:+.4f}",
            f"- Mojahid label-source-group DRO current/task-aware balanced accuracy deltas: {mojahid_group_dro_protocols['current_fold0_test_fold1_val']['delta_label_source_group_dro_minus_erm']['balanced_accuracy']['mean']:+.4f} / {mojahid_group_dro_protocols['task_aware_fold0_test_fold3_val']['delta_label_source_group_dro_minus_erm']['balanced_accuracy']['mean']:+.4f}",
            f"- Mojahid processing-role DRO current/task-aware balanced accuracy deltas: {mojahid_group_dro_protocols['current_fold0_test_fold1_val']['delta_processing_role_dro_minus_erm']['balanced_accuracy']['mean']:+.4f} / {mojahid_group_dro_protocols['task_aware_fold0_test_fold3_val']['delta_processing_role_dro_minus_erm']['balanced_accuracy']['mean']:+.4f}",
            f"- 4TU Land type per-matrix zscore balanced accuracy delta: {four_tu_repair['split']['delta_per_matrix_zscore_minus_raw']['balanced_accuracy']['mean']:+.4f}",
            f"- 4TU Land type mean/std balanced accuracy delta: {four_tu_repair['split']['delta_mean_std_minus_raw']['balanced_accuracy']['mean']:+.4f}",
            f"- 4TU Land type CORAL balanced accuracy delta: {four_tu_repair['split']['delta_coral_minus_raw']['balanced_accuracy']['mean']:+.4f}",
            f"- 4TU strongest task/project association: {four_tu_strongest_association['target_field']} NMI / Cramer's V {four_tu_strongest_association['normalized_mutual_information']:.4f} / {four_tu_strongest_association['cramers_v']:.4f}",
            f"- 4TU log_clip stress fixed vs group-aware mean delta: {four_tu_stability_layers['fixed_split_seed_sweep']['delta']['mean']:.4f} vs {four_tu_stability_layers['group_aware_project_splits']['delta']['mean']:.4f}",
            f"- 4TU log_clip exact negative-tail sign p fixed vs group-aware: {signflip_rows['4tu_log_clip_stress_delta::fixed_split_seed_sweep']['exact_sign_negative_tail_p']:.4f} vs {signflip_rows['4tu_log_clip_stress_delta::group_aware_project_splits']['exact_sign_negative_tail_p']:.4f}",
            f"- Mojahid lineage leakage dose 0.00 balanced accuracy: {leakage_dose['dose_summary']['0.00']['balanced_accuracy']['mean']:.4f}",
            f"- Mojahid lineage leakage dose 0.40 balanced accuracy: {leakage_dose['dose_summary']['0.40']['balanced_accuracy']['mean']:.4f}",
            f"- Mojahid lineage leakage dose 0.40 delta vs 0.00: {leakage_dose['dose_summary']['0.40']['balanced_accuracy']['mean'] - leakage_dose['dose_summary']['0.00']['balanced_accuracy']['mean']:+.4f}",
            f"- Mojahid lineage leakage dose 0.00 mean confidence / ECE: {leakage_dose['dose_summary']['0.00']['mean_confidence']['mean']:.4f} / {leakage_dose['dose_summary']['0.00']['ece_10bin']['mean']:.4f}",
            f"- Mojahid lineage leakage dose 0.40 mean confidence / ECE: {leakage_dose['dose_summary']['0.40']['mean_confidence']['mean']:.4f} / {leakage_dose['dose_summary']['0.40']['ece_10bin']['mean']:.4f}",
            f"- Mojahid lineage leakage dose 0.00 worst recall / recall spread: {leakage_dose['dose_summary']['0.00']['worst_class_recall']['mean']:.4f} / {leakage_dose['dose_summary']['0.00']['class_recall_spread']['mean']:.4f}",
            f"- Mojahid lineage leakage dose 0.40 worst recall / recall spread: {leakage_dose['dose_summary']['0.40']['worst_class_recall']['mean']:.4f} / {leakage_dose['dose_summary']['0.40']['class_recall_spread']['mean']:.4f}",
            f"- Res-SAM environment source predictability balanced accuracy: {source_tasks['ressam_environment_source_group']['metrics']['balanced_accuracy']['mean']:.4f} vs chance {source_tasks['ressam_environment_source_group']['chance_balanced_accuracy']:.4f}",
            f"- Mojahid lineage source_group predictability balanced accuracy: {source_tasks['mojahid_augmentation_lineage_source_group']['metrics']['balanced_accuracy']['mean']:.4f} vs chance {source_tasks['mojahid_augmentation_lineage_source_group']['chance_balanced_accuracy']:.4f}",
            f"- Mojahid processing-role predictability balanced accuracy: {source_tasks['mojahid_processing_role_is_augmented']['metrics']['balanced_accuracy']['mean']:.4f} vs chance {source_tasks['mojahid_processing_role_is_augmented']['chance_balanced_accuracy']:.4f}",
            f"- Mojahid label vs source_group NMI / Cramer's V: {association_rows['mojahid_label_vs_source_group']['normalized_mutual_information']:.4f} / {association_rows['mojahid_label_vs_source_group']['cramers_v']:.4f}",
            f"- Res-SAM label vs environment NMI / Cramer's V: {association_rows['ressam_label_vs_environment']['normalized_mutual_information']:.4f} / {association_rows['ressam_label_vs_environment']['cramers_v']:.4f}",
            f"- Res-SAM real_world -> synthetic cross-model delta CI: [{ressam_bootstrap_rows['within_minus_transfer_real_world_to_synthetic']['ci95_low']:.4f}, {ressam_bootstrap_rows['within_minus_transfer_real_world_to_synthetic']['ci95_high']:.4f}]",
            f"- Res-SAM synthetic -> real_world cross-model delta CI: [{ressam_bootstrap_rows['within_minus_transfer_synthetic_to_real_world']['ci95_low']:.4f}, {ressam_bootstrap_rows['within_minus_transfer_synthetic_to_real_world']['ci95_high']:.4f}]",
            "",
            "Boundary: the strongest positive repair remains dataset-dependent",
            "transductive evidence. Non-transductive repair attempts are bounded",
            "negative or near-null results, 4TU alignment is negative, and",
            "Mojahid train-only source reweighting is negative or neutral.",
            "Temperature calibration improves confidence calibration but leaves",
            "balanced accuracy unchanged. Source residualization suppresses",
            "processing-role predictability only with a material target-performance",
            "cost. Group-DRO source-group repair is negative, and processing-role",
            "DRO gains are too small to close a repair gate. These",
            "results do not close",
            "the blind external validation or external-repair gate.",
            "",
            "## Next Experiment Actions",
            "",
        ]
    )
    for row in next_actions:
        report.append(f"{row['priority']}. {row['action']} ({row['can_run_locally']})")

    write_csv(
        OUT_DIR / "experiment_only_module_scores.csv",
        ["module", "weight_percent", "earned_percent", "status", "evidence", "basis", "remaining_gap"],
        modules,
    )
    write_csv(
        OUT_DIR / "experiment_only_next_actions.csv",
        ["priority", "action", "can_run_locally", "reason"],
        next_actions,
    )
    write_csv(OUT_DIR / "experiment_only_qa.csv", ["check", "result", "detail"], qa_rows)
    (OUT_DIR / "experiment_only_progress_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (OUT_DIR / "experiment_only_progress_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
