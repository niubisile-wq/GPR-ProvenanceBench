#!/usr/bin/env python3
"""Summarize Mojahid HOG + RBF-SVM seed sweep results."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


METRICS = ["accuracy", "balanced_accuracy", "macro_f1"]
SPLITS = ["random_stratified_80_20", "grouped_fold_0_test_fold_1_val"]


def load_results(result_dir: Path) -> list[dict]:
    paths = sorted(result_dir.glob("result_seed_*.json"))
    if not paths:
        raise FileNotFoundError(f"No result files found in {result_dir}")
    return [json.loads(path.read_text(encoding="utf-8")) for path in paths]


def summarize(results: list[dict]) -> dict:
    summary: dict[str, object] = {
        "n_runs": len(results),
        "seeds": [item["seed"] for item in results],
        "run_ids": [item["run_id"] for item in results],
        "splits": {},
        "random_minus_grouped": {},
    }

    split_summary: dict[str, dict] = {}
    for split in SPLITS:
        split_summary[split] = {}
        for metric in METRICS:
            values = np.asarray([item["evaluations"][split][metric] for item in results], dtype=np.float64)
            split_summary[split][metric] = {
                "mean": float(values.mean()),
                "std": float(values.std(ddof=1)) if len(values) > 1 else 0.0,
                "min": float(values.min()),
                "max": float(values.max()),
            }
    summary["splits"] = split_summary

    deltas: dict[str, dict] = {}
    for metric in METRICS:
        values = np.asarray(
            [
                item["evaluations"]["random_stratified_80_20"][metric]
                - item["evaluations"]["grouped_fold_0_test_fold_1_val"][metric]
                for item in results
            ],
            dtype=np.float64,
        )
        deltas[metric] = {
            "mean": float(values.mean()),
            "std": float(values.std(ddof=1)) if len(values) > 1 else 0.0,
            "min": float(values.min()),
            "max": float(values.max()),
        }
    summary["random_minus_grouped"] = deltas
    return summary


def write_md(path: Path, summary: dict) -> None:
    lines = [
        "# Mojahid HOG + RBF-SVM Seed Sweep 2026-08-10",
        "",
        f"Runs: {summary['n_runs']}",
        f"Seeds: {summary['seeds']}",
        "",
        "## Split Summary",
        "",
        "| split | metric | mean | std | min | max |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for split, metric_map in summary["splits"].items():
        for metric, stats in metric_map.items():
            lines.append(
                f"| {split} | {metric} | {stats['mean']:.4f} | {stats['std']:.4f} | "
                f"{stats['min']:.4f} | {stats['max']:.4f} |"
            )

    lines.extend(
        [
            "",
            "## Random Minus Grouped",
            "",
            "| metric | mean_delta | std | min | max |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for metric, stats in summary["random_minus_grouped"].items():
        lines.append(
            f"| {metric} | {stats['mean']:.4f} | {stats['std']:.4f} | "
            f"{stats['min']:.4f} | {stats['max']:.4f} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation Boundary",
            "",
            "This seed sweep is still a Mojahid-only smoke/stability result. It supports",
            "the split-sensitivity direction but cannot serve as final manuscript evidence",
            "until repeated across independent assets and frozen split protocols.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-dir", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()

    results = load_results(args.result_dir)
    summary = summarize(results)
    args.output_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_md(args.output_md, summary)
    print(json.dumps(summary["random_minus_grouped"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

