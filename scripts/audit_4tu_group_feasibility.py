#!/usr/bin/env python3
"""Audit whether 4TU can support stronger project-level validation splits."""

from __future__ import annotations

import argparse
import csv
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path


TARGET_FIELDS = [
    "Land type",
    "Land use",
    "Land cover",
    "Utility crossing",
    "Construction workers",
    "Relative groundwater level",
]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def non_unknown(value: str) -> bool:
    return value.strip() not in {"", "unknown", "None"}


def project_label_counts(rows: list[dict[str, str]], target: str) -> dict[str, Counter]:
    counts: dict[str, Counter] = defaultdict(Counter)
    for row in rows:
        label = row.get(target, "")
        if non_unknown(label):
            counts[row["project_id"]][label] += 1
    return dict(counts)


def label_project_support(project_counts: dict[str, Counter]) -> dict[str, int]:
    support: Counter = Counter()
    for counts in project_counts.values():
        for label in counts:
            support[label] += 1
    return dict(sorted(support.items()))


def label_sample_counts(project_counts: dict[str, Counter]) -> dict[str, int]:
    totals: Counter = Counter()
    for counts in project_counts.values():
        totals.update(counts)
    return dict(sorted(totals.items()))


def split_label_set(project_counts: dict[str, Counter], projects: tuple[str, ...]) -> set[str]:
    labels: set[str] = set()
    for project in projects:
        labels.update(project_counts.get(project, {}).keys())
    return labels


def count_feasible_splits(project_counts: dict[str, Counter], test_size: int, val_size: int) -> dict[str, object]:
    projects = sorted(project_counts)
    feasible = 0
    attempted = 0
    examples = []
    for test_projects in itertools.combinations(projects, test_size):
        remaining_after_test = [project for project in projects if project not in test_projects]
        for val_projects in itertools.combinations(remaining_after_test, val_size):
            train_projects = tuple(project for project in remaining_after_test if project not in val_projects)
            attempted += 1
            train_labels = split_label_set(project_counts, train_projects)
            val_labels = split_label_set(project_counts, val_projects)
            test_labels = split_label_set(project_counts, test_projects)
            if len(train_labels) < 2 or len(val_labels) < 2 or len(test_labels) < 2:
                continue
            if not val_labels.issubset(train_labels):
                continue
            if not test_labels.issubset(train_labels):
                continue
            feasible += 1
            if len(examples) < 5:
                examples.append(
                    {
                        "train_projects": list(train_projects),
                        "val_projects": list(val_projects),
                        "test_projects": list(test_projects),
                        "train_labels": sorted(train_labels),
                        "val_labels": sorted(val_labels),
                        "test_labels": sorted(test_labels),
                    }
                )
    return {"attempted": attempted, "feasible": feasible, "examples": examples}


def summarize_target(rows: list[dict[str, str]], target: str) -> dict[str, object]:
    project_counts = project_label_counts(rows, target)
    project_count = len(project_counts)
    sample_count = sum(sum(counts.values()) for counts in project_counts.values())
    label_counts = label_sample_counts(project_counts)
    label_support = label_project_support(project_counts)
    rare_labels = {label: count for label, count in label_support.items() if count < 3}
    singleton_labels = {label: count for label, count in label_support.items() if count == 1}
    project_rows = []
    for project, counts in sorted(project_counts.items()):
        project_rows.append(
            {
                "project_id": project,
                "n_samples": int(sum(counts.values())),
                "n_labels": int(len(counts)),
                "labels": dict(sorted(counts.items())),
            }
        )
    split_grid = {}
    if project_count >= 5:
        for test_size, val_size in [(1, 1), (1, 2), (2, 1), (2, 2), (3, 2)]:
            if project_count > test_size + val_size:
                split_grid[f"test{test_size}_val{val_size}"] = count_feasible_splits(
                    project_counts,
                    test_size,
                    val_size,
                )
    status = "usable_with_caution"
    if project_count < 5 or len(label_counts) < 2:
        status = "not_viable"
    elif singleton_labels:
        status = "weak_due_to_single_project_labels"
    elif rare_labels:
        status = "weak_due_to_rare_project_labels"
    if all(item["feasible"] == 0 for item in split_grid.values()):
        status = "not_viable_for_group_holdout"
    return {
        "target": target,
        "status": status,
        "sample_count": sample_count,
        "project_count": project_count,
        "label_counts": label_counts,
        "label_project_support": label_support,
        "rare_labels_project_support_lt3": rare_labels,
        "singleton_labels": singleton_labels,
        "project_rows": project_rows,
        "split_grid": split_grid,
    }


def read_existing_group_result(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    selected = [row for row in data.get("aggregate", []) if row.get("variant") == "log_clip"]
    compact = []
    for row in selected:
        compact.append(
            {
                "model": row.get("model"),
                "n_splits": row.get("n_splits"),
                "original_BA_mean": row.get("test_balanced_accuracy_mean")
                if row.get("variant") == "original"
                else None,
                "log_clip_BA_mean": row.get("test_balanced_accuracy_mean"),
                "log_clip_delta_mean": row.get("balanced_accuracy_delta_mean"),
                "flip_mean": row.get("prediction_flip_rate_mean"),
            }
        )
    return {
        "path": str(path),
        "target": data.get("target"),
        "n_metric_rows": data.get("n_metric_rows"),
        "split_seeds": data.get("split_seeds"),
        "selected_models_by_run": [run.get("selected_model") for run in data.get("runs", [])],
        "log_clip_aggregate": compact,
    }


def write_csvs(out_dir: Path, result: dict[str, object]) -> None:
    target_path = out_dir / "4tu_group_feasibility_targets.csv"
    with target_path.open("w", newline="", encoding="utf-8") as handle:
        fields = [
            "target",
            "status",
            "sample_count",
            "project_count",
            "n_labels",
            "singleton_labels",
            "rare_labels_project_support_lt3",
            "test2_val2_attempted",
            "test2_val2_feasible",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for item in result["targets"]:
            grid = item["split_grid"].get("test2_val2", {})
            writer.writerow(
                {
                    "target": item["target"],
                    "status": item["status"],
                    "sample_count": item["sample_count"],
                    "project_count": item["project_count"],
                    "n_labels": len(item["label_counts"]),
                    "singleton_labels": "; ".join(item["singleton_labels"].keys()),
                    "rare_labels_project_support_lt3": "; ".join(item["rare_labels_project_support_lt3"].keys()),
                    "test2_val2_attempted": grid.get("attempted", ""),
                    "test2_val2_feasible": grid.get("feasible", ""),
                }
            )

    project_path = out_dir / "4tu_group_feasibility_project_labels.csv"
    with project_path.open("w", newline="", encoding="utf-8") as handle:
        fields = ["target", "project_id", "n_samples", "n_labels", "labels_json"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for item in result["targets"]:
            for row in item["project_rows"]:
                writer.writerow(
                    {
                        "target": item["target"],
                        "project_id": row["project_id"],
                        "n_samples": row["n_samples"],
                        "n_labels": row["n_labels"],
                        "labels_json": json.dumps(row["labels"], ensure_ascii=False, sort_keys=True),
                    }
                )


def write_md(path: Path, result: dict[str, object]) -> None:
    lines = [
        "# 4TU Group-Aware Feasibility Audit 2026-08-10",
        "",
        "Purpose: determine whether the current 4TU metadata labels can support stronger project-level validation, or whether effort should move to external validation.",
        "",
        "## Target Summary",
        "",
        "| target | status | samples | projects | labels | test2/val2 feasible | rare project labels |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in result["targets"]:
        grid = item["split_grid"].get("test2_val2", {})
        rare = ", ".join(item["rare_labels_project_support_lt3"].keys()) or "none"
        lines.append(
            f"| {item['target']} | {item['status']} | {item['sample_count']} | "
            f"{item['project_count']} | {len(item['label_counts'])} | "
            f"{grid.get('feasible', '')}/{grid.get('attempted', '')} | {rare} |"
        )

    lines.extend(["", "## Land Type Project Coverage", "", "| project | n | labels |", "| --- | ---: | --- |"])
    land_type = next(item for item in result["targets"] if item["target"] == "Land type")
    for row in land_type["project_rows"]:
        labels = ", ".join(f"{label}: {count}" for label, count in row["labels"].items())
        lines.append(f"| {row['project_id']} | {row['n_samples']} | {labels} |")

    lines.extend(
        [
            "",
            "## Existing Group-Split Result",
            "",
            f"- Existing target: `{result['existing_group_result'].get('target', '')}`.",
            f"- Metric rows: `{result['existing_group_result'].get('n_metric_rows', '')}`.",
            f"- Selected models by split: `{', '.join(result['existing_group_result'].get('selected_models_by_run', []))}`.",
            "",
            "| model | n_splits | log_clip BA_mean | log_clip delta_mean | flip_mean |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in result["existing_group_result"].get("log_clip_aggregate", []):
        lines.append(
            f"| {row['model']} | {row['n_splits']} | {row['log_clip_BA_mean']:.4f} | "
            f"{row['log_clip_delta_mean']:.4f} | {row['flip_mean']:.4f} |"
        )

    lines.extend(
        [
            "",
            "## Decision",
            "",
            "The current 4TU labels can produce some project-level holdouts, but they are not strong enough to serve as the main cross-model confirmation layer. Land type has feasible test2/val2 project splits, but model selection collapses to weak classifiers in several splits and the selected ExtraTrees signal appears in only 2/5 repeated splits.",
            "",
            "## Protocol Consequence",
            "",
            "1. Keep 4TU as raw-trace counterfactual and stress-test evidence.",
            "2. Do not force a full five-model 4TU matrix as the next priority unless a stronger grouped split design or more balanced labels are added.",
            "3. Prioritize external or 4TU-like validation data for the next confirmation layer.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--task-manifest",
        type=Path,
        default=Path("GPR-ProvenanceBench/reports/4tu_p4v2_multitarget_20260810/4tu_p4v2_task_labels_20260810.csv"),
    )
    parser.add_argument(
        "--group-result",
        type=Path,
        default=Path("GPR-ProvenanceBench/reports/4tu_counterfactual_hog_group_splits_20260810/hog_group_split_summary.json"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("GPR-ProvenanceBench/reports/4tu_group_feasibility_20260810"),
    )
    args = parser.parse_args()

    rows = read_rows(args.task_manifest)
    result = {
        "run_id": "20260810_E00_4tu_group_feasibility_audit",
        "task_manifest": str(args.task_manifest),
        "targets": [summarize_target(rows, target) for target in TARGET_FIELDS],
        "existing_group_result": read_existing_group_result(args.group_result),
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "4tu_group_feasibility_summary.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_csvs(args.output_dir, result)
    write_md(args.output_dir / "4tu_group_feasibility_summary.md", result)
    compact = []
    for item in result["targets"]:
        grid = item["split_grid"].get("test2_val2", {})
        compact.append(
            {
                "target": item["target"],
                "status": item["status"],
                "samples": item["sample_count"],
                "projects": item["project_count"],
                "test2_val2_feasible": grid.get("feasible", 0),
                "test2_val2_attempted": grid.get("attempted", 0),
            }
        )
    print(json.dumps({"targets": compact}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
