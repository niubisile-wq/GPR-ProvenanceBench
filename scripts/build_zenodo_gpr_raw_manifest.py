#!/usr/bin/env python3
"""Build a file-level manifest for Zenodo record 14637589 raw GPR assets."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from datetime import date
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
ROOT = BENCH_ROOT.parent
ASSET_DIR = ROOT / "external_assets" / "zenodo_gpr_14637589"
ARCHIVE = ASSET_DIR / "Data Set.zip"
EXTRACTED_ROOT = ASSET_DIR / "extracted" / "Data Set"
OUT_DIR = BENCH_ROOT / "reports" / "zenodo_gpr_raw_asset_audit_20260811"
ROOT_MANIFEST = ROOT / "manifest" / "zenodo_gpr_14637589_raw_manifest_20260811.csv"
BENCH_MANIFEST = BENCH_ROOT / "data_manifests" / "zenodo_gpr_14637589_raw_manifest_20260811.csv"

EXPECTED_ARCHIVE_MD5 = "a20da497549c01f7f079e68e46ed7c87"
RAW_EXTENSIONS = {".dt", ".rd3", ".sgy", ".dat", ".srd"}
CALIBRATION_EXTENSIONS = {".bkg", ".stc", ".rad", ".zon", ".par", ".ini", ".mis", ".rep"}


def file_hash(path: Path, algorithm: str = "sha256") -> str:
    digest = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel_to_root(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def classify_extension(ext: str) -> str:
    ext = ext.lower()
    if ext in RAW_EXTENSIONS:
        return "raw_trace"
    if ext in CALIBRATION_EXTENSIONS:
        return "instrument_or_processing_metadata"
    if ext in {".jpg", ".txt", ".m", ".zip"}:
        return "supporting_file"
    return "other_or_vendor_specific"


def project_from_parts(parts: tuple[str, ...]) -> str:
    if len(parts) >= 3:
        return parts[1]
    if len(parts) >= 2:
        return parts[0]
    return "unknown"


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_md(path: Path, result: dict[str, object]) -> None:
    lines = [
        "# Zenodo GPR Raw Asset Audit",
        "",
        "Dataset: Zenodo record 14637589, DOI 10.5281/zenodo.14637589.",
        "",
        "This is a public labelled/organized dataset and is not blind-external validation.",
        "",
        "## Archive",
        "",
        f"- Local archive: `{result['archive']['local_path']}`",
        f"- Size bytes: {result['archive']['size_bytes']}",
        f"- Expected MD5: `{result['archive']['expected_md5']}`",
        f"- Actual MD5: `{result['archive']['actual_md5']}`",
        f"- MD5 verified: {result['archive']['md5_verified']}",
        "",
        "## File Inventory",
        "",
        f"- Total files: {result['inventory']['total_files']}",
        f"- Total bytes: {result['inventory']['total_bytes']}",
        f"- Raw trace files: {result['inventory']['raw_trace_files']}",
        f"- Raw trace bytes: {result['inventory']['raw_trace_bytes']}",
        f"- Manifest rows: {result['manifest_rows']}",
        "",
        "## Top Category Counts",
        "",
        "| category | all files | raw trace files | raw trace bytes |",
        "| --- | ---: | ---: | ---: |",
    ]
    for category, row in result["category_summary"].items():
        lines.append(
            f"| {category} | {row['all_files']} | {row['raw_trace_files']} | {row['raw_trace_bytes']} |"
        )
    lines.extend(
        [
            "",
            "## Extension Counts",
            "",
            "| extension | count | bytes | role |",
            "| --- | ---: | ---: | --- |",
        ]
    )
    for ext, row in result["extension_summary"].items():
        lines.append(f"| `{ext}` | {row['count']} | {row['bytes']} | {row['role']} |")
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            f"- Root manifest: `{result['outputs']['root_manifest']}`",
            f"- Bench manifest: `{result['outputs']['bench_manifest']}`",
            "",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if not ARCHIVE.exists():
        raise FileNotFoundError(f"Missing archive: {ARCHIVE}")
    if not EXTRACTED_ROOT.exists():
        raise FileNotFoundError(f"Missing extracted root: {EXTRACTED_ROOT}")

    archive_md5 = file_hash(ARCHIVE, "md5")
    all_files = [path for path in EXTRACTED_ROOT.rglob("*") if path.is_file()]
    rows: list[dict[str, object]] = []
    category_counts: dict[str, Counter[str]] = {}
    category_bytes: dict[str, Counter[str]] = {}
    extension_counts: dict[str, Counter[str]] = {}

    for path in sorted(all_files, key=lambda item: item.relative_to(EXTRACTED_ROOT).as_posix().lower()):
        rel_parts = path.relative_to(EXTRACTED_ROOT).parts
        top_category = rel_parts[0] if rel_parts else "unknown"
        project_id = project_from_parts(rel_parts)
        acquisition_id = path.parent.name
        ext = path.suffix.lower()
        role = classify_extension(ext)
        size = path.stat().st_size
        category_counts.setdefault(top_category, Counter())
        category_bytes.setdefault(top_category, Counter())
        extension_counts.setdefault(ext or "<none>", Counter())
        category_counts[top_category]["all_files"] += 1
        category_bytes[top_category]["all_bytes"] += size
        extension_counts[ext or "<none>"]["count"] += 1
        extension_counts[ext or "<none>"]["bytes"] += size
        if role == "raw_trace":
            category_counts[top_category]["raw_trace_files"] += 1
            category_bytes[top_category]["raw_trace_bytes"] += size
            rows.append(
                {
                    "dataset_id": "zenodo_14637589",
                    "doi": "10.5281/zenodo.14637589",
                    "license": "cc-by-4.0",
                    "sample_id": f"zenodo_14637589_{len(rows):05d}",
                    "label": top_category,
                    "top_category": top_category,
                    "project_id": project_id,
                    "source_group": f"{top_category}/{project_id}",
                    "split_group": f"{top_category}/{project_id}",
                    "acquisition_id": acquisition_id,
                    "extension": ext,
                    "modality": "raw_gpr_trace",
                    "file_role": role,
                    "size_bytes": size,
                    "sha256": file_hash(path, "sha256"),
                    "relative_path": path.relative_to(EXTRACTED_ROOT).as_posix(),
                    "root_relative_path": rel_to_root(path),
                    "absolute_path": str(path),
                    "manifest_date": date.today().isoformat(),
                    "blind_external_eligible": False,
                    "blind_external_reason": "public labelled or organized dataset; labels are visible before prediction freeze",
                }
            )

    fieldnames = [
        "dataset_id",
        "doi",
        "license",
        "sample_id",
        "label",
        "top_category",
        "project_id",
        "source_group",
        "split_group",
        "acquisition_id",
        "extension",
        "modality",
        "file_role",
        "size_bytes",
        "sha256",
        "relative_path",
        "root_relative_path",
        "absolute_path",
        "manifest_date",
        "blind_external_eligible",
        "blind_external_reason",
    ]
    write_csv(ROOT_MANIFEST, rows, fieldnames)
    write_csv(BENCH_MANIFEST, rows, fieldnames)

    category_summary = {}
    for category in sorted(category_counts):
        category_summary[category] = {
            "all_files": int(category_counts[category]["all_files"]),
            "all_bytes": int(category_bytes[category]["all_bytes"]),
            "raw_trace_files": int(category_counts[category]["raw_trace_files"]),
            "raw_trace_bytes": int(category_bytes[category]["raw_trace_bytes"]),
        }
    extension_summary = {}
    for ext, counts in sorted(extension_counts.items(), key=lambda item: (-item[1]["count"], item[0])):
        extension_summary[ext] = {
            "count": int(counts["count"]),
            "bytes": int(counts["bytes"]),
            "role": classify_extension("" if ext == "<none>" else ext),
        }

    result = {
        "run_id": "20260811_E17_zenodo_gpr_raw_asset_audit",
        "archive": {
            "local_path": rel_to_root(ARCHIVE),
            "size_bytes": ARCHIVE.stat().st_size,
            "expected_md5": EXPECTED_ARCHIVE_MD5,
            "actual_md5": archive_md5,
            "md5_verified": archive_md5 == EXPECTED_ARCHIVE_MD5,
        },
        "extracted_root": rel_to_root(EXTRACTED_ROOT),
        "inventory": {
            "total_files": len(all_files),
            "total_bytes": sum(path.stat().st_size for path in all_files),
            "raw_trace_files": len(rows),
            "raw_trace_bytes": sum(int(row["size_bytes"]) for row in rows),
        },
        "manifest_rows": len(rows),
        "category_summary": category_summary,
        "extension_summary": extension_summary,
        "outputs": {
            "root_manifest": rel_to_root(ROOT_MANIFEST),
            "bench_manifest": BENCH_MANIFEST.relative_to(BENCH_ROOT).as_posix(),
        },
        "blind_external_eligible": False,
        "status": "downloaded_verified_extracted_manifested",
    }
    (OUT_DIR / "zenodo_gpr_raw_asset_audit_summary.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    write_md(OUT_DIR / "zenodo_gpr_raw_asset_audit_summary.md", result)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
