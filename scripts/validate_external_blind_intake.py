#!/usr/bin/env python3
"""Validate blind external intake templates and filled manifests.

The default mode validates the template files only. When a real manifest is
provided with --manifest, this script also enforces label blinding and basic
sample-level integrity rules.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = BENCH_ROOT / "data_manifests"
REPORT_DIR = BENCH_ROOT / "reports" / "external_blind_intake_20260810"

MANIFEST_TEMPLATE = DATA_DIR / "external_blind_manifest_template_20260810.csv"
LABEL_TEMPLATE = DATA_DIR / "external_blind_label_holdout_template_20260810.csv"
PREDICTION_TEMPLATE = DATA_DIR / "external_blind_prediction_submission_template_20260810.csv"
PROTOCOL = BENCH_ROOT / "protocols" / "blind_external_validation_protocol_20260810.md"

REQUIRED_MANIFEST_COLUMNS = [
    "sample_id",
    "rel_path",
    "abs_path",
    "file_sha256",
    "label_placeholder",
    "source_group",
    "asset_track",
    "modality",
    "target_task",
    "notes",
]
REQUIRED_LABEL_COLUMNS = [
    "sample_id",
    "sealed_label",
    "label_space_version",
    "label_holder",
    "sealed_timestamp",
    "unlock_timestamp",
    "unlock_authorized_by",
]
REQUIRED_PREDICTION_COLUMNS = [
    "sample_id",
    "predicted_label",
    "prediction_score",
    "model_family",
    "model_version",
    "preprocessing_version",
    "seed",
    "submission_id",
    "prediction_timestamp",
]

ALLOWED_PLACEHOLDERS = {"", "NA", "N/A", "HELD_OUT", "BLINDED"}
ALLOWED_TRACKS = {
    "tigpr_restoration",
    "third_party_blind",
    "4tu_like_raw_trace",
    "other_external",
}
ALLOWED_MODALITIES = {"image", "raw_trace", "mixed"}
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
PLACEHOLDER_SHA = "64_hex_sha256_here"


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def check_columns(path: Path, required: list[str]) -> list[str]:
    issues: list[str] = []
    if not path.exists():
        return [f"missing file: {path}"]
    columns, _ = read_rows(path)
    missing = [column for column in required if column not in columns]
    extra = [column for column in columns if column not in required]
    if missing:
        issues.append(f"{path.name}: missing columns: {', '.join(missing)}")
    if extra:
        issues.append(f"{path.name}: unexpected columns: {', '.join(extra)}")
    return issues


def resolve_payload_path(row: dict[str, str], asset_root: Path | None) -> Path | None:
    abs_path = row.get("abs_path", "").strip()
    if abs_path:
        path = Path(abs_path)
        if path.exists():
            return path
    rel_path = row.get("rel_path", "").strip()
    if rel_path and asset_root is not None:
        path = asset_root / rel_path
        if path.exists():
            return path
    return None


def validate_manifest_rows(
    path: Path,
    strict_sha: bool,
    asset_root: Path | None,
) -> tuple[list[str], dict[str, object]]:
    issues: list[str] = []
    columns, rows = read_rows(path)
    if columns != REQUIRED_MANIFEST_COLUMNS:
        issues.append(
            f"{path.name}: column order differs from protocol contract: {columns}"
        )

    sample_ids: set[str] = set()
    source_groups: set[str] = set()
    target_tasks: set[str] = set()
    tracks: set[str] = set()
    modalities: set[str] = set()
    hash_verified = 0

    for row_number, row in enumerate(rows, start=2):
        sample_id = row.get("sample_id", "").strip()
        if not sample_id:
            issues.append(f"{path.name}:{row_number}: missing sample_id")
        elif sample_id in sample_ids:
            issues.append(f"{path.name}:{row_number}: duplicate sample_id {sample_id}")
        sample_ids.add(sample_id)

        rel_path = row.get("rel_path", "").strip()
        abs_path = row.get("abs_path", "").strip()
        if not rel_path and not abs_path:
            issues.append(f"{path.name}:{row_number}: rel_path or abs_path is required")

        file_sha256 = row.get("file_sha256", "").strip()
        if strict_sha and not SHA256_RE.match(file_sha256):
            issues.append(f"{path.name}:{row_number}: file_sha256 is not a 64-hex digest")
        elif file_sha256 and file_sha256 != PLACEHOLDER_SHA and not SHA256_RE.match(file_sha256):
            issues.append(f"{path.name}:{row_number}: invalid file_sha256 format")
        if strict_sha and SHA256_RE.match(file_sha256):
            payload_path = resolve_payload_path(row, asset_root)
            if payload_path is None:
                issues.append(f"{path.name}:{row_number}: payload file cannot be resolved for SHA-256 verification")
            else:
                observed_sha = sha256_file(payload_path)
                if observed_sha.lower() != file_sha256.lower():
                    issues.append(
                        f"{path.name}:{row_number}: file_sha256 mismatch for {sample_id}: "
                        f"manifest={file_sha256.lower()} observed={observed_sha.lower()}"
                    )
                else:
                    hash_verified += 1

        placeholder = row.get("label_placeholder", "").strip()
        if placeholder not in ALLOWED_PLACEHOLDERS:
            issues.append(
                f"{path.name}:{row_number}: label_placeholder must be blinded, got {placeholder!r}"
            )

        source_group = row.get("source_group", "").strip()
        if not source_group:
            issues.append(f"{path.name}:{row_number}: missing source_group")
        source_groups.add(source_group)

        track = row.get("asset_track", "").strip()
        if track not in ALLOWED_TRACKS:
            issues.append(f"{path.name}:{row_number}: invalid asset_track {track!r}")
        tracks.add(track)

        modality = row.get("modality", "").strip()
        if modality not in ALLOWED_MODALITIES:
            issues.append(f"{path.name}:{row_number}: invalid modality {modality!r}")
        modalities.add(modality)

        target_task = row.get("target_task", "").strip()
        if not target_task:
            issues.append(f"{path.name}:{row_number}: missing target_task")
        target_tasks.add(target_task)

    summary = {
        "rows": len(rows),
        "unique_sample_ids": len(sample_ids),
        "source_groups": sorted(source_groups),
        "asset_tracks": sorted(tracks),
        "modalities": sorted(modalities),
        "target_tasks": sorted(target_tasks),
        "hash_verified_rows": hash_verified,
    }
    return issues, summary


def write_report(result: dict[str, object]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = REPORT_DIR / "external_blind_intake_validation_summary.json"
    md_path = REPORT_DIR / "external_blind_intake_validation_summary.md"
    json_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    lines = [
        "# External Blind Intake Validation 2026-08-10",
        "",
        f"Status: **{result['status']}**",
        "",
        f"Protocol present: `{result['protocol_present']}`",
        f"Manifest checked: `{result['manifest_checked']}`",
        f"Asset root: `{result.get('asset_root', '')}`",
        "",
        "## Summary",
        "",
        f"- rows: {result['manifest_summary'].get('rows', 0)}",
        f"- unique_sample_ids: {result['manifest_summary'].get('unique_sample_ids', 0)}",
        f"- hash_verified_rows: {result['manifest_summary'].get('hash_verified_rows', 0)}",
        f"- source_groups: {', '.join(result['manifest_summary'].get('source_groups', []))}",
        f"- asset_tracks: {', '.join(result['manifest_summary'].get('asset_tracks', []))}",
        f"- modalities: {', '.join(result['manifest_summary'].get('modalities', []))}",
        f"- target_tasks: {', '.join(result['manifest_summary'].get('target_tasks', []))}",
        "",
        "## Issues",
        "",
    ]
    issues = result["issues"]
    if issues:
        lines.extend(f"- {issue}" for issue in issues)
    else:
        lines.append("- none")
    lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        type=Path,
        default=MANIFEST_TEMPLATE,
        help="Manifest to validate. Defaults to the blind intake template.",
    )
    parser.add_argument(
        "--strict-sha",
        action="store_true",
        help="Require every file_sha256 to be a real 64-hex digest.",
    )
    parser.add_argument(
        "--asset-root",
        type=Path,
        help="Root used to resolve rel_path values when abs_path is omitted.",
    )
    args = parser.parse_args()

    issues: list[str] = []
    issues.extend(check_columns(MANIFEST_TEMPLATE, REQUIRED_MANIFEST_COLUMNS))
    issues.extend(check_columns(LABEL_TEMPLATE, REQUIRED_LABEL_COLUMNS))
    issues.extend(check_columns(PREDICTION_TEMPLATE, REQUIRED_PREDICTION_COLUMNS))
    if not PROTOCOL.exists():
        issues.append(f"missing protocol: {PROTOCOL}")

    manifest = args.manifest
    if not manifest.exists():
        issues.append(f"manifest to validate does not exist: {manifest}")
        manifest_summary: dict[str, object] = {}
    else:
        row_issues, manifest_summary = validate_manifest_rows(manifest, args.strict_sha, args.asset_root)
        issues.extend(row_issues)

    result = {
        "status": "PASS" if not issues else "FAIL",
        "protocol_present": PROTOCOL.exists(),
        "manifest_checked": str(manifest),
        "strict_sha": bool(args.strict_sha),
        "asset_root": str(args.asset_root) if args.asset_root else "",
        "manifest_summary": manifest_summary,
        "issues": issues,
        "note": "PASS validates structure and blinding contract only; it does not mean a real blind external asset is available.",
    }
    write_report(result)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
