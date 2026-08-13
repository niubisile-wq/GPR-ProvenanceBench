#!/usr/bin/env python3
"""Build the local TIGPR sample index from restored source media."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = ROOT / "external_assets" / "tigpr" / "extracted" / "TIGPR" / "Damage Classification"
OUT_PATH = ROOT / "manifest" / "tigpr_sample_index_v1.csv"

CLASS_COUNTS = {
    "Crack": 1224,
    "Interlayer_bonding_deficiency": 2020,
    "Loose": 2100,
    "No_damage": 1520,
    "Void": 305,
}

FIELDS = [
    "dataset_id",
    "sample_id",
    "label",
    "rel_path",
    "abs_path",
    "path_verified",
    "split_group",
    "source_role",
    "is_augmented",
    "width_px",
    "height_px",
    "mode",
    "size_bytes",
    "sha256",
    "fold_id",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def image_info(path: Path) -> tuple[int, int, str]:
    with Image.open(path) as image:
        return image.width, image.height, image.mode


def natural_key(path: Path) -> tuple[int, str]:
    stem = path.stem
    if stem.isdigit():
        return int(stem), stem
    return 10**12, stem


def main() -> None:
    if not SOURCE_ROOT.exists():
        raise FileNotFoundError(f"missing TIGPR source root: {SOURCE_ROOT}")

    rows: list[dict[str, str]] = []
    observed_counts: dict[str, int] = {}
    for label in CLASS_COUNTS:
        class_dir = SOURCE_ROOT / label
        files = sorted(class_dir.glob("*.jpg"), key=natural_key)
        observed_counts[label] = len(files)
        for ordinal, path in enumerate(files, start=1):
            digest = sha256(path)
            width, height, mode = image_info(path)
            rel_path = path.relative_to(ROOT).as_posix()
            rows.append(
                {
                    "dataset_id": "tigpr",
                    "sample_id": f"tigpr:{label}:{path.stem}",
                    "label": label,
                    "rel_path": rel_path,
                    "abs_path": str(path),
                    "path_verified": "1",
                    "split_group": f"sha256:{digest}",
                    "source_role": "damage_classification_image",
                    "is_augmented": "0",
                    "width_px": str(width),
                    "height_px": str(height),
                    "mode": mode,
                    "size_bytes": str(path.stat().st_size),
                    "sha256": digest,
                    "fold_id": str((ordinal - 1) % 5),
                }
            )

    mismatches = {
        label: {"expected": expected, "observed": observed_counts.get(label, 0)}
        for label, expected in CLASS_COUNTS.items()
        if observed_counts.get(label, 0) != expected
    }
    if mismatches:
        raise RuntimeError(f"TIGPR class count mismatch: {mismatches}")
    if len(rows) != sum(CLASS_COUNTS.values()):
        raise RuntimeError(f"TIGPR row count mismatch: {len(rows)}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote {len(rows)} rows to {OUT_PATH}")
    print(observed_counts)


if __name__ == "__main__":
    main()
