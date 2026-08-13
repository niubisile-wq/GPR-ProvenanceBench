#!/usr/bin/env python3
"""Summarize Res-SAM environment-transfer seed sweep results."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


METRICS = ["accuracy", "balanced_accuracy", "macro_f1"]


def load_results(result_dir: Path) -> list[dict]:
    paths = sorted(result_dir.glob("result_seed_*.json"))
    if not paths:
        raise FileNotFoundError(f"No result_seed_*.json files found in {result_dir}")
    return [json.loads(path.read_text(encoding="utf-8")) for path in paths]


def stats(values: list[float]) -> dict[str, float]:
    arr = np.asarray(values, dtype=np.float64)
    return {
        "mean": float(arr.mean()),
        "std": float(arr.std(ddof=1)) if len(arr) > 1 else 0.0,
        "min": float(arr.min()),
        "max": float(arr.max()),
    }


def summarize(results: list[dict]) -> dict:
    within_names = sorted(results[0]["within_environment"])
    transfer_names = [
        f"{item['train_environment']}_to_{item['test_environment']}"
        for item in results[0]["transfer"]
    ]

    summary: dict[str, object] = {
        "n_runs": len(results),
        "seeds": [item["seed"] for item in results],
        "within_environment": {},
        "transfer": {},
        "within_minus_transfer": {},
    }

    for name in within_names:
        summary["within_environment"][name] = {
            metric: stats([item["within_environment"][name]["metrics"][metric] for item in results])
            for metric in METRICS
        }

    for transfer_name in transfer_names:
        train_env, _, test_env = transfer_name.partition("_to_")
        summary["transfer"][transfer_name] = {
            metric: stats(
                [
                    next(
                        row
                        for row in item["transfer"]
                        if row["train_environment"] == train_env and row["test_environment"] == test_env
                    )["metrics"][metric]
                    for item in results
                ]
            )
            for metric in METRICS
        }

    # Compare each transfer direction against the within-environment test side.
    for transfer_name in transfer_names:
        train_env, _, test_env = transfer_name.partition("_to_")
        summary["within_minus_transfer"][transfer_name] = {
            metric: stats(
                [
                    item["within_environment"][test_env]["metrics"][metric]
                    - next(
                        row
                        for row in item["transfer"]
                        if row["train_environment"] == train_env and row["test_environment"] == test_env
                    )["metrics"][metric]
                    for item in results
                ]
            )
            for metric in METRICS
        }

    return summary


def write_md(path: Path, summary: dict) -> None:
    lines = [
        "# Res-SAM Environment-Transfer Seed Sweep 2026-08-10",
        "",
        f"Runs: {summary['n_runs']}",
        f"Seeds: {summary['seeds']}",
        "",
        "## Within-Environment Baselines",
        "",
        "| environment | metric | mean | std | min | max |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for environment, metric_map in summary["within_environment"].items():
        for metric, values in metric_map.items():
            lines.append(
                f"| {environment} | {metric} | {values['mean']:.4f} | {values['std']:.4f} | "
                f"{values['min']:.4f} | {values['max']:.4f} |"
            )

    lines.extend(
        [
            "",
            "## Cross-Environment Transfer",
            "",
            "| direction | metric | mean | std | min | max |",
            "| --- | --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for direction, metric_map in summary["transfer"].items():
        for metric, values in metric_map.items():
            lines.append(
                f"| {direction} | {metric} | {values['mean']:.4f} | {values['std']:.4f} | "
                f"{values['min']:.4f} | {values['max']:.4f} |"
            )

    lines.extend(
        [
            "",
            "## Within Minus Transfer",
            "",
            "For each transfer direction, the within-environment baseline on the test",
            "environment is subtracted by the corresponding transfer performance.",
            "",
            "| direction | metric | mean_delta | std | min | max |",
            "| --- | --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for direction, metric_map in summary["within_minus_transfer"].items():
        for metric, values in metric_map.items():
            lines.append(
                f"| {direction} | {metric} | {values['mean']:.4f} | {values['std']:.4f} | "
                f"{values['min']:.4f} | {values['max']:.4f} |"
            )

    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This is a lightweight HOG+RBF-SVM seed sweep on Res-SAM JPG exports.",
            "It supports environment-shift auditing but is not a reproduction of the",
            "full Res-SAM model.",
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
    print(json.dumps(summary["within_minus_transfer"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

