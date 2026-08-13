#!/usr/bin/env python3
"""Build a manifest for Zenodo MCG GPR images and downstream masks."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image


BENCH_ROOT = Path(__file__).resolve().parents[1]
CNS_ROOT = BENCH_ROOT.parents[0]
ASSET_DIR = CNS_ROOT / "external_assets" / "zenodo_mcg_gpr_14270869"
EXTRACT_DIR = ASSET_DIR / "extracted"
IMAGES_DIR = EXTRACT_DIR / "images"
ANNOTATIONS_DIR = EXTRACT_DIR / "annotations"
OUT_MANIFEST = BENCH_ROOT / "data_manifests" / "zenodo_mcg_gpr_manifest_20260811.csv"
OUT_DIR = BENCH_ROOT / "reports" / "zenodo_mcg_gpr_manifest_20260811"


FIELDNAMES = [
    "sample_id",
    "dataset",
    "subset",
    "split_role",
    "label",
    "source_group",
    "image_abs_path",
    "image_rel_path_from_cns1",
    "image_sha256",
    "mask_abs_path",
    "mask_rel_path_from_cns1",
    "mask_sha256",
    "width_px",
    "height_px",
    "image_size_bytes",
    "mask_size_bytes",
    "foreground_ratio",
    "has_annotation",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def mask_foreground_ratio(path: Path) -> float:
    with Image.open(path) as image:
        image.load()
        arr = np.asarray(image.convert("L"), dtype=np.uint8)
    return float(np.mean(arr > 0))


def split_role_from_path(rel: Path) -> str:
    parts = rel.parts
    if len(parts) >= 2:
        if parts[1] == "D_TRAIN":
            return "train"
        if parts[1] == "D_VALIDATION":
            return "val"
        if parts[1] == "D_TEST":
            return "test"
        if parts[1] == "P_TRAIN":
            return "pretext_train"
        if parts[1] == "P_VALIDATION":
            return "pretext_val"
    return "unknown"


def label_from_ratio(ratio: float | None) -> str:
    if ratio is None:
        return "unlabelled_pretext"
    return "foreground_present" if ratio > 0 else "background_only"


def build_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for image_path in sorted(IMAGES_DIR.rglob("*.png")):
        rel_under_images = image_path.relative_to(IMAGES_DIR)
        subset = rel_under_images.parts[0] if rel_under_images.parts else "unknown"
        mask_path = ANNOTATIONS_DIR / rel_under_images
        has_annotation = mask_path.exists()
        foreground_ratio = mask_foreground_ratio(mask_path) if has_annotation else None
        with Image.open(image_path) as image:
            image.load()
            width, height = image.size
        sample_stem = rel_under_images.with_suffix("").as_posix().replace("/", "::")
        sample_id = f"zenodo_mcg_gpr::{sample_stem}"
        rows.append(
            {
                "sample_id": sample_id,
                "dataset": "zenodo_mcg_gpr_14270869",
                "subset": subset,
                "split_role": split_role_from_path(rel_under_images),
                "label": label_from_ratio(foreground_ratio),
                "source_group": "::".join(rel_under_images.parts[:2]) if len(rel_under_images.parts) >= 2 else subset,
                "image_abs_path": str(image_path),
                "image_rel_path_from_cns1": image_path.relative_to(CNS_ROOT).as_posix(),
                "image_sha256": sha256(image_path),
                "mask_abs_path": str(mask_path) if has_annotation else "",
                "mask_rel_path_from_cns1": mask_path.relative_to(CNS_ROOT).as_posix() if has_annotation else "",
                "mask_sha256": sha256(mask_path) if has_annotation else "",
                "width_px": str(width),
                "height_px": str(height),
                "image_size_bytes": str(image_path.stat().st_size),
                "mask_size_bytes": str(mask_path.stat().st_size) if has_annotation else "",
                "foreground_ratio": "" if foreground_ratio is None else f"{foreground_ratio:.8f}",
                "has_annotation": str(has_annotation).lower(),
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_md(path: Path, summary: dict[str, object]) -> None:
    lines = [
        "# Zenodo MCG GPR Manifest",
        "",
        f"Rows: {summary['rows']}",
        f"Annotated rows: {summary['annotated_rows']}",
        f"Pretext rows: {summary['pretext_rows']}",
        f"Label counts: {summary['label_counts']}",
        f"Split counts: {summary['split_role_counts']}",
        "",
        "## Boundary",
        "",
        "This public segmentation-style asset is non-blind. It can support public",
        "stress tests and collision audits, but cannot close blind external validation.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = build_rows()
    if not rows:
        raise SystemExit(f"No PNG images found under {IMAGES_DIR}")
    write_csv(OUT_MANIFEST, rows)
    annotated = [row for row in rows if row["has_annotation"] == "true"]
    summary = {
        "run_id": "20260811_E38_zenodo_mcg_gpr_manifest",
        "manifest": OUT_MANIFEST.relative_to(BENCH_ROOT).as_posix(),
        "rows": len(rows),
        "annotated_rows": len(annotated),
        "pretext_rows": len(rows) - len(annotated),
        "label_counts": dict(Counter(row["label"] for row in rows)),
        "split_role_counts": dict(Counter(row["split_role"] for row in rows)),
        "source_groups": len({row["source_group"] for row in rows}),
        "image_sha_unique": len({row["image_sha256"] for row in rows}),
        "mask_sha_unique": len({row["mask_sha256"] for row in annotated}),
        "blind_external_eligible": False,
        "status": "complete_public_mcg_gpr_manifest",
    }
    (OUT_DIR / "zenodo_mcg_gpr_manifest_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_md(OUT_DIR / "zenodo_mcg_gpr_manifest_summary.md", summary)
    print(json.dumps({"status": summary["status"], "rows": summary["rows"], "annotated_rows": summary["annotated_rows"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
