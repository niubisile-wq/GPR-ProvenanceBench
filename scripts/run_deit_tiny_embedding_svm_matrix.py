#!/usr/bin/env python3
"""Run frozen DeiT-Tiny embeddings + LinearSVM for the planned model matrix."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

import timm
import torch

from run_resnet18_embedding_svm_matrix import (
    SEEDS,
    extract_embeddings,
    read_rows,
    run_mojahid,
    run_ressam,
    summarize,
)


MODEL_NAME = "deit_tiny_patch16_224.fb_in1k"


def load_model(weights_mode: str) -> tuple[torch.nn.Module, dict[str, str]]:
    status = {
        "requested": weights_mode,
        "loaded": "none",
        "source": f"timm:{MODEL_NAME}:pretrained=False",
        "note": "",
    }
    pretrained = weights_mode in {"auto", "imagenet"}
    try:
        model = timm.create_model(MODEL_NAME, pretrained=pretrained, num_classes=0)
        if pretrained:
            status["loaded"] = "imagenet_default"
            status["source"] = f"timm:{MODEL_NAME}:pretrained=True"
    except Exception as exc:
        if weights_mode == "imagenet":
            raise
        status["note"] = f"failed_to_load_imagenet_weights_then_fell_back_to_none: {exc}"
        model = timm.create_model(MODEL_NAME, pretrained=False, num_classes=0)
    model.eval()
    torch.set_num_threads(max(1, min(4, torch.get_num_threads())))
    return model, status


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
        "# DeiT-Tiny Embedding + LinearSVM Model Matrix 2026-08-11",
        "",
        "This adds the DeiT-Tiny family explicitly named in the frozen 18-month plan.",
        "",
        "## Model",
        "",
        f"- Architecture: `{MODEL_NAME}`.",
        f"- Weight status: `{result['weights']['loaded']}`.",
        f"- Weight source: `{result['weights']['source']}`.",
        f"- Image size: {result['image_size']} x {result['image_size']} RGB.",
        f"- Feature: frozen {result['embedding_dim']}-dimensional DeiT-Tiny embedding.",
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
            "This is a frozen ImageNet representation plus a train-fold classifier. It closes the missing DeiT-Tiny architecture slot for directional split/transfer evidence, but it is not end-to-end GPR fine-tuning or blind external validation.",
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
    parser.add_argument("--image-size", type=int, default=224)
    parser.add_argument("--embedding-batch-size", type=int, default=16)
    parser.add_argument("--weights", choices=["auto", "imagenet", "none"], default="auto")
    parser.add_argument("--seeds", nargs="+", type=int, default=SEEDS)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    model, weight_status = load_model(args.weights)
    pretrained = weight_status["loaded"] == "imagenet_default"

    mojahid_rows = read_rows(args.mojahid_manifest)
    ressam_rows = read_rows(args.ressam_manifest)
    mojahid_features, mojahid_labels, mojahid_folds, _ = extract_embeddings(
        mojahid_rows, args.mojahid_data_root, model, args.image_size,
        args.embedding_batch_size, pretrained,
    )
    ressam_features, ressam_labels, _, ressam_env = extract_embeddings(
        ressam_rows, args.ressam_data_root, model, args.image_size,
        args.embedding_batch_size, pretrained,
    )

    metric_rows: list[dict[str, object]] = []
    for seed in args.seeds:
        metric_rows.extend(run_mojahid(mojahid_features, mojahid_labels, mojahid_folds, seed))
        metric_rows.extend(run_ressam(ressam_features, ressam_labels, ressam_env, seed))

    result = {
        "run_id": "20260811_E37_deit_tiny_embedding_svm_model_matrix",
        "model_family": "deit_tiny_embedding_linear_svm",
        "architecture": MODEL_NAME,
        "weights": weight_status,
        "seeds": args.seeds,
        "image_size": args.image_size,
        "embedding_dim": int(mojahid_features.shape[1]),
        "sample_counts": {"mojahid": len(mojahid_rows), "res_sam": len(ressam_rows)},
        "label_counts": {
            "mojahid": {str(k): int(v) for k, v in Counter(mojahid_labels).items()},
            "res_sam": {str(k): int(v) for k, v in Counter(ressam_labels).items()},
        },
        "summary": summarize(metric_rows),
        "blind_external_eligible": False,
    }
    write_csv(args.output_dir / "deit_tiny_embedding_svm_metrics.csv", metric_rows)
    (args.output_dir / "deit_tiny_embedding_svm_summary.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    write_md(args.output_dir / "deit_tiny_embedding_svm_summary.md", result)
    print(json.dumps(result["summary"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
