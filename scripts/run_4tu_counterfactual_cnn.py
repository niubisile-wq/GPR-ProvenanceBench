#!/usr/bin/env python3
"""Evaluate 4TU counterfactual reliance with a small CPU CNN."""

from __future__ import annotations

import argparse
import csv
import json
import random
from collections import Counter
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from run_4tu_counterfactual_reliance import (
    VARIANT_ORDER,
    is_viable,
    label_coverage,
    read_csv,
    split_indices,
    variant,
)


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.set_num_threads(max(1, min(4, torch.get_num_threads())))


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


def image_tensor(array: np.ndarray, image_size: int) -> np.ndarray:
    image = Image.fromarray(np.uint8(np.clip(normalize(array) * 255.0, 0, 255)), mode="L")
    resized = image.resize((image_size, image_size), resample=Image.Resampling.BILINEAR)
    return (np.asarray(resized, dtype=np.float32) / 255.0)[None, :, :]


def matrix_tensor(rows: list[dict[str, str]], variant_name: str, image_size: int) -> torch.Tensor:
    arrays = []
    for row in rows:
        matrix = np.load(row["package_npy_path"])
        arrays.append(image_tensor(variant(matrix, variant_name), image_size))
    return torch.tensor(np.asarray(arrays, dtype=np.float32))


class SmallCnn(nn.Module):
    def __init__(self, n_classes: int) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(1, 12, kernel_size=3, padding=1),
            nn.BatchNorm2d(12),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(12, 24, kernel_size=3, padding=1),
            nn.BatchNorm2d(24),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.AdaptiveAvgPool2d((4, 4)),
            nn.Flatten(),
            nn.Linear(24 * 4 * 4, 64),
            nn.ReLU(),
            nn.Dropout(0.20),
            nn.Linear(64, n_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


def class_weights(y: np.ndarray, n_classes: int) -> torch.Tensor:
    counts = np.bincount(y, minlength=n_classes).astype(np.float32)
    counts[counts == 0] = 1.0
    weights = counts.sum() / (n_classes * counts)
    return torch.tensor(weights, dtype=torch.float32)


def predict(model: nn.Module, x: torch.Tensor, batch_size: int) -> np.ndarray:
    model.eval()
    preds = []
    with torch.no_grad():
        for start in range(0, len(x), batch_size):
            logits = model(x[start : start + batch_size])
            preds.append(torch.argmax(logits, dim=1).cpu().numpy())
    return np.concatenate(preds)


def train_model(
    x_train: torch.Tensor,
    y_train: np.ndarray,
    x_val: torch.Tensor,
    y_val: np.ndarray,
    seed: int,
    epochs: int,
    batch_size: int,
    learning_rate: float,
) -> tuple[nn.Module, dict[str, float]]:
    set_seed(seed)
    n_classes = int(np.max(y_train)) + 1
    model = SmallCnn(n_classes)
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=1e-3)
    criterion = nn.CrossEntropyLoss(weight=class_weights(y_train, n_classes))
    loader = DataLoader(
        TensorDataset(x_train, torch.tensor(y_train, dtype=torch.long)),
        batch_size=batch_size,
        shuffle=True,
        generator=torch.Generator().manual_seed(seed),
    )
    best_state = None
    best = {"epoch": 0, "val_balanced_accuracy": -1.0, "val_macro_f1": -1.0}
    for epoch in range(1, epochs + 1):
        model.train()
        for xb, yb in loader:
            optimizer.zero_grad(set_to_none=True)
            loss = criterion(model(xb), yb)
            loss.backward()
            optimizer.step()
        val_pred = predict(model, x_val, batch_size)
        val_ba = float(balanced_accuracy_score(y_val, val_pred))
        val_f1 = float(f1_score(y_val, val_pred, average="macro"))
        if (val_ba, val_f1) > (best["val_balanced_accuracy"], best["val_macro_f1"]):
            best = {"epoch": epoch, "val_balanced_accuracy": val_ba, "val_macro_f1": val_f1}
            best_state = {key: value.detach().clone() for key, value in model.state_dict().items()}
    if best_state is not None:
        model.load_state_dict(best_state)
    return model, best


def encode_labels(labels: np.ndarray) -> tuple[np.ndarray, dict[int, str]]:
    classes = sorted(set(map(str, labels)))
    to_idx = {label: idx for idx, label in enumerate(classes)}
    return np.asarray([to_idx[str(label)] for label in labels], dtype=np.int64), {idx: label for label, idx in to_idx.items()}


def evaluate_predictions(y_true: np.ndarray, pred: np.ndarray, reference_pred: np.ndarray | None = None) -> dict[str, object]:
    unseen_pred = sorted(set(map(int, np.unique(pred))) - set(map(int, np.unique(y_true))))
    result = {
        "accuracy": float(accuracy_score(y_true, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, pred)),
        "macro_f1": float(f1_score(y_true, pred, average="macro")),
        "n_predicted_classes_not_in_test": len(unseen_pred),
        "predicted_classes_not_in_test": unseen_pred,
    }
    result["prediction_flip_rate_vs_original"] = float(np.mean(pred != reference_pred)) if reference_pred is not None else 0.0
    return result


def evaluate_target(rows: list[dict[str, str]], target: str, args: argparse.Namespace) -> dict:
    target_rows = [row for row in rows if row.get(target, "unknown") != "unknown"]
    labels_raw = np.asarray([row[target] for row in target_rows])
    idx_by_split = split_indices(target_rows)
    coverage = label_coverage(labels_raw, idx_by_split)
    result = {
        "target_field": target,
        "records": len(target_rows),
        "split_counts": {split: int(len(idx)) for split, idx in idx_by_split.items()},
        "label_counts": {str(k): int(v) for k, v in Counter(labels_raw).items()},
        "split_label_counts": coverage,
        "is_viable": is_viable(coverage),
        "feature": "cnn_pixels",
        "image_size": args.image_size,
        "epochs": args.epochs,
        "seed": args.seed,
        "models": [],
    }
    if not result["is_viable"]:
        result["reason"] = "one_or_more_splits_have_fewer_than_two_classes"
        return result

    y, class_map = encode_labels(labels_raw)
    train_idx = idx_by_split["train"]
    val_idx = idx_by_split["val"]
    test_idx = idx_by_split["test"]
    original_x = matrix_tensor(target_rows, "original", args.image_size)
    model, best = train_model(
        original_x[train_idx],
        y[train_idx],
        original_x[val_idx],
        y[val_idx],
        args.seed,
        args.epochs,
        args.batch_size,
        args.learning_rate,
    )
    test_rows = [target_rows[i] for i in test_idx]
    original_test_pred = predict(model, original_x[test_idx], args.batch_size)
    variant_rows = []
    original_metrics = None
    for variant_name in VARIANT_ORDER:
        x_variant = matrix_tensor(test_rows, variant_name, args.image_size)
        pred = predict(model, x_variant, args.batch_size)
        metrics = evaluate_predictions(y[test_idx], pred, original_test_pred)
        if variant_name == "original":
            original_metrics = metrics
        row = {"variant": variant_name, **metrics}
        row["balanced_accuracy_delta_vs_original"] = float(metrics["balanced_accuracy"] - original_metrics["balanced_accuracy"])
        row["macro_f1_delta_vs_original"] = float(metrics["macro_f1"] - original_metrics["macro_f1"])
        variant_rows.append(row)
    result["models"].append(
        {
            "model": "small_cnn",
            "best_epoch": best["epoch"],
            "val_balanced_accuracy": best["val_balanced_accuracy"],
            "val_macro_f1": best["val_macro_f1"],
            "variant_rows": variant_rows,
        }
    )
    result["selected_model"] = "small_cnn"
    result["class_map"] = {str(k): v for k, v in class_map.items()}
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
                        "epochs": target["epochs"],
                        "seed": target["seed"],
                        "model": model["model"],
                        "best_epoch": model["best_epoch"],
                        "variant": item["variant"],
                        "val_balanced_accuracy": model["val_balanced_accuracy"],
                        "test_balanced_accuracy": item["balanced_accuracy"],
                        "balanced_accuracy_delta_vs_original": item["balanced_accuracy_delta_vs_original"],
                        "test_macro_f1": item["macro_f1"],
                        "macro_f1_delta_vs_original": item["macro_f1_delta_vs_original"],
                        "prediction_flip_rate_vs_original": item["prediction_flip_rate_vs_original"],
                        "n_predicted_classes_not_in_test": item["n_predicted_classes_not_in_test"],
                        "predicted_classes_not_in_test": "; ".join(map(str, item["predicted_classes_not_in_test"])),
                    }
                )
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_md(path: Path, results: list[dict], flat_rows: list[dict[str, object]]) -> None:
    ranked = sorted(
        [row for row in flat_rows if row["variant"] != "original"],
        key=lambda row: (row["balanced_accuracy_delta_vs_original"], -row["prediction_flip_rate_vs_original"]),
    )[:12]
    lines = [
        "# 4TU Small-CNN Counterfactual Reliance 2026-08-10",
        "",
        "Protocol: normalize raw matrix, resize to 64x64 grayscale, train a small CPU CNN on original train matrices, select best epoch by validation balanced accuracy, then evaluate original and variant test matrices.",
        "",
        "## Target Status",
        "",
        "| target | records | viable | best_epoch | val_BA |",
        "| --- | ---: | --- | ---: | ---: |",
    ]
    for target in results:
        model = target.get("models", [{}])[0] if target.get("models") else {}
        lines.append(
            f"| {target['target_field']} | {target['records']} | {target['is_viable']} | {model.get('best_epoch', 0)} | {model.get('val_balanced_accuracy', 0.0):.4f} |"
        )
    lines.extend(
        [
            "",
            "## Largest Drops",
            "",
            "| target | variant | test_BA | delta_BA | flip_rate |",
            "| --- | --- | ---: | ---: | ---: |",
        ]
    )
    for row in ranked:
        lines.append(
            f"| {row['target_field']} | {row['variant']} | {row['test_balanced_accuracy']:.4f} | "
            f"{row['balanced_accuracy_delta_vs_original']:.4f} | {row['prediction_flip_rate_vs_original']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This is a CPU proof-of-execution CNN. It establishes that the counterfactual pipeline can run with a learned image model, but it is single-seed and underpowered; final claims require repeated seeds, stronger tuning and external validation.",
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
    parser.add_argument("--epochs", type=int, default=40)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--targets", nargs="+", default=["Land type", "Land cover", "Utility crossing", "Construction workers"])
    args = parser.parse_args()

    set_seed(args.seed)
    rows = read_csv(args.task_manifest)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    results = [evaluate_target(rows, target, args) for target in args.targets]
    flat_rows = flatten_results(results)
    result = {
        "task_manifest": str(args.task_manifest),
        "seed": args.seed,
        "image_size": args.image_size,
        "epochs": args.epochs,
        "feature": "cnn_pixels",
        "variants": VARIANT_ORDER,
        "targets": results,
        "flat_csv": "cnn_reliance_metrics.csv",
    }
    (args.output_dir / "cnn_reliance_summary.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_csv(args.output_dir / "cnn_reliance_metrics.csv", flat_rows)
    write_md(args.output_dir / "cnn_reliance_summary.md", results, flat_rows)
    print(json.dumps({"targets": len(results), "metric_rows": len(flat_rows), "seed": args.seed}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
