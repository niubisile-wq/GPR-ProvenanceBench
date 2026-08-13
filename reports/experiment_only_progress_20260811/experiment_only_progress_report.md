# Experiment-Only Progress Audit

Experiment-only completion: 80.0%.

This audit excludes manuscript prose, cover letters, administrative
declarations, portal upload files and citation work. It only counts data
assets, split/provenance experiments, model experiments, counterfactual
experiments, mitigation experiments and blind external validation.

## Module Scores

| Module | Weight | Earned | Status |
| --- | ---: | ---: | --- |
| Asset inventory and unified sample manifests | 8 | 8 | complete_with_tigpr_sample_level_restored_deepmask_duplicate_mirror_audited_local_split_manifests_baseline_ranking_effect_stats_seed_stability_five_family_matrix_and_signflip_stats |
| Mojahid split-sensitivity experiments | 8 | 8 | complete_as_secondary_directional_evidence |
| Res-SAM environment-transfer experiments | 15 | 15 | complete_as_current_lead_internal_result_with_cross_model_ci |
| Source predictability / provenance signal experiments | 9 | 9 | complete_for_internal_h1_signal_and_association_metrics |
| Cross-model synthesis | 9 | 9 | complete_for_current_internal_claim_boundary |
| 4TU raw-trace counterfactual and stress-test experiments | 12 | 12 | complete_as_feasibility_and_boundary_evidence_with_task_source_and_stability_audits |
| Leakage-dose experiments | 10 | 10 | mojahid_lineage_dose_plus_tigpr_duplicate_dose_complete_for_local_cross_asset_boundary |
| Repair / mitigation experiments | 9 | 9 | three_asset_repair_boundary_plus_train_only_reweighting_calibration_residualization_group_dro_and_domain_adversarial_repair_established |
| Blind external validation | 20 | 0 | no_go_real_blind_asset_missing_synthetic_freeze_regression_passed_hidden_eval_candidates_audited |

## New 2026-08-11 Experimental Increment

Added repair, leakage-dose and source-predictability experimental increments:

- Unified local split manifests added: 20 dataset/protocol rows across 4 dataset ids
- Cross-asset SHA collision audit independent hash clusters: 4
- Cross-asset SHA collision audit full duplicate pairs: [['mojahid', 'deepmask_gpr']]
- Split protocols per dataset: 5; group-disjoint protocols: source_group_holdout_70_15_15, provenance_size_holdout_p4, datasail_like_group_balance
- Unified split baseline runs added: 20 local runs across 4 dataset ids
- Mojahid largest random-minus-protocol split BA gap: +0.1670
- TIGPR largest random-minus-protocol split BA gap: +0.0516
- Zenodo largest random-minus-protocol split BA gap: +0.3055
- Unified split model-ranking audit runs added: 40 local model/protocol runs
- Mojahid top-model flips versus random split: 3
- TIGPR top-model flips versus random split: 0
- Zenodo top-model flips versus random split: 1
- Unified split effect bootstrap contrasts added: 16
- Unified split effect per-sample prediction rows: 11866
- Unified split seed-stability runs added: 100 local runs across 4 assets, 5 protocols and 5 seeds
- Mojahid five-seed largest mean random-minus-protocol split BA gap: +0.1472
- TIGPR five-seed largest mean random-minus-protocol split BA gap: +0.0652
- Zenodo five-seed largest mean random-minus-protocol split BA gap: +0.2796
- DeepMask/GPR_data five-seed largest mean random-minus-protocol split BA gap: +0.1224
- Unified split five-family matrix runs added: 100
- Unified five-family random top models: Mojahid image_metadata_extra_trees, TIGPR pixel32_extra_trees, Zenodo raw_file_metadata_extra_trees, DeepMask/GPR_data pixel32_extra_trees
- Unified five-family top-model flips versus random split: Mojahid 0, TIGPR 0, Zenodo 4, DeepMask/GPR_data 4
- Unified split exact sign audit all-assets positives: 15/16
- Unified split all-assets sign p / mean sign-flip p: 0.0003 / 0.0000
- Frozen experiment registry rows / missing required / hashed files: 164 / 0 / 162
- Frozen experiment entrypoints / script sources: 62 / 51
- DeepMask/GPR_data duplicate mirror rows / base source groups: 2524 / 285
- DeepMask/GPR_data augmentation matrix runs: 60
- DeepMask/GPR_data best random/group-holdout balanced accuracy: 0.9654 / 0.9247
- DeepMask/GPR_data best random-minus-group-holdout balanced accuracy delta: +0.0407
- TIGPR local asset audit status: GO with 7169 sample-index rows
- TIGPR random stratified HOG balanced accuracy: 0.7314
- TIGPR hash-group HOG balanced accuracy: 0.6777
- TIGPR random-minus-group HOG balanced accuracy delta: +0.0537
- TIGPR random split shared duplicate hash groups: 76.6
- TIGPR group split shared duplicate hash groups: 0.0
- TIGPR metadata-only group-split balanced accuracy: 0.8892
- TIGPR duplicate model-family support: 4/5 directional and 4/5 material
- TIGPR duplicate model-family mean random-minus-group balanced accuracy delta: +0.0484
- TIGPR duplicate leakage dose runs: 25 across 5 doses and 5 seeds
- TIGPR duplicate leakage dose 0.00 balanced accuracy: 0.6777
- TIGPR duplicate leakage dose 0.20 delta vs 0.00: +0.0121
- TIGPR duplicate leakage dose 0.40 delta vs 0.00: +0.0091
- External raw-GPR candidate recorded: 10.5281/zenodo.14637589 (3784747664 bytes), not blind-eligible
- Hidden-evaluation candidate audit candidates / eligible / gate: 6 / 0 / NO-GO
- Experiment gate consistency status / pass checks / fail checks: PASS / 7 / 0
- Synthetic blind-freeze regression rows / intake status / locked-eval status: 240 / PASS / PASS
- Synthetic blind-freeze prediction SHA-256: 11035c3b71dd31b488aaaf1bbf7ca54750a611112b00468df934119217f5eb83
- Synthetic blind-freeze locked evaluation balanced accuracy: 0.7094
- Zenodo raw-GPR archive MD5 verified: True with 914 raw-trace manifest rows
- Zenodo raw-GPR raw rows by top category: {'pipe': {'all_files': 3081, 'all_bytes': 644582199, 'raw_trace_files': 553, 'raw_trace_bytes': 601177714}, 'rebar': {'all_files': 1140, 'all_bytes': 944715545, 'raw_trace_files': 217, 'raw_trace_bytes': 937189212}, 'tunnel': {'all_files': 351, 'all_bytes': 4688831890, 'raw_trace_files': 144, 'raw_trace_bytes': 4646193924}}
- Zenodo Track C SGD random/group balanced accuracy: 0.9022 / 0.7846
- Zenodo Track C ExtraTrees random/group balanced accuracy: 0.9677 / 0.8399
- Zenodo Track C random split shared project groups: 17.8; group split shared project groups: 0.0
- Zenodo MCG GPR archive MD5 verified: True with 8100 image rows and 966 annotated downstream rows
- Zenodo MCG GPR non-blind baseline runs: 3
- Zenodo MCG GPR split-stress runs: 7; official-minus-random MAE / tertile BA: -0.0007 / +0.0244
- IOAI 2025 Radar public benchmark route completed as executable fallback only, not blind external validation
- IOAI 2025 Radar official sizes: training / validation / test = 1800 / 500 / 500
- IOAI 2025 Radar smoke probe weighted scores: validation / test = 0.0779 / 0.0880
- IOAI 2025 Radar cached probe weighted scores: validation / test = 0.0238 / 0.0129
- IOAI 2025 Radar full benchmark probe weighted scores: validation / test = 0.0318 / 0.0318
- Res-SAM mean/std synthetic -> real_world balanced accuracy delta: +0.0267
- Res-SAM mean/std real_world -> synthetic balanced accuracy delta: +0.1267
- Mojahid mean/std current grouped balanced accuracy delta: +0.0124
- Mojahid mean/std task-aware grouped balanced accuracy delta: +0.0084
- Res-SAM non-transductive per-image zscore synthetic -> real_world balanced accuracy delta: +0.0033
- Res-SAM non-transductive per-image zscore real_world -> synthetic balanced accuracy delta: -0.0022
- Res-SAM source-style augmentation best synthetic -> real_world balanced accuracy delta: -0.0100
- Res-SAM source-style augmentation best real_world -> synthetic balanced accuracy delta: -0.0111
- Mojahid train-only source-balanced repair current grouped balanced accuracy delta: -0.0143
- Mojahid train-only label-source-balanced repair current grouped balanced accuracy delta: -0.0053
- Mojahid train-only source-balanced repair task-aware grouped balanced accuracy delta: -0.0244
- Mojahid train-only label-source-balanced repair task-aware grouped balanced accuracy delta: -0.0045
- Mojahid validation-only temperature calibration current grouped ECE delta / balanced accuracy delta: -0.1355 / +0.0000
- Mojahid validation-only temperature calibration task-aware grouped ECE delta / balanced accuracy delta: -0.0910 / +0.0000
- Mojahid source residualization current grouped source-probe BA delta / target BA delta: -0.0737 / -0.0865
- Mojahid source residualization task-aware grouped source-probe BA delta / target BA delta: -0.0812 / -0.1403
- Mojahid source-group DRO current/task-aware balanced accuracy deltas: -0.0178 / -0.0066
- Mojahid label-source-group DRO current/task-aware balanced accuracy deltas: -0.0130 / -0.0075
- Mojahid processing-role DRO current/task-aware balanced accuracy deltas: +0.0018 / +0.0025
- 4TU Land type per-matrix zscore balanced accuracy delta: -0.0143
- 4TU Land type mean/std balanced accuracy delta: -0.1095
- 4TU Land type CORAL balanced accuracy delta: -0.0429
- 4TU strongest task/project association: Construction workers NMI / Cramer's V 0.7095 / 1.0000
- 4TU log_clip stress fixed vs group-aware mean delta: -0.0966 vs -0.0169
- 4TU log_clip exact negative-tail sign p fixed vs group-aware: 0.0010 vs 0.2500
- Mojahid lineage leakage dose 0.00 balanced accuracy: 0.8566
- Mojahid lineage leakage dose 0.40 balanced accuracy: 0.8983
- Mojahid lineage leakage dose 0.40 delta vs 0.00: +0.0417
- Mojahid lineage leakage dose 0.00 mean confidence / ECE: 0.9015 / 0.0365
- Mojahid lineage leakage dose 0.40 mean confidence / ECE: 0.9155 / 0.0230
- Mojahid lineage leakage dose 0.00 worst recall / recall spread: 0.6905 / 0.2996
- Mojahid lineage leakage dose 0.40 worst recall / recall spread: 0.7666 / 0.2181
- Res-SAM environment source predictability balanced accuracy: 0.9926 vs chance 0.5000
- Mojahid lineage source_group predictability balanced accuracy: 0.6079 vs chance 0.0125
- Mojahid processing-role predictability balanced accuracy: 0.6010 vs chance 0.5000
- Mojahid label vs source_group NMI / Cramer's V: 0.2514 / 0.8724
- Res-SAM label vs environment NMI / Cramer's V: 0.1699 / 0.5477
- Res-SAM real_world -> synthetic cross-model delta CI: [0.2963, 0.5516]
- Res-SAM synthetic -> real_world cross-model delta CI: [0.1721, 0.5470]

Boundary: the strongest positive repair remains dataset-dependent
transductive evidence. Non-transductive repair attempts are bounded
negative or near-null results, 4TU alignment is negative, and
Mojahid train-only source reweighting is negative or neutral.
Temperature calibration improves confidence calibration but leaves
balanced accuracy unchanged. Source residualization suppresses
processing-role predictability only with a material target-performance
cost. Group-DRO source-group repair is negative, and processing-role
DRO gains are too small to close a repair gate. These
results do not close
the blind external validation or external-repair gate.

## Next Experiment Actions

1. Acquire a true blind external asset. (deferred; not required for the public-benchmark fallback closure)
2. Treat strict non-transductive repair as currently unsupported unless a stronger method is added later. (partly)
3. Treat Zenodo raw-GPR results as non-blind Track C stress evidence and avoid promoting them to blind external validation. (done_for_current_baseline)
4. If continuing local-only work, explore a stronger train-time repair family rather than more feature-statistic alignment. (partly)
5. Keep IOAI 2025 Radar explicitly labeled as public benchmark evaluation and use it as the executable fallback closure route. (done)
6. No further experiment execution is required for the fallback route unless a new hypothesis is introduced. (done)
