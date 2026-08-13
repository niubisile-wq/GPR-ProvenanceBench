# Asset Inventory 2026-08-10

This file freezes the current evidence boundary for the strengthened plan. Claims
below should be revised only through dated checkpoint files.

| Asset | Current usable evidence | Main role | Blocking issue | Next required action |
| --- | --- | --- | --- | --- |
| Mojahid | Sample index and manifest exist; previous audit reports 285 originals and 2239 augmented samples | Exploratory signal, first baseline, augmentation ancestry leakage test | Cannot be the sole confirmatory evidence | Validate manifest, run grouped baseline, quantify augmentation ancestry leakage |
| 4TU | Project index, file inventory, baseline packages, split packages and rendered examples exist | Raw-trace counterfactual and project-level sign-flip tests | Current results remain exploratory until protocol is frozen and no test reuse is guaranteed | Freeze project holdout rules, verify raw trace coverage, run strict counterfactual |
| TIGPR | Mendeley `TIGPR.rar` restored under `external_assets/tigpr/`, SHA-256 verified, five-class image tree extracted and 7169-row sample index/unified manifest rebuilt | Restored local sample-level asset; not blind external validation | No local asset blocker remains; duplicate-aware modeling is still needed before using TIGPR as confirmatory performance evidence | Run duplicate-aware TIGPR split/provenance experiments under a frozen protocol |
| P4 | Split package exists and supports protocol comparison | Split benchmark evidence | Prior test reuse risk limits claim strength | Treat as protocol comparison only unless rebuilt under frozen split rules |
| Res-SAM | Repository and 1050-image data archive now exist locally; unified manifest generated | Third local GPR data asset for protocol work | Full model still lacks SAM ViT-L checkpoint and version-compatible runtime | Use as data asset now; defer full model replication |

## Evidence Rules

1. Mojahid results are exploratory until repeated on at least two independent assets.
2. 4TU raw-trace counterfactual is the central causal evidence and must be frozen.
3. TIGPR source media and the 7169-row local sample index are now restored; duplicate-aware split evaluation is still required before making confirmatory TIGPR performance claims.
4. P4 cannot be used as a main confirmatory claim unless rebuilt without test reuse.
5. Res-SAM can be counted as a local data asset after `res_sam_unified_samples_20260810.csv`, but full Res-SAM model outputs cannot be counted until the SAM checkpoint and compatible runtime are reproducible.
