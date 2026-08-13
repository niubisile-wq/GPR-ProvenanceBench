#!/usr/bin/env python3
"""Run non-transductive source-side style augmentation repair for Res-SAM."""

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


SHARED_LABELS = {"cavity", "crack", "pipe"}
PREPROCESSORS = ["raw", "per_image_zscore", "per_image_equalized"]
TEST_MODES = ["raw", "per_image_zscore", "per_image_equalized"]
METRICS = ["accuracy", "balanced_accuracy", "macro_f1"]


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


def preprocess_image(image: np.ndarray, method: str) -> np.ndarray:
    if method == "raw":
        return image
    if method == "per_image_zscore":
        centered = (image - float(image.mean())) / (float(image.std()) + 1e-6)
        return ((np.clip(centered, -3.0, 3.0) + 3.0) / 6.0).astype(np.float32)
    if method == "per_image_equalized":
        flat = image.ravel()
        order = np.argsort(flat, kind="mergesort")
        ranks = np.empty_like(order, dtype=np.float32)
        ranks[order] = np.linspace(0.0, 1.0, num=flat.size, dtype=np.float32)
        return ranks.reshape(image.shape)
    raise ValueError(method)


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


def extract_all(rows: list[dict[str, str]], data_root: Path, image_size: int) -> tuple[dict[str, np.ndarray], np.ndarray, np.ndarray]:
    labels: list[str] = []
    environments: list[str] = []
    features_by_preprocessor: dict[str, list[np.ndarray]] = {method: [] for method in PREPROCESSORS}
    for row in rows:
        image_path = data_root / row["rel_path"]
        if not image_path.exists():
            raise FileNotFoundError(f"Missing Res-SAM image: {image_path}")
        image = load_gray(image_path, image_size)
        for method in PREPROCESSORS:
            features_by_preprocessor[method].append(simple_hog(preprocess_image(image, method)))
        labels.append(row["label"])
        environments.append(row["project_id"])
    return (
        {method: np.stack(values) for method, values in features_by_preprocessor.items()},
        np.asarray(labels),
        np.asarray(environments),
    )


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
    lines = [
        "# Res-SAM Source-Side Style Augmentation Repair",
        "",
        f"Runs: `{summary['n_runs']}`",
        "",
        "| transfer | raw baseline | best aug test mode | best aug bal acc | best delta |",
        "| --- | ---: | --- | ---: | ---: |",
    ]
    for direction, item in summary["transfer"].items():
        raw = item["raw_source_to_raw_target"]["balanced_accuracy"]["mean"]
        candidates = {
            key: value["balanced_accuracy"]["mean"]
            for key, value in item.items()
            if key.startswith("source_style_aug_to_")
        }
        best_key, best_value = max(candidates.items(), key=lambda row: row[1])
        lines.append(f"| {direction} | {raw:.4f} | {best_key} | {best_value:.4f} | {best_value - raw:+.4f} |")
    lines.extend(
        [
            "",
            "Boundary: source-style augmentation only uses source-domain labels and",
            "per-image deterministic transforms. It does not inspect target-domain",
            "batch statistics, but it is still internal evidence because Res-SAM is",
            "already part of local model development.",
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
    args = parser.parse_args()

    rows = read_rows(args.manifest)
    features_by_method, labels, env = extract_all(rows, args.data_root, args.image_size)
    shared_idx = np.flatnonzero(np.isin(labels, sorted(SHARED_LABELS)))
    seeds = [20260811, 20260812, 20260813, 20260814, 20260815]

    metric_values: dict[str, dict[str, dict[str, list[float]]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    long_rows: list[dict[str, object]] = []
    detailed: list[dict] = []
    for seed in seeds:
        for train_environment, test_environment in [("synthetic", "real_world"), ("real_world", "synthetic")]:
            direction = f"{train_environment}_to_{test_environment}"
            train_idx = shared_idx[env[shared_idx] == train_environment]
            test_idx = shared_idx[env[shared_idx] == test_environment]
            raw_result = evaluate(
                features_by_method["raw"][train_idx],
                labels[train_idx],
                features_by_method["raw"][test_idx],
                labels[test_idx],
                seed,
            )
            method_key = "raw_source_to_raw_target"
            for metric, value in raw_result.items():
                metric_values[direction][method_key][metric].append(value)
                long_rows.append({"seed": seed, "direction": direction, "method": method_key, "metric": metric, "value": value})
            detailed.append({"seed": seed, "direction": direction, "method": method_key, "metrics": raw_result})

            aug_train_x = np.concatenate([features_by_method[method][train_idx] for method in PREPROCESSORS], axis=0)
            aug_train_y = np.concatenate([labels[train_idx] for _ in PREPROCESSORS], axis=0)
            for test_mode in TEST_MODES:
                result = evaluate(aug_train_x, aug_train_y, features_by_method[test_mode][test_idx], labels[test_idx], seed)
                method_key = f"source_style_aug_to_{test_mode}_target"
                for metric, value in result.items():
                    metric_values[direction][method_key][metric].append(value)
                    long_rows.append({"seed": seed, "direction": direction, "method": method_key, "metric": metric, "value": value})
                detailed.append({"seed": seed, "direction": direction, "method": method_key, "metrics": result})

    summary = {
        "run_id": "20260811_E04_ressam_source_style_aug_repair",
        "n_runs": len(detailed),
        "seeds": seeds,
        "source_preprocessors": PREPROCESSORS,
        "test_modes": TEST_MODES,
        "transfer": {
            direction: {
                method: {
                    metric: summarize(values)
                    for metric, values in metric_rows.items()
                }
                for method, metric_rows in method_rows.items()
            }
            for direction, method_rows in metric_values.items()
        },
        "detailed_runs": detailed,
        "claim_boundary": "Non-transductive source-style augmentation; not blind external validation.",
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "seed_sweep_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    write_csv(args.output_dir / "seed_sweep_long.csv", long_rows)
    write_md(args.output_dir / "seed_sweep_summary.md", summary)
    print(json.dumps(summary["transfer"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
