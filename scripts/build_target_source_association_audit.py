#!/usr/bin/env python3
"""Audit target-source association metrics from unified manifests."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from sklearn.metrics import mutual_info_score, normalized_mutual_info_score


DEFAULT_TASKS = [
    ("mojahid_label_vs_source_group", "mojahid", "label", "source_group"),
    ("mojahid_label_vs_processing_role", "mojahid", "label", "is_augmented"),
    ("ressam_label_vs_environment", "res_sam", "label", "source_group"),
    ("four_tu_label_vs_project", "four_tu", "label", "project_id"),
]


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


def entropy(values: list[str]) -> float:
    counts = np.asarray(list(Counter(values).values()), dtype=np.float64)
    probs = counts / counts.sum()
    return float(-(probs * np.log2(probs)).sum())


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


def source_purity(target: list[str], source: list[str]) -> dict[str, float]:
    by_source: dict[str, list[str]] = defaultdict(list)
    for t, s in zip(target, source):
        by_source[s].append(t)
    purities = []
    pure_groups = 0
    singleton_groups = 0
    for labels in by_source.values():
        counts = Counter(labels)
        purity = max(counts.values()) / len(labels)
        purities.append(purity)
        pure_groups += int(len(counts) == 1)
        singleton_groups += int(len(labels) == 1)
    return {
        "source_groups": float(len(by_source)),
        "mean_source_purity": float(np.mean(purities)) if purities else 0.0,
        "pure_source_group_fraction": float(pure_groups / len(by_source)) if by_source else 0.0,
        "singleton_source_group_fraction": float(singleton_groups / len(by_source)) if by_source else 0.0,
    }


def permutation_p_value(target: list[str], source: list[str], observed_mi: float, seed: int, n_permutations: int) -> float:
    rng = np.random.default_rng(seed)
    target_arr = np.asarray(target)
    source_arr = np.asarray(source)
    ge = 0
    for _ in range(n_permutations):
        shuffled = rng.permutation(source_arr)
        perm_mi = float(mutual_info_score(target_arr, shuffled))
        ge += int(perm_mi >= observed_mi)
    return float((ge + 1) / (n_permutations + 1))


def audit_task(
    task_id: str,
    rows: list[dict[str, str]],
    target_field: str,
    source_field: str,
    seed: int,
    n_permutations: int,
) -> dict[str, object]:
    filtered = [
        row
        for row in rows
        if row.get(target_field, "").strip()
        and row.get(source_field, "").strip()
        and row.get(target_field, "").strip() not in {"unknown", "unlabeled_raw_trace_matrix"}
        and row.get(source_field, "").strip() not in {"unknown", "NA", "N/A"}
    ]
    target = [row[target_field].strip() for row in filtered]
    source = [row[source_field].strip() for row in filtered]
    if len(set(target)) < 2 or len(set(source)) < 2:
        return {
            "task_id": task_id,
            "status": "not_viable",
            "samples": len(filtered),
            "target_field": target_field,
            "source_field": source_field,
            "target_classes": len(set(target)),
            "source_classes": len(set(source)),
            "reason": "fewer than two classes in target or source",
        }
    mi = float(mutual_info_score(target, source))
    nmi = float(normalized_mutual_info_score(target, source))
    result = {
        "task_id": task_id,
        "status": "complete",
        "samples": int(len(filtered)),
        "target_field": target_field,
        "source_field": source_field,
        "target_classes": int(len(set(target))),
        "source_classes": int(len(set(source))),
        "target_entropy_bits": entropy(target),
        "source_entropy_bits": entropy(source),
        "mutual_information_nats": mi,
        "normalized_mutual_information": nmi,
        "cramers_v": cramer_v(target, source),
        "permutation_p_value_mi": permutation_p_value(target, source, mi, seed, n_permutations),
        **source_purity(target, source),
    }
    return result


def write_md(path: Path, summary: dict[str, object]) -> None:
    lines = [
        "# Target-Source Association Audit",
        "",
        f"Permutation draws per complete task: `{summary['n_permutations']}`",
        "",
        "| task | samples | target classes | source classes | NMI | Cramer's V | MI permutation p | mean source purity | pure source groups |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in summary["task_rows"]:
        if row["status"] != "complete":
            lines.append(
                f"| {row['task_id']} | {row['samples']} | {row['target_classes']} | "
                f"{row['source_classes']} | NA | NA | NA | NA | NA |"
            )
            continue
        lines.append(
            f"| {row['task_id']} | {row['samples']} | {row['target_classes']} | {row['source_classes']} | "
            f"{row['normalized_mutual_information']:.4f} | {row['cramers_v']:.4f} | "
            f"{row['permutation_p_value_mi']:.4f} | {row['mean_source_purity']:.4f} | "
            f"{row['pure_source_group_fraction']:.4f} |"
        )
    lines.extend(
        [
            "",
            "Boundary: this is a manifest-level target-source coupling audit. It",
            "quantifies label/source association but does not prove external",
            "generalization or causal mechanism by itself.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mojahid-manifest", type=Path, required=True)
    parser.add_argument("--ressam-manifest", type=Path, required=True)
    parser.add_argument("--four-tu-manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20260811)
    parser.add_argument("--n-permutations", type=int, default=1000)
    args = parser.parse_args()

    manifests = {
        "mojahid": read_csv(args.mojahid_manifest),
        "res_sam": read_csv(args.ressam_manifest),
        "four_tu": read_csv(args.four_tu_manifest),
    }
    task_rows = [
        audit_task(task_id, manifests[manifest_key], target_field, source_field, args.seed, args.n_permutations)
        for task_id, manifest_key, target_field, source_field in DEFAULT_TASKS
    ]
    summary = {
        "run_id": "20260811_E09_target_source_association_audit",
        "seed": args.seed,
        "n_permutations": args.n_permutations,
        "task_rows": task_rows,
        "complete_tasks": int(sum(row["status"] == "complete" for row in task_rows)),
        "claim_boundary": "Manifest-level target-source coupling audit; not blind external validation.",
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "target_source_association_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_csv(args.output_dir / "target_source_association_rows.csv", task_rows)
    write_md(args.output_dir / "target_source_association_summary.md", summary)
    print(json.dumps(task_rows, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
