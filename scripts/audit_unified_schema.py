#!/usr/bin/env python3
"""Audit existing sample indexes against the frozen unified schema."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BENCH_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = BENCH_ROOT / "data_manifests" / "unified_sample_schema_20260810.csv"
OUT_PATH = BENCH_ROOT / "reports" / "unified_schema_gap_report_20260810.md"

SAMPLE_INDEXES = {
    "mojahid": ROOT / "manifest" / "mojahid_sample_index_v1.csv",
    "tigpr": ROOT / "manifest" / "tigpr_sample_index_v1.csv",
}


def read_schema_fields() -> list[str]:
    with SCHEMA_PATH.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return [row["field"] for row in reader]


def read_header(path: Path) -> list[str]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.reader(handle)
        return next(reader)


def main() -> None:
    schema_fields = read_schema_fields()
    schema_set = set(schema_fields)
    lines = [
        "# Unified Schema Gap Report 2026-08-10",
        "",
        "This report checks current sample indexes against the frozen unified schema.",
        "",
    ]

    for dataset_id, path in SAMPLE_INDEXES.items():
        current_fields = read_header(path)
        current_set = set(current_fields)
        missing = [field for field in schema_fields if field not in current_set]
        extra = [field for field in current_fields if field not in schema_set]

        lines.extend(
            [
                f"## {dataset_id}",
                "",
                f"Source: `{path.relative_to(ROOT)}`",
                "",
                f"Current field count: {len(current_fields)}",
                f"Unified schema field count: {len(schema_fields)}",
                f"Missing field count: {len(missing)}",
                f"Extra field count: {len(extra)}",
                "",
                "Missing fields:",
                "",
            ]
        )
        lines.extend([f"- `{field}`" for field in missing] or ["- None"])
        lines.extend(["", "Extra fields:", ""])
        lines.extend([f"- `{field}`" for field in extra] or ["- None"])
        lines.append("")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
