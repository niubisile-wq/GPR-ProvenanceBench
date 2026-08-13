#!/usr/bin/env python3
"""Build a unified sample manifest for the local Res-SAM GPR data archive."""

from __future__ import annotations

import argparse
import csv
import hashlib
import zipfile
from io import BytesIO
from pathlib import Path

from PIL import Image


BENCH_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = BENCH_ROOT / "data_manifests" / "unified_sample_schema_20260810.csv"
CREATED_DATE = "2026-08-10"


def schema_fields() -> list[str]:
    with SCHEMA_PATH.open(newline="", encoding="utf-8-sig") as handle:
        return [row["field"] for row in csv.DictReader(handle)]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_info(data: bytes) -> tuple[int, int, str]:
    with Image.open(BytesIO(data)) as image:
        image.load()
        return image.size[0], image.size[1], image.mode


def safe_extract(zip_path: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as archive:
        for member in archive.infolist():
            target = (output_dir / member.filename).resolve()
            if not str(target).startswith(str(output_dir.resolve())):
                raise ValueError(f"unsafe zip member path: {member.filename}")
        archive.extractall(output_dir)


def build_rows(zip_path: Path, extracted_root: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with zipfile.ZipFile(zip_path) as archive:
        for name in sorted(archive.namelist()):
            if name.endswith("/") or not name.lower().endswith((".jpg", ".jpeg", ".png")):
                continue
            parts = name.split("/")
            if len(parts) < 4 or parts[0] != "GPR_data":
                continue
            environment = parts[1]
            label = parts[2]
            filename = parts[-1]
            data = archive.read(name)
            width, height, mode = image_info(data)
            rel_path = str(Path(name)).replace("\\", "/")
            abs_path = extracted_root / rel_path
            rows.append(
                {
                    "dataset_id": "res_sam",
                    "asset_role": "core",
                    "sample_id": f"res_sam:{environment}:{label}:{Path(filename).stem}",
                    "label": label,
                    "label_source": "dataset_folder_name",
                    "rel_path": rel_path,
                    "abs_path": str(abs_path),
                    "file_sha256": sha256_bytes(data),
                    "raw_trace_id": "",
                    "project_id": environment,
                    "activity_id": "",
                    "site_id": "",
                    "survey_line_id": "",
                    "device_id": "",
                    "antenna_frequency_mhz": "",
                    "acquisition_date": "",
                    "operator_id": "",
                    "processing_chain_id": "published_res_sam_image_export_v1",
                    "export_format": Path(filename).suffix.lower().lstrip("."),
                    "width_px": str(width),
                    "height_px": str(height),
                    "is_augmented": "0",
                    "augmentation_ancestor_id": "",
                    "exact_duplicate_group": "",
                    "near_duplicate_group": "",
                    "source_group": environment,
                    "fold_id": "",
                    "split_protocol": "",
                    "split_role": "",
                    "created_by": "build_ressam_unified_manifest.py",
                    "created_date": CREATED_DATE,
                    "notes": f"mode={mode}; source_archive={zip_path.name}",
                }
            )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip-path", type=Path, required=True)
    parser.add_argument("--extract-dir", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path, required=True)
    parser.add_argument("--summary-md", type=Path, required=True)
    args = parser.parse_args()

    safe_extract(args.zip_path, args.extract_dir)
    fields = schema_fields()
    rows = build_rows(args.zip_path, args.extract_dir)
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})

    counts: dict[tuple[str, str], int] = {}
    for row in rows:
        key = (row["project_id"], row["label"])
        counts[key] = counts.get(key, 0) + 1

    lines = [
        "# Res-SAM Unified Manifest 2026-08-10",
        "",
        f"Archive: `{args.zip_path.name}`",
        f"Samples: {len(rows)}",
        "",
        "| environment | label | count |",
        "| --- | --- | ---: |",
    ]
    for (environment, label), count in sorted(counts.items()):
        lines.append(f"| {environment} | {label} | {count} |")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This manifest establishes Res-SAM as a local data asset. It does not prove",
            "that the full Res-SAM model is reproducible, because the SAM ViT-L checkpoint",
            "is not present in the cloned repository.",
            "",
        ]
    )
    args.summary_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"res_sam rows={len(rows)}")


if __name__ == "__main__":
    main()

