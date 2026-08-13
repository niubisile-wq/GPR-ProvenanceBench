#!/usr/bin/env python3
"""Build unified sample manifests from existing audited sample indexes."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BENCH_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = BENCH_ROOT / "data_manifests" / "unified_sample_schema_20260810.csv"
OUT_DIR = BENCH_ROOT / "data_manifests"
CREATED_DATE = "2026-08-10"

INPUTS = {
    "mojahid": ROOT / "manifest" / "mojahid_sample_index_v1.csv",
    "tigpr": ROOT / "manifest" / "tigpr_sample_index_v1.csv",
}
FOUR_TU_INPUT = ROOT / "reports" / "4tu_baseline_package_v1" / "package_manifest.csv"


def schema_fields() -> list[str]:
    with SCHEMA_PATH.open(newline="", encoding="utf-8-sig") as handle:
        return [row["field"] for row in csv.DictReader(handle)]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def common_base(row: dict[str, str], dataset_id: str) -> dict[str, str]:
    source_group = row.get("split_group", "")
    return {
        "dataset_id": dataset_id,
        "asset_role": "exploratory" if dataset_id == "mojahid" else "support",
        "sample_id": row.get("sample_id", ""),
        "label": row.get("label", ""),
        "label_source": "dataset_annotation",
        "rel_path": row.get("rel_path", ""),
        "abs_path": row.get("abs_path", ""),
        "file_sha256": row.get("sha256", ""),
        "raw_trace_id": "",
        "project_id": "",
        "activity_id": "",
        "site_id": "",
        "survey_line_id": "",
        "device_id": "",
        "antenna_frequency_mhz": "",
        "acquisition_date": "",
        "operator_id": "",
        "processing_chain_id": infer_processing_chain(row, dataset_id),
        "export_format": infer_export_format(row.get("rel_path", "")),
        "width_px": row.get("width_px", ""),
        "height_px": row.get("height_px", ""),
        "is_augmented": row.get("is_augmented", "0"),
        "augmentation_ancestor_id": source_group if dataset_id == "mojahid" else "",
        "exact_duplicate_group": source_group if dataset_id == "tigpr" else "",
        "near_duplicate_group": "",
        "source_group": source_group,
        "fold_id": row.get("fold_id", ""),
        "split_protocol": "stratified_group_kfold_v1",
        "split_role": "",
        "created_by": "build_unified_sample_manifests.py",
        "created_date": CREATED_DATE,
        "notes": build_notes(row, dataset_id),
    }


def four_tu_row(row: dict[str, str]) -> dict[str, str]:
    project_id = row.get("project_id", "")
    activity_id = row.get("activity_id", "")
    member = row.get("member", "")
    package_path = row.get("package_npy_path", "")
    source_group = f"project:{project_id}"
    return {
        "dataset_id": "four_tu",
        "asset_role": "core",
        "sample_id": f"four_tu:{activity_id}:{Path(member).stem}",
        "label": "unlabeled_raw_trace_matrix",
        "label_source": "not_applicable_for_current_raw_trace_manifest",
        "rel_path": member.replace("\\", "/"),
        "abs_path": package_path,
        "file_sha256": sha256_if_available(package_path),
        "raw_trace_id": member.replace("\\", "/"),
        "project_id": project_id,
        "activity_id": activity_id,
        "site_id": "",
        "survey_line_id": Path(member).stem,
        "device_id": "",
        "antenna_frequency_mhz": "",
        "acquisition_date": "",
        "operator_id": "",
        "processing_chain_id": "segy_to_fixed_shape_npy_baseline_v1",
        "export_format": "npy",
        "width_px": row.get("shape_cols", ""),
        "height_px": row.get("shape_rows", ""),
        "is_augmented": "0",
        "augmentation_ancestor_id": "",
        "exact_duplicate_group": "",
        "near_duplicate_group": "",
        "source_group": source_group,
        "fold_id": "",
        "split_protocol": "project_holdout_baseline_v1",
        "split_role": row.get("split_role", ""),
        "created_by": "build_unified_sample_manifests.py",
        "created_date": CREATED_DATE,
        "notes": "4TU baseline package matrix; target labels require task-specific joins",
    }


def sha256_if_available(path_value: str) -> str:
    path = Path(path_value)
    if not path.exists():
        return ""
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def infer_processing_chain(row: dict[str, str], dataset_id: str) -> str:
    if dataset_id == "mojahid" and row.get("is_augmented") == "1":
        return "augmented_image_export"
    if dataset_id == "mojahid":
        return "original_image_export"
    if dataset_id == "tigpr":
        return "dataset_image_export"
    return "unknown"


def infer_export_format(rel_path: str) -> str:
    suffix = Path(rel_path).suffix.lower().lstrip(".")
    return suffix or "unknown"


def build_notes(row: dict[str, str], dataset_id: str) -> str:
    notes = []
    if row.get("path_verified"):
        notes.append(f"path_verified={row['path_verified']}")
    if row.get("source_role"):
        notes.append(f"source_role={row['source_role']}")
    if row.get("mode"):
        notes.append(f"mode={row['mode']}")
    if row.get("size_bytes"):
        notes.append(f"size_bytes={row['size_bytes']}")
    if dataset_id == "tigpr":
        notes.append("exact duplicate grouping currently uses file hash")
    return "; ".join(notes)


def write_unified(dataset_id: str, rows: list[dict[str, str]], fields: list[str]) -> Path:
    out_path = OUT_DIR / f"{dataset_id}_unified_samples_20260810.csv"
    with out_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            unified = common_base(row, dataset_id)
            writer.writerow({field: unified.get(field, "") for field in fields})
    return out_path


def write_four_tu(fields: list[str]) -> Path:
    rows = read_rows(FOUR_TU_INPUT)
    out_path = OUT_DIR / "four_tu_unified_samples_20260810.csv"
    with out_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            unified = four_tu_row(row)
            writer.writerow({field: unified.get(field, "") for field in fields})
    print(f"four_tu: wrote {len(rows)} rows to {out_path}")
    return out_path


def main() -> None:
    fields = schema_fields()
    for dataset_id, input_path in INPUTS.items():
        rows = read_rows(input_path)
        out_path = write_unified(dataset_id, rows, fields)
        print(f"{dataset_id}: wrote {len(rows)} rows to {out_path}")
    write_four_tu(fields)


if __name__ == "__main__":
    main()
