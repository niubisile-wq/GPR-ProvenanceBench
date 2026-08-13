#!/usr/bin/env python3
"""Run LBP + LinearSVM as the second lightweight model family."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from PIL import Image
from skimage.feature import local_binary_pattern
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC


SHARED_RESSAM_LABELS = {"cavity", "crack", "pipe"}
SEEDS = [20260810, 20260811, 20260812, 20260813, 20260814]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def load_gray(path: Path, size: int) -> np.ndarray:
    with Image.open(path) as image:
        image.load()
        arr = np.asarray(
            image.convert("L").resize((size, size), Image.Resampling.BILINEAR),
            dtype=np.uint8,
        )
    return arr


def lbp_histogram(image: np.ndarray, radius: int = 2, points: int = 16) -> np.ndarray:
    lbp = local_binary_pattern(image, P=points, R=radius, method="uniform")
    n_bins = points + 2
    hist, _ = np.histogram(lbp.ravel(), bins=np.arange(n_bins + 1), range=(0, n_bins), density=False)
    hist = hist.astype(np.float32)
    hist /= float(hist.sum() + 1e-8)
    return hist


def extract_features(rows: list[dict[str, str]], data_root: Path, image_size: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    features: list[np.ndarray] = []
    labels: list[str] = []
    fold_ids: list[str] = []
    environments: list[str] = []
    for row in rows:
        rel_path = row["rel_path"].replace("/", "\\")
        image_path = data_root / rel_path
        if not image_path.exists():
            raise FileNotFoundError(f"Missing image: {image_path}")
        features.append(lbp_histogram(load_gray(image_path, image_size)))
        labels.append(row["label"])
        fold_ids.append(row.get("fold_id", ""))
        environments.append(row.get("project_id", row.get("source_group", "")))
    return (
        np.stack(features),
        np.asarray(labels),
        np.asarray(fold_ids),
        np.asarray(environments),
    )


def make_model(seed: int):
    return make_pipeline(
        StandardScaler(),
        LinearSVC(C=1.0, class_weight="balanced", random_state=seed, max_iter=20000),
    )


def evaluate(x: np.ndarray, y: np.ndarray, train_idx: np.ndarray, test_idx: np.ndarray, seed: int) -> dict[str, float | int]:
    model = make_model(seed)
    model.fit(x[train_idx], y[train_idx])
    pred = model.predict(x[test_idx])
    return {
        "train_n": int(len(train_idx)),
        "test_n": int(len(test_idx)),
        "accuracy": float(accuracy_score(y[test_idx], pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y[test_idx], pred)),
        "macro_f1": float(f1_score(y[test_idx], pred, average="macro")),
    }


def run_mojahid(x: np.ndarray, y: np.ndarray, fold_ids: np.ndarray, seed: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    splitter = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=seed)
    train_idx, test_idx = next(splitter.split(np.zeros(len(y)), y))
    rows.append(
        {
            "dataset": "mojahid",
            "seed": seed,
            "protocol": "random_stratified_80_20",
            **evaluate(x, y, train_idx, test_idx, seed),
        }
    )

    grouped_train_idx = np.flatnonzero(~np.isin(fold_ids, ["0", "1"]))
    grouped_test_idx = np.flatnonzero(fold_ids == "0")
    rows.append(
        {
            "dataset": "mojahid",
            "seed": seed,
            "protocol": "grouped_fold_0_test_fold_1_val",
            **evaluate(x, y, grouped_train_idx, grouped_test_idx, seed),
        }
    )
    return rows


def run_ressam(x: np.ndarray, y: np.ndarray, env: np.ndarray, seed: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for environment in ["real_world", "synthetic"]:
        idx = np.flatnonzero(env == environment)
        splitter = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=seed)
        local_train, local_test = next(splitter.split(np.zeros(len(idx)), y[idx]))
        rows.append(
            {
                "dataset": "res_sam",
                "seed": seed,
                "protocol": f"within_{environment}_random_80_20",
                "train_environment": environment,
                "test_environment": environment,
                **evaluate(x, y, idx[local_train], idx[local_test], seed),
            }
        )

    shared_idx = np.flatnonzero(np.isin(y, sorted(SHARED_RESSAM_LABELS)))
    for train_environment, test_environment in [("synthetic", "real_world"), ("real_world", "synthetic")]:
        train_idx = shared_idx[env[shared_idx] == train_environment]
        test_idx = shared_idx[env[shared_idx] == test_environment]
        rows.append(
            {
                "dataset": "res_sam",
                "seed": seed,
                "protocol": f"transfer_{train_environment}_to_{test_environment}",
                "train_environment": train_environment,
                "test_environment": test_environment,
                **evaluate(x, y, train_idx, test_idx, seed),
            }
        )
    return rows


def summarize(metric_rows: list[dict[str, object]]) -> dict[str, object]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in metric_rows:
        grouped[(str(row["dataset"]), str(row["protocol"]))].append(row)

    summaries = []
    for (dataset, protocol), rows in sorted(grouped.items()):
        ba = np.asarray([float(row["balanced_accuracy"]) for row in rows], dtype=np.float64)
        f1 = np.asarray([float(row["macro_f1"]) for row in rows], dtype=np.float64)
        summaries.append(
            {
                "dataset": dataset,
                "protocol": protocol,
                "n_seeds": int(len(rows)),
                "balanced_accuracy_mean": float(ba.mean()),
                "balanced_accuracy_std": float(ba.std(ddof=0)),
                "balanced_accuracy_min": float(ba.min()),
                "balanced_accuracy_max": float(ba.max()),
                "macro_f1_mean": float(f1.mean()),
                "macro_f1_std": float(f1.std(ddof=0)),
            }
        )

    by_protocol = {(item["dataset"], item["protocol"]): item for item in summaries}
    contrasts = []
    if ("mojahid", "random_stratified_80_20") in by_protocol and ("mojahid", "grouped_fold_0_test_fold_1_val") in by_protocol:
        random_item = by_protocol[("mojahid", "random_stratified_80_20")]
        grouped_item = by_protocol[("mojahid", "grouped_fold_0_test_fold_1_val")]
        contrasts.append(
            {
                "dataset": "mojahid",
                "contrast": "random_minus_grouped_balanced_accuracy",
                "delta_mean": random_item["balanced_accuracy_mean"] - grouped_item["balanced_accuracy_mean"],
            }
        )
    for within_protocol, transfer_protocol, direction in [
        ("within_real_world_random_80_20", "transfer_synthetic_to_real_world", "synthetic_to_real_world"),
        ("within_synthetic_random_80_20", "transfer_real_world_to_synthetic", "real_world_to_synthetic"),
    ]:
        if ("res_sam", within_protocol) in by_protocol and ("res_sam", transfer_protocol) in by_protocol:
            within_item = by_protocol[("res_sam", within_protocol)]
            transfer_item = by_protocol[("res_sam", transfer_protocol)]
            contrasts.append(
                {
                    "dataset": "res_sam",
                    "contrast": f"within_minus_transfer_{direction}",
                    "delta_mean": within_item["balanced_accuracy_mean"] - transfer_item["balanced_accuracy_mean"],
                }
            )

    return {"summaries": summaries, "contrasts": contrasts}


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fields = [
        "dataset",
        "seed",
        "protocol",
        "train_environment",
        "test_environment",
        "train_n",
        "test_n",
        "accuracy",
        "balanced_accuracy",
        "macro_f1",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_md(path: Path, result: dict[str, object]) -> None:
    lines = [
        "# LBP + LinearSVM Lightweight Model Matrix 2026-08-10",
        "",
        "This is the second lightweight model family after HOG+RBF-SVM.",
        "",
        "## Model",
        "",
        "- Feature: uniform local binary pattern histogram, P=16, R=2.",
        "- Classifier: `LinearSVC(C=1.0, class_weight='balanced')`.",
        "- Image size: 64 x 64 grayscale.",
        "- Seeds: 20260810 to 20260814.",
        "",
        "## Aggregate Results",
        "",
        "| dataset | protocol | n_seeds | BA_mean | BA_std | BA_min | BA_max | macro_f1_mean |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in result["summary"]["summaries"]:
        lines.append(
            f"| {item['dataset']} | {item['protocol']} | {item['n_seeds']} | "
            f"{item['balanced_accuracy_mean']:.4f} | {item['balanced_accuracy_std']:.4f} | "
            f"{item['balanced_accuracy_min']:.4f} | {item['balanced_accuracy_max']:.4f} | "
            f"{item['macro_f1_mean']:.4f} |"
        )
    lines.extend(["", "## Key Contrasts", "", "| dataset | contrast | delta_mean |", "| --- | --- | ---: |"])
    for item in result["summary"]["contrasts"]:
        lines.append(f"| {item['dataset']} | {item['contrast']} | {item['delta_mean']:.4f} |")
    lines.extend(
        [
            "",
            "## Interpretation Boundary",
            "",
            "These runs expand the model matrix but remain CPU-only lightweight baselines. They should be used to test whether split and environment effects persist outside HOG+RBF-SVM, not as final deep-learning evidence.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mojahid-manifest", type=Path, required=True)
    parser.add_argument("--mojahid-data-root", type=Path, required=True)
    parser.add_argument("--ressam-manifest", type=Path, required=True)
    parser.add_argument("--ressam-data-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--image-size", type=int, default=64)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    mojahid_rows = read_rows(args.mojahid_manifest)
    mojahid_x, mojahid_y, mojahid_folds, _ = extract_features(mojahid_rows, args.mojahid_data_root, args.image_size)
    ressam_rows = read_rows(args.ressam_manifest)
    ressam_x, ressam_y, _, ressam_env = extract_features(ressam_rows, args.ressam_data_root, args.image_size)

    metric_rows: list[dict[str, object]] = []
    for seed in SEEDS:
        metric_rows.extend(run_mojahid(mojahid_x, mojahid_y, mojahid_folds, seed))
        metric_rows.extend(run_ressam(ressam_x, ressam_y, ressam_env, seed))

    result = {
        "run_id": "20260810_E00_lbp_linear_svm_model_matrix",
        "model_family": "lbp_linear_svm",
        "seeds": SEEDS,
        "image_size": args.image_size,
        "sample_counts": {
            "mojahid": len(mojahid_rows),
            "res_sam": len(ressam_rows),
        },
        "label_counts": {
            "mojahid": {str(k): int(v) for k, v in Counter(mojahid_y).items()},
            "res_sam": {str(k): int(v) for k, v in Counter(ressam_y).items()},
        },
        "summary": summarize(metric_rows),
    }

    write_csv(args.output_dir / "lbp_linear_svm_metrics.csv", metric_rows)
    (args.output_dir / "lbp_linear_svm_summary.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_md(args.output_dir / "lbp_linear_svm_summary.md", result)
    print(json.dumps(result["summary"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
