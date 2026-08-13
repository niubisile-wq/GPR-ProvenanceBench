#!/usr/bin/env python3
"""Run group-aware repeated-split 4TU HOG counterfactual tests."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from sklearn.metrics import balanced_accuracy_score, f1_score

from run_4tu_counterfactual_hog_image import matrix_features
from run_4tu_counterfactual_reliance import VARIANT_ORDER, evaluate_predictions, make_models, read_csv


def viable_split(rows: list[dict[str, str]], target: str, roles: dict[str, str]) -> tuple[bool, dict[str, dict[str, int]], str]:
    by_split: dict[str, Counter] = {split: Counter() for split in ("train", "val", "test")}
    for row in rows:
        by_split[roles[row["project_id"]]][row[target]] += 1
    coverage = {split: dict(counts) for split, counts in by_split.items()}
    if any(len(counts) < 2 for counts in by_split.values()):
        return False, coverage, "one_or_more_splits_have_fewer_than_two_classes"
    train_labels = set(by_split["train"])
    heldout_labels = set(by_split["val"]) | set(by_split["test"])
    if not heldout_labels.issubset(train_labels):
        return False, coverage, "heldout_label_not_seen_in_train"
    return True, coverage, "ok"


def make_group_split(rows: list[dict[str, str]], target: str, seed: int, val_projects: int, test_projects: int) -> dict:
    projects = sorted({row["project_id"] for row in rows})
    rng = np.random.default_rng(seed)
    for attempt in range(1, 5001):
        shuffled = list(projects)
        rng.shuffle(shuffled)
        test = set(shuffled[:test_projects])
        val = set(shuffled[test_projects : test_projects + val_projects])
        train = set(shuffled[test_projects + val_projects :])
        roles = {project: "train" for project in train}
        roles.update({project: "val" for project in val})
        roles.update({project: "test" for project in test})
        ok, coverage, reason = viable_split(rows, target, roles)
        if ok:
            return {
                "seed": seed,
                "attempt": attempt,
                "roles": roles,
                "projects": {
                    "train": sorted(train),
                    "val": sorted(val),
                    "test": sorted(test),
                },
                "split_label_counts": coverage,
                "reason": reason,
            }
    raise RuntimeError(f"could not find viable group split for seed {seed}")


def split_indices(rows: list[dict[str, str]], roles: dict[str, str]) -> dict[str, np.ndarray]:
    row_roles = np.asarray([roles[row["project_id"]] for row in rows])
    return {split: np.flatnonzero(row_roles == split) for split in ("train", "val", "test")}


def evaluate_split(rows: list[dict[str, str]], target: str, split: dict, model_seed: int, image_size: int) -> dict:
    labels = np.asarray([row[target] for row in rows])
    idx = split_indices(rows, split["roles"])
    original_x = matrix_features(rows, "original", image_size)
    test_rows = [rows[i] for i in idx["test"]]
    variant_features = {name: matrix_features(test_rows, name, image_size) for name in VARIANT_ORDER}

    models = make_models(model_seed, len(np.unique(labels[idx["train"]])))
    model_results = []
    for model_name, model in models.items():
        fitted = model.fit(original_x[idx["train"]], labels[idx["train"]])
        val_pred = fitted.predict(original_x[idx["val"]])
        original_test_pred = fitted.predict(original_x[idx["test"]])
        model_result = {
            "model": model_name,
            "val_balanced_accuracy": float(balanced_accuracy_score(labels[idx["val"]], val_pred)),
            "val_macro_f1": float(f1_score(labels[idx["val"]], val_pred, average="macro")),
            "variant_rows": [],
        }
        original_metrics = None
        for variant_name in VARIANT_ORDER:
            pred = fitted.predict(variant_features[variant_name])
            metrics = evaluate_predictions(labels[idx["test"]], pred, original_test_pred)
            if variant_name == "original":
                original_metrics = metrics
            row = {"variant": variant_name, **metrics}
            row["balanced_accuracy_delta_vs_original"] = float(metrics["balanced_accuracy"] - original_metrics["balanced_accuracy"])
            row["macro_f1_delta_vs_original"] = float(metrics["macro_f1"] - original_metrics["macro_f1"])
            model_result["variant_rows"].append(row)
        model_results.append(model_result)

    selected = max(model_results, key=lambda item: (item["val_balanced_accuracy"], item["val_macro_f1"]))["model"]
    return {
        "target_field": target,
        "split_seed": split["seed"],
        "model_seed": model_seed,
        "image_size": image_size,
        "split_projects": split["projects"],
        "split_label_counts": split["split_label_counts"],
        "split_counts": {name: int(len(values)) for name, values in idx.items()},
        "selected_model": selected,
        "models": model_results,
    }


def flatten(results: list[dict]) -> list[dict[str, object]]:
    rows = []
    for result in results:
        for model in result["models"]:
            for item in model["variant_rows"]:
                rows.append(
                    {
                        "target_field": result["target_field"],
                        "split_seed": result["split_seed"],
                        "model_seed": result["model_seed"],
                        "image_size": result["image_size"],
                        "selected_model": result["selected_model"],
                        "model": model["model"],
                        "variant": item["variant"],
                        "train_projects": ";".join(result["split_projects"]["train"]),
                        "val_projects": ";".join(result["split_projects"]["val"]),
                        "test_projects": ";".join(result["split_projects"]["test"]),
                        "val_balanced_accuracy": model["val_balanced_accuracy"],
                        "test_balanced_accuracy": item["balanced_accuracy"],
                        "balanced_accuracy_delta_vs_original": item["balanced_accuracy_delta_vs_original"],
                        "test_macro_f1": item["macro_f1"],
                        "macro_f1_delta_vs_original": item["macro_f1_delta_vs_original"],
                        "prediction_flip_rate_vs_original": item["prediction_flip_rate_vs_original"],
                        "n_predicted_classes_not_in_test": item["n_predicted_classes_not_in_test"],
                        "predicted_classes_not_in_test": "; ".join(item["predicted_classes_not_in_test"]),
                    }
                )
    return rows


def summarize(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    groups: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        if row["model"] == row["selected_model"]:
            groups[(str(row["model"]), str(row["variant"]))].append(row)
    summary = []
    for (model, variant), items in sorted(groups.items()):
        ba = np.asarray([float(item["test_balanced_accuracy"]) for item in items])
        delta = np.asarray([float(item["balanced_accuracy_delta_vs_original"]) for item in items])
        flip = np.asarray([float(item["prediction_flip_rate_vs_original"]) for item in items])
        summary.append(
            {
                "model": model,
                "variant": variant,
                "n_splits": len(items),
                "test_balanced_accuracy_mean": float(ba.mean()),
                "test_balanced_accuracy_std": float(ba.std(ddof=0)),
                "balanced_accuracy_delta_mean": float(delta.mean()),
                "balanced_accuracy_delta_std": float(delta.std(ddof=0)),
                "prediction_flip_rate_mean": float(flip.mean()),
                "prediction_flip_rate_std": float(flip.std(ddof=0)),
                "all_delta_nonpositive": bool(np.all(delta <= 1e-12)),
            }
        )
    return summary


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_md(path: Path, result: dict) -> None:
    variant_rows = [row for row in result["aggregate"] if row["variant"] != "original"]
    top = sorted(variant_rows, key=lambda row: (row["balanced_accuracy_delta_mean"], -row["prediction_flip_rate_mean"]))
    original_rows = [row for row in result["aggregate"] if row["variant"] == "original"]
    lines = [
        "# 4TU HOG Group-Repeated Split Counterfactual Reliance 2026-08-10",
        "",
        f"Target: {result['target']}",
        f"Split seeds: {', '.join(str(seed) for seed in result['split_seeds'])}",
        f"Image size: {result['image_size']}",
        f"Metric rows: {result['n_metric_rows']}",
        "",
        "## Original Baseline By Selected Model",
        "",
        "| model | n_splits | BA_mean | BA_std |",
        "| --- | ---: | ---: | ---: |",
    ]
    for row in original_rows:
        lines.append(
            f"| {row['model']} | {row['n_splits']} | {row['test_balanced_accuracy_mean']:.4f} | {row['test_balanced_accuracy_std']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Counterfactual Drops For Split-Selected Models",
            "",
            "| model | variant | n_splits | BA_mean | delta_mean | delta_std | flip_mean | all_delta_nonpositive |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for row in top:
        lines.append(
            f"| {row['model']} | {row['variant']} | {row['n_splits']} | {row['test_balanced_accuracy_mean']:.4f} | "
            f"{row['balanced_accuracy_delta_mean']:.4f} | {row['balanced_accuracy_delta_std']:.4f} | "
            f"{row['prediction_flip_rate_mean']:.4f} | {row['all_delta_nonpositive']} |"
        )
    lines.extend(
        [
            "",
            "## Split Audit",
            "",
            "| split_seed | train_projects | val_projects | test_projects | selected_model |",
            "| ---: | --- | --- | --- | --- |",
        ]
    )
    for split_result in result["runs"]:
        lines.append(
            f"| {split_result['split_seed']} | `{';'.join(split_result['split_projects']['train'])}` | "
            f"`{';'.join(split_result['split_projects']['val'])}` | `{';'.join(split_result['split_projects']['test'])}` | "
            f"{split_result['selected_model']} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This is group-aware repeated split replication across 4TU projects. The small number of projects and uneven labels make it a stress test rather than a final external validation protocol.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--target", default="Land type")
    parser.add_argument("--split-seeds", nargs="+", type=int, default=[20260810, 20260811, 20260812, 20260813, 20260814])
    parser.add_argument("--model-seed", type=int, default=20260810)
    parser.add_argument("--image-size", type=int, default=64)
    parser.add_argument("--val-projects", type=int, default=2)
    parser.add_argument("--test-projects", type=int, default=2)
    args = parser.parse_args()

    rows = [row for row in read_csv(args.task_manifest) if row.get(args.target, "unknown") != "unknown"]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    split_defs = [
        make_group_split(rows, args.target, seed, args.val_projects, args.test_projects)
        for seed in args.split_seeds
    ]
    results = [
        evaluate_split(rows, args.target, split, args.model_seed, args.image_size)
        for split in split_defs
    ]
    flat_rows = flatten(results)
    aggregate = summarize(flat_rows)
    result = {
        "task_manifest": str(args.task_manifest),
        "target": args.target,
        "split_seeds": args.split_seeds,
        "model_seed": args.model_seed,
        "image_size": args.image_size,
        "n_metric_rows": len(flat_rows),
        "runs": results,
        "aggregate": aggregate,
        "flat_csv": "hog_group_split_metrics.csv",
    }
    write_csv(args.output_dir / "hog_group_split_metrics.csv", flat_rows)
    (args.output_dir / "hog_group_split_summary.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_md(args.output_dir / "hog_group_split_summary.md", result)
    print(json.dumps({"splits": len(results), "metric_rows": len(flat_rows), "aggregate_rows": len(aggregate)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
