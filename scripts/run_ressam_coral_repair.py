#!/usr/bin/env python3
"""Run a lightweight Res-SAM CORAL mitigation experiment.

This is an internal, transductive domain-alignment stress test. It uses target
images without target labels to align HOG feature covariance before training a
classifier on source labels. It is not blind external validation.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


SHARED_LABELS = {"cavity", "crack", "pipe"}


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
    environments: list[str] = []
    for row in rows:
        image_path = data_root / row["rel_path"]
        if not image_path.exists():
            raise FileNotFoundError(f"Missing Res-SAM image: {image_path}")
        features.append(simple_hog(load_gray(image_path, image_size)))
        labels.append(row["label"])
        environments.append(row["project_id"])
    return np.stack(features), np.asarray(labels), np.asarray(environments)


def matrix_power_spd(cov: np.ndarray, power: float, eps: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(cov)
    values = np.maximum(values, eps)
    return (vectors * np.power(values, power)) @ vectors.T


def coral_align_source_to_target(
    source_x: np.ndarray,
    target_x_unlabeled: np.ndarray,
    eps: float,
) -> np.ndarray:
    source_mean = source_x.mean(axis=0, keepdims=True)
    target_mean = target_x_unlabeled.mean(axis=0, keepdims=True)
    source_centered = source_x - source_mean
    target_centered = target_x_unlabeled - target_mean

    source_cov = np.cov(source_centered, rowvar=False) + np.eye(source_x.shape[1]) * eps
    target_cov = np.cov(target_centered, rowvar=False) + np.eye(target_x_unlabeled.shape[1]) * eps

    whitening = matrix_power_spd(source_cov, -0.5, eps)
    coloring = matrix_power_spd(target_cov, 0.5, eps)
    return source_centered @ whitening @ coloring + target_mean


def mean_std_align_source_to_target(
    source_x: np.ndarray,
    target_x_unlabeled: np.ndarray,
    eps: float,
) -> np.ndarray:
    source_mean = source_x.mean(axis=0, keepdims=True)
    source_std = source_x.std(axis=0, keepdims=True) + eps
    target_mean = target_x_unlabeled.mean(axis=0, keepdims=True)
    target_std = target_x_unlabeled.std(axis=0, keepdims=True) + eps
    return ((source_x - source_mean) / source_std) * target_std + target_mean


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


def run_direction(
    x: np.ndarray,
    y: np.ndarray,
    env: np.ndarray,
    train_environment: str,
    test_environment: str,
    seed: int,
    eps: float,
) -> dict:
    shared_idx = np.flatnonzero(np.isin(y, sorted(SHARED_LABELS)))
    train_idx = shared_idx[env[shared_idx] == train_environment]
    test_idx = shared_idx[env[shared_idx] == test_environment]
    train_x = x[train_idx]
    train_y = y[train_idx]
    test_x = x[test_idx]
    test_y = y[test_idx]
    mean_std_train_x = mean_std_align_source_to_target(train_x, test_x, eps)
    coral_train_x = coral_align_source_to_target(train_x, test_x, eps)

    baseline = evaluate(train_x, train_y, test_x, test_y, seed)
    mean_std = evaluate(mean_std_train_x, train_y, test_x, test_y, seed)
    coral = evaluate(coral_train_x, train_y, test_x, test_y, seed)
    delta_mean_std = {
        key: float(mean_std[key] - baseline[key])
        for key in ["accuracy", "balanced_accuracy", "macro_f1"]
    }
    delta_coral = {
        key: float(coral[key] - baseline[key])
        for key in ["accuracy", "balanced_accuracy", "macro_f1"]
    }
    return {
        "train_environment": train_environment,
        "test_environment": test_environment,
        "label_space": sorted(SHARED_LABELS),
        "train_n": int(len(train_idx)),
        "test_n": int(len(test_idx)),
        "train_label_counts": {str(k): int(v) for k, v in Counter(train_y).items()},
        "test_label_counts": {str(k): int(v) for k, v in Counter(test_y).items()},
        "baseline_source_only": baseline,
        "mean_std_unlabeled_target": mean_std,
        "coral_unlabeled_target": coral,
        "delta_mean_std_minus_baseline": delta_mean_std,
        "delta_coral_minus_baseline": delta_coral,
    }


def write_md(path: Path, result: dict) -> None:
    lines = [
        "# Res-SAM CORAL Mitigation Experiment",
        "",
        f"Run ID: `{result['run_id']}`",
        f"Seed: `{result['seed']}`",
        f"Samples: `{result['n_samples']}`",
        "",
        "## Transfer Results",
        "",
        "| train | test | train_n | test_n | baseline bal acc | mean/std bal acc | CORAL bal acc | mean/std delta | CORAL delta |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in result["transfer"]:
        base = item["baseline_source_only"]
        mean_std = item["mean_std_unlabeled_target"]
        coral = item["coral_unlabeled_target"]
        delta_mean_std = item["delta_mean_std_minus_baseline"]
        delta_coral = item["delta_coral_minus_baseline"]
        lines.append(
            f"| {item['train_environment']} | {item['test_environment']} | "
            f"{item['train_n']} | {item['test_n']} | "
            f"{base['balanced_accuracy']:.4f} | {mean_std['balanced_accuracy']:.4f} | "
            f"{coral['balanced_accuracy']:.4f} | "
            f"{delta_mean_std['balanced_accuracy']:+.4f} | "
            f"{delta_coral['balanced_accuracy']:+.4f} |"
        )

    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "Mean/std alignment and CORAL use unlabeled target-environment images.",
            "This is an internal mitigation stress test, not blind external validation",
            "and not evidence that repair improves a locked external submission.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20260811)
    parser.add_argument("--image-size", type=int, default=64)
    parser.add_argument("--eps", type=float, default=1e-3)
    args = parser.parse_args()

    rows = read_rows(args.manifest)
    x, y, env = extract(rows, args.data_root, args.image_size)
    result = {
        "run_id": f"20260811_E01_ressam_hog_rbf_svm_coral_repair_seed_{args.seed}",
        "manifest": str(args.manifest),
        "data_root": str(args.data_root),
        "seed": args.seed,
        "image_size": args.image_size,
        "feature": "simple_hog_cell8_bins9",
        "model": "rbf_svm_C3_gamma_scale_class_weight_balanced",
        "mitigation": "mean/std feature alignment and CORAL covariance alignment using unlabeled target environment images",
        "n_samples": int(len(rows)),
        "shared_labels": sorted(SHARED_LABELS),
        "transfer": [
            run_direction(x, y, env, "synthetic", "real_world", args.seed, args.eps),
            run_direction(x, y, env, "real_world", "synthetic", args.seed, args.eps),
        ],
        "boundary": "Internal transductive mitigation stress test; not blind external validation.",
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    write_md(args.output_md, result)
    print(json.dumps(result["transfer"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
