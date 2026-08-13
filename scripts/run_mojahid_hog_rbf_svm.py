#!/usr/bin/env python3
"""Run the first frozen Mojahid HOG + RBF-SVM baseline."""

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


BENCH_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path(__file__).resolve().parents[2]


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
    orientation = (np.arctan2(gy, gx) + np.pi) * (180.0 / np.pi)
    orientation = np.mod(orientation, 180.0)
    bin_idx = np.minimum((orientation / (180.0 / bins)).astype(np.int32), bins - 1)

    h, w = image.shape
    cells_y = h // cell_size
    cells_x = w // cell_size
    features: list[float] = []
    for cy in range(cells_y):
        for cx in range(cells_x):
            y0 = cy * cell_size
            x0 = cx * cell_size
            cell_bins = bin_idx[y0 : y0 + cell_size, x0 : x0 + cell_size].ravel()
            cell_mag = magnitude[y0 : y0 + cell_size, x0 : x0 + cell_size].ravel()
            hist = np.bincount(cell_bins, weights=cell_mag, minlength=bins).astype(np.float32)
            norm = float(np.linalg.norm(hist) + 1e-8)
            features.extend((hist / norm).tolist())
    return np.asarray(features, dtype=np.float32)


def extract_features(rows: list[dict[str, str]], data_root: Path, image_size: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    features: list[np.ndarray] = []
    labels: list[str] = []
    fold_ids: list[int] = []
    for row in rows:
        rel_path = row["rel_path"].replace("/", "\\")
        image_path = data_root / rel_path
        if not image_path.exists():
            raise FileNotFoundError(f"Missing image: {image_path}")
        features.append(simple_hog(load_gray(image_path, image_size)))
        labels.append(row["label"])
        fold_ids.append(int(row["fold_id"]))
    return np.stack(features), np.asarray(labels), np.asarray(fold_ids)


def evaluate(features: np.ndarray, labels: np.ndarray, train_idx: np.ndarray, test_idx: np.ndarray, seed: int) -> dict[str, float]:
    model = make_pipeline(
        StandardScaler(),
        SVC(C=3.0, gamma="scale", class_weight="balanced", random_state=seed),
    )
    model.fit(features[train_idx], labels[train_idx])
    pred = model.predict(features[test_idx])
    return {
        "accuracy": float(accuracy_score(labels[test_idx], pred)),
        "balanced_accuracy": float(balanced_accuracy_score(labels[test_idx], pred)),
        "macro_f1": float(f1_score(labels[test_idx], pred, average="macro")),
    }


def write_summary(output_md: Path, results: dict) -> None:
    grouped = results["evaluations"]["grouped_fold_0_test_fold_1_val"]
    random_split = results["evaluations"]["random_stratified_80_20"]
    lines = [
        "# Mojahid HOG + RBF-SVM Baseline 2026-08-10",
        "",
        "This is the first frozen end-to-end model run under GPR-ProvenanceBench.",
        "",
        "## Inputs",
        "",
        f"- Manifest: `{results['manifest']}`",
        f"- Data root: `{results['data_root']}`",
        f"- Samples: {results['n_samples']}",
        f"- Labels: {results['label_counts']}",
        "",
        "## Split Results",
        "",
        "| split | train_n | val_n | test_n | accuracy | balanced_accuracy | macro_f1 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        (
            f"| random_stratified_80_20 | {results['splits']['random_stratified_80_20']['train_n']} | "
            f"0 | {results['splits']['random_stratified_80_20']['test_n']} | "
            f"{random_split['accuracy']:.4f} | {random_split['balanced_accuracy']:.4f} | {random_split['macro_f1']:.4f} |"
        ),
        (
            f"| grouped_fold_0_test_fold_1_val | {results['splits']['grouped_fold_0_test_fold_1_val']['train_n']} | "
            f"{results['splits']['grouped_fold_0_test_fold_1_val']['val_n']} | "
            f"{results['splits']['grouped_fold_0_test_fold_1_val']['test_n']} | "
            f"{grouped['accuracy']:.4f} | {grouped['balanced_accuracy']:.4f} | {grouped['macro_f1']:.4f} |"
        ),
        "",
        "## Interpretation Boundary",
        "",
        "This is a G0 smoke baseline. It proves that one frozen model can run end to end,",
        "but it is not a final manuscript claim and must be repeated across assets, seeds,",
        "split protocols and model classes.",
        "",
    ]
    output_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20260810)
    parser.add_argument("--image-size", type=int, default=64)
    parser.add_argument("--test-fold", type=int, default=0)
    parser.add_argument("--val-fold", type=int, default=1)
    args = parser.parse_args()

    rows = read_rows(args.manifest)
    features, labels, fold_ids = extract_features(rows, args.data_root, args.image_size)

    random_split = StratifiedShuffleSplit(n_splits=1, test_size=0.20, random_state=args.seed)
    random_train_idx, random_test_idx = next(random_split.split(np.zeros(len(labels)), labels))

    grouped_train_idx = np.flatnonzero(~np.isin(fold_ids, [args.test_fold, args.val_fold]))
    grouped_val_idx = np.flatnonzero(fold_ids == args.val_fold)
    grouped_test_idx = np.flatnonzero(fold_ids == args.test_fold)

    label_counts = {str(key): int(value) for key, value in Counter(labels).items()}
    fold_counts = {str(key): int(value) for key, value in Counter(fold_ids).items()}

    results = {
        "run_id": f"20260810_E00_mojahid_hog_rbf_svm_seed_{args.seed}",
        "manifest": stable_path(args.manifest),
        "data_root": stable_path(args.data_root),
        "seed": args.seed,
        "image_size": args.image_size,
        "feature": "simple_hog_cell8_bins9",
        "model": "rbf_svm_C3_gamma_scale_class_weight_balanced",
        "n_samples": len(rows),
        "label_counts": label_counts,
        "fold_counts": fold_counts,
        "splits": {
            "random_stratified_80_20": {
                "train_n": int(len(random_train_idx)),
                "test_n": int(len(random_test_idx)),
            },
            "grouped_fold_0_test_fold_1_val": {
                "train_n": int(len(grouped_train_idx)),
                "val_n": int(len(grouped_val_idx)),
                "test_n": int(len(grouped_test_idx)),
            },
        },
        "evaluations": {
            "random_stratified_80_20": evaluate(features, labels, random_train_idx, random_test_idx, args.seed),
            "grouped_fold_0_test_fold_1_val": evaluate(features, labels, grouped_train_idx, grouped_test_idx, args.seed),
        },
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    write_summary(args.output_md, results)
    print(json.dumps(results["evaluations"], ensure_ascii=False, indent=2))


def stable_path(path: Path) -> str:
    resolved = path.resolve()
    for base in (BENCH_ROOT, PROJECT_ROOT):
        try:
            return str(resolved.relative_to(base)).replace("\\", "/")
        except ValueError:
            pass
    return resolved.name


if __name__ == "__main__":
    main()
