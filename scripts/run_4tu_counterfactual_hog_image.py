#!/usr/bin/env python3
"""Evaluate 4TU counterfactual reliance with HOG image features."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image
from skimage.feature import hog
from sklearn.metrics import balanced_accuracy_score, f1_score

from run_4tu_counterfactual_reliance import (
    VARIANT_ORDER,
    evaluate_predictions,
    is_viable,
    label_coverage,
    make_models,
    read_csv,
    split_indices,
    variant,
)


def normalize(array: np.ndarray) -> np.ndarray:
    arr = np.asarray(array, dtype=np.float32)
    finite = np.isfinite(arr)
    if not np.any(finite):
        return np.zeros_like(arr, dtype=np.float32)
    clean = arr.copy()
    clean[~finite] = 0.0
    minimum = float(np.min(clean))
    maximum = float(np.max(clean))
    if maximum <= minimum:
        return np.zeros_like(clean, dtype=np.float32)
    return (clean - minimum) / (maximum - minimum)


def image_array(array: np.ndarray, image_size: int) -> np.ndarray:
    image = Image.fromarray(np.uint8(np.clip(normalize(array) * 255.0, 0, 255)), mode="L")
    resized = image.resize((image_size, image_size), resample=Image.Resampling.BILINEAR)
    return np.asarray(resized, dtype=np.float32) / 255.0


def hog_vector(array: np.ndarray, image_size: int) -> np.ndarray:
    img = image_array(array, image_size)
    return hog(
        img,
        orientations=9,
        pixels_per_cell=(8, 8),
        cells_per_block=(2, 2),
        block_norm="L2-Hys",
        transform_sqrt=False,
        feature_vector=True,
    ).astype(np.float32)


def matrix_features(rows: list[dict[str, str]], variant_name: str, image_size: int) -> np.ndarray:
    vectors = []
    for row in rows:
        matrix = np.load(row["package_npy_path"])
        vectors.append(hog_vector(variant(matrix, variant_name), image_size))
    return np.asarray(vectors, dtype=np.float32)


def evaluate_target(rows: list[dict[str, str]], target: str, seed: int, image_size: int) -> dict:
    target_rows = [row for row in rows if row.get(target, "unknown") != "unknown"]
    labels = np.asarray([row[target] for row in target_rows])
    idx_by_split = split_indices(target_rows)
    coverage = label_coverage(labels, idx_by_split)
    result = {
        "target_field": target,
        "records": len(target_rows),
        "split_counts": {split: int(len(idx)) for split, idx in idx_by_split.items()},
        "label_counts": {str(k): int(v) for k, v in Counter(labels).items()},
        "split_label_counts": coverage,
        "is_viable": is_viable(coverage),
        "feature": "hog",
        "image_size": image_size,
        "models": [],
    }
    if not result["is_viable"]:
        result["reason"] = "one_or_more_splits_have_fewer_than_two_classes"
        return result

    original_x = matrix_features(target_rows, "original", image_size)
    train_idx = idx_by_split["train"]
    val_idx = idx_by_split["val"]
    test_idx = idx_by_split["test"]
    test_rows = [target_rows[i] for i in test_idx]
    variant_features = {
        name: matrix_features(test_rows, name, image_size)
        for name in VARIANT_ORDER
    }

    for model_name, model in make_models(seed, len(np.unique(labels[train_idx]))).items():
        fitted = model.fit(original_x[train_idx], labels[train_idx])
        val_pred = fitted.predict(original_x[val_idx])
        original_test_pred = fitted.predict(original_x[test_idx])
        model_result = {
            "model": model_name,
            "val_balanced_accuracy": float(balanced_accuracy_score(labels[val_idx], val_pred)),
            "val_macro_f1": float(f1_score(labels[val_idx], val_pred, average="macro")),
            "variant_rows": [],
        }
        original_metrics = None
        for variant_name in VARIANT_ORDER:
            pred = fitted.predict(variant_features[variant_name])
            metrics = evaluate_predictions(labels[test_idx], pred, original_test_pred)
            if variant_name == "original":
                original_metrics = metrics
            row = {"variant": variant_name, **metrics}
            row["balanced_accuracy_delta_vs_original"] = float(metrics["balanced_accuracy"] - original_metrics["balanced_accuracy"])
            row["macro_f1_delta_vs_original"] = float(metrics["macro_f1"] - original_metrics["macro_f1"])
            model_result["variant_rows"].append(row)
        result["models"].append(model_result)

    result["selected_model"] = max(
        result["models"],
        key=lambda item: (item["val_balanced_accuracy"], item["val_macro_f1"]),
    )["model"]
    result["hog_dimension"] = int(original_x.shape[1])
    return result


def flatten_results(results: list[dict]) -> list[dict[str, object]]:
    rows = []
    for target in results:
        for model in target.get("models", []):
            for item in model["variant_rows"]:
                rows.append(
                    {
                        "target_field": target["target_field"],
                        "records": target["records"],
                        "feature": target["feature"],
                        "image_size": target["image_size"],
                        "hog_dimension": target.get("hog_dimension", 0),
                        "selected_model": target.get("selected_model", ""),
                        "model": model["model"],
                        "variant": item["variant"],
                        "val_balanced_accuracy": model["val_balanced_accuracy"],
                        "test_balanced_accuracy": item["balanced_accuracy"],
                        "balanced_accuracy_delta_vs_original": item["balanced_accuracy_delta_vs_original"],
                        "test_macro_f1": item["macro_f1"],
                        "macro_f1_delta_vs_original": item["macro_f1_delta_vs_original"],
                        "prediction_flip_rate_vs_original": item["prediction_flip_rate_vs_original"],
                        "n_predicted_classes_not_in_test": item["n_predicted_classes_not_in_test"],
                        "predicted_classes_not_in_test": "; ".join(item["predicted_classes_not_in_test"]),
                    }
                )
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_md(path: Path, results: list[dict], flat_rows: list[dict[str, object]]) -> None:
    selected = [row for row in flat_rows if row["model"] == row["selected_model"] and row["variant"] != "original"]
    non_dummy = [row for row in flat_rows if row["model"] != "dummy_majority" and row["variant"] != "original"]
    top_selected = sorted(selected, key=lambda row: (row["balanced_accuracy_delta_vs_original"], -row["prediction_flip_rate_vs_original"]))[:12]
    top_non_dummy = sorted(non_dummy, key=lambda row: (row["balanced_accuracy_delta_vs_original"], -row["prediction_flip_rate_vs_original"]))[:12]

    lines = [
        "# 4TU HOG Image Counterfactual Reliance 2026-08-10",
        "",
        "Feature protocol: normalize each raw matrix, resize to 64x64 grayscale, extract HOG features, train on original train matrices, then evaluate original and variant test matrices.",
        "",
        "## Target Status",
        "",
        "| target | records | viable | selected_model | hog_dimension |",
        "| --- | ---: | --- | --- | ---: |",
    ]
    for target in results:
        lines.append(
            f"| {target['target_field']} | {target['records']} | {target['is_viable']} | {target.get('selected_model', 'not_run')} | {target.get('hog_dimension', 0)} |"
        )

    lines.extend(
        [
            "",
            "## Largest Drops For Validation-Selected Models",
            "",
            "| target | model | variant | test_BA | delta_BA | flip_rate |",
            "| --- | --- | --- | ---: | ---: | ---: |",
        ]
    )
    for row in top_selected:
        lines.append(
            f"| {row['target_field']} | {row['model']} | {row['variant']} | "
            f"{row['test_balanced_accuracy']:.4f} | {row['balanced_accuracy_delta_vs_original']:.4f} | "
            f"{row['prediction_flip_rate_vs_original']:.4f} |"
        )

    lines.extend(
        [
            "",
            "## Largest Drops For Non-Dummy Models",
            "",
            "| target | model | variant | test_BA | delta_BA | flip_rate |",
            "| --- | --- | --- | ---: | ---: | ---: |",
        ]
    )
    for row in top_non_dummy:
        lines.append(
            f"| {row['target_field']} | {row['model']} | {row['variant']} | "
            f"{row['test_balanced_accuracy']:.4f} | {row['balanced_accuracy_delta_vs_original']:.4f} | "
            f"{row['prediction_flip_rate_vs_original']:.4f} |"
        )

    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This is an image-feature classifier test on raw-trace-derived HOG vectors. It is stronger than the 16-feature summary test and more structured than the raw pixel baseline, but it is still not a deep raw-trace model or external blind validation.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20260810)
    parser.add_argument("--image-size", type=int, default=64)
    parser.add_argument("--targets", nargs="+", default=[
        "Land type",
        "Land cover",
        "Utility crossing",
        "Construction workers",
        "Land use",
        "Relative groundwater level",
    ])
    args = parser.parse_args()

    rows = read_csv(args.task_manifest)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    results = [evaluate_target(rows, target, args.seed, args.image_size) for target in args.targets]
    flat_rows = flatten_results(results)
    result = {
        "task_manifest": str(args.task_manifest),
        "seed": args.seed,
        "image_size": args.image_size,
        "feature": "hog",
        "variants": VARIANT_ORDER,
        "targets": results,
        "flat_csv": "hog_image_reliance_metrics.csv",
    }
    (args.output_dir / "hog_image_reliance_summary.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_csv(args.output_dir / "hog_image_reliance_metrics.csv", flat_rows)
    write_md(args.output_dir / "hog_image_reliance_summary.md", results, flat_rows)
    print(json.dumps({"targets": len(results), "metric_rows": len(flat_rows), "image_size": args.image_size, "feature": "hog"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
