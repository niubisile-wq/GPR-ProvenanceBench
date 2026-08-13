# TIGPR Local Asset Audit 2026-08-10

## Decision

Status: **GO** for core executable asset use.

TIGPR is locally executable for sample-level audit use: the restored source image tree, 7169-row sample index, expected five-class layout and verified archive identity are present.

## Local Evidence

- Manifest path: `manifest\tigpr_manifest_v1.yaml`; exists: `True`.
- Sample index path: `manifest\tigpr_sample_index_v1.csv`; data rows: `7169`.
- Prior provenance gate JSON: `gpr_leakage_research\tigpr_provenance_gate_v1.json`; exists: `True`.
- Candidate archive: `external_assets\tigpr\TIGPR.rar`; exists: `True`.
- Candidate archive identity: `possible_tigpr`.
- Candidate archive SHA256: `f609c9e29cdb76f83c13d6d7f9986250842e03836b75acb567c48753d34a8c9a`.

## Expected TIGPR Counts

| Class | Expected images |
| --- | ---: |
| Crack | 1224 |
| Interlayer_bonding_deficiency | 2020 |
| Loose | 2100 |
| No_damage | 1520 |
| Void | 305 |
| **Total** | **7169** |

## Local TIGPR Root Search

| Candidate root | Classes found | Missing classes | Complete |
| --- | --- | --- | --- |
| `external_assets\tigpr\extracted\TIGPR\Damage Classification` | Crack, Interlayer_bonding_deficiency, Loose, No_damage, Void |  | True |

Non-TIGPR same-name class hits were found and intentionally excluded from GO/NO-GO logic:

| Class | Relative path |
| --- | --- |
| Crack | `external_assets\res_sam_data\GPR_data\real_world\crack` |
| Crack | `external_assets\res_sam_data\GPR_data\synthetic\crack` |
| Loose | `external_assets\res_sam_data\GPR_data\real_world\loose` |

## Prior Audit Evidence

- Prior audit image count: `7169`.
- Prior audit exact duplicate groups: `243`.
- Prior audit exact duplicate images: `486`.
- Prior audit cross-label duplicate groups: `2`.
- Prior audit geometry/filesize/JPEG provenance BA: `0.8116729078940541`.

This prior audit is useful for risk framing, but it points to a non-local historical path and cannot substitute for executable local media.

## Blockers

- None.

## Required Recovery Steps

1. Download TIGPR from the Mendeley dataset page with authorized access.
2. Place the archive under `external_assets/tigpr/`.
3. Extract to a layout equivalent to `TIGPR/Damage Classification/{Crack,Interlayer_bonding_deficiency,Loose,No_damage,Void}`.
4. Rebuild `manifest/tigpr_sample_index_v1.csv` from local files.
5. Verify 7169 rows, class counts, exact duplicate groups and cross-label conflicts before enabling TIGPR as a core asset.

## Protocol Consequence

TIGPR can now be counted as a restored local sample-level asset. This does not by itself close blind external validation, because the labels and media are now available locally.
