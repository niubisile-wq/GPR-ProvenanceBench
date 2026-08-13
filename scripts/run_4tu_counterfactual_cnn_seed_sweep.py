#!/usr/bin/env python3
"""Run a repeated-seed sweep for 4TU small-CNN counterfactual reliance."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from run_4tu_counterfactual_cnn import evaluate_target, flatten_results
from run_4tu_counterfactual_reliance import read_csv


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    groups: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        groups[(str(row["target_field"]), str(row["variant"]))].append(row)

    summary = []
    for (target, variant), items in sorted(groups.items()):
        ba = np.asarray([float(item["test_balanced_accuracy"]) for item in items], dtype=np.float64)
        delta = np.asarray([float(item["balanced_accuracy_delta_vs_original"]) for item in items], dtype=np.float64)
        flip = np.asarray([float(item["prediction_flip_rate_vs_original"]) for item in items], dtype=np.float64)
        val_ba = np.asarray([float(item["val_balanced_accuracy"]) for item in items], dtype=np.float64)
        summary.append(
            {
                "target_field": target,
                "model": "small_cnn",
                "variant": variant,
                "n_seeds": len(items),
                "val_balanced_accuracy_mean": float(val_ba.mean()),
                "val_balanced_accuracy_std": float(val_ba.std(ddof=0)),
                "test_balanced_accuracy_mean": float(ba.mean()),
                "test_balanced_accuracy_std": float(ba.std(ddof=0)),
                "balanced_accuracy_delta_mean": float(delta.mean()),
                "balanced_accuracy_delta_std": float(delta.std(ddof=0)),
                "prediction_flip_rate_mean": float(flip.mean()),
                "prediction_flip_rate_std": float(flip.std(ddof=0)),
                "all_delta_nonpositive": bool(np.all(delta <= 1e-12)),
            }
        )
    return summary


def write_md(path: Path, result: dict) -> None:
    variant_rows = [row for row in result["aggregate"] if row["variant"] != "original"]
    top = sorted(variant_rows, key=lambda row: (row["balanced_accuracy_delta_mean"], -row["prediction_flip_rate_mean"]))
    original = next(row for row in result["aggregate"] if row["variant"] == "original")
    lines = [
        "# 4TU Small-CNN Counterfactual Reliance Seed Sweep 2026-08-10",
        "",
        f"Target(s): {', '.join(result['targets'])}",
        f"Seeds: {', '.join(str(seed) for seed in result['seeds'])}",
        f"Image size: {result['image_size']}",
        f"Epochs per seed: {result['epochs']}",
        f"Metric rows: {result['n_metric_rows']}",
        "",
        "## Original Baseline",
        "",
        "| target | model | BA_mean | BA_std | val_BA_mean |",
        "| --- | --- | ---: | ---: | ---: |",
        f"| {original['target_field']} | small_cnn | {original['test_balanced_accuracy_mean']:.4f} | {original['test_balanced_accuracy_std']:.4f} | {original['val_balanced_accuracy_mean']:.4f} |",
        "",
        "## Counterfactual Drops",
        "",
        "| target | variant | BA_mean | delta_mean | delta_std | flip_mean | all_delta_nonpositive |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in top:
        lines.append(
            f"| {row['target_field']} | {row['variant']} | {row['test_balanced_accuracy_mean']:.4f} | "
            f"{row['balanced_accuracy_delta_mean']:.4f} | {row['balanced_accuracy_delta_std']:.4f} | "
            f"{row['prediction_flip_rate_mean']:.4f} | {row['all_delta_nonpositive']} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This sweep tests CNN model-randomness stability for the key Land type counterfactual result. It remains fixed-split and CPU-scale, so it does not replace split/package replication or a tuned deep-learning benchmark.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--seeds", nargs="+", type=int, default=[20260810, 20260811, 20260812, 20260813, 20260814])
    parser.add_argument("--image-size", type=int, default=64)
    parser.add_argument("--epochs", type=int, default=40)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--targets", nargs="+", default=["Land type"])
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest_rows = read_csv(args.task_manifest)
    all_results = []
    flat_rows = []
    for seed in args.seeds:
        seed_args = argparse.Namespace(
            image_size=args.image_size,
            epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate,
            seed=seed,
        )
        seed_results = [evaluate_target(manifest_rows, target, seed_args) for target in args.targets]
        seed_flat = flatten_results(seed_results)
        all_results.append({"seed": seed, "targets": seed_results})
        flat_rows.extend(seed_flat)

    aggregate = summarize(flat_rows)
    result = {
        "task_manifest": str(args.task_manifest),
        "seeds": args.seeds,
        "targets": args.targets,
        "image_size": args.image_size,
        "epochs": args.epochs,
        "feature": "cnn_pixels",
        "n_metric_rows": len(flat_rows),
        "runs": all_results,
        "aggregate": aggregate,
        "flat_csv": "cnn_seed_sweep_metrics.csv",
    }
    write_csv(args.output_dir / "cnn_seed_sweep_metrics.csv", flat_rows)
    (args.output_dir / "cnn_seed_sweep_summary.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_md(args.output_dir / "cnn_seed_sweep_summary.md", result)
    print(json.dumps({"seeds": args.seeds, "targets": args.targets, "metric_rows": len(flat_rows)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
