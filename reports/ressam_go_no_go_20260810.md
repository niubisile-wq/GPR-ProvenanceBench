# Res-SAM Go/No-Go Audit 2026-08-10

## Decision

Res-SAM is a **GO as the third local GPR data asset** for M0-M2 protocol work.

Res-SAM is a **NO-GO for full model replication today** until the SAM ViT-L
checkpoint and a version-compatible runtime are prepared.

## Evidence

Local repository:

1. Path: `external_assets/res_sam_repo`
2. GitHub repository: `https://github.com/zhouxr6066/Res-SAM`
3. Local HEAD: `f201236d63dd730e32f08499e8f8ba480f15d35f`
4. License: GPL-3.0

Zenodo record:

1. DOI: `10.5281/zenodo.17615326`
2. Version: `v1.0.0`
3. Publication date: `2025-11-15`
4. Access: open
5. Archive file listed by Zenodo: `zhouxr6066/Res-SAM-v1.0.0.zip`
6. Archive size listed by Zenodo: `43,751,401` bytes

Local data:

1. Repository contains `gpr_data.zip`.
2. The archive has 1050 JPG images.
3. The archive has been extracted to `external_assets/res_sam_data`.
4. Unified manifest: `GPR-ProvenanceBench/data_manifests/res_sam_unified_samples_20260810.csv`.

Local data counts:

| environment | label | count |
| --- | --- | ---: |
| real_world | cavity | 100 |
| real_world | crack | 100 |
| real_world | loose | 100 |
| real_world | manhole | 100 |
| real_world | normal | 100 |
| real_world | pipe | 100 |
| synthetic | cavity | 150 |
| synthetic | crack | 150 |
| synthetic | pipe | 150 |

## Runtime Audit

Current runtime:

1. `py` launches Python 3.12.5.
2. Current torch stack is CPU-only: torch 2.8.0+cpu, torchvision 0.23.0+cpu.
3. `PySide6` imports successfully.
4. `segment_anything` imports successfully.
5. `faiss` imports successfully.
6. `cv2` imports successfully.

Compatibility concerns:

1. Official CPU environment requests Python 3.8, NumPy <2, scikit-learn 1.3,
   SciPy <1.14, and faiss-cpu.
2. Official GPU environment requests Python 3.9 and CUDA-compatible PyTorch.
3. Current runtime uses Python 3.12, NumPy 2.1.3, scikit-learn 1.5.2, SciPy
   1.16.3 and CPU-only PyTorch.
4. The full GUI/model path imports `sam/sam.py`, which expects
   `sam/sam_vit_l_0b3195.pth`.
5. `sam/sam_vit_l_0b3195.pth` is not present locally.

## Go/No-Go Table

| Requirement | Status | Decision |
| --- | --- | --- |
| Repository available locally | Complete | GO |
| Published software DOI and license identifiable | Complete | GO |
| GPR image data available locally | Complete | GO |
| Unified sample manifest generated | Complete | GO |
| SAM ViT-L checkpoint present | Missing | NO-GO for full model |
| Version-compatible official environment | Not prepared | NO-GO for full model |
| GPU-capable runtime for full matrix | Not present | NO-GO for deep/full replication |

## Use In Current Plan

Allowed now:

1. Count Res-SAM as the third local GPR data asset for M0-M2 manifest and
   lightweight split/provenance experiments.
2. Use real_world versus synthetic as source/environment labels.
3. Build harmonized anomaly-vs-normal or class-level image baselines from the
   extracted JPG data.

Not allowed yet:

1. Claim that the full Res-SAM method has been reproduced.
2. Use Res-SAM model outputs as manuscript evidence.
3. Claim external validation until a frozen split and label harmonization protocol
   are defined.

## Next Step

Run a lightweight Res-SAM image baseline using the unified manifest, with
environment-aware splits:

1. Train on `synthetic`, test on `real_world`.
2. Train on `real_world`, test on `synthetic`.
3. Compare against within-environment random/grouped splits.

