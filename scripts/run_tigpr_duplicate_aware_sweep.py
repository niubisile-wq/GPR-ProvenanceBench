#!/usr/bin/env python3
"""Run TIGPR random-vs-duplicate-aware split experiments."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from PIL import Image
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score
from sklearn.model_selection import StratifiedGroupKFold, StratifiedShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler


ROOT = Path(__file__).resolve().parents[2]
SEEDS = [20260811, 20260812, 20260813, 20260814, 20260815]
METRICS = ["accuracy", "balanced_accuracy", "macro_f1"]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def resolve_path(row: dict[str, str]) -> Path:
    path = ROOT / row["rel_path"]
    if path.exists():
        return path
    abs_path = Path(row["abs_path"])
    if abs_path.exists():
        return abs_path
    raise FileNotFoundError(row["sample_id"])


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


def load_or_build_features(rows: list[dict[str, str]], cache_path: Path, image_size: int) -> np.ndarray:
    if cache_path.exists():
        cached = np.load(cache_path)
        if int(cached["image_size"]) == image_size and int(cached["n_rows"]) == len(rows):
            return cached["features"]

    features = []
    for i, row in enumerate(rows, start=1):
        features.append(simple_hog(load_gray(resolve_path(row), image_size)))
        if i % 500 == 0:
            print(f"extracted {i}/{len(rows)} TIGPR HOG features")
    x = np.stack(features).astype(np.float32)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(cache_path, features=x, image_size=image_size, n_rows=len(rows))
    return x


def metadata_features(rows: list[dict[str, str]]) -> np.ndarray:
    values = []
    for row in rows:
        values.append(
            [
                float(row.get("width_px") or 0),
                float(row.get("height_px") or 0),
                float(row.get("size_bytes") or 0),
                float(len(row.get("sample_id", ""))),
            ]
        )
    return np.asarray(values, dtype=np.float32)


def make_model(seed: int):
    return make_pipeline(
        StandardScaler(),
        SGDClassifier(
            loss="log_loss",
            alpha=1e-4,
            class_weight="balanced",
            random_state=seed,
            max_iter=1500,
            tol=1e-3,
        ),
    )


def evaluate(x: np.ndarray, y: np.ndarray, train_idx: np.ndarray, test_idx: np.ndarray, seed: int) -> dict[str, float]:
    model = make_model(seed)
    model.fit(x[train_idx], y[train_idx])
    pred = model.predict(x[test_idx])
    return {
        "accuracy": float(accuracy_score(y[test_idx], pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y[test_idx], pred)),
        "macro_f1": float(f1_score(y[test_idx], pred, average="macro")),
    }


def summarize(values: list[float]) -> dict[str, float]:
    arr = np.asarray(values, dtype=np.float64)
    return {
        "mean": float(arr.mean()),
        "std": float(arr.std(ddof=1)) if len(arr) > 1 else 0.0,
        "min": float(arr.min()),
        "max": float(arr.max()),
    }


def split_overlap(groups: np.ndarray, train_idx: np.ndarray, test_idx: np.ndarray) -> dict[str, int]:
    train_groups = set(groups[train_idx])
    test_groups = set(groups[test_idx])
    shared = train_groups & test_groups
    return {
        "train_groups": len(train_groups),
        "test_groups": len(test_groups),
        "shared_groups": len(shared),
        "shared_test_samples": int(sum(group in shared for group in groups[test_idx])),
    }


def duplicate_audit(rows: list[dict[str, str]]) -> dict[str, object]:
    by_hash: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_hash[row["sha256"]].append(row)
    duplicate_groups = {key: value for key, value in by_hash.items() if len(value) > 1}
    cross_label = {
        key: sorted({row["label"] for row in value})
        for key, value in duplicate_groups.items()
        if len({row["label"] for row in value}) > 1
    }
    return {
        "exact_duplicate_group_count": len(duplicate_groups),
        "exact_duplicate_image_count": int(sum(len(value) for value in duplicate_groups.values())),
        "cross_label_exact_duplicate_group_count": len(cross_label),
        "cross_label_exact_duplicate_groups": cross_label,
    }


def run_sweep(rows: list[dict[str, str]], x_hog: np.ndarray, x_meta: np.ndarray) -> tuple[dict[str, object], list[dict[str, object]]]:
    y = np.asarray([row["label"] for row in rows])
    groups = np.asarray([row["split_group"] for row in rows])
    le = LabelEncoder().fit(y)
    y_encoded = le.transform(y)
    detailed: list[dict[str, object]] = []

    for seed in SEEDS:
        random_splitter = StratifiedShuffleSplit(n_splits=1, test_size=0.20, random_state=seed)
        random_train, random_test = next(random_splitter.split(np.zeros(len(y)), y))

        group_splitter = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=seed)
        group_train, group_test = next(group_splitter.split(np.zeros(len(y)), y, groups))

        for split_name, train_idx, test_idx in [
            ("random_stratified_80_20", random_train, random_test),
            ("hash_group_stratified_80_20", group_train, group_test),
        ]:
            hog_metrics = evaluate(x_hog, y, train_idx, test_idx, seed)
            meta_metrics = evaluate(x_meta, y, train_idx, test_idx, seed)
            overlap = split_overlap(groups, train_idx, test_idx)
            detailed.append(
                {
                    "seed": seed,
                    "split": split_name,
                    "train_n": int(len(train_idx)),
                    "test_n": int(len(test_idx)),
                    "hog_accuracy": hog_metrics["accuracy"],
                    "hog_balanced_accuracy": hog_metrics["balanced_accuracy"],
                    "hog_macro_f1": hog_metrics["macro_f1"],
                    "metadata_accuracy": meta_metrics["accuracy"],
                    "metadata_balanced_accuracy": meta_metrics["balanced_accuracy"],
                    "metadata_macro_f1": meta_metrics["macro_f1"],
                    **overlap,
                }
            )

    split_summary: dict[str, dict[str, dict[str, float]]] = {}
    for split_name in sorted({row["split"] for row in detailed}):
        split_rows = [row for row in detailed if row["split"] == split_name]
        split_summary[split_name] = {}
        for prefix in ["hog", "metadata"]:
            for metric in METRICS:
                key = f"{prefix}_{metric}"
                split_summary[split_name][key] = summarize([float(row[key]) for row in split_rows])
        for key in ["shared_groups", "shared_test_samples"]:
            split_summary[split_name][key] = summarize([float(row[key]) for row in split_rows])

    deltas: dict[str, dict[str, float]] = {}
    by_seed_split = {(row["seed"], row["split"]): row for row in detailed}
    for prefix in ["hog", "metadata"]:
        for metric in METRICS:
            key = f"{prefix}_{metric}"
            values = [
                float(by_seed_split[(seed, "random_stratified_80_20")][key])
                - float(by_seed_split[(seed, "hash_group_stratified_80_20")][key])
                for seed in SEEDS
            ]
            deltas[f"random_minus_group_{key}"] = summarize(values)

    summary = {
        "run_id": "20260811_E14_tigpr_duplicate_aware_sweep",
        "seeds": SEEDS,
        "n_samples": len(rows),
        "label_counts": {str(key): int(value) for key, value in Counter(y).items()},
        "n_classes": int(len(set(y))),
        "chance_balanced_accuracy": float(1.0 / len(set(y))),
        "duplicate_audit": duplicate_audit(rows),
        "split_summary": split_summary,
        "random_minus_group": deltas,
        "claim_boundary": "TIGPR is restored local data. These tests are duplicate-aware internal experiments, not blind external validation.",
    }
    return summary, detailed


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_md(path: Path, summary: dict[str, object]) -> None:
    lines = [
        "# TIGPR Duplicate-Aware Sweep",
        "",
        f"Samples: `{summary['n_samples']}`",
        f"Labels: `{summary['label_counts']}`",
        f"Seeds: `{summary['seeds']}`",
        "",
        "## Duplicate Audit",
        "",
        f"- Exact duplicate groups: `{summary['duplicate_audit']['exact_duplicate_group_count']}`",
        f"- Exact duplicate images: `{summary['duplicate_audit']['exact_duplicate_image_count']}`",
        f"- Cross-label exact duplicate groups: `{summary['duplicate_audit']['cross_label_exact_duplicate_group_count']}`",
        "",
        "## Split Summary",
        "",
        "| split | HOG BA | metadata BA | shared hash groups | shared test samples |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for split, stats in summary["split_summary"].items():
        lines.append(
            f"| {split} | {stats['hog_balanced_accuracy']['mean']:.4f} | "
            f"{stats['metadata_balanced_accuracy']['mean']:.4f} | "
            f"{stats['shared_groups']['mean']:.1f} | {stats['shared_test_samples']['mean']:.1f} |"
        )
    lines.extend(
        [
            "",
            "## Random Minus Group-Aware",
            "",
            "| metric | mean delta | std | min | max |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for metric, stats in summary["random_minus_group"].items():
        lines.append(
            f"| {metric} | {stats['mean']:.4f} | {stats['std']:.4f} | "
            f"{stats['min']:.4f} | {stats['max']:.4f} |"
        )
    lines.extend(
        [
            "",
            "Boundary: this closes a restored-local TIGPR duplicate-aware baseline,",
            "but it does not close blind external validation because labels and media",
            "are visible before model development.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--image-size", type=int, default=64)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows = read_rows(args.manifest)
    cache_path = args.output_dir / f"tigpr_hog_features_{args.image_size}.npz"
    x_hog = load_or_build_features(rows, cache_path, args.image_size)
    x_meta = metadata_features(rows)
    summary, detailed = run_sweep(rows, x_hog, x_meta)

    (args.output_dir / "tigpr_duplicate_aware_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_csv(args.output_dir / "tigpr_duplicate_aware_runs.csv", detailed)
    write_md(args.output_dir / "tigpr_duplicate_aware_summary.md", summary)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
