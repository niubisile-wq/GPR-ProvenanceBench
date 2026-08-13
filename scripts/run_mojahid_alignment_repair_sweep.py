#!/usr/bin/env python3
"""Run Mojahid grouped-split alignment mitigation sweeps."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


METRICS = ["accuracy", "balanced_accuracy", "macro_f1"]
METHODS = [
    "baseline_source_only",
    "mean_std_unlabeled_target",
    "coral_unlabeled_target",
    "delta_mean_std_minus_baseline",
    "delta_coral_minus_baseline",
]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def load_gray(path: Path, size: int) -> np.ndarray:
    with Image.open(path) as image:
        image.load()
        arr = np.asarray(
            image.convert("L").resize((size, size), Image.Resampling.BILINEAR),
            dtype=np.float32,
        )
    return arr / 255.0


def simple_hog(image: np.ndarray, cell_size: int = 8, bins: int = 9) -> np.ndarray:
    gy, gx = np.gradient(image)
    magnitude = np.sqrt(gx * gx + gy * gy)
    orientation = np.mod((np.arctan2(gy, gx) + np.pi) * (180.0 / np.pi), 180.0)
    bin_idx = np.minimum((orientation / (180.0 / bins)).astype(np.int32), bins - 1)
    cells_y = image.shape[0] // cell_size
    cells_x = image.shape[1] // cell_size
    features: list[float] = []
    for cy in range(cells_y):
        for cx in range(cells_x):
            y0 = cy * cell_size
            x0 = cx * cell_size
            cell_bins = bin_idx[y0 : y0 + cell_size, x0 : x0 + cell_size].ravel()
            cell_mag = magnitude[y0 : y0 + cell_size, x0 : x0 + cell_size].ravel()
            hist = np.bincount(cell_bins, weights=cell_mag, minlength=bins).astype(np.float32)
            features.extend((hist / (float(np.linalg.norm(hist)) + 1e-8)).tolist())
    return np.asarray(features, dtype=np.float32)


def extract(rows: list[dict[str, str]], data_root: Path, image_size: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    features: list[np.ndarray] = []
    labels: list[str] = []
    folds: list[int] = []
    for row in rows:
        image_path = data_root / row["rel_path"]
        if not image_path.exists():
            raise FileNotFoundError(f"Missing Mojahid image: {image_path}")
        features.append(simple_hog(load_gray(image_path, image_size)))
        labels.append(row["label"])
        folds.append(int(row["fold_id"]))
    return np.stack(features), np.asarray(labels), np.asarray(folds)


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


def protocol_result(
    x: np.ndarray,
    y: np.ndarray,
    folds: np.ndarray,
    protocol_name: str,
    test_fold: int,
    val_fold: int,
    seed: int,
    eps: float,
) -> dict:
    train_idx = np.flatnonzero(~np.isin(folds, [test_fold, val_fold]))
    test_idx = np.flatnonzero(folds == test_fold)
    train_x = x[train_idx]
    train_y = y[train_idx]
    test_x = x[test_idx]
    test_y = y[test_idx]
    mean_std_x = mean_std_align(train_x, test_x, eps)
    coral_x = coral_align(train_x, test_x, eps)
    baseline = evaluate(train_x, train_y, test_x, test_y, seed)
    mean_std = evaluate(mean_std_x, train_y, test_x, test_y, seed)
    coral = evaluate(coral_x, train_y, test_x, test_y, seed)
    return {
        "protocol": protocol_name,
        "test_fold": test_fold,
        "val_fold": val_fold,
        "seed": seed,
        "train_n": int(len(train_idx)),
        "test_n": int(len(test_idx)),
        "baseline_source_only": baseline,
        "mean_std_unlabeled_target": mean_std,
        "coral_unlabeled_target": coral,
        "delta_mean_std_minus_baseline": {metric: float(mean_std[metric] - baseline[metric]) for metric in METRICS},
        "delta_coral_minus_baseline": {metric: float(coral[metric] - baseline[metric]) for metric in METRICS},
    }


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_md(path: Path, summary: dict) -> None:
    lines = [
        "# Mojahid Alignment Mitigation Sweep",
        "",
        f"Runs: `{summary['n_runs']}`",
        f"Seeds: `{', '.join(str(seed) for seed in summary['seeds'])}`",
        "",
        "| protocol | baseline bal acc | mean/std bal acc | CORAL bal acc | mean/std delta | CORAL delta |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for protocol, item in summary["protocols"].items():
        lines.append(
            f"| {protocol} | "
            f"{item['baseline_source_only']['balanced_accuracy']['mean']:.4f} | "
            f"{item['mean_std_unlabeled_target']['balanced_accuracy']['mean']:.4f} | "
            f"{item['coral_unlabeled_target']['balanced_accuracy']['mean']:.4f} | "
            f"{item['delta_mean_std_minus_baseline']['balanced_accuracy']['mean']:+.4f} | "
            f"{item['delta_coral_minus_baseline']['balanced_accuracy']['mean']:+.4f} |"
        )
    lines.extend(
        [
            "",
            "Boundary: this is an internal transductive mitigation stress test on",
            "Mojahid grouped splits. It uses unlabeled test-fold images for feature",
            "alignment and therefore cannot be used as blind external repair evidence.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--image-size", type=int, default=64)
    parser.add_argument("--eps", type=float, default=1e-3)
    args = parser.parse_args()

    rows = read_rows(args.manifest)
    x, y, folds = extract(rows, args.data_root, args.image_size)
    seeds = [20260811, 20260812, 20260813, 20260814, 20260815]
    protocols = [
        ("current_fold0_test_fold1_val", 0, 1),
        ("task_aware_fold0_test_fold3_val", 0, 3),
    ]

    run_rows: list[dict[str, object]] = []
    metric_values: dict[str, dict[str, dict[str, list[float]]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    detailed: list[dict] = []
    for seed in seeds:
        for protocol_name, test_fold, val_fold in protocols:
            result = protocol_result(x, y, folds, protocol_name, test_fold, val_fold, seed, args.eps)
            detailed.append(result)
            for method in METHODS:
                for metric in METRICS:
                    value = float(result[method][metric])
                    metric_values[protocol_name][method][metric].append(value)
                    run_rows.append(
                        {
                            "seed": seed,
                            "protocol": protocol_name,
                            "method": method,
                            "metric": metric,
                            "value": value,
                        }
                    )

    summary = {
        "run_id": "20260811_E02_mojahid_alignment_repair_sweep",
        "n_runs": len(seeds) * len(protocols),
        "seeds": seeds,
        "protocols": {
            protocol: {
                method: {
                    metric: summarize(values)
                    for metric, values in method_values.items()
                }
                for method, method_values in protocol_values.items()
            }
            for protocol, protocol_values in metric_values.items()
        },
        "detailed_runs": detailed,
        "claim_boundary": "Internal transductive mitigation; not blind external repair evidence.",
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "seed_sweep_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    write_csv(args.output_dir / "seed_sweep_long.csv", run_rows)
    write_md(args.output_dir / "seed_sweep_summary.md", summary)
    print(json.dumps(summary["protocols"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
