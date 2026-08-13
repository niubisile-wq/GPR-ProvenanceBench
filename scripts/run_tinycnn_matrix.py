#!/usr/bin/env python3
"""Run a CPU TinyCNN as the third model family for Mojahid and Res-SAM."""

from __future__ import annotations

import argparse
import csv
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score
from sklearn.model_selection import StratifiedShuffleSplit
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


SHARED_RESSAM_LABELS = {"cavity", "crack", "pipe"}
SEEDS = [20260810, 20260811, 20260812, 20260813, 20260814]


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.set_num_threads(max(1, min(4, torch.get_num_threads())))


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def load_tensor(path: Path, image_size: int) -> np.ndarray:
    with Image.open(path) as image:
        image.load()
        arr = np.asarray(
            image.convert("L").resize((image_size, image_size), Image.Resampling.BILINEAR),
            dtype=np.float32,
        )
    return (arr / 255.0)[None, :, :]


def extract_images(rows: list[dict[str, str]], data_root: Path, image_size: int) -> tuple[torch.Tensor, np.ndarray, np.ndarray, np.ndarray]:
    images: list[np.ndarray] = []
    labels: list[str] = []
    fold_ids: list[str] = []
    environments: list[str] = []
    for row in rows:
        image_path = data_root / row["rel_path"].replace("/", "\\")
        if not image_path.exists():
            raise FileNotFoundError(f"Missing image: {image_path}")
        images.append(load_tensor(image_path, image_size))
        labels.append(row["label"])
        fold_ids.append(row.get("fold_id", ""))
        environments.append(row.get("project_id", row.get("source_group", "")))
    return (
        torch.tensor(np.asarray(images, dtype=np.float32)),
        np.asarray(labels),
        np.asarray(fold_ids),
        np.asarray(environments),
    )


def encode_labels(labels: np.ndarray) -> tuple[np.ndarray, dict[int, str]]:
    classes = sorted(set(map(str, labels)))
    mapping = {label: idx for idx, label in enumerate(classes)}
    return np.asarray([mapping[str(label)] for label in labels], dtype=np.int64), {idx: label for label, idx in mapping.items()}


class TinyCnn(nn.Module):
    def __init__(self, n_classes: int) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(1, 8, kernel_size=3, padding=1),
            nn.BatchNorm2d(8),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(8, 16, kernel_size=3, padding=1),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((4, 4)),
            nn.Flatten(),
            nn.Linear(32 * 4 * 4, 64),
            nn.ReLU(),
            nn.Dropout(0.20),
            nn.Linear(64, n_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


def class_weights(y: np.ndarray, n_classes: int) -> torch.Tensor:
    counts = np.bincount(y, minlength=n_classes).astype(np.float32)
    counts[counts == 0] = 1.0
    return torch.tensor(counts.sum() / (n_classes * counts), dtype=torch.float32)


def predict(model: nn.Module, x: torch.Tensor, batch_size: int) -> np.ndarray:
    model.eval()
    preds = []
    with torch.no_grad():
        for start in range(0, len(x), batch_size):
            logits = model(x[start : start + batch_size])
            preds.append(torch.argmax(logits, dim=1).cpu().numpy())
    return np.concatenate(preds)


def train_fixed_epoch(
    x: torch.Tensor,
    y: np.ndarray,
    train_idx: np.ndarray,
    seed: int,
    epochs: int,
    batch_size: int,
    learning_rate: float,
) -> nn.Module:
    set_seed(seed)
    n_classes = int(np.max(y[train_idx])) + 1
    model = TinyCnn(n_classes)
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=1e-3)
    criterion = nn.CrossEntropyLoss(weight=class_weights(y[train_idx], n_classes))
    loader = DataLoader(
        TensorDataset(x[train_idx], torch.tensor(y[train_idx], dtype=torch.long)),
        batch_size=batch_size,
        shuffle=True,
        generator=torch.Generator().manual_seed(seed),
    )
    for _ in range(epochs):
        model.train()
        for xb, yb in loader:
            optimizer.zero_grad(set_to_none=True)
            loss = criterion(model(xb), yb)
            loss.backward()
            optimizer.step()
    return model


def evaluate_split(
    x: torch.Tensor,
    labels: np.ndarray,
    train_idx: np.ndarray,
    test_idx: np.ndarray,
    seed: int,
    epochs: int,
    batch_size: int,
    learning_rate: float,
) -> dict[str, object]:
    protocol_idx = np.concatenate([train_idx, test_idx])
    protocol_labels = labels[protocol_idx]
    _, class_map = encode_labels(protocol_labels)
    class_to_idx = {label: idx for idx, label in class_map.items()}
    y_train = np.asarray([class_to_idx[str(label)] for label in labels[train_idx]], dtype=np.int64)
    y_test = np.asarray([class_to_idx[str(label)] for label in labels[test_idx]], dtype=np.int64)
    y_protocol = np.full(len(labels), -1, dtype=np.int64)
    y_protocol[train_idx] = y_train
    y_protocol[test_idx] = y_test
    model = train_fixed_epoch(x, y_protocol, train_idx, seed, epochs, batch_size, learning_rate)
    pred = predict(model, x[test_idx], batch_size)
    return {
        "train_n": int(len(train_idx)),
        "test_n": int(len(test_idx)),
        "accuracy": float(accuracy_score(y_test, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_test, pred)),
        "macro_f1": float(f1_score(y_test, pred, average="macro")),
        "train_label_counts": {str(k): int(v) for k, v in Counter(labels[train_idx]).items()},
        "test_label_counts": {str(k): int(v) for k, v in Counter(labels[test_idx]).items()},
    }


def run_mojahid(x: torch.Tensor, labels: np.ndarray, fold_ids: np.ndarray, seed: int, args: argparse.Namespace) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    splitter = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=seed)
    train_idx, test_idx = next(splitter.split(np.zeros(len(labels)), labels))
    rows.append(
        {
            "dataset": "mojahid",
            "seed": seed,
            "protocol": "random_stratified_80_20",
            **evaluate_split(x, labels, train_idx, test_idx, seed, args.epochs, args.batch_size, args.learning_rate),
        }
    )

    grouped_train_idx = np.flatnonzero(~np.isin(fold_ids, ["0", "1"]))
    grouped_test_idx = np.flatnonzero(fold_ids == "0")
    rows.append(
        {
            "dataset": "mojahid",
            "seed": seed,
            "protocol": "grouped_fold_0_test_fold_1_val",
            **evaluate_split(x, labels, grouped_train_idx, grouped_test_idx, seed, args.epochs, args.batch_size, args.learning_rate),
        }
    )
    return rows


def run_ressam(x: torch.Tensor, labels: np.ndarray, env: np.ndarray, seed: int, args: argparse.Namespace) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for environment in ["real_world", "synthetic"]:
        idx = np.flatnonzero(env == environment)
        splitter = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=seed)
        local_train, local_test = next(splitter.split(np.zeros(len(idx)), labels[idx]))
        rows.append(
            {
                "dataset": "res_sam",
                "seed": seed,
                "protocol": f"within_{environment}_random_80_20",
                "train_environment": environment,
                "test_environment": environment,
                **evaluate_split(x, labels, idx[local_train], idx[local_test], seed, args.epochs, args.batch_size, args.learning_rate),
            }
        )

    shared_idx = np.flatnonzero(np.isin(labels, sorted(SHARED_RESSAM_LABELS)))
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
                **evaluate_split(x, labels, train_idx, test_idx, seed, args.epochs, args.batch_size, args.learning_rate),
            }
        )
    return rows


def summarize(rows: list[dict[str, object]]) -> dict[str, object]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["dataset"]), str(row["protocol"]))].append(row)

    summaries = []
    for (dataset, protocol), items in sorted(grouped.items()):
        ba = np.asarray([float(item["balanced_accuracy"]) for item in items], dtype=np.float64)
        f1 = np.asarray([float(item["macro_f1"]) for item in items], dtype=np.float64)
        summaries.append(
            {
                "dataset": dataset,
                "protocol": protocol,
                "n_seeds": int(len(items)),
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
        "# TinyCNN Lightweight Model Matrix 2026-08-10",
        "",
        "This is the third model family after HOG+RBF-SVM and LBP+LinearSVM.",
        "",
        "## Model",
        "",
        "- Input: 64 x 64 grayscale pixels.",
        "- Architecture: three small convolution blocks with batch normalization and adaptive pooling.",
        f"- Epochs: {result['epochs']} fixed epochs, no validation-based epoch selection.",
        f"- Batch size: {result['batch_size']}.",
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
            "This is a CPU-scale deep baseline. It expands model-family coverage but is intentionally not tuned; use it as directional evidence only until the full frozen model matrix is complete.",
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
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--seeds", nargs="+", type=int, default=SEEDS)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    mojahid_rows = read_rows(args.mojahid_manifest)
    ressam_rows = read_rows(args.ressam_manifest)
    mojahid_x, mojahid_labels, mojahid_folds, _ = extract_images(mojahid_rows, args.mojahid_data_root, args.image_size)
    ressam_x, ressam_labels, _, ressam_env = extract_images(ressam_rows, args.ressam_data_root, args.image_size)

    metric_rows: list[dict[str, object]] = []
    for seed in args.seeds:
        metric_rows.extend(run_mojahid(mojahid_x, mojahid_labels, mojahid_folds, seed, args))
        metric_rows.extend(run_ressam(ressam_x, ressam_labels, ressam_env, seed, args))

    result = {
        "run_id": "20260810_E00_tinycnn_model_matrix",
        "model_family": "tinycnn",
        "seeds": args.seeds,
        "image_size": args.image_size,
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "learning_rate": args.learning_rate,
        "sample_counts": {
            "mojahid": len(mojahid_rows),
            "res_sam": len(ressam_rows),
        },
        "label_counts": {
            "mojahid": {str(k): int(v) for k, v in Counter(mojahid_labels).items()},
            "res_sam": {str(k): int(v) for k, v in Counter(ressam_labels).items()},
        },
        "summary": summarize(metric_rows),
    }
    write_csv(args.output_dir / "tinycnn_metrics.csv", metric_rows)
    (args.output_dir / "tinycnn_summary.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_md(args.output_dir / "tinycnn_summary.md", result)
    print(json.dumps(result["summary"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
