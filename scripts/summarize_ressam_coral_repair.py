#!/usr/bin/env python3
"""Summarize Res-SAM CORAL mitigation seed runs."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np


METRICS = ["accuracy", "balanced_accuracy", "macro_f1"]
METHODS = [
    "baseline_source_only",
    "mean_std_unlabeled_target",
    "coral_unlabeled_target",
    "delta_mean_std_minus_baseline",
    "delta_coral_minus_baseline",
]


def summarize(values: list[float]) -> dict[str, float]:
    arr = np.asarray(values, dtype=np.float64)
    return {
        "mean": float(arr.mean()),
        "std": float(arr.std(ddof=0)),
        "min": float(arr.min()),
        "max": float(arr.max()),
    }


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_md(path: Path, summary: dict) -> None:
    lines = [
        "# Res-SAM Alignment Mitigation Seed Sweep",
        "",
        f"Runs: `{summary['n_runs']}`",
        f"Seeds: `{', '.join(str(seed) for seed in summary['seeds'])}`",
        "",
        "## Balanced Accuracy",
        "",
        "| transfer | baseline mean | mean/std mean | CORAL mean | mean/std delta | CORAL delta |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for direction, item in summary["transfer"].items():
        lines.append(
            f"| {direction} | "
            f"{item['baseline_source_only']['balanced_accuracy']['mean']:.4f} | "
            f"{item['mean_std_unlabeled_target']['balanced_accuracy']['mean']:.4f} | "
            f"{item['coral_unlabeled_target']['balanced_accuracy']['mean']:.4f} | "
            f"{item['delta_mean_std_minus_baseline']['balanced_accuracy']['mean']:+.4f} | "
            f"{item['delta_coral_minus_baseline']['balanced_accuracy']['mean']:+.4f} | "
        )

    lines.extend(
        [
            "",
            "## Macro-F1",
            "",
            "| transfer | baseline mean | mean/std mean | CORAL mean | mean/std delta | CORAL delta |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for direction, item in summary["transfer"].items():
        lines.append(
            f"| {direction} | "
            f"{item['baseline_source_only']['macro_f1']['mean']:.4f} | "
            f"{item['mean_std_unlabeled_target']['macro_f1']['mean']:.4f} | "
            f"{item['coral_unlabeled_target']['macro_f1']['mean']:.4f} | "
            f"{item['delta_mean_std_minus_baseline']['macro_f1']['mean']:+.4f} | "
            f"{item['delta_coral_minus_baseline']['macro_f1']['mean']:+.4f} | "
        )

    lines.extend(
        [
            "",
            "## Interpretation Boundary",
            "",
            "This run tests whether a simple unsupervised covariance alignment can reduce",
            "Res-SAM environment-transfer fragility on published image exports. It is",
            "internal repair evidence only. It does not satisfy the blind external",
            "validation or external-repair gate because the target images are available",
            "during alignment and no one-shot locked external submission is involved.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-dir", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path, required=True)
    args = parser.parse_args()

    files = sorted(args.result_dir.glob("result_seed_*.json"))
    if not files:
        raise FileNotFoundError(f"No result_seed_*.json files in {args.result_dir}")

    values: dict[str, dict[str, dict[str, list[float]]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(list))
    )
    rows: list[dict[str, object]] = []
    seeds: list[int] = []

    for path in files:
        result = json.loads(path.read_text(encoding="utf-8"))
        seeds.append(int(result["seed"]))
        for item in result["transfer"]:
            direction = f"{item['train_environment']}_to_{item['test_environment']}"
            for method in METHODS:
                if method not in item:
                    continue
                for metric in METRICS:
                    value = float(item[method][metric])
                    values[direction][method][metric].append(value)
                    rows.append(
                        {
                            "seed": result["seed"],
                            "direction": direction,
                            "method": method,
                            "metric": metric,
                            "value": value,
                        }
                    )

    summary = {
        "run_id": "20260811_E01_ressam_coral_repair_seed_sweep",
        "n_runs": len(files),
        "seeds": sorted(seeds),
        "transfer": {
            direction: {
                method: {
                    metric: summarize(metric_values)
                    for metric, metric_values in method_values.items()
                }
                for method, method_values in direction_values.items()
            }
            for direction, direction_values in values.items()
        },
        "claim_boundary": "Internal transductive mitigation; not blind external repair evidence.",
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_csv(args.output_csv, rows)
    write_md(args.output_md, summary)
    print(json.dumps(summary["transfer"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
