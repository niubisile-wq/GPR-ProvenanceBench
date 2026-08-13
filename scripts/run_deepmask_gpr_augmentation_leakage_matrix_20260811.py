#!/usr/bin/env python3
"""Run split and augmentation-leakage stress tests for DeepMask GPR_data."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score
from sklearn.model_selection import StratifiedGroupKFold, StratifiedShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler


BENCH_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = BENCH_ROOT / "data_manifests" / "deepmask_gpr_unified_samples_20260811.csv"
OUT_DIR = BENCH_ROOT / "reports" / "deepmask_gpr_augmentation_leakage_matrix_20260811"
SEEDS = [20260811, 20260812, 20260813, 20260814, 20260815]


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


def load_or_build_features(rows: list[dict[str, str]]) -> dict[str, np.ndarray]:
    cache = OUT_DIR / "deepmask_gpr_features_20260811.npz"
    if cache.exists():
        data = np.load(cache)
        if int(data["n_rows"]) == len(rows):
            return {"hog64": data["hog64"], "pixel32": data["pixel32"], "metadata": data["metadata"]}

    hog_features = []
    pixel_features = []
    metadata_features = []
    for row in rows:
        path = Path(row["abs_path"])
        gray64 = load_gray(path, 64)
        gray32 = load_gray(path, 32)
        hog_features.append(simple_hog(gray64))
        pixel_features.append(gray32.ravel())
        metadata_features.append(
            [
                float(row["width_px"]),
                float(row["height_px"]),
                float(row["size_bytes"]),
                1.0 if row["augmentation_status"] == "augmented" else 0.0,
                float(row["augmentation_index"] or 0),
            ]
        )
    features = {
        "hog64": np.stack(hog_features).astype(np.float32),
        "pixel32": np.stack(pixel_features).astype(np.float32),
        "metadata": np.asarray(metadata_features, dtype=np.float32),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(cache, n_rows=len(rows), **features)
    return features


def model_for(model_name: str, seed: int):
    if model_name.endswith("sgd"):
        return make_pipeline(
            StandardScaler(),
            SGDClassifier(
                loss="log_loss",
                alpha=1e-4,
                class_weight="balanced",
                max_iter=2000,
                tol=1e-4,
                random_state=seed,
            ),
        )
    return ExtraTreesClassifier(
        n_estimators=300,
        max_features="sqrt",
        class_weight="balanced",
        random_state=seed,
        n_jobs=-1,
    )


def stratified_random_indices(y: np.ndarray, seed: int) -> tuple[np.ndarray, np.ndarray]:
    splitter = StratifiedShuffleSplit(n_splits=1, test_size=0.20, random_state=seed)
    return next(splitter.split(np.zeros(len(y)), y))


def group_holdout_indices(y: np.ndarray, groups: np.ndarray, seed: int) -> tuple[np.ndarray, np.ndarray]:
    splitter = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=seed)
    return next(splitter.split(np.zeros(len(y)), y, groups))


def fixed_status_indices(rows: list[dict[str, str]], train_status: str, test_status: str) -> tuple[np.ndarray, np.ndarray]:
    train_idx = np.asarray([idx for idx, row in enumerate(rows) if row["augmentation_status"] == train_status], dtype=np.int64)
    test_idx = np.asarray([idx for idx, row in enumerate(rows) if row["augmentation_status"] == test_status], dtype=np.int64)
    return train_idx, test_idx


def overlap(rows: list[dict[str, str]], train_idx: np.ndarray, test_idx: np.ndarray) -> dict[str, int]:
    train_groups = {rows[int(idx)]["base_source_group"] for idx in train_idx}
    test_groups = {rows[int(idx)]["base_source_group"] for idx in test_idx}
    shared = train_groups & test_groups
    return {
        "train_groups": len(train_groups),
        "test_groups": len(test_groups),
        "shared_train_test_base_groups": len(shared),
        "shared_test_samples": int(sum(rows[int(idx)]["base_source_group"] in shared for idx in test_idx)),
    }


def evaluate(
    rows: list[dict[str, str]],
    features: dict[str, np.ndarray],
    labels: np.ndarray,
    train_idx: np.ndarray,
    test_idx: np.ndarray,
    protocol: str,
    seed: int,
    feature_name: str,
    model_name: str,
) -> dict[str, object]:
    encoder = LabelEncoder().fit(labels[train_idx])
    known_test = np.asarray([label in set(labels[train_idx]) for label in labels[test_idx]])
    if not np.all(known_test):
        raise ValueError(f"{protocol} has unseen labels in test set")
    y_train = encoder.transform(labels[train_idx])
    y_test = encoder.transform(labels[test_idx])
    model = model_for(model_name, seed)
    model.fit(features[feature_name][train_idx], y_train)
    pred = model.predict(features[feature_name][test_idx])
    return {
        "dataset": "deepmask_gpr",
        "protocol": protocol,
        "seed": seed,
        "feature": feature_name,
        "model": model_name,
        "train_n": int(len(train_idx)),
        "test_n": int(len(test_idx)),
        "train_label_counts": dict(Counter(labels[train_idx])),
        "test_label_counts": dict(Counter(labels[test_idx])),
        **overlap(rows, train_idx, test_idx),
        "accuracy": float(accuracy_score(y_test, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_test, pred)),
        "macro_f1": float(f1_score(y_test, pred, average="macro")),
    }


def summarize(values: list[float]) -> dict[str, float]:
    arr = np.asarray(values, dtype=np.float64)
    return {
        "mean": float(arr.mean()),
        "std": float(arr.std(ddof=1)) if len(arr) > 1 else 0.0,
        "min": float(arr.min()),
        "max": float(arr.max()),
    }


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = list(rows[0].keys())
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else value
                    for key, value in row.items()
                }
            )


def summarize_runs(runs: list[dict[str, object]]) -> dict[str, object]:
    by_key: dict[tuple[str, str, str], list[dict[str, object]]] = {}
    for row in runs:
        key = (str(row["protocol"]), str(row["feature"]), str(row["model"]))
        by_key.setdefault(key, []).append(row)
    protocol_model_summary = []
    for (protocol, feature, model), rows in sorted(by_key.items()):
        protocol_model_summary.append(
            {
                "protocol": protocol,
                "feature": feature,
                "model": model,
                "runs": len(rows),
                "balanced_accuracy": summarize([float(row["balanced_accuracy"]) for row in rows]),
                "macro_f1": summarize([float(row["macro_f1"]) for row in rows]),
                "shared_train_test_base_groups": summarize([float(row["shared_train_test_base_groups"]) for row in rows]),
            }
        )

    def ba_mean(row: dict[str, object]) -> float:
        return float(row["balanced_accuracy"]["mean"])

    best_random = max(
        (row for row in protocol_model_summary if row["protocol"] == "random_stratified_80_20"),
        key=ba_mean,
    )
    best_group = max(
        (row for row in protocol_model_summary if row["protocol"] == "base_source_group_holdout_80_20"),
        key=ba_mean,
    )
    best_original_test = max(
        (row for row in protocol_model_summary if row["protocol"] == "train_augmented_test_original"),
        key=ba_mean,
    )
    random_minus_group = (
        float(best_random["balanced_accuracy"]["mean"]) - float(best_group["balanced_accuracy"]["mean"])
    )
    random_minus_original_test = (
        float(best_random["balanced_accuracy"]["mean"]) - float(best_original_test["balanced_accuracy"]["mean"])
    )
    return {
        "run_id": "20260811_E33_deepmask_gpr_augmentation_leakage_matrix",
        "runs": len(runs),
        "seeds": SEEDS,
        "protocol_model_summary": protocol_model_summary,
        "best_random_balanced_accuracy": best_random,
        "best_group_holdout_balanced_accuracy": best_group,
        "best_train_augmented_test_original_balanced_accuracy": best_original_test,
        "best_random_minus_best_group_holdout_ba": random_minus_group,
        "best_random_minus_best_train_augmented_test_original_ba": random_minus_original_test,
        "status": "complete_local_public_augmentation_leakage_matrix",
        "blind_external_eligible": False,
        "reason_not_blind": "Labels, augmentation status and source-group structure are visible in the local folders before model execution.",
    }


def write_md(path: Path, summary: dict[str, object]) -> None:
    lines = [
        "# DeepMask GPR Augmentation Leakage Matrix",
        "",
        f"Runs: {summary['runs']}",
        f"Best random minus best group-holdout BA: {summary['best_random_minus_best_group_holdout_ba']:+.4f}",
        f"Best random minus train-augmented/test-original BA: {summary['best_random_minus_best_train_augmented_test_original_ba']:+.4f}",
        "",
        "| protocol | feature | model | runs | BA mean | BA std | shared base groups mean |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for row in summary["protocol_model_summary"]:
        ba = row["balanced_accuracy"]
        shared = row["shared_train_test_base_groups"]
        lines.append(
            f"| {row['protocol']} | {row['feature']} | {row['model']} | {row['runs']} | "
            f"{ba['mean']:.4f} | {ba['std']:.4f} | {shared['mean']:.1f} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This matrix is a fourth local/public asset stress test. It does not close",
            "the hard blind external validation gate.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = read_rows(MANIFEST)
    features = load_or_build_features(rows)
    labels = np.asarray([row["label"] for row in rows])
    groups = np.asarray([row["base_source_group"] for row in rows])
    model_specs = [
        ("hog64", "hog64_sgd"),
        ("pixel32", "pixel32_extra_trees"),
        ("metadata", "metadata_extra_trees"),
    ]
    runs: list[dict[str, object]] = []
    for seed in SEEDS:
        protocol_indices = {
            "random_stratified_80_20": stratified_random_indices(labels, seed),
            "base_source_group_holdout_80_20": group_holdout_indices(labels, groups, seed),
            "train_original_test_augmented": fixed_status_indices(rows, "original", "augmented"),
            "train_augmented_test_original": fixed_status_indices(rows, "augmented", "original"),
        }
        for protocol, (train_idx, test_idx) in protocol_indices.items():
            for feature_name, model_name in model_specs:
                runs.append(evaluate(rows, features, labels, train_idx, test_idx, protocol, seed, feature_name, model_name))

    write_csv(OUT_DIR / "deepmask_gpr_augmentation_leakage_runs.csv", runs)
    summary = summarize_runs(runs)
    (OUT_DIR / "deepmask_gpr_augmentation_leakage_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_md(OUT_DIR / "deepmask_gpr_augmentation_leakage_summary.md", summary)
    print(json.dumps({"runs": summary["runs"], "status": summary["status"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
