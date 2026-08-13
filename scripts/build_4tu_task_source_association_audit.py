#!/usr/bin/env python3
"""Audit 4TU task-label association with project/split source fields."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from sklearn.metrics import mutual_info_score, normalized_mutual_info_score


TARGET_FIELDS = [
    "Land type",
    "Land use",
    "Land cover",
    "Utility crossing",
    "Construction workers",
    "Relative groundwater level",
]
SOURCE_FIELDS = ["project_id", "split_role"]
MISSING = {"", "unknown", "NA", "N/A"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fieldnames = sorted({key for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def cramer_v(target: list[str], source: list[str]) -> float:
    target_levels = sorted(set(target))
    source_levels = sorted(set(source))
    table = np.zeros((len(target_levels), len(source_levels)), dtype=np.float64)
    ti = {value: idx for idx, value in enumerate(target_levels)}
    si = {value: idx for idx, value in enumerate(source_levels)}
    for t, s in zip(target, source):
        table[ti[t], si[s]] += 1.0
    n = table.sum()
    expected = np.outer(table.sum(axis=1), table.sum(axis=0)) / n
    mask = expected > 0
    chi2 = float(((table[mask] - expected[mask]) ** 2 / expected[mask]).sum())
    denom = n * max(1, min(table.shape[0] - 1, table.shape[1] - 1))
    return float(np.sqrt(chi2 / denom)) if denom > 0 else 0.0


def source_purity(target: list[str], source: list[str]) -> tuple[float, float]:
    by_source: dict[str, list[str]] = defaultdict(list)
    for t, s in zip(target, source):
        by_source[s].append(t)
    purities = []
    pure = 0
    for labels in by_source.values():
        counts = Counter(labels)
        purities.append(max(counts.values()) / len(labels))
        pure += int(len(counts) == 1)
    return float(np.mean(purities)), float(pure / len(by_source))


def permutation_p_value(target: list[str], source: list[str], observed_mi: float, seed: int, n_permutations: int) -> float:
    rng = np.random.default_rng(seed)
    source_arr = np.asarray(source)
    target_arr = np.asarray(target)
    ge = 0
    for _ in range(n_permutations):
        permuted = rng.permutation(source_arr)
        ge += int(float(mutual_info_score(target_arr, permuted)) >= observed_mi)
    return float((ge + 1) / (n_permutations + 1))


def feasible_status(feasibility_rows: list[dict[str, str]]) -> dict[str, str]:
    return {row["target"]: row["status"] for row in feasibility_rows}


def audit_pair(
    rows: list[dict[str, str]],
    target_field: str,
    source_field: str,
    status_by_target: dict[str, str],
    seed: int,
    n_permutations: int,
) -> dict[str, object]:
    filtered = [
        row
        for row in rows
        if row.get(target_field, "").strip() not in MISSING
        and row.get(source_field, "").strip() not in MISSING
    ]
    target = [row[target_field].strip() for row in filtered]
    source = [row[source_field].strip() for row in filtered]
    result: dict[str, object] = {
        "target_field": target_field,
        "source_field": source_field,
        "feasibility_status": status_by_target.get(target_field, "not_in_feasibility_audit"),
        "samples": int(len(filtered)),
        "target_classes": int(len(set(target))),
        "source_classes": int(len(set(source))),
    }
    if len(set(target)) < 2 or len(set(source)) < 2:
        result.update({"status": "not_viable", "reason": "fewer than two target or source classes"})
        return result

    mi = float(mutual_info_score(target, source))
    mean_purity, pure_fraction = source_purity(target, source)
    result.update(
        {
            "status": "complete",
            "mutual_information_nats": mi,
            "normalized_mutual_information": float(normalized_mutual_info_score(target, source)),
            "cramers_v": cramer_v(target, source),
            "permutation_p_value_mi": permutation_p_value(target, source, mi, seed, n_permutations),
            "mean_source_purity": mean_purity,
            "pure_source_group_fraction": pure_fraction,
        }
    )
    return result


def write_md(path: Path, summary: dict[str, object]) -> None:
    lines = [
        "# 4TU Task-Source Association Audit",
        "",
        f"Permutation draws per complete pair: `{summary['n_permutations']}`",
        "",
        "| target | source | feasibility | samples | labels | source classes | NMI | Cramer's V | MI p | mean purity |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in summary["pair_rows"]:
        if row["status"] != "complete":
            lines.append(
                f"| {row['target_field']} | {row['source_field']} | {row['feasibility_status']} | "
                f"{row['samples']} | {row['target_classes']} | {row['source_classes']} | NA | NA | NA | NA |"
            )
            continue
        lines.append(
            f"| {row['target_field']} | {row['source_field']} | {row['feasibility_status']} | "
            f"{row['samples']} | {row['target_classes']} | {row['source_classes']} | "
            f"{row['normalized_mutual_information']:.4f} | {row['cramers_v']:.4f} | "
            f"{row['permutation_p_value_mi']:.4f} | {row['mean_source_purity']:.4f} |"
        )
    lines.extend(
        [
            "",
            "Boundary: this uses 4TU task-level metadata labels, not pixel-level or",
            "trace-level target annotations. It strengthens the feasibility-boundary",
            "audit and should not be promoted to main confirmation evidence.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-labels", type=Path, required=True)
    parser.add_argument("--feasibility-targets", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20260811)
    parser.add_argument("--n-permutations", type=int, default=1000)
    args = parser.parse_args()

    rows = read_csv(args.task_labels)
    status_by_target = feasible_status(read_csv(args.feasibility_targets))
    pair_rows = [
        audit_pair(rows, target, source, status_by_target, args.seed, args.n_permutations)
        for target in TARGET_FIELDS
        for source in SOURCE_FIELDS
    ]
    project_rows = [row for row in pair_rows if row["source_field"] == "project_id" and row["status"] == "complete"]
    strongest_project = max(project_rows, key=lambda row: float(row["normalized_mutual_information"]))
    summary = {
        "run_id": "20260811_E10_4tu_task_source_association_audit",
        "seed": args.seed,
        "n_permutations": args.n_permutations,
        "pair_rows": pair_rows,
        "complete_pairs": int(sum(row["status"] == "complete" for row in pair_rows)),
        "strongest_project_association": strongest_project,
        "claim_boundary": "4TU task-metadata feasibility-boundary association; not main confirmation.",
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "4tu_task_source_association_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_csv(args.output_dir / "4tu_task_source_association_rows.csv", pair_rows)
    write_md(args.output_dir / "4tu_task_source_association_summary.md", summary)
    print(json.dumps(summary["strongest_project_association"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
