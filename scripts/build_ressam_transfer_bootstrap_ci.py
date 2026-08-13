#!/usr/bin/env python3
"""Bootstrap Res-SAM cross-model transfer delta confidence intervals."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np


CONTRASTS = [
    "within_minus_transfer_synthetic_to_real_world",
    "within_minus_transfer_real_world_to_synthetic",
]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def bootstrap_mean(values: np.ndarray, seed: int, n_bootstrap: int) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    draws = rng.choice(values, size=(n_bootstrap, len(values)), replace=True).mean(axis=1)
    return {
        "mean": float(values.mean()),
        "std": float(values.std(ddof=0)),
        "ci95_low": float(np.quantile(draws, 0.025)),
        "ci95_high": float(np.quantile(draws, 0.975)),
        "bootstrap_positive_fraction": float(np.mean(draws > 0.0)),
        "bootstrap_material_fraction_ge_0.05": float(np.mean(draws >= 0.05)),
    }


def write_md(path: Path, summary: dict) -> None:
    lines = [
        "# Res-SAM Transfer Delta Bootstrap CI",
        "",
        f"Bootstrap draws per contrast: `{summary['n_bootstrap']}`",
        "Bootstrap unit: model family delta rows from the five-model synthesis.",
        "",
        "| contrast | models | mean delta | 95% CI | positive fraction | material fraction >=0.05 |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in summary["contrast_rows"]:
        lines.append(
            f"| {row['contrast']} | {row['n_model_families']} | {row['mean']:.4f} | "
            f"[{row['ci95_low']:.4f}, {row['ci95_high']:.4f}] | "
            f"{row['bootstrap_positive_fraction']:.4f} | {row['bootstrap_material_fraction_ge_0.05']:.4f} |"
        )
    lines.extend(
        [
            "",
            "Boundary: this is a cross-model-family uncertainty check over the",
            "current five local model-family deltas. It is not a sample-level",
            "external validation interval.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--five-model-summary", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20260811)
    parser.add_argument("--n-bootstrap", type=int, default=10000)
    args = parser.parse_args()

    source = read_json(args.five_model_summary)
    rows: list[dict[str, object]] = []
    for contrast in CONTRASTS:
        contrast_rows = [
            row
            for row in source["model_rows"]
            if row["dataset"] == "res_sam" and row["contrast"] == contrast
        ]
        values = np.asarray([float(row["delta_mean"]) for row in contrast_rows], dtype=np.float64)
        item = {
            "contrast": contrast,
            "n_model_families": int(len(values)),
            "model_families": [row["model_family"] for row in contrast_rows],
            "delta_values": values.tolist(),
            **bootstrap_mean(values, args.seed, args.n_bootstrap),
        }
        rows.append(item)

    summary = {
        "run_id": "20260811_E08_ressam_transfer_delta_bootstrap_ci",
        "source_summary": str(args.five_model_summary),
        "seed": args.seed,
        "n_bootstrap": args.n_bootstrap,
        "contrast_rows": rows,
        "claim_boundary": "Cross-model-family uncertainty check; not blind external validation.",
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "ressam_transfer_bootstrap_ci_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_csv(args.output_dir / "ressam_transfer_bootstrap_ci_rows.csv", rows)
    write_md(args.output_dir / "ressam_transfer_bootstrap_ci_summary.md", summary)
    print(json.dumps(rows, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
