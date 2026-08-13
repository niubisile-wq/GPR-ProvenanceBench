#!/usr/bin/env python3
"""Run 4TU task-metadata baselines from a joined task manifest."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def feature_vector(array: np.ndarray) -> dict[str, float]:
    arr = np.asarray(array, dtype=np.float32)
    if arr.ndim != 2:
        raise ValueError(f"expected 2D matrix, got shape {arr.shape}")
    h, w = arr.shape
    top = arr[: max(1, h // 10), :]
    bottom = arr[-max(1, h // 10) :, :]
    left = arr[:, : max(1, w // 10)]
    right = arr[:, -max(1, w // 10) :]
    center = arr[max(1, h // 10) : max(1, h - h // 10), max(1, w // 10) : max(1, w - w // 10)]
    center = center if center.size else arr
    grad_y = np.diff(arr, axis=0)
    grad_x = np.diff(arr, axis=1)
    return {
        "shape_rows": float(h),
        "shape_cols": float(w),
        "mean": float(arr.mean()),
        "std": float(arr.std()),
        "min": float(arr.min()),
        "max": float(arr.max()),
        "p05": float(np.quantile(arr, 0.05)),
        "p95": float(np.quantile(arr, 0.95)),
        "top_mean": float(top.mean()),
        "bottom_mean": float(bottom.mean()),
        "left_mean": float(left.mean()),
        "right_mean": float(right.mean()),
        "center_mean": float(center.mean()),
        "edge_center_gap": float(((top.mean() + bottom.mean() + left.mean() + right.mean()) / 4.0) - center.mean()),
        "grad_y_abs_mean": float(np.abs(grad_y).mean()) if grad_y.size else 0.0,
        "grad_x_abs_mean": float(np.abs(grad_x).mean()) if grad_x.size else 0.0,
    }


def make_models(seed: int, n_train_classes: int) -> dict:
    models = {"dummy_majority": DummyClassifier(strategy="most_frequent")}
    if n_train_classes >= 2:
        models.update(
            {
                "extra_trees": ExtraTreesClassifier(
                    n_estimators=500,
                    min_samples_leaf=2,
                    class_weight="balanced",
                    random_state=seed,
                    n_jobs=-1,
                ),
                "rbf_svm": make_pipeline(
                    StandardScaler(),
                    SVC(C=3.0, gamma="scale", class_weight="balanced", random_state=seed),
                ),
            }
        )
    return models


def evaluate_model(model, x: np.ndarray, y: np.ndarray, train_idx: np.ndarray, val_idx: np.ndarray, test_idx: np.ndarray) -> dict:
    fitted = model.fit(x[train_idx], y[train_idx])
    val_pred = fitted.predict(x[val_idx])
    test_pred = fitted.predict(x[test_idx])
    return {
        "val_accuracy": float(accuracy_score(y[val_idx], val_pred)),
        "val_balanced_accuracy": float(balanced_accuracy_score(y[val_idx], val_pred)),
        "val_macro_f1": float(f1_score(y[val_idx], val_pred, average="macro")),
        "test_accuracy": float(accuracy_score(y[test_idx], test_pred)),
        "test_balanced_accuracy": float(balanced_accuracy_score(y[test_idx], test_pred)),
        "test_macro_f1": float(f1_score(y[test_idx], test_pred, average="macro")),
    }


def split_label_counts(labels: np.ndarray, split_roles: list[str]) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = {}
    split_arr = np.asarray(split_roles)
    for split in ("train", "val", "test"):
        idx = np.flatnonzero(split_arr == split)
        counts[split] = {str(k): int(v) for k, v in Counter(labels[idx]).items()}
    return counts


def viability(split_counts_by_label: dict[str, dict[str, int]]) -> dict[str, object]:
    n_classes = {split: len(counts) for split, counts in split_counts_by_label.items()}
    complete = all(value >= 2 for value in n_classes.values())
    return {
        "is_viable_smoke_target": complete,
        "reason": "ok" if complete else "one_or_more_splits_have_fewer_than_two_classes",
        "n_classes_by_split": n_classes,
    }


def write_md(path: Path, result: dict) -> None:
    lines = [
        f"# 4TU Task Baseline: {result['target_field']}",
        "",
        f"Rows: {result['records']}",
        f"Seed: {result['seed']}",
        "",
        "## Split Counts",
        "",
        "| split | count |",
        "| --- | ---: |",
    ]
    for split, count in result["split_counts"].items():
        lines.append(f"| {split} | {count} |")
    lines.extend(["", "## Label Counts", "", "| label | count |", "| --- | ---: |"])
    for label, count in result["label_counts"].items():
        lines.append(f"| {label} | {count} |")
    lines.extend(
        [
            "",
            "## Split Label Coverage",
            "",
            f"Viable smoke target: `{result['viability']['is_viable_smoke_target']}`",
            f"Reason: `{result['viability']['reason']}`",
            "",
            "| split | class_count | label_counts |",
            "| --- | ---: | --- |",
        ]
    )
    for split, counts in result["split_label_counts"].items():
        lines.append(f"| {split} | {len(counts)} | `{counts}` |")
    lines.extend(
        [
            "",
            "## Model Comparison",
            "",
            "| model | val_balanced_accuracy | test_balanced_accuracy | val_macro_f1 | test_macro_f1 |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in result["rows"]:
        lines.append(
            f"| {row['model']} | {row['val_balanced_accuracy']:.3f} | {row['test_balanced_accuracy']:.3f} | "
            f"{row['val_macro_f1']:.3f} | {row['test_macro_f1']:.3f} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This is a 4TU task-metadata smoke baseline. It uses activity-level labels",
            "and fixed matrix summary features, so it supports protocol development but",
            "does not establish the final raw-trace counterfactual claim.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-manifest", type=Path, required=True)
    parser.add_argument("--target-field", type=str, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20260810)
    args = parser.parse_args()

    rows = [row for row in read_csv(args.task_manifest) if row.get(args.target_field, "unknown") != "unknown"]
    if not rows:
        raise SystemExit(f"no usable rows for target field {args.target_field}")

    feature_rows = []
    labels = []
    split_roles = []
    feature_names = None
    for row in rows:
        arr = np.load(row["package_npy_path"])
        feats = feature_vector(arr)
        if feature_names is None:
            feature_names = list(feats.keys())
        feature_rows.append(feats)
        labels.append(row[args.target_field])
        split_roles.append(row["split_role"])

    x = np.asarray([[row[name] for name in feature_names] for row in feature_rows], dtype=np.float32)
    y = np.asarray(labels)
    split_roles_arr = np.asarray(split_roles)
    train_idx = np.flatnonzero(split_roles_arr == "train")
    val_idx = np.flatnonzero(split_roles_arr == "val")
    test_idx = np.flatnonzero(split_roles_arr == "test")
    if not len(train_idx) or not len(val_idx) or not len(test_idx):
        raise SystemExit("train/val/test split is incomplete")

    eval_rows = []
    for name, model in make_models(args.seed, len(np.unique(y[train_idx]))).items():
        metrics = evaluate_model(model, x, y, train_idx, val_idx, test_idx)
        eval_rows.append({"model": name, **metrics})

    coverage = split_label_counts(y, split_roles)
    result = {
        "target_field": args.target_field,
        "task_manifest": str(args.task_manifest.name),
        "seed": args.seed,
        "records": len(rows),
        "split_counts": {str(k): int(v) for k, v in Counter(split_roles).items()},
        "label_counts": {str(k): int(v) for k, v in Counter(labels).items()},
        "split_label_counts": coverage,
        "viability": viability(coverage),
        "rows": eval_rows,
        "selected_model": max(eval_rows, key=lambda row: (row["val_balanced_accuracy"], row["val_macro_f1"]))["model"],
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    write_md(args.output_md, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
