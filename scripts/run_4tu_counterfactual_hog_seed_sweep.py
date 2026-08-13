#!/usr/bin/env python3
"""Run a repeated-seed sweep for 4TU HOG counterfactual reliance."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from run_4tu_counterfactual_hog_image import evaluate_target, flatten_results
from run_4tu_counterfactual_reliance import read_csv


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    groups: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        groups[(str(row["target_field"]), str(row["model"]), str(row["variant"]))].append(row)

    summary = []
    for (target, model, variant), items in sorted(groups.items()):
        ba = np.asarray([float(item["test_balanced_accuracy"]) for item in items], dtype=np.float64)
        delta = np.asarray([float(item["balanced_accuracy_delta_vs_original"]) for item in items], dtype=np.float64)
        flip = np.asarray([float(item["prediction_flip_rate_vs_original"]) for item in items], dtype=np.float64)
        selected_count = sum(1 for item in items if item["model"] == item["selected_model"])
        summary.append(
            {
                "target_field": target,
                "model": model,
                "variant": variant,
                "n_seeds": len(items),
                "selected_count": selected_count,
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
    selected_rows = [
        row for row in result["aggregate"]
        if row["selected_count"] > 0 and row["variant"] != "original"
    ]
    non_dummy_rows = [
        row for row in result["aggregate"]
        if row["model"] != "dummy_majority" and row["variant"] != "original"
    ]
    selected_top = sorted(selected_rows, key=lambda row: (row["balanced_accuracy_delta_mean"], -row["prediction_flip_rate_mean"]))[:12]
    non_dummy_top = sorted(non_dummy_rows, key=lambda row: (row["balanced_accuracy_delta_mean"], -row["prediction_flip_rate_mean"]))[:12]

    lines = [
        "# 4TU HOG Counterfactual Reliance Seed Sweep 2026-08-10",
        "",
        f"Seeds: {', '.join(str(seed) for seed in result['seeds'])}",
        f"Image size: {result['image_size']}",
        f"Metric rows: {result['n_metric_rows']}",
        "",
        "## Largest Mean Drops For Seed-Selected Models",
        "",
        "| target | model | variant | selected_count | BA_mean | delta_mean | delta_std | flip_mean |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in selected_top:
        lines.append(
            f"| {row['target_field']} | {row['model']} | {row['variant']} | {row['selected_count']} | "
            f"{row['test_balanced_accuracy_mean']:.4f} | {row['balanced_accuracy_delta_mean']:.4f} | "
            f"{row['balanced_accuracy_delta_std']:.4f} | {row['prediction_flip_rate_mean']:.4f} |"
        )

    lines.extend(
        [
            "",
            "## Largest Mean Drops For Non-Dummy Models",
            "",
            "| target | model | variant | BA_mean | delta_mean | delta_std | flip_mean | all_delta_nonpositive |",
            "| --- | --- | --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for row in non_dummy_top:
        lines.append(
            f"| {row['target_field']} | {row['model']} | {row['variant']} | "
            f"{row['test_balanced_accuracy_mean']:.4f} | {row['balanced_accuracy_delta_mean']:.4f} | "
            f"{row['balanced_accuracy_delta_std']:.4f} | {row['prediction_flip_rate_mean']:.4f} | "
            f"{row['all_delta_nonpositive']} |"
        )

    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This sweep tests model-randomness stability for the HOG image-feature counterfactual result. The split itself is still fixed, so it does not replace future protocol-level split replication or external blind validation.",
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
    parser.add_argument("--targets", nargs="+", default=[
        "Land type",
        "Land cover",
        "Utility crossing",
        "Construction workers",
        "Land use",
        "Relative groundwater level",
    ])
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest_rows = read_csv(args.task_manifest)
    all_results = []
    flat_rows = []
    for seed in args.seeds:
        seed_results = [evaluate_target(manifest_rows, target, seed, args.image_size) for target in args.targets]
        seed_flat = flatten_results(seed_results)
        for row in seed_flat:
            row["seed"] = seed
        all_results.append({"seed": seed, "targets": seed_results})
        flat_rows.extend(seed_flat)

    aggregate = summarize(flat_rows)
    result = {
        "task_manifest": str(args.task_manifest),
        "seeds": args.seeds,
        "image_size": args.image_size,
        "feature": "hog",
        "n_metric_rows": len(flat_rows),
        "runs": all_results,
        "aggregate": aggregate,
        "flat_csv": "hog_seed_sweep_metrics.csv",
    }
    write_csv(args.output_dir / "hog_seed_sweep_metrics.csv", flat_rows)
    (args.output_dir / "hog_seed_sweep_summary.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_md(args.output_dir / "hog_seed_sweep_summary.md", result)
    print(json.dumps({"seeds": args.seeds, "metric_rows": len(flat_rows), "aggregate_rows": len(aggregate)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
