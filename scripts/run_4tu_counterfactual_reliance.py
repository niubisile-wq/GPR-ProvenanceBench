#!/usr/bin/env python3
"""Evaluate classifier sensitivity to 4TU raw-trace counterfactual variants."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


VARIANT_ORDER = [
    "original",
    "log_clip",
    "zscore_clip",
    "amplitude_jitter",
    "remove_top_band",
    "remove_bottom_band",
    "remove_border",
    "time_reverse",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def normalize_path(value: str) -> Path:
    path = Path(value)
    if path.exists():
        return path
    raise FileNotFoundError(value)


def feature_vector(array: np.ndarray) -> dict[str, float]:
    arr = np.asarray(array, dtype=np.float32)
    if arr.ndim != 2:
        raise ValueError(f"expected 2D matrix, got shape {arr.shape}")
    h, w = arr.shape
    top = arr[: max(1, h // 10), :]
    bottom = arr[-max(1, h // 10) :, :]
    left = arr[:, : max(1, w // 10)]
    right = arr[:, -max(1, w // 10) :]
    center = arr[max(1, h // 10) : max(1, h - h // 10), max(1, w // 10) : max(1, w - w // 10)]
    center = center if center.size else arr
    grad_y = np.diff(arr, axis=0)
    grad_x = np.diff(arr, axis=1)
    return {
        "shape_rows": float(h),
        "shape_cols": float(w),
        "mean": float(arr.mean()),
        "std": float(arr.std()),
        "min": float(arr.min()),
        "max": float(arr.max()),
        "p05": float(np.quantile(arr, 0.05)),
        "p95": float(np.quantile(arr, 0.95)),
        "top_mean": float(top.mean()),
        "bottom_mean": float(bottom.mean()),
        "left_mean": float(left.mean()),
        "right_mean": float(right.mean()),
        "center_mean": float(center.mean()),
        "edge_center_gap": float(((top.mean() + bottom.mean() + left.mean() + right.mean()) / 4.0) - center.mean()),
        "grad_y_abs_mean": float(np.abs(grad_y).mean()) if grad_y.size else 0.0,
        "grad_x_abs_mean": float(np.abs(grad_x).mean()) if grad_x.size else 0.0,
    }


def variant(array: np.ndarray, name: str) -> np.ndarray:
    arr = np.asarray(array, dtype=np.float32)
    if name == "original":
        return arr.copy()
    if name == "log_clip":
        return np.sign(arr) * np.log1p(np.abs(arr))
    if name == "zscore_clip":
        std = float(np.std(arr))
        if std <= 1e-8:
            return np.zeros_like(arr, dtype=np.float32)
        return np.clip((arr - float(np.mean(arr))) / std, -3.0, 3.0)
    if name == "amplitude_jitter":
        offset = float(np.median(arr))
        return (arr - offset) * 0.85 + offset
    if name == "remove_top_band":
        out = arr.copy()
        rows = min(24, max(1, out.shape[0] // 10))
        out[:rows, :] = np.median(out[rows : rows * 2, :], axis=0, keepdims=True)
        return out
    if name == "remove_bottom_band":
        out = arr.copy()
        rows = min(24, max(1, out.shape[0] // 10))
        out[-rows:, :] = np.median(out[-rows * 2 : -rows, :], axis=0, keepdims=True)
        return out
    if name == "remove_border":
        out = arr.copy()
        border = min(24, max(1, min(out.shape) // 10))
        if out.shape[0] <= border * 2 or out.shape[1] <= border * 2:
            return out
        fill = float(np.median(out[border:-border, border:-border]))
        out[:border, :] = fill
        out[-border:, :] = fill
        out[:, :border] = fill
        out[:, -border:] = fill
        return out
    if name == "time_reverse":
        return arr[::-1, :]
    raise ValueError(f"unknown variant: {name}")


def make_models(seed: int, n_train_classes: int) -> dict:
    models = {"dummy_majority": DummyClassifier(strategy="most_frequent")}
    if n_train_classes >= 2:
        models.update(
            {
                "extra_trees": ExtraTreesClassifier(
                    n_estimators=500,
                    min_samples_leaf=2,
                    class_weight="balanced",
                    random_state=seed,
                    n_jobs=-1,
                ),
                "rbf_svm": make_pipeline(
                    StandardScaler(),
                    SVC(C=3.0, gamma="scale", class_weight="balanced", random_state=seed),
                ),
            }
        )
    return models


def matrix_features(rows: list[dict[str, str]], variant_name: str) -> tuple[np.ndarray, list[str]]:
    feature_rows = []
    feature_names = None
    for row in rows:
        matrix = np.load(normalize_path(row["package_npy_path"]))
        feats = feature_vector(variant(matrix, variant_name))
        if feature_names is None:
            feature_names = list(feats.keys())
        feature_rows.append(feats)
    assert feature_names is not None
    return np.asarray([[item[name] for name in feature_names] for item in feature_rows], dtype=np.float32), feature_names


def split_indices(rows: list[dict[str, str]]) -> dict[str, np.ndarray]:
    roles = np.asarray([row["split_role"] for row in rows])
    return {role: np.flatnonzero(roles == role) for role in ("train", "val", "test")}


def label_coverage(labels: np.ndarray, idx_by_split: dict[str, np.ndarray]) -> dict[str, dict[str, int]]:
    return {
        split: {str(k): int(v) for k, v in Counter(labels[idx]).items()}
        for split, idx in idx_by_split.items()
    }


def is_viable(coverage: dict[str, dict[str, int]]) -> bool:
    return all(len(counts) >= 2 for counts in coverage.values())


def evaluate_predictions(y_true: np.ndarray, pred: np.ndarray, reference_pred: np.ndarray | None = None) -> dict[str, float]:
    unseen_pred = sorted(set(map(str, np.unique(pred))) - set(map(str, np.unique(y_true))))
    result = {
        "accuracy": float(accuracy_score(y_true, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, pred)),
        "macro_f1": float(f1_score(y_true, pred, average="macro")),
        "n_predicted_classes_not_in_test": float(len(unseen_pred)),
        "predicted_classes_not_in_test": unseen_pred,
    }
    if reference_pred is not None:
        result["prediction_flip_rate_vs_original"] = float(np.mean(pred != reference_pred))
    else:
        result["prediction_flip_rate_vs_original"] = 0.0
    return result


def evaluate_target(rows: list[dict[str, str]], target: str, seed: int) -> dict:
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
        "models": [],
    }
    if not result["is_viable"]:
        result["reason"] = "one_or_more_splits_have_fewer_than_two_classes"
        return result

    original_x, feature_names = matrix_features(target_rows, "original")
    train_idx = idx_by_split["train"]
    val_idx = idx_by_split["val"]
    test_idx = idx_by_split["test"]
    models = make_models(seed, len(np.unique(labels[train_idx])))

    variant_features = {
        name: matrix_features([target_rows[i] for i in test_idx], name)[0]
        for name in VARIANT_ORDER
    }

    for model_name, model in models.items():
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
            if original_metrics is not None:
                row["balanced_accuracy_delta_vs_original"] = float(metrics["balanced_accuracy"] - original_metrics["balanced_accuracy"])
                row["macro_f1_delta_vs_original"] = float(metrics["macro_f1"] - original_metrics["macro_f1"])
            model_result["variant_rows"].append(row)
        result["models"].append(model_result)

    result["selected_model"] = max(
        result["models"],
        key=lambda item: (item["val_balanced_accuracy"], item["val_macro_f1"]),
    )["model"]
    result["feature_names"] = feature_names
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
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_md(path: Path, results: list[dict], flat_rows: list[dict[str, object]]) -> None:
    selected_rows = [
        row for row in flat_rows
        if row["model"] == row["selected_model"] and row["variant"] != "original"
    ]
    nontrivial_rows = [
        row for row in flat_rows
        if row["model"] != "dummy_majority" and row["variant"] != "original"
    ]
    top_selected = sorted(selected_rows, key=lambda row: (row["balanced_accuracy_delta_vs_original"], -row["prediction_flip_rate_vs_original"]))[:12]
    top_nontrivial = sorted(nontrivial_rows, key=lambda row: (row["balanced_accuracy_delta_vs_original"], -row["prediction_flip_rate_vs_original"]))[:12]

    lines = [
        "# 4TU Classifier-Level Counterfactual Reliance 2026-08-10",
        "",
        "Training protocol: train each model on original train matrices, select by original validation balanced accuracy, then evaluate original and variant test matrices.",
        "",
        "## Target Status",
        "",
        "| target | records | viable | selected_model |",
        "| --- | ---: | --- | --- |",
    ]
    for target in results:
        lines.append(
            f"| {target['target_field']} | {target['records']} | {target['is_viable']} | {target.get('selected_model', 'not_run')} |"
        )

    lines.extend(
        [
            "",
            "## Largest Drops For Validation-Selected Models",
            "",
            "| target | model | variant | test_BA | delta_BA | flip_rate | unseen_pred_classes |",
            "| --- | --- | --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in top_selected:
        lines.append(
            f"| {row['target_field']} | {row['model']} | {row['variant']} | "
            f"{row['test_balanced_accuracy']:.4f} | {row['balanced_accuracy_delta_vs_original']:.4f} | "
            f"{row['prediction_flip_rate_vs_original']:.4f} | {int(row['n_predicted_classes_not_in_test'])} |"
        )

    lines.extend(
        [
            "",
            "## Largest Drops For Non-Dummy Models",
            "",
            "| target | model | variant | test_BA | delta_BA | flip_rate | unseen_pred_classes |",
            "| --- | --- | --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in top_nontrivial:
        lines.append(
            f"| {row['target_field']} | {row['model']} | {row['variant']} | "
            f"{row['test_balanced_accuracy']:.4f} | {row['balanced_accuracy_delta_vs_original']:.4f} | "
            f"{row['prediction_flip_rate_vs_original']:.4f} | {int(row['n_predicted_classes_not_in_test'])} |"
        )

    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This is a classifier-level stress test on matrix summary features. It is stronger than the generation-only audit, but it is not yet final raw-trace causal evidence because the models are lightweight feature classifiers and the target labels are task metadata.",
            "",
            "`unseen_pred_classes` records when a variant makes the classifier predict labels absent from the test split. Treat this as an instability warning, not as a separate success criterion.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20260810)
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
    results = [evaluate_target(rows, target, args.seed) for target in args.targets]
    flat_rows = flatten_results(results)
    result = {
        "task_manifest": str(args.task_manifest),
        "seed": args.seed,
        "variants": VARIANT_ORDER,
        "targets": results,
        "flat_csv": "counterfactual_reliance_metrics.csv",
    }
    (args.output_dir / "counterfactual_reliance_summary.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_csv(args.output_dir / "counterfactual_reliance_metrics.csv", flat_rows)
    write_md(args.output_dir / "counterfactual_reliance_summary.md", results, flat_rows)
    print(json.dumps({"targets": len(results), "metric_rows": len(flat_rows)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
