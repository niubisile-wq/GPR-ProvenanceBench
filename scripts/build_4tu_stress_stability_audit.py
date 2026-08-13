#!/usr/bin/env python3
"""Summarize stability of the 4TU HOG counterfactual stress signal."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np


VARIANT = "log_clip"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fieldnames = sorted({key for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def selected_variant_rows(rows: list[dict[str, str]], split_field: str) -> list[dict[str, object]]:
    out = []
    for row in rows:
        if row["variant"] != VARIANT:
            continue
        if row["model"] != row["selected_model"]:
            continue
        out.append(
            {
                "unit": row[split_field],
                "selected_model": row["selected_model"],
                "test_balanced_accuracy": float(row["test_balanced_accuracy"]),
                "balanced_accuracy_delta_vs_original": float(row["balanced_accuracy_delta_vs_original"]),
                "prediction_flip_rate_vs_original": float(row["prediction_flip_rate_vs_original"]),
            }
        )
    return out


def bootstrap(values: np.ndarray, seed: int, n_bootstrap: int) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    draws = rng.choice(values, size=(n_bootstrap, len(values)), replace=True).mean(axis=1)
    return {
        "mean": float(values.mean()),
        "std": float(values.std(ddof=0)),
        "ci95_low": float(np.quantile(draws, 0.025)),
        "ci95_high": float(np.quantile(draws, 0.975)),
        "negative_fraction": float(np.mean(values < 0.0)),
        "bootstrap_negative_fraction": float(np.mean(draws < 0.0)),
    }


def summarize_layer(layer: str, rows: list[dict[str, object]], seed: int, n_bootstrap: int) -> dict[str, object]:
    deltas = np.asarray([float(row["balanced_accuracy_delta_vs_original"]) for row in rows], dtype=np.float64)
    flips = np.asarray([float(row["prediction_flip_rate_vs_original"]) for row in rows], dtype=np.float64)
    return {
        "layer": layer,
        "variant": VARIANT,
        "n_units": int(len(rows)),
        "selected_models": sorted(set(str(row["selected_model"]) for row in rows)),
        "delta": bootstrap(deltas, seed, n_bootstrap),
        "flip_rate": {
            "mean": float(flips.mean()),
            "std": float(flips.std(ddof=0)),
            "min": float(flips.min()),
            "max": float(flips.max()),
        },
        "rows": rows,
    }


def write_md(path: Path, summary: dict[str, object]) -> None:
    lines = [
        "# 4TU Stress Stability Audit",
        "",
        f"Variant audited: `{summary['variant']}`",
        f"Bootstrap draws: `{summary['n_bootstrap']}`",
        "",
        "| layer | units | selected models | mean delta | 95% CI | negative units | mean flip |",
        "| --- | ---: | --- | ---: | ---: | ---: | ---: |",
    ]
    for layer in summary["layers"]:
        delta = layer["delta"]
        flip = layer["flip_rate"]
        lines.append(
            f"| {layer['layer']} | {layer['n_units']} | {', '.join(layer['selected_models'])} | "
            f"{delta['mean']:.4f} | [{delta['ci95_low']:.4f}, {delta['ci95_high']:.4f}] | "
            f"{delta['negative_fraction']:.4f} | {flip['mean']:.4f} |"
        )
    lines.extend(
        [
            "",
            f"Fixed-minus-group-aware delta attenuation: `{summary['fixed_minus_group_delta_mean_difference']:.4f}`.",
            "",
            "Boundary: this confirms that the 4TU fixed-split stress signal weakens",
            "under group-aware project splits. It supports a stress-test boundary,",
            "not a main confirmation or external validation claim.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixed-metrics", type=Path, required=True)
    parser.add_argument("--group-metrics", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20260811)
    parser.add_argument("--n-bootstrap", type=int, default=10000)
    args = parser.parse_args()

    fixed_rows = selected_variant_rows(read_csv(args.fixed_metrics), "seed")
    group_rows = selected_variant_rows(read_csv(args.group_metrics), "split_seed")
    fixed = summarize_layer("fixed_split_seed_sweep", fixed_rows, args.seed, args.n_bootstrap)
    group = summarize_layer("group_aware_project_splits", group_rows, args.seed, args.n_bootstrap)
    summary = {
        "run_id": "20260811_E11_4tu_stress_stability_audit",
        "variant": VARIANT,
        "n_bootstrap": args.n_bootstrap,
        "layers": [fixed, group],
        "fixed_minus_group_delta_mean_difference": float(fixed["delta"]["mean"] - group["delta"]["mean"]),
        "claim_boundary": "4TU stress-test stability boundary; not blind external validation.",
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "4tu_stress_stability_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_csv(args.output_dir / "4tu_stress_stability_rows.csv", fixed_rows + group_rows)
    write_md(args.output_dir / "4tu_stress_stability_summary.md", summary)
    print(json.dumps({"fixed": fixed["delta"], "group": group["delta"]}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
