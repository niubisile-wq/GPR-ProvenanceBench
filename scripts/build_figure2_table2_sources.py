#!/usr/bin/env python3
"""Build frozen source data for Figure 2 and manuscript-ready Table 2."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
IN_DIR = BENCH_ROOT / "reports" / "five_model_synthesis_20260810"
OUT_DIR = BENCH_ROOT / "reports" / "figure2_table2_sources_20260810"

MODEL_ROWS = IN_DIR / "five_model_synthesis_model_rows.csv"
CLAIM_ROWS = IN_DIR / "five_model_synthesis_claim_summary.csv"

MODEL_LABELS = {
    "hog_rbf_svm": "HOG + RBF-SVM",
    "lbp_linear_svm": "LBP + LinearSVM",
    "tinycnn": "TinyCNN",
    "resnet18_embedding_linear_svm": "ResNet18 emb. + LinearSVM",
    "efficientnet_b0_embedding_linear_svm": "EfficientNetB0 emb. + LinearSVM",
}

CONTRAST_LABELS = {
    "random_minus_grouped_balanced_accuracy": "Mojahid: random - grouped",
    "within_minus_transfer_real_world_to_synthetic": "Res-SAM: within real - real->synthetic",
    "within_minus_transfer_synthetic_to_real_world": "Res-SAM: within synthetic - synthetic->real",
}

DATASET_LABELS = {
    "mojahid": "Mojahid",
    "res_sam": "Res-SAM",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def bool_text(value: str) -> str:
    return "yes" if value == "True" else "no"


def build_figure2_source(model_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in model_rows:
        delta = float(row["delta_mean"])
        rows.append(
            {
                "panel": "Figure 2",
                "dataset": row["dataset"],
                "dataset_label": DATASET_LABELS.get(row["dataset"], row["dataset"]),
                "contrast": row["contrast"],
                "contrast_label": CONTRAST_LABELS.get(row["contrast"], row["contrast"]),
                "model_family": row["model_family"],
                "model_label": MODEL_LABELS.get(row["model_family"], row["model_family"]),
                "delta_mean_balanced_accuracy": round(delta, 4),
                "directional_support": bool_text(row["directional_support"]),
                "material_support": bool_text(row["material_support"]),
                "material_threshold": 0.05,
                "recommended_encoding": (
                    "bar_positive_material"
                    if row["material_support"] == "True"
                    else "bar_positive_directional_only"
                    if row["directional_support"] == "True"
                    else "bar_negative_or_unsupported"
                ),
            }
        )
    return rows


def build_table2_rows(claim_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in claim_rows:
        rows.append(
            {
                "dataset": DATASET_LABELS.get(row["dataset"], row["dataset"]),
                "contrast": CONTRAST_LABELS.get(row["contrast"], row["contrast"]),
                "directional_support": f"{row['directional_support_count']}/{row['n_model_families']}",
                "material_support": f"{row['material_support_count']}/{row['n_model_families']}",
                "mean_delta_balanced_accuracy": f"{float(row['delta_mean_across_models']):.4f}",
                "delta_range_balanced_accuracy": f"{float(row['delta_min']):.4f} to {float(row['delta_max']):.4f}",
                "claim_status": row["claim_status"],
                "manuscript_interpretation": interpretation(row),
            }
        )
    return rows


def interpretation(row: dict[str, str]) -> str:
    dataset = row["dataset"]
    contrast = row["contrast"]
    status = row["claim_status"]
    if dataset == "res_sam" and status == "supported":
        if contrast == "within_minus_transfer_real_world_to_synthetic":
            return "Strong material support for real-to-synthetic environment-transfer fragility."
        return "Strong material support for synthetic-to-real environment-transfer fragility, with one model-family exception."
    if dataset == "mojahid":
        return "Directional but modest/model-dependent split effect; do not frame as a universal inflation result."
    return "Report with boundary."


def write_markdown(path: Path, figure_rows: list[dict[str, object]], table_rows: list[dict[str, object]]) -> None:
    lines = [
        "# Figure 2 and Table 2 Source Data 2026-08-10",
        "",
        "Purpose: freeze the source data for the current strongest manuscript claim before plotting.",
        "",
        "Main claim: Res-SAM environment-transfer fragility has stronger cross-model support than Mojahid random-minus-grouped split inflation.",
        "",
        "Boundary: this source package excludes 4TU and true blind external validation. It must not be used to claim completed external blind validation.",
        "",
        "## Figure 2 Source Data",
        "",
        "| contrast | model | delta BA | directional | material |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for row in figure_rows:
        lines.append(
            f"| {row['contrast_label']} | {row['model_label']} | "
            f"{row['delta_mean_balanced_accuracy']:.4f} | {row['directional_support']} | "
            f"{row['material_support']} |"
        )
    lines.extend(
        [
            "",
            "## Table 2 Manuscript Draft",
            "",
            "| dataset | contrast | directional support | material support | mean delta BA | delta range BA | status | interpretation |",
            "| --- | --- | ---: | ---: | ---: | --- | --- | --- |",
        ]
    )
    for row in table_rows:
        lines.append(
            f"| {row['dataset']} | {row['contrast']} | {row['directional_support']} | "
            f"{row['material_support']} | {row['mean_delta_balanced_accuracy']} | "
            f"{row['delta_range_balanced_accuracy']} | {row['claim_status']} | "
            f"{row['manuscript_interpretation']} |"
        )
    lines.extend(
        [
            "",
            "## Plotting Notes",
            "",
            "1. Lead panel: model-family delta balanced accuracy for the three contrasts.",
            "2. Use a clear material-support threshold line at 0.05 balanced accuracy.",
            "3. Encode unsupported or negative TinyCNN synthetic-to-real result distinctly.",
            "4. Keep Mojahid visually secondary to avoid overstating the split gap.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    model_rows = read_csv(MODEL_ROWS)
    claim_rows = read_csv(CLAIM_ROWS)
    figure_rows = build_figure2_source(model_rows)
    table_rows = build_table2_rows(claim_rows)

    write_csv(
        OUT_DIR / "figure2_source_data.csv",
        figure_rows,
        [
            "panel",
            "dataset",
            "dataset_label",
            "contrast",
            "contrast_label",
            "model_family",
            "model_label",
            "delta_mean_balanced_accuracy",
            "directional_support",
            "material_support",
            "material_threshold",
            "recommended_encoding",
        ],
    )
    write_csv(
        OUT_DIR / "table2_model_family_support.csv",
        table_rows,
        [
            "dataset",
            "contrast",
            "directional_support",
            "material_support",
            "mean_delta_balanced_accuracy",
            "delta_range_balanced_accuracy",
            "claim_status",
            "manuscript_interpretation",
        ],
    )
    write_markdown(OUT_DIR / "figure2_table2_source_summary.md", figure_rows, table_rows)
    result = {
        "run_id": "20260810_figure2_table2_sources",
        "figure2_rows": len(figure_rows),
        "table2_rows": len(table_rows),
        "source_inputs": [str(MODEL_ROWS), str(CLAIM_ROWS)],
        "boundary": "Source data only; no rendered figure yet and no blind external validation claim.",
    }
    (OUT_DIR / "figure2_table2_source_summary.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
