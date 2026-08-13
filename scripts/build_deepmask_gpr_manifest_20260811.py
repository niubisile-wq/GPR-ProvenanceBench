#!/usr/bin/env python3
"""Build a manifest and audit for the local DeepMask-style GPR_data asset."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image


BENCH_ROOT = Path(__file__).resolve().parents[1]
CNS_ROOT = BENCH_ROOT.parents[0]
DATA_ROOT = CNS_ROOT / "gpr_leakage_research" / "dataset_inspect" / "GPR_data"
ARCHIVE = CNS_ROOT / "gpr_leakage_research" / "GPR_data.rar"
OUT_MANIFEST = BENCH_ROOT / "data_manifests" / "deepmask_gpr_unified_samples_20260811.csv"
OUT_DIR = BENCH_ROOT / "reports" / "deepmask_gpr_asset_audit_20260811"


FIELDNAMES = [
    "sample_id",
    "dataset",
    "label",
    "raw_label_dir",
    "augmentation_status",
    "base_source_group",
    "augmentation_index",
    "abs_path",
    "rel_path_from_cns1",
    "file_sha256",
    "size_bytes",
    "width_px",
    "height_px",
    "mode",
]


LABEL_MAP = {
    "cavities": "cavity",
    "augmented_cavities": "cavity",
    "intact": "intact",
    "augmented_intact": "intact",
    "Utilities": "utility",
    "augmented_utilities": "utility",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def archive_sha256() -> str:
    return sha256(ARCHIVE) if ARCHIVE.exists() else ""


def normalize_base_group(path: Path, label_dir: str) -> tuple[str, str]:
    stem = path.stem
    if label_dir.startswith("augmented_"):
        match = re.match(r"^(?P<base>.+?)_aug_(?P<idx>\d+)$", stem, flags=re.IGNORECASE)
        if match:
            return match.group("base"), match.group("idx")
    return stem, ""


def build_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for label_dir, label in LABEL_MAP.items():
        root = DATA_ROOT / label_dir
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".bmp"}:
                continue
            base_group, aug_idx = normalize_base_group(path, label_dir)
            with Image.open(path) as image:
                image.load()
                width, height = image.size
                mode = image.mode
            augmentation_status = "augmented" if label_dir.startswith("augmented_") else "original"
            sample_id = f"deepmask_gpr::{label_dir}::{path.stem}"
            rows.append(
                {
                    "sample_id": sample_id,
                    "dataset": "deepmask_gpr",
                    "label": label,
                    "raw_label_dir": label_dir,
                    "augmentation_status": augmentation_status,
                    "base_source_group": f"{label}::{base_group}",
                    "augmentation_index": aug_idx,
                    "abs_path": str(path),
                    "rel_path_from_cns1": path.relative_to(CNS_ROOT).as_posix(),
                    "file_sha256": sha256(path),
                    "size_bytes": str(path.stat().st_size),
                    "width_px": str(width),
                    "height_px": str(height),
                    "mode": mode,
                }
            )
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def audit(rows: list[dict[str, str]]) -> dict[str, object]:
    by_hash: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_hash[row["file_sha256"]].append(row)
    duplicate_hashes = {key: value for key, value in by_hash.items() if len(value) > 1}
    cross_label_duplicate_hashes = {
        key: value
        for key, value in duplicate_hashes.items()
        if len({row["label"] for row in value}) > 1
    }
    by_group: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_group[row["base_source_group"]].append(row)
    augmented_groups_with_original = 0
    augmented_groups_without_original = 0
    for group_rows in by_group.values():
        statuses = {row["augmentation_status"] for row in group_rows}
        if "augmented" in statuses and "original" in statuses:
            augmented_groups_with_original += 1
        elif "augmented" in statuses:
            augmented_groups_without_original += 1
    return {
        "run_id": "20260811_E32_deepmask_gpr_asset_audit",
        "dataset": "deepmask_gpr",
        "manifest": OUT_MANIFEST.relative_to(BENCH_ROOT).as_posix(),
        "data_root": str(DATA_ROOT),
        "archive": str(ARCHIVE),
        "archive_exists": ARCHIVE.exists(),
        "archive_sha256": archive_sha256(),
        "rows": len(rows),
        "label_counts": dict(Counter(row["label"] for row in rows)),
        "raw_label_dir_counts": dict(Counter(row["raw_label_dir"] for row in rows)),
        "augmentation_status_counts": dict(Counter(row["augmentation_status"] for row in rows)),
        "base_source_groups": len(by_group),
        "augmented_groups_with_original": augmented_groups_with_original,
        "augmented_groups_without_original": augmented_groups_without_original,
        "exact_duplicate_hash_groups": len(duplicate_hashes),
        "exact_duplicate_image_rows": int(sum(len(value) for value in duplicate_hashes.values())),
        "cross_label_duplicate_hash_groups": len(cross_label_duplicate_hashes),
        "status": "complete_local_public_asset_manifest",
        "blind_external_eligible": False,
        "reason_not_blind": "Local/public labelled image folders and augmentation lineage are visible before prediction freeze.",
    }


def write_md(path: Path, summary: dict[str, object]) -> None:
    lines = [
        "# DeepMask GPR Asset Audit",
        "",
        f"Rows: {summary['rows']}",
        f"Labels: {summary['label_counts']}",
        f"Augmentation status: {summary['augmentation_status_counts']}",
        f"Base source groups: {summary['base_source_groups']}",
        f"Exact duplicate hash groups: {summary['exact_duplicate_hash_groups']}",
        f"Cross-label duplicate hash groups: {summary['cross_label_duplicate_hash_groups']}",
        "",
        "## Boundary",
        "",
        "This is a local/public labelled asset. It strengthens non-blind cross-asset",
        "stress evidence but cannot close the real blind external validation gate.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = build_rows()
    if not rows:
        raise SystemExit(f"No images found under {DATA_ROOT}")
    write_csv(OUT_MANIFEST, rows)
    summary = audit(rows)
    (OUT_DIR / "deepmask_gpr_asset_audit_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_md(OUT_DIR / "deepmask_gpr_asset_audit_summary.md", summary)
    print(json.dumps({"rows": summary["rows"], "status": summary["status"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
