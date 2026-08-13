#!/usr/bin/env python3
"""Audit cross-asset hash collisions and independence among local manifests."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "cross_asset_collision_audit_20260811"

DATASETS = {
    "mojahid": BENCH_ROOT / "data_manifests" / "mojahid_unified_samples_20260810.csv",
    "tigpr": BENCH_ROOT / "data_manifests" / "tigpr_unified_samples_20260810.csv",
    "zenodo_14637589": BENCH_ROOT / "data_manifests" / "zenodo_gpr_14637589_raw_manifest_20260811.csv",
    "deepmask_gpr": BENCH_ROOT / "data_manifests" / "deepmask_gpr_unified_samples_20260811.csv",
    "zenodo_mcg_gpr_14270869": BENCH_ROOT / "data_manifests" / "zenodo_mcg_gpr_manifest_20260811.csv",
}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def hash_value(row: dict[str, str]) -> str:
    return row.get("file_sha256", "") or row.get("sha256", "") or row.get("image_sha256", "")


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows_by_dataset = {dataset: read_rows(path) for dataset, path in DATASETS.items()}
    hash_maps: dict[str, dict[str, dict[str, str]]] = {}
    for dataset, rows in rows_by_dataset.items():
        current = {}
        for row in rows:
            digest = hash_value(row)
            if digest:
                current[digest] = row
        hash_maps[dataset] = current

    pair_rows = []
    datasets = list(DATASETS)
    overlap_graph: dict[str, set[str]] = {dataset: set() for dataset in datasets}
    for i, left in enumerate(datasets):
        for right in datasets[i + 1 :]:
            left_hashes = set(hash_maps[left])
            right_hashes = set(hash_maps[right])
            shared = left_hashes & right_hashes
            label_mismatches = 0
            for digest in shared:
                if hash_maps[left][digest].get("label", "") != hash_maps[right][digest].get("label", ""):
                    label_mismatches += 1
            left_fraction = len(shared) / len(left_hashes) if left_hashes else 0.0
            right_fraction = len(shared) / len(right_hashes) if right_hashes else 0.0
            if shared:
                overlap_graph[left].add(right)
                overlap_graph[right].add(left)
            pair_rows.append(
                {
                    "left_dataset": left,
                    "right_dataset": right,
                    "left_rows": len(rows_by_dataset[left]),
                    "right_rows": len(rows_by_dataset[right]),
                    "left_unique_hashes": len(left_hashes),
                    "right_unique_hashes": len(right_hashes),
                    "shared_hashes": len(shared),
                    "left_overlap_fraction": f"{left_fraction:.6f}",
                    "right_overlap_fraction": f"{right_fraction:.6f}",
                    "label_mismatches": label_mismatches,
                    "independent_by_hash": len(shared) == 0,
                }
            )

    seen = set()
    clusters = []
    for dataset in datasets:
        if dataset in seen:
            continue
        stack = [dataset]
        cluster = set()
        while stack:
            item = stack.pop()
            if item in cluster:
                continue
            cluster.add(item)
            stack.extend(sorted(overlap_graph[item] - cluster))
        seen.update(cluster)
        clusters.append(sorted(cluster))

    fully_duplicate_pairs = [
        row
        for row in pair_rows
        if float(row["left_overlap_fraction"]) == 1.0 and float(row["right_overlap_fraction"]) == 1.0
    ]
    summary = {
        "run_id": "20260811_E34_cross_asset_collision_audit",
        "datasets": datasets,
        "dataset_rows": {dataset: len(rows) for dataset, rows in rows_by_dataset.items()},
        "pair_rows": pair_rows,
        "overlap_clusters": clusters,
        "independent_asset_clusters_by_hash": len(clusters),
        "fully_duplicate_pairs": [
            [row["left_dataset"], row["right_dataset"]]
            for row in fully_duplicate_pairs
        ],
        "mojahid_deepmask_complete_sha_overlap": any(
            set(pair) == {"mojahid", "deepmask_gpr"}
            for pair in ([row["left_dataset"], row["right_dataset"]] for row in fully_duplicate_pairs)
        ),
        "deepmask_independent_external_evidence_eligible": False,
        "blind_external_eligible": False,
        "status": "complete_local_cross_asset_collision_audit",
    }
    (OUT_DIR / "cross_asset_collision_audit_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_csv(OUT_DIR / "cross_asset_collision_pair_rows.csv", pair_rows)
    lines = [
        "# Cross-Asset Collision Audit",
        "",
        "| left | right | shared hashes | left overlap | right overlap | label mismatches | independent |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in pair_rows:
        lines.append(
            f"| {row['left_dataset']} | {row['right_dataset']} | {row['shared_hashes']} | "
            f"{row['left_overlap_fraction']} | {row['right_overlap_fraction']} | "
            f"{row['label_mismatches']} | {row['independent_by_hash']} |"
        )
    lines.extend(
        [
            "",
            f"Independent hash clusters: {len(clusters)}",
            f"Fully duplicate pairs: {summary['fully_duplicate_pairs']}",
            "",
            "## Boundary",
            "",
            "Hash-overlapping dataset identifiers must not be counted as independent",
            "external or cross-asset evidence. This audit is local and non-blind.",
            "",
        ]
    )
    (OUT_DIR / "cross_asset_collision_audit_summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": summary["status"],
                "independent_asset_clusters_by_hash": summary["independent_asset_clusters_by_hash"],
                "fully_duplicate_pairs": summary["fully_duplicate_pairs"],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
