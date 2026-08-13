#!/usr/bin/env python3
"""Run 4TU Land type alignment repair sweeps on matrix summary features."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


METRICS = ["accuracy", "balanced_accuracy", "macro_f1"]
METHODS = [
    "raw_source_only",
    "per_matrix_zscore_source_only",
    "mean_std_unlabeled_target",
    "coral_unlabeled_target",
    "delta_per_matrix_zscore_minus_raw",
    "delta_mean_std_minus_raw",
    "delta_coral_minus_raw",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def normalize_matrix(arr: np.ndarray, method: str) -> np.ndarray:
    arr = np.asarray(arr, dtype=np.float32)
    if method == "raw":
        return arr
    if method == "per_matrix_zscore":
        return (arr - float(arr.mean())) / (float(arr.std()) + 1e-6)
    raise ValueError(method)


def feature_vector(array: np.ndarray) -> list[float]:
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
    return [
        float(h),
        float(w),
        float(arr.mean()),
        float(arr.std()),
        float(arr.min()),
        float(arr.max()),
        float(np.quantile(arr, 0.05)),
        float(np.quantile(arr, 0.95)),
        float(top.mean()),
        float(bottom.mean()),
        float(left.mean()),
        float(right.mean()),
        float(center.mean()),
        float(((top.mean() + bottom.mean() + left.mean() + right.mean()) / 4.0) - center.mean()),
        float(np.abs(grad_y).mean()) if grad_y.size else 0.0,
        float(np.abs(grad_x).mean()) if grad_x.size else 0.0,
    ]


def extract(rows: list[dict[str, str]], matrix_method: str) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    features: list[list[float]] = []
    labels: list[str] = []
    splits: list[str] = []
    projects: list[str] = []
    for row in rows:
        arr = np.load(row["package_npy_path"])
        features.append(feature_vector(normalize_matrix(arr, matrix_method)))
        labels.append(row["Land type"])
        splits.append(row["split_role"])
        projects.append(row["project_id"])
    return np.asarray(features, dtype=np.float32), np.asarray(labels), np.asarray(splits), np.asarray(projects)


def matrix_power_spd(cov: np.ndarray, power: float, eps: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(cov)
    values = np.maximum(values, eps)
    return (vectors * np.power(values, power)) @ vectors.T


def mean_std_align(source_x: np.ndarray, target_x: np.ndarray, eps: float) -> np.ndarray:
    return ((source_x - source_x.mean(axis=0, keepdims=True)) / (source_x.std(axis=0, keepdims=True) + eps)) * (
        target_x.std(axis=0, keepdims=True) + eps
    ) + target_x.mean(axis=0, keepdims=True)


def coral_align(source_x: np.ndarray, target_x: np.ndarray, eps: float) -> np.ndarray:
    source_mean = source_x.mean(axis=0, keepdims=True)
    target_mean = target_x.mean(axis=0, keepdims=True)
    source_centered = source_x - source_mean
    target_centered = target_x - target_mean
    source_cov = np.cov(source_centered, rowvar=False) + np.eye(source_x.shape[1]) * eps
    target_cov = np.cov(target_centered, rowvar=False) + np.eye(target_x.shape[1]) * eps
    return source_centered @ matrix_power_spd(source_cov, -0.5, eps) @ matrix_power_spd(target_cov, 0.5, eps) + target_mean


def make_model(seed: int):
    return make_pipeline(
        StandardScaler(),
        SVC(C=3.0, gamma="scale", class_weight="balanced", random_state=seed),
    )


def evaluate(train_x: np.ndarray, train_y: np.ndarray, test_x: np.ndarray, test_y: np.ndarray, seed: int) -> dict[str, float]:
    model = make_model(seed)
    model.fit(train_x, train_y)
    pred = model.predict(test_x)
    return {
        "accuracy": float(accuracy_score(test_y, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(test_y, pred)),
        "macro_f1": float(f1_score(test_y, pred, average="macro")),
    }


def summarize(values: list[float]) -> dict[str, float]:
    arr = np.asarray(values, dtype=np.float64)
    return {
        "mean": float(arr.mean()),
        "std": float(arr.std(ddof=0)),
        "min": float(arr.min()),
        "max": float(arr.max()),
    }


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_md(path: Path, summary: dict) -> None:
    item = summary["split"]
    lines = [
        "# 4TU Land Type Alignment Repair Sweep",
        "",
        f"Runs: `{summary['n_runs']}`",
        f"Target: `{summary['target_field']}`",
        "",
        "| method | balanced accuracy | delta vs raw | macro-F1 |",
        "| --- | ---: | ---: | ---: |",
    ]
    raw = item["raw_source_only"]["balanced_accuracy"]["mean"]
    for method in [
        "raw_source_only",
        "per_matrix_zscore_source_only",
        "mean_std_unlabeled_target",
        "coral_unlabeled_target",
    ]:
        ba = item[method]["balanced_accuracy"]["mean"]
        mf1 = item[method]["macro_f1"]["mean"]
        lines.append(f"| {method} | {ba:.4f} | {ba - raw:+.4f} | {mf1:.4f} |")
    lines.extend(
        [
            "",
            "Boundary: Land type is usable with caution on the P4 v2 split. The",
            "mean/std and CORAL variants use unlabeled test-split feature statistics,",
            "so they are transductive internal repair tests. The per-matrix zscore",
            "variant is non-transductive.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--eps", type=float, default=1e-3)
    args = parser.parse_args()

    rows = [
        row
        for row in read_csv(args.task_manifest)
        if row.get("Land type", "unknown") != "unknown" and row.get("split_role") in {"train", "val", "test"}
    ]
    raw_x, labels, splits, projects = extract(rows, "raw")
    zscore_x, _, _, _ = extract(rows, "per_matrix_zscore")
    train_idx = np.flatnonzero(splits == "train")
    test_idx = np.flatnonzero(splits == "test")
    if len(np.unique(labels[train_idx])) < 2 or len(np.unique(labels[test_idx])) < 2:
        raise SystemExit("Land type split is degenerate")

    seeds = [20260811, 20260812, 20260813, 20260814, 20260815]
    metric_values: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    long_rows: list[dict[str, object]] = []
    detailed: list[dict] = []
    for seed in seeds:
        raw = evaluate(raw_x[train_idx], labels[train_idx], raw_x[test_idx], labels[test_idx], seed)
        zscore = evaluate(zscore_x[train_idx], labels[train_idx], zscore_x[test_idx], labels[test_idx], seed)
        mean_std_x = mean_std_align(raw_x[train_idx], raw_x[test_idx], args.eps)
        coral_x = coral_align(raw_x[train_idx], raw_x[test_idx], args.eps)
        mean_std = evaluate(mean_std_x, labels[train_idx], raw_x[test_idx], labels[test_idx], seed)
        coral = evaluate(coral_x, labels[train_idx], raw_x[test_idx], labels[test_idx], seed)
        results = {
            "raw_source_only": raw,
            "per_matrix_zscore_source_only": zscore,
            "mean_std_unlabeled_target": mean_std,
            "coral_unlabeled_target": coral,
            "delta_per_matrix_zscore_minus_raw": {metric: float(zscore[metric] - raw[metric]) for metric in METRICS},
            "delta_mean_std_minus_raw": {metric: float(mean_std[metric] - raw[metric]) for metric in METRICS},
            "delta_coral_minus_raw": {metric: float(coral[metric] - raw[metric]) for metric in METRICS},
        }
        detailed.append({"seed": seed, **results})
        for method in METHODS:
            for metric in METRICS:
                value = float(results[method][metric])
                metric_values[method][metric].append(value)
                long_rows.append({"seed": seed, "method": method, "metric": metric, "value": value})

    summary = {
        "run_id": "20260811_E05_4tu_land_type_alignment_repair_sweep",
        "target_field": "Land type",
        "n_runs": len(seeds),
        "seeds": seeds,
        "records": int(len(rows)),
        "split_counts": {str(k): int(v) for k, v in Counter(splits).items()},
        "label_counts": {str(k): int(v) for k, v in Counter(labels).items()},
        "train_projects": sorted(set(projects[train_idx])),
        "test_projects": sorted(set(projects[test_idx])),
        "split": {
            method: {
                metric: summarize(values)
                for metric, values in metric_rows.items()
            }
            for method, metric_rows in metric_values.items()
        },
        "detailed_runs": detailed,
        "claim_boundary": "4TU internal repair feasibility; not external blind validation.",
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "seed_sweep_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    write_csv(args.output_dir / "seed_sweep_long.csv", long_rows)
    write_md(args.output_dir / "seed_sweep_summary.md", summary)
    print(json.dumps(summary["split"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
