#!/usr/bin/env python3
"""Run frozen ResNet18 embeddings + LinearSVM as the fourth model family."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import torch
import torchvision.models as models
from PIL import Image
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


def load_model(weights_mode: str) -> tuple[torch.nn.Module, dict[str, str]]:
    status = {
        "requested": weights_mode,
        "loaded": "none",
        "source": "torchvision.models.resnet18(weights=None)",
        "note": "",
    }
    weights = None
    if weights_mode in {"auto", "imagenet"}:
        try:
            weights = models.ResNet18_Weights.DEFAULT
            status["loaded"] = "imagenet_default"
            status["source"] = weights.url
        except Exception as exc:  # pragma: no cover - defensive only
            if weights_mode == "imagenet":
                raise
            status["note"] = f"failed_to_resolve_default_weights: {exc}"
            weights = None
    try:
        model = models.resnet18(weights=weights)
    except Exception as exc:
        if weights_mode == "imagenet":
            raise
        status["loaded"] = "none"
        status["source"] = "torchvision.models.resnet18(weights=None)"
        status["note"] = f"failed_to_load_imagenet_weights_then_fell_back_to_none: {exc}"
        model = models.resnet18(weights=None)
    model.fc = torch.nn.Identity()
    model.eval()
    torch.set_num_threads(max(1, min(4, torch.get_num_threads())))
    return model, status


def image_tensor(path: Path, image_size: int, pretrained: bool) -> torch.Tensor:
    with Image.open(path) as image:
        image.load()
        arr = np.asarray(
            image.convert("RGB").resize((image_size, image_size), Image.Resampling.BILINEAR),
            dtype=np.float32,
        )
    arr = arr / 255.0
    if pretrained:
        mean = np.asarray([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.asarray([0.229, 0.224, 0.225], dtype=np.float32)
        arr = (arr - mean) / std
    arr = np.transpose(arr, (2, 0, 1))
    return torch.tensor(arr, dtype=torch.float32)


def extract_embeddings(
    rows: list[dict[str, str]],
    data_root: Path,
    model: torch.nn.Module,
    image_size: int,
    batch_size: int,
    pretrained: bool,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    tensors: list[torch.Tensor] = []
    labels: list[str] = []
    fold_ids: list[str] = []
    environments: list[str] = []
    for row in rows:
        image_path = data_root / row["rel_path"].replace("/", "\\")
        if not image_path.exists():
            raise FileNotFoundError(f"Missing image: {image_path}")
        tensors.append(image_tensor(image_path, image_size, pretrained))
        labels.append(row["label"])
        fold_ids.append(row.get("fold_id", ""))
        environments.append(row.get("project_id", row.get("source_group", "")))

    embeddings: list[np.ndarray] = []
    with torch.no_grad():
        for start in range(0, len(tensors), batch_size):
            batch = torch.stack(tensors[start : start + batch_size])
            embedding = model(batch).cpu().numpy().astype(np.float32)
            embeddings.append(embedding)
    return (
        np.concatenate(embeddings, axis=0),
        np.asarray(labels),
        np.asarray(fold_ids),
        np.asarray(environments),
    )


def encode_subset(train_labels: np.ndarray, test_labels: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    classes = sorted(set(map(str, np.concatenate([train_labels, test_labels]))))
    mapping = {label: idx for idx, label in enumerate(classes)}
    return (
        np.asarray([mapping[str(label)] for label in train_labels], dtype=np.int64),
        np.asarray([mapping[str(label)] for label in test_labels], dtype=np.int64),
    )


def evaluate_split(features: np.ndarray, labels: np.ndarray, train_idx: np.ndarray, test_idx: np.ndarray, seed: int) -> dict[str, object]:
    y_train, y_test = encode_subset(labels[train_idx], labels[test_idx])
    model = make_pipeline(
        StandardScaler(),
        LinearSVC(C=1.0, class_weight="balanced", random_state=seed, max_iter=30000),
    )
    model.fit(features[train_idx], y_train)
    pred = model.predict(features[test_idx])
    return {
        "train_n": int(len(train_idx)),
        "test_n": int(len(test_idx)),
        "accuracy": float(accuracy_score(y_test, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_test, pred)),
        "macro_f1": float(f1_score(y_test, pred, average="macro")),
    }


def run_mojahid(features: np.ndarray, labels: np.ndarray, fold_ids: np.ndarray, seed: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    splitter = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=seed)
    train_idx, test_idx = next(splitter.split(np.zeros(len(labels)), labels))
    rows.append(
        {
            "dataset": "mojahid",
            "seed": seed,
            "protocol": "random_stratified_80_20",
            **evaluate_split(features, labels, train_idx, test_idx, seed),
        }
    )

    grouped_train_idx = np.flatnonzero(~np.isin(fold_ids, ["0", "1"]))
    grouped_test_idx = np.flatnonzero(fold_ids == "0")
    rows.append(
        {
            "dataset": "mojahid",
            "seed": seed,
            "protocol": "grouped_fold_0_test_fold_1_val",
            **evaluate_split(features, labels, grouped_train_idx, grouped_test_idx, seed),
        }
    )
    return rows


def run_ressam(features: np.ndarray, labels: np.ndarray, env: np.ndarray, seed: int) -> list[dict[str, object]]:
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
                **evaluate_split(features, labels, idx[local_train], idx[local_test], seed),
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
                **evaluate_split(features, labels, train_idx, test_idx, seed),
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
        "# ResNet18 Embedding + LinearSVM Model Matrix 2026-08-10",
        "",
        "This is the fourth model family after HOG+RBF-SVM, LBP+LinearSVM and TinyCNN.",
        "",
        "## Model",
        "",
        f"- ResNet18 weight status: `{result['weights']['loaded']}`.",
        f"- Weight source: `{result['weights']['source']}`.",
        f"- Image size: {result['image_size']} x {result['image_size']} RGB.",
        "- Feature: frozen 512-dimensional ResNet18 penultimate embedding.",
        "- Classifier: `LinearSVC(C=1.0, class_weight='balanced')`.",
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
            "This run uses frozen image embeddings and a linear classifier. It tests whether split and environment effects persist under a generic convolutional representation, but it is not a fine-tuned GPR model.",
            "",
        ]
    )
    if result["weights"].get("note"):
        lines.extend(["## Weight Note", "", str(result["weights"]["note"]), ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mojahid-manifest", type=Path, required=True)
    parser.add_argument("--mojahid-data-root", type=Path, required=True)
    parser.add_argument("--ressam-manifest", type=Path, required=True)
    parser.add_argument("--ressam-data-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--image-size", type=int, default=128)
    parser.add_argument("--embedding-batch-size", type=int, default=32)
    parser.add_argument("--weights", choices=["auto", "imagenet", "none"], default="auto")
    parser.add_argument("--seeds", nargs="+", type=int, default=SEEDS)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    model, weight_status = load_model(args.weights)
    pretrained = weight_status["loaded"] == "imagenet_default"

    mojahid_rows = read_rows(args.mojahid_manifest)
    ressam_rows = read_rows(args.ressam_manifest)
    mojahid_features, mojahid_labels, mojahid_folds, _ = extract_embeddings(
        mojahid_rows,
        args.mojahid_data_root,
        model,
        args.image_size,
        args.embedding_batch_size,
        pretrained,
    )
    ressam_features, ressam_labels, _, ressam_env = extract_embeddings(
        ressam_rows,
        args.ressam_data_root,
        model,
        args.image_size,
        args.embedding_batch_size,
        pretrained,
    )

    metric_rows: list[dict[str, object]] = []
    for seed in args.seeds:
        metric_rows.extend(run_mojahid(mojahid_features, mojahid_labels, mojahid_folds, seed))
        metric_rows.extend(run_ressam(ressam_features, ressam_labels, ressam_env, seed))

    result = {
        "run_id": "20260810_E00_resnet18_embedding_svm_model_matrix",
        "model_family": "resnet18_embedding_linear_svm",
        "weights": weight_status,
        "seeds": args.seeds,
        "image_size": args.image_size,
        "embedding_dim": int(mojahid_features.shape[1]),
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
    write_csv(args.output_dir / "resnet18_embedding_svm_metrics.csv", metric_rows)
    (args.output_dir / "resnet18_embedding_svm_summary.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_md(args.output_dir / "resnet18_embedding_svm_summary.md", result)
    print(json.dumps(result["summary"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
