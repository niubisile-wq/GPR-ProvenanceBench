#!/usr/bin/env python3
"""Synthesize the first five-model Mojahid/Res-SAM matrix."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "five_model_synthesis_20260810"
MATERIAL_DELTA = 0.05


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def add_row(rows: list[dict[str, object]], model: str, dataset: str, contrast: str, delta: float) -> None:
    rows.append(
        {
            "model_family": model,
            "dataset": dataset,
            "contrast": contrast,
            "delta_mean": float(delta),
            "directional_support": bool(delta > 0.0),
            "material_support": bool(delta >= MATERIAL_DELTA),
        }
    )


def contrast_from_matrix(data: dict, dataset: str, contrast: str) -> float:
    for item in data["summary"]["contrasts"]:
        if item["dataset"] == dataset and item["contrast"] == contrast:
            return float(item["delta_mean"])
    raise KeyError(f"Missing contrast: {dataset} {contrast}")


def build_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []

    mojahid_hog = load_json(REPORTS / "mojahid_hog_rbf_svm_seed_sweep_20260810" / "seed_sweep_summary.json")
    add_row(
        rows,
        "hog_rbf_svm",
        "mojahid",
        "random_minus_grouped_balanced_accuracy",
        mojahid_hog["random_minus_grouped"]["balanced_accuracy"]["mean"],
    )

    ressam_hog = load_json(REPORTS / "ressam_environment_transfer_seed_sweep_20260810" / "seed_sweep_summary.json")
    add_row(
        rows,
        "hog_rbf_svm",
        "res_sam",
        "within_minus_transfer_synthetic_to_real_world",
        ressam_hog["within_minus_transfer"]["synthetic_to_real_world"]["balanced_accuracy"]["mean"],
    )
    add_row(
        rows,
        "hog_rbf_svm",
        "res_sam",
        "within_minus_transfer_real_world_to_synthetic",
        ressam_hog["within_minus_transfer"]["real_world_to_synthetic"]["balanced_accuracy"]["mean"],
    )

    matrix_sources = [
        (
            "lbp_linear_svm",
            REPORTS / "lbp_linear_svm_matrix_20260810" / "lbp_linear_svm_summary.json",
        ),
        (
            "tinycnn",
            REPORTS / "tinycnn_matrix_20260810" / "tinycnn_summary.json",
        ),
        (
            "resnet18_embedding_linear_svm",
            REPORTS / "resnet18_embedding_svm_matrix_20260810" / "resnet18_embedding_svm_summary.json",
        ),
        (
            "efficientnet_b0_embedding_linear_svm",
            REPORTS / "efficientnet_b0_embedding_svm_matrix_20260810" / "efficientnet_b0_embedding_svm_summary.json",
        ),
    ]
    for model, path in matrix_sources:
        data = load_json(path)
        add_row(
            rows,
            model,
            "mojahid",
            "random_minus_grouped_balanced_accuracy",
            contrast_from_matrix(data, "mojahid", "random_minus_grouped_balanced_accuracy"),
        )
        add_row(
            rows,
            model,
            "res_sam",
            "within_minus_transfer_synthetic_to_real_world",
            contrast_from_matrix(data, "res_sam", "within_minus_transfer_synthetic_to_real_world"),
        )
        add_row(
            rows,
            model,
            "res_sam",
            "within_minus_transfer_real_world_to_synthetic",
            contrast_from_matrix(data, "res_sam", "within_minus_transfer_real_world_to_synthetic"),
        )
    return rows


def summarize(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    keys = sorted({(str(row["dataset"]), str(row["contrast"])) for row in rows})
    summary = []
    for dataset, contrast in keys:
        subset = [row for row in rows if row["dataset"] == dataset and row["contrast"] == contrast]
        directional = sum(1 for row in subset if row["directional_support"])
        material = sum(1 for row in subset if row["material_support"])
        deltas = [float(row["delta_mean"]) for row in subset]
        claim_status = "supported" if material >= 3 else "directional_only" if directional >= 3 else "not_supported"
        summary.append(
            {
                "dataset": dataset,
                "contrast": contrast,
                "n_model_families": len(subset),
                "directional_support_count": directional,
                "material_support_count": material,
                "delta_mean_across_models": sum(deltas) / len(deltas),
                "delta_min": min(deltas),
                "delta_max": max(deltas),
                "claim_status": claim_status,
            }
        )
    return summary


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_md(path: Path, result: dict[str, object]) -> None:
    lines = [
        "# Five-Model Cross-Model Synthesis 2026-08-10",
        "",
        "Scope: Mojahid and Res-SAM only. This synthesis does not include a full 4TU five-model matrix or external blind validation.",
        "",
        f"Material-support threshold: delta_mean >= {MATERIAL_DELTA:.2f} balanced accuracy.",
        "",
        "## Claim-Level Summary",
        "",
        "| dataset | contrast | directional support | material support | mean delta | min delta | max delta | status |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in result["claim_summary"]:
        lines.append(
            f"| {item['dataset']} | {item['contrast']} | "
            f"{item['directional_support_count']}/{item['n_model_families']} | "
            f"{item['material_support_count']}/{item['n_model_families']} | "
            f"{item['delta_mean_across_models']:.4f} | {item['delta_min']:.4f} | "
            f"{item['delta_max']:.4f} | {item['claim_status']} |"
        )

    lines.extend(
        [
            "",
            "## Model-Level Evidence",
            "",
            "| model | dataset | contrast | delta_mean | directional | material |",
            "| --- | --- | --- | ---: | --- | --- |",
        ]
    )
    for row in result["model_rows"]:
        lines.append(
            f"| {row['model_family']} | {row['dataset']} | {row['contrast']} | "
            f"{row['delta_mean']:.4f} | {row['directional_support']} | {row['material_support']} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "1. Res-SAM environment transfer is the strongest current cross-model claim: both transfer directions reach material support in at least 4/5 model families.",
            "2. Mojahid random-minus-grouped inflation is directionally consistent across 5/5 model families, but only HOG+RBF-SVM reaches the 0.05 material threshold. This should be framed as a modest, model-dependent split effect rather than a strong universal inflation claim.",
            "3. TinyCNN weakens the synthetic-to-real Res-SAM direction and nearly removes the Mojahid gap, so the manuscript must explicitly report model-family dependence.",
            "",
            "## Boundary",
            "",
            "This synthesis closes the first five-model matrix for Mojahid and Res-SAM only. It does not close G0/G1 for Nature Communications because 4TU group-aware evidence remains weak, TIGPR is local NO-GO, and blind external validation is still absent.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    model_rows = build_rows()
    claim_summary = summarize(model_rows)
    result = {
        "run_id": "20260810_E00_five_model_cross_model_synthesis",
        "material_delta_threshold": MATERIAL_DELTA,
        "scope": "mojahid_and_res_sam_only",
        "model_rows": model_rows,
        "claim_summary": claim_summary,
    }
    write_csv(
        OUT_DIR / "five_model_synthesis_model_rows.csv",
        model_rows,
        ["model_family", "dataset", "contrast", "delta_mean", "directional_support", "material_support"],
    )
    write_csv(
        OUT_DIR / "five_model_synthesis_claim_summary.csv",
        claim_summary,
        [
            "dataset",
            "contrast",
            "n_model_families",
            "directional_support_count",
            "material_support_count",
            "delta_mean_across_models",
            "delta_min",
            "delta_max",
            "claim_status",
        ],
    )
    (OUT_DIR / "five_model_synthesis_summary.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_md(OUT_DIR / "five_model_synthesis_summary.md", result)
    print(json.dumps({"claim_summary": claim_summary}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
