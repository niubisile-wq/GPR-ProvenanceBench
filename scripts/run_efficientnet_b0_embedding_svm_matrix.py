#!/usr/bin/env python3
"""Run frozen EfficientNetB0 embeddings + LinearSVM as the fifth model family."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import torch
import torchvision.models as models

from run_resnet18_embedding_svm_matrix import (
    SEEDS,
    extract_embeddings,
    read_rows,
    run_mojahid,
    run_ressam,
    summarize,
    write_csv,
)


def load_model(weights_mode: str) -> tuple[torch.nn.Module, dict[str, str]]:
    status = {
        "requested": weights_mode,
        "loaded": "none",
        "source": "torchvision.models.efficientnet_b0(weights=None)",
        "note": "",
    }
    weights = None
    if weights_mode in {"auto", "imagenet"}:
        try:
            weights = models.EfficientNet_B0_Weights.DEFAULT
            status["loaded"] = "imagenet_default"
            status["source"] = weights.url
        except Exception as exc:  # pragma: no cover - defensive only
            if weights_mode == "imagenet":
                raise
            status["note"] = f"failed_to_resolve_default_weights: {exc}"
            weights = None
    try:
        model = models.efficientnet_b0(weights=weights)
    except Exception as exc:
        if weights_mode == "imagenet":
            raise
        status["loaded"] = "none"
        status["source"] = "torchvision.models.efficientnet_b0(weights=None)"
        status["note"] = f"failed_to_load_imagenet_weights_then_fell_back_to_none: {exc}"
        model = models.efficientnet_b0(weights=None)
    model.classifier = torch.nn.Identity()
    model.eval()
    torch.set_num_threads(max(1, min(4, torch.get_num_threads())))
    return model, status


def write_md(path: Path, result: dict[str, object]) -> None:
    lines = [
        "# EfficientNetB0 Embedding + LinearSVM Model Matrix 2026-08-10",
        "",
        "This is the fifth model family after HOG+RBF-SVM, LBP+LinearSVM, TinyCNN and ResNet18 embeddings.",
        "",
        "## Model",
        "",
        f"- EfficientNetB0 weight status: `{result['weights']['loaded']}`.",
        f"- Weight source: `{result['weights']['source']}`.",
        f"- Image size: {result['image_size']} x {result['image_size']} RGB.",
        f"- Feature: frozen {result['embedding_dim']}-dimensional EfficientNetB0 embedding.",
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
            "This run uses frozen EfficientNetB0 image embeddings and a linear classifier. It completes the first five-model matrix, but it remains a feature-transfer baseline rather than a fine-tuned GPR model.",
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
        "run_id": "20260810_E00_efficientnet_b0_embedding_svm_model_matrix",
        "model_family": "efficientnet_b0_embedding_linear_svm",
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
    write_csv(args.output_dir / "efficientnet_b0_embedding_svm_metrics.csv", metric_rows)
    (args.output_dir / "efficientnet_b0_embedding_svm_summary.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_md(args.output_dir / "efficientnet_b0_embedding_svm_summary.md", result)
    print(json.dumps(result["summary"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
