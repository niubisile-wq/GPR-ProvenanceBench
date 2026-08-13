#!/usr/bin/env python3
"""Synthesize the five model families explicitly frozen in the 18-month plan."""

from __future__ import annotations

import json

from synthesize_five_model_matrix import (
    MATERIAL_DELTA,
    REPORTS,
    add_row,
    contrast_from_matrix,
    load_json,
    summarize,
    write_csv,
)


OUT_DIR = REPORTS / "planned_five_model_synthesis_20260811"


def build_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []

    mojahid_hog = load_json(REPORTS / "mojahid_hog_rbf_svm_seed_sweep_20260810" / "seed_sweep_summary.json")
    add_row(
        rows, "hog_rbf_svm", "mojahid", "random_minus_grouped_balanced_accuracy",
        mojahid_hog["random_minus_grouped"]["balanced_accuracy"]["mean"],
    )
    ressam_hog = load_json(REPORTS / "ressam_environment_transfer_seed_sweep_20260810" / "seed_sweep_summary.json")
    add_row(
        rows, "hog_rbf_svm", "res_sam", "within_minus_transfer_synthetic_to_real_world",
        ressam_hog["within_minus_transfer"]["synthetic_to_real_world"]["balanced_accuracy"]["mean"],
    )
    add_row(
        rows, "hog_rbf_svm", "res_sam", "within_minus_transfer_real_world_to_synthetic",
        ressam_hog["within_minus_transfer"]["real_world_to_synthetic"]["balanced_accuracy"]["mean"],
    )

    matrix_sources = [
        ("lightweight_cnn", REPORTS / "tinycnn_matrix_20260810" / "tinycnn_summary.json"),
        ("resnet18_embedding_linear_svm", REPORTS / "resnet18_embedding_svm_matrix_20260810" / "resnet18_embedding_svm_summary.json"),
        ("efficientnet_b0_embedding_linear_svm", REPORTS / "efficientnet_b0_embedding_svm_matrix_20260810" / "efficientnet_b0_embedding_svm_summary.json"),
        ("deit_tiny_embedding_linear_svm", REPORTS / "deit_tiny_embedding_svm_matrix_20260811" / "deit_tiny_embedding_svm_summary.json"),
    ]
    for model, path in matrix_sources:
        data = load_json(path)
        for dataset, contrast in [
            ("mojahid", "random_minus_grouped_balanced_accuracy"),
            ("res_sam", "within_minus_transfer_synthetic_to_real_world"),
            ("res_sam", "within_minus_transfer_real_world_to_synthetic"),
        ]:
            add_row(rows, model, dataset, contrast, contrast_from_matrix(data, dataset, contrast))
    return rows


def write_md(result: dict[str, object]) -> None:
    lines = [
        "# Planned Five-Model Cross-Model Synthesis 2026-08-11",
        "",
        "This matrix uses the five families explicitly named in the frozen plan: HOG+RBF-SVM, lightweight CNN, ResNet18, EfficientNetB0 and DeiT-Tiny.",
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
    lines.extend([
        "", "## Model-Level Evidence", "",
        "| model | dataset | contrast | delta_mean | directional | material |",
        "| --- | --- | --- | ---: | --- | --- |",
    ])
    for row in result["model_rows"]:
        lines.append(
            f"| {row['model_family']} | {row['dataset']} | {row['contrast']} | "
            f"{row['delta_mean']:.4f} | {row['directional_support']} | {row['material_support']} |"
        )
    lines.extend([
        "", "## Boundary", "",
        "The architecture slot is now complete for the planned Mojahid/Res-SAM directional matrix. ResNet18, EfficientNetB0 and DeiT-Tiny use frozen ImageNet embeddings rather than end-to-end fine-tuning. This matrix does not include a real blind external asset and does not establish external repair benefit.",
        "",
    ])
    (OUT_DIR / "planned_five_model_synthesis_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    model_rows = build_rows()
    claim_summary = summarize(model_rows)
    result = {
        "run_id": "20260811_E38_planned_five_model_cross_model_synthesis",
        "material_delta_threshold": MATERIAL_DELTA,
        "scope": "planned_five_families_mojahid_and_res_sam",
        "planned_model_families": [
            "hog_rbf_svm", "lightweight_cnn", "resnet18_embedding_linear_svm",
            "efficientnet_b0_embedding_linear_svm", "deit_tiny_embedding_linear_svm",
        ],
        "model_rows": model_rows,
        "claim_summary": claim_summary,
        "blind_external_eligible": False,
    }
    write_csv(
        OUT_DIR / "planned_five_model_synthesis_model_rows.csv", model_rows,
        ["model_family", "dataset", "contrast", "delta_mean", "directional_support", "material_support"],
    )
    write_csv(
        OUT_DIR / "planned_five_model_synthesis_claim_summary.csv", claim_summary,
        ["dataset", "contrast", "n_model_families", "directional_support_count",
         "material_support_count", "delta_mean_across_models", "delta_min", "delta_max", "claim_status"],
    )
    (OUT_DIR / "planned_five_model_synthesis_summary.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    write_md(result)
    print(json.dumps({"claim_summary": claim_summary}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
