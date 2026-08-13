#!/usr/bin/env python3
"""Join 4TU package rows with activity-level task metadata."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


TARGET_FIELDS = [
    "Land type",
    "Land use",
    "Land cover",
    "Utility crossing",
    "Construction workers",
    "Relative groundwater level",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def normalize(value: str) -> str:
    text = str(value).strip()
    return text if text else "unknown"


def activity_number(value: str) -> str:
    text = normalize(value)
    return text.split(".", 1)[1] if "." in text else text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-manifest", type=Path, required=True)
    parser.add_argument("--activity-manifest", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path, required=True)
    parser.add_argument("--unmatched-csv", type=Path, required=True)
    parser.add_argument("--summary-md", type=Path, required=True)
    args = parser.parse_args()

    package_rows = read_csv(args.package_manifest)
    activity_rows = read_csv(args.activity_manifest)
    activity_lookup = {
        (normalize(row["project_id"]), normalize(row["activity_id"])): row
        for row in activity_rows
    }

    joined: list[dict[str, str]] = []
    unmatched: list[dict[str, str]] = []
    for row in package_rows:
        key = (normalize(row["project_id"]), activity_number(row["activity_id"]))
        meta = activity_lookup.get(key)
        if meta is None:
            unmatched.append(row)
            continue
        out = {
            "split_role": row["split_role"],
            "project_id": row["project_id"],
            "activity_id": row["activity_id"],
            "member": row["member"],
            "package_npy_path": row["package_npy_path"],
            "shape_rows": row.get("shape_rows", ""),
            "shape_cols": row.get("shape_cols", ""),
        }
        for field in TARGET_FIELDS:
            out[field] = normalize(meta.get(field, "unknown"))
        joined.append(out)

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "split_role",
        "project_id",
        "activity_id",
        "member",
        "package_npy_path",
        "shape_rows",
        "shape_cols",
        *TARGET_FIELDS,
    ]
    with args.output_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(joined)

    with args.unmatched_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(package_rows[0].keys()))
        writer.writeheader()
        writer.writerows(unmatched)

    lines = [
        "# 4TU Task Label Join 2026-08-10",
        "",
        f"Package rows: {len(package_rows)}",
        f"Activity metadata rows: {len(activity_rows)}",
        f"Matched rows: {len(joined)}",
        f"Unmatched rows: {len(unmatched)}",
        "",
        "## Target Fields",
        "",
    ]
    lines.extend([f"- `{field}`" for field in TARGET_FIELDS])
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This join supports task-specific 4TU smoke baselines. These labels are",
            "activity-level metadata, not pixel-level or trace-level target annotations.",
            "",
        ]
    )
    args.summary_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"matched={len(joined)} unmatched={len(unmatched)}")


if __name__ == "__main__":
    main()

