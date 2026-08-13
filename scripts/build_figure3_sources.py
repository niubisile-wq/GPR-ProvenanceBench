#!/usr/bin/env python3
"""Build frozen source data for Figure 3: Mojahid split inflation baseline."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "figure3_sources_20260810"

HOG_SUMMARY = REPORTS / "mojahid_hog_rbf_svm_seed_sweep_20260810" / "seed_sweep_summary.json"
FIVE_MODEL_ROWS = REPORTS / "five_model_synthesis_20260810" / "five_model_synthesis_model_rows.csv"
FIVE_MODEL_CLAIMS = REPORTS / "five_model_synthesis_20260810" / "five_model_synthesis_claim_summary.csv"

MODEL_LABELS = {
    "hog_rbf_svm": "HOG + RBF-SVM",
    "lbp_linear_svm": "LBP + LinearSVM",
    "tinycnn": "TinyCNN",
    "resnet18_embedding_linear_svm": "ResNet18 emb. + LinearSVM",
    "efficientnet_b0_embedding_linear_svm": "EfficientNetB0 emb. + LinearSVM",
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def build_hog_split_rows(summary: dict) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for split, metrics in summary["splits"].items():
        for metric_name in ["accuracy", "balanced_accuracy", "macro_f1"]:
            metric = metrics[metric_name]
            rows.append(
                {
                    "panel": "Figure 3A",
                    "dataset": "Mojahid",
                    "model": "HOG + RBF-SVM",
                    "split": split,
                    "metric": metric_name,
                    "mean": round(float(metric["mean"]), 4),
                    "std": round(float(metric["std"]), 4),
                    "min": round(float(metric["min"]), 4),
                    "max": round(float(metric["max"]), 4),
                    "n_runs": int(summary["n_runs"]),
                    "interpretation": "random split higher" if split == "random_stratified_80_20" else "grouped split lower",
                }
            )
    return rows


def build_model_delta_rows(model_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in model_rows:
        if row["dataset"] != "mojahid":
            continue
        delta = float(row["delta_mean"])
        rows.append(
            {
                "panel": "Figure 3B",
                "dataset": "Mojahid",
                "contrast": "random - grouped balanced accuracy",
                "model_family": row["model_family"],
                "model_label": MODEL_LABELS.get(row["model_family"], row["model_family"]),
                "delta_mean_balanced_accuracy": round(delta, 4),
                "directional_support": "yes" if row["directional_support"] == "True" else "no",
                "material_support": "yes" if row["material_support"] == "True" else "no",
                "material_threshold": 0.05,
                "interpretation": "material support" if row["material_support"] == "True" else "directional only",
            }
        )
    return rows


def build_claim_boundary(claim_rows: list[dict[str, str]]) -> dict[str, object]:
    claim = next(
        row for row in claim_rows
        if row["dataset"] == "mojahid" and row["contrast"] == "random_minus_grouped_balanced_accuracy"
    )
    return {
        "panel": "Figure 3C",
        "dataset": "Mojahid",
        "contrast": "random - grouped balanced accuracy",
        "directional_support": f"{claim['directional_support_count']}/{claim['n_model_families']}",
        "material_support": f"{claim['material_support_count']}/{claim['n_model_families']}",
        "mean_delta_balanced_accuracy": round(float(claim["delta_mean_across_models"]), 4),
        "delta_min": round(float(claim["delta_min"]), 4),
        "delta_max": round(float(claim["delta_max"]), 4),
        "claim_status": claim["claim_status"],
        "boundary": "Directional but modest/model-dependent split effect; do not frame as universal leakage.",
    }


def write_markdown(
    path: Path,
    hog_rows: list[dict[str, object]],
    model_rows: list[dict[str, object]],
    claim: dict[str, object],
) -> None:
    lines = [
        "# Figure 3 Source Data 2026-08-10",
        "",
        "Purpose: freeze the Mojahid split-inflation baseline source data before plotting.",
        "",
        "Main claim: Mojahid random-minus-grouped split inflation is directionally consistent across model families but modest and model-dependent.",
        "",
        "Boundary: Figure 3 is secondary support. It must not be framed as a universal leakage result because only 1/5 model families reaches material support.",
        "",
        "## HOG + RBF-SVM Seed-Sweep Split Metrics",
        "",
        "| split | metric | mean | std | min | max |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for row in hog_rows:
        lines.append(
            f"| {row['split']} | {row['metric']} | {row['mean']:.4f} | "
            f"{row['std']:.4f} | {row['min']:.4f} | {row['max']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Five-Model Mojahid Delta",
            "",
            "| model | delta BA | directional | material | interpretation |",
            "| --- | ---: | --- | --- | --- |",
        ]
    )
    for row in model_rows:
        lines.append(
            f"| {row['model_label']} | {row['delta_mean_balanced_accuracy']:.4f} | "
            f"{row['directional_support']} | {row['material_support']} | {row['interpretation']} |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            f"- directional support: {claim['directional_support']}",
            f"- material support: {claim['material_support']}",
            f"- mean delta BA: {claim['mean_delta_balanced_accuracy']:.4f}",
            f"- delta range BA: {claim['delta_min']:.4f} to {claim['delta_max']:.4f}",
            f"- claim status: {claim['claim_status']}",
            f"- boundary: {claim['boundary']}",
            "",
            "## Plotting Notes",
            "",
            "1. Show HOG random vs grouped as a concrete split-sensitivity example.",
            "2. Show five-model deltas to prevent overgeneralizing the HOG result.",
            "3. Visually mark the 0.05 material-support threshold.",
            "4. Keep Figure 3 secondary to Figure 2.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    hog = read_json(HOG_SUMMARY)
    model_rows = read_csv(FIVE_MODEL_ROWS)
    claim_rows = read_csv(FIVE_MODEL_CLAIMS)

    hog_rows = build_hog_split_rows(hog)
    delta_rows = build_model_delta_rows(model_rows)
    claim = build_claim_boundary(claim_rows)

    write_csv(
        OUT_DIR / "figure3_hog_split_source_data.csv",
        hog_rows,
        ["panel", "dataset", "model", "split", "metric", "mean", "std", "min", "max", "n_runs", "interpretation"],
    )
    write_csv(
        OUT_DIR / "figure3_model_delta_source_data.csv",
        delta_rows,
        [
            "panel",
            "dataset",
            "contrast",
            "model_family",
            "model_label",
            "delta_mean_balanced_accuracy",
            "directional_support",
            "material_support",
            "material_threshold",
            "interpretation",
        ],
    )
    write_csv(
        OUT_DIR / "figure3_claim_boundary.csv",
        [claim],
        [
            "panel",
            "dataset",
            "contrast",
            "directional_support",
            "material_support",
            "mean_delta_balanced_accuracy",
            "delta_min",
            "delta_max",
            "claim_status",
            "boundary",
        ],
    )
    write_markdown(OUT_DIR / "figure3_source_summary.md", hog_rows, delta_rows, claim)
    result = {
        "run_id": "20260810_figure3_sources",
        "hog_split_rows": len(hog_rows),
        "model_delta_rows": len(delta_rows),
        "claim_status": claim["claim_status"],
        "boundary": claim["boundary"],
    }
    (OUT_DIR / "figure3_source_summary.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
