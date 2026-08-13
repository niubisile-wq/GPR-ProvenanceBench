#!/usr/bin/env python3
"""Run a TIGPR duplicate-aware model-family matrix."""

from __future__ import annotations

import argparse
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
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[2]
SEEDS = [20260811, 20260812, 20260813, 20260814, 20260815]
MATERIAL_DELTA = 0.05


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


def load_or_build_hog(rows: list[dict[str, str]], cache_path: Path, image_size: int) -> np.ndarray:
    if cache_path.exists():
        cached = np.load(cache_path)
        if int(cached["image_size"]) == image_size and int(cached["n_rows"]) == len(rows):
            return cached["features"]
    features = []
    for i, row in enumerate(rows, start=1):
        features.append(simple_hog(load_gray(resolve_path(row), image_size)))
        if i % 500 == 0:
            print(f"extracted {i}/{len(rows)} HOG features")
    x = np.stack(features).astype(np.float32)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(cache_path, features=x, image_size=image_size, n_rows=len(rows))
    return x


def load_or_build_pixels(rows: list[dict[str, str]], cache_path: Path, image_size: int) -> np.ndarray:
    if cache_path.exists():
        cached = np.load(cache_path)
        if int(cached["image_size"]) == image_size and int(cached["n_rows"]) == len(rows):
            return cached["features"]
    features = []
    for i, row in enumerate(rows, start=1):
        features.append(load_gray(resolve_path(row), image_size).ravel())
        if i % 500 == 0:
            print(f"extracted {i}/{len(rows)} pixel features")
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
                float(len(Path(row["rel_path"]).name)),
            ]
        )
    return np.asarray(values, dtype=np.float32)


def make_model(model_family: str, seed: int):
    if model_family.endswith("extra_trees"):
        return ExtraTreesClassifier(
            n_estimators=120,
            max_features="sqrt",
            class_weight="balanced",
            random_state=seed,
            n_jobs=-1,
        )
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


def metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro")),
    }


def evaluate(model_family: str, x: np.ndarray, y: np.ndarray, train_idx: np.ndarray, test_idx: np.ndarray, seed: int) -> dict[str, float]:
    model = make_model(model_family, seed)
    model.fit(x[train_idx], y[train_idx])
    pred = model.predict(x[test_idx])
    return metrics(y[test_idx], pred)


def split_overlap(groups: np.ndarray, train_idx: np.ndarray, test_idx: np.ndarray) -> dict[str, int]:
    shared = set(groups[train_idx]) & set(groups[test_idx])
    return {
        "shared_groups": len(shared),
        "shared_test_samples": int(sum(group in shared for group in groups[test_idx])),
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
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_md(path: Path, result: dict[str, object]) -> None:
    lines = [
        "# TIGPR Model-Family Duplicate Matrix",
        "",
        f"Samples: `{result['n_samples']}`",
        f"Seeds: `{result['seeds']}`",
        f"Material-support threshold: `{result['material_delta_threshold']}` balanced accuracy.",
        "",
        "## Model-Family Summary",
        "",
        "| model_family | random BA | group BA | random-minus-group BA | material support |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for row in result["model_family_summary"]:
        lines.append(
            f"| {row['model_family']} | {row['random_balanced_accuracy']['mean']:.4f} | "
            f"{row['group_balanced_accuracy']['mean']:.4f} | "
            f"{row['random_minus_group_balanced_accuracy']['mean']:.4f} | "
            f"{row['material_support']} |"
        )
    lines.extend(
        [
            "",
            "## Claim Summary",
            "",
            f"- Directional support: `{result['claim_summary']['directional_support_count']}/{result['claim_summary']['n_model_families']}`",
            f"- Material support: `{result['claim_summary']['material_support_count']}/{result['claim_summary']['n_model_families']}`",
            f"- Mean delta across model families: `{result['claim_summary']['delta_mean_across_models']:.4f}`",
            f"- Claim status: `{result['claim_summary']['claim_status']}`",
            "",
            "Boundary: TIGPR is restored local evidence. This matrix tests duplicate",
            "isolation and model-family dependence; it does not satisfy blind external",
            "validation because the asset and labels are visible locally.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--hog-image-size", type=int, default=64)
    parser.add_argument("--pixel-image-size", type=int, default=32)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows = read_rows(args.manifest)
    y = np.asarray([row["label"] for row in rows])
    groups = np.asarray([row["split_group"] for row in rows])

    hog = load_or_build_hog(rows, args.output_dir / f"tigpr_hog_features_{args.hog_image_size}.npz", args.hog_image_size)
    pixels = load_or_build_pixels(rows, args.output_dir / f"tigpr_pixel_features_{args.pixel_image_size}.npz", args.pixel_image_size)
    meta = metadata_features(rows)
    features = {
        "hog_logistic_sgd": hog,
        "pixel_logistic_sgd": pixels,
        "metadata_logistic_sgd": meta,
        "hog_metadata_logistic_sgd": np.hstack([hog, StandardScaler().fit_transform(meta)]).astype(np.float32),
        "hog_extra_trees": hog,
    }

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
            overlap = split_overlap(groups, train_idx, test_idx)
            for model_family, x in features.items():
                block = evaluate(model_family, x, y, train_idx, test_idx, seed)
                detailed.append(
                    {
                        "seed": seed,
                        "split": split_name,
                        "model_family": model_family,
                        "train_n": int(len(train_idx)),
                        "test_n": int(len(test_idx)),
                        "accuracy": block["accuracy"],
                        "balanced_accuracy": block["balanced_accuracy"],
                        "macro_f1": block["macro_f1"],
                        **overlap,
                    }
                )

    by_key = {(row["seed"], row["split"], row["model_family"]): row for row in detailed}
    model_summary: list[dict[str, object]] = []
    for model_family in features:
        random_ba = [
            float(by_key[(seed, "random_stratified_80_20", model_family)]["balanced_accuracy"])
            for seed in SEEDS
        ]
        group_ba = [
            float(by_key[(seed, "hash_group_stratified_80_20", model_family)]["balanced_accuracy"])
            for seed in SEEDS
        ]
        delta = [random - group for random, group in zip(random_ba, group_ba)]
        model_summary.append(
            {
                "model_family": model_family,
                "random_balanced_accuracy": summarize(random_ba),
                "group_balanced_accuracy": summarize(group_ba),
                "random_minus_group_balanced_accuracy": summarize(delta),
                "directional_support": bool(np.mean(delta) > 0.0),
                "material_support": bool(np.mean(delta) >= MATERIAL_DELTA),
            }
        )

    deltas = [row["random_minus_group_balanced_accuracy"]["mean"] for row in model_summary]
    directional = sum(1 for row in model_summary if row["directional_support"])
    material = sum(1 for row in model_summary if row["material_support"])
    claim_summary = {
        "dataset": "tigpr",
        "contrast": "random_minus_hash_group_balanced_accuracy",
        "n_model_families": len(model_summary),
        "directional_support_count": directional,
        "material_support_count": material,
        "delta_mean_across_models": float(np.mean(deltas)),
        "delta_min": float(np.min(deltas)),
        "delta_max": float(np.max(deltas)),
        "claim_status": "supported" if material >= 3 else "directional_only" if directional >= 3 else "not_supported",
    }

    result = {
        "run_id": "20260811_E15_tigpr_model_family_duplicate_matrix",
        "n_samples": len(rows),
        "label_counts": {str(key): int(value) for key, value in Counter(y).items()},
        "seeds": SEEDS,
        "material_delta_threshold": MATERIAL_DELTA,
        "model_family_summary": model_summary,
        "claim_summary": claim_summary,
        "claim_boundary": "Restored-local TIGPR model-family duplicate test; not blind external validation.",
    }
    write_csv(args.output_dir / "tigpr_model_family_duplicate_runs.csv", detailed)
    (args.output_dir / "tigpr_model_family_duplicate_summary.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_md(args.output_dir / "tigpr_model_family_duplicate_summary.md", result)
    print(json.dumps({"claim_summary": claim_summary}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
