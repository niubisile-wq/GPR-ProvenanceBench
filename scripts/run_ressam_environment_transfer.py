#!/usr/bin/env python3
"""Run lightweight Res-SAM environment-transfer baselines."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score
from sklearn.model_selection import StratifiedShuffleSplit
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
        rel_path = row["rel_path"].replace("/", "\\")
        image_path = data_root / rel_path
        if not image_path.exists():
            raise FileNotFoundError(f"Missing Res-SAM image: {image_path}")
        features.append(simple_hog(load_gray(image_path, image_size)))
        labels.append(row["label"])
        environments.append(row["project_id"])
    return np.stack(features), np.asarray(labels), np.asarray(environments)


def make_model(seed: int):
    return make_pipeline(
        StandardScaler(),
        SVC(C=3.0, gamma="scale", class_weight="balanced", random_state=seed),
    )


def eval_split(x: np.ndarray, y: np.ndarray, train_idx: np.ndarray, test_idx: np.ndarray, seed: int) -> dict[str, float]:
    model = make_model(seed)
    model.fit(x[train_idx], y[train_idx])
    pred = model.predict(x[test_idx])
    return {
        "accuracy": float(accuracy_score(y[test_idx], pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y[test_idx], pred)),
        "macro_f1": float(f1_score(y[test_idx], pred, average="macro")),
    }


def random_within_environment(
    x: np.ndarray,
    y: np.ndarray,
    env: np.ndarray,
    environment: str,
    seed: int,
) -> dict:
    idx = np.flatnonzero(env == environment)
    splitter = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=seed)
    local_train, local_test = next(splitter.split(np.zeros(len(idx)), y[idx]))
    train_idx = idx[local_train]
    test_idx = idx[local_test]
    return {
        "train_n": int(len(train_idx)),
        "test_n": int(len(test_idx)),
        "label_counts": {str(k): int(v) for k, v in Counter(y[idx]).items()},
        "metrics": eval_split(x, y, train_idx, test_idx, seed),
    }


def transfer(
    x: np.ndarray,
    y: np.ndarray,
    env: np.ndarray,
    train_environment: str,
    test_environment: str,
    seed: int,
) -> dict:
    shared_idx = np.flatnonzero(np.isin(y, sorted(SHARED_LABELS)))
    train_idx = shared_idx[env[shared_idx] == train_environment]
    test_idx = shared_idx[env[shared_idx] == test_environment]
    return {
        "train_environment": train_environment,
        "test_environment": test_environment,
        "label_space": sorted(SHARED_LABELS),
        "train_n": int(len(train_idx)),
        "test_n": int(len(test_idx)),
        "train_label_counts": {str(k): int(v) for k, v in Counter(y[train_idx]).items()},
        "test_label_counts": {str(k): int(v) for k, v in Counter(y[test_idx]).items()},
        "metrics": eval_split(x, y, train_idx, test_idx, seed),
    }


def write_md(path: Path, result: dict) -> None:
    lines = [
        "# Res-SAM HOG + RBF-SVM Environment Transfer 2026-08-10",
        "",
        f"Samples: {result['n_samples']}",
        f"Seed: {result['seed']}",
        "",
        "## Overall Counts",
        "",
        "| environment | label | count |",
        "| --- | --- | ---: |",
    ]
    for environment, labels in result["counts"].items():
        for label, count in labels.items():
            lines.append(f"| {environment} | {label} | {count} |")

    lines.extend(
        [
            "",
            "## Within-Environment Random Baselines",
            "",
            "| environment | train_n | test_n | balanced_accuracy | macro_f1 |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for environment, item in result["within_environment"].items():
        lines.append(
            f"| {environment} | {item['train_n']} | {item['test_n']} | "
            f"{item['metrics']['balanced_accuracy']:.4f} | {item['metrics']['macro_f1']:.4f} |"
        )

    lines.extend(
        [
            "",
            "## Cross-Environment Transfer",
            "",
            "Transfer uses only shared labels: `cavity`, `crack`, `pipe`.",
            "",
            "| train | test | train_n | test_n | balanced_accuracy | macro_f1 |",
            "| --- | --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for item in result["transfer"]:
        lines.append(
            f"| {item['train_environment']} | {item['test_environment']} | "
            f"{item['train_n']} | {item['test_n']} | "
            f"{item['metrics']['balanced_accuracy']:.4f} | {item['metrics']['macro_f1']:.4f} |"
        )

    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This is a lightweight data-asset baseline, not a reproduction of the full",
            "Res-SAM model. It tests environment transfer on published JPG exports with",
            "a simple HOG+RBF-SVM model.",
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
    parser.add_argument("--seed", type=int, default=20260810)
    parser.add_argument("--image-size", type=int, default=64)
    args = parser.parse_args()

    rows = read_rows(args.manifest)
    x, y, env = extract(rows, args.data_root, args.image_size)

    counts: dict[str, dict[str, int]] = {}
    for environment in sorted(set(env)):
        idx = env == environment
        counts[str(environment)] = {str(k): int(v) for k, v in Counter(y[idx]).items()}

    result = {
        "run_id": f"20260810_E00_ressam_hog_rbf_svm_env_transfer_seed_{args.seed}",
        "manifest": args.manifest.name,
        "data_root": args.data_root.name,
        "seed": args.seed,
        "image_size": args.image_size,
        "feature": "simple_hog_cell8_bins9",
        "model": "rbf_svm_C3_gamma_scale_class_weight_balanced",
        "n_samples": len(rows),
        "counts": counts,
        "within_environment": {
            "real_world": random_within_environment(x, y, env, "real_world", args.seed),
            "synthetic": random_within_environment(x, y, env, "synthetic", args.seed),
        },
        "transfer": [
            transfer(x, y, env, "synthetic", "real_world", args.seed),
            transfer(x, y, env, "real_world", "synthetic", args.seed),
        ],
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    write_md(args.output_md, result)
    print(json.dumps(result["transfer"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

