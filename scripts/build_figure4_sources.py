#!/usr/bin/env python3
"""Build frozen source data for Figure 4: 4TU counterfactual stress test."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "figure4_sources_20260810"

FIXED_SUMMARY = REPORTS / "4tu_counterfactual_hog_seed_sweep_20260810" / "hog_seed_sweep_summary.json"
GROUP_SUMMARY = REPORTS / "4tu_counterfactual_hog_group_splits_20260810" / "hog_group_split_summary.json"
EXTENSION_MATRIX = REPORTS / "4tu_model_family_extension_audit_20260810" / "4tu_model_family_extension_matrix.csv"
EXTENSION_DECISIONS = REPORTS / "4tu_model_family_extension_audit_20260810" / "4tu_evidence_layer_upgrade_decisions.csv"
EXTENSION_SUMMARY = REPORTS / "4tu_model_family_extension_audit_20260810" / "4tu_model_family_extension_audit_summary.json"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"

VARIANT_ORDER = [
    "log_clip",
    "zscore_clip",
    "time_reverse",
    "remove_top_band",
    "remove_bottom_band",
    "remove_border",
    "amplitude_jitter",
]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return str(path.relative_to(BENCH_ROOT)).replace("\\", "/")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def aggregate_rows(summary_rows: list[dict[str, object]], layer: str) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for variant in VARIANT_ORDER:
        candidates = [
            row for row in summary_rows
            if row.get("model") == "extra_trees"
            and row.get("variant") == variant
            and row.get("selected_count", row.get("n_splits", 0))
        ]
        if layer == "fixed_split_seed_sweep":
            candidates = [
                row for row in candidates
                if row.get("target_field") == "Land type"
            ]
        if not candidates:
            continue
        row = candidates[0]
        replicate_key = "selected_count" if layer == "fixed_split_seed_sweep" else "n_splits"
        delta_mean = float(row["balanced_accuracy_delta_mean"])
        flip_mean = float(row["prediction_flip_rate_mean"])
        out.append(
            {
                "panel": "Figure 4",
                "layer": layer,
                "target": "Land type",
                "feature": "HOG image features from 4TU raw traces",
                "model": "ExtraTrees",
                "variant": variant,
                "n_replicates": int(row[replicate_key]),
                "test_balanced_accuracy_mean": round(float(row["test_balanced_accuracy_mean"]), 4),
                "test_balanced_accuracy_std": round(float(row["test_balanced_accuracy_std"]), 4),
                "delta_balanced_accuracy_mean": round(delta_mean, 4),
                "delta_balanced_accuracy_std": round(float(row["balanced_accuracy_delta_std"]), 4),
                "prediction_flip_rate_mean": round(flip_mean, 4),
                "prediction_flip_rate_std": round(float(row["prediction_flip_rate_std"]), 4),
                "interpretation": interpretation(layer, variant, delta_mean, flip_mean),
            }
        )
    return out


def interpretation(layer: str, variant: str, delta_mean: float, flip_mean: float) -> str:
    if layer == "fixed_split_seed_sweep" and variant == "log_clip":
        return "Strong fixed-split sensitivity signal."
    if layer == "group_aware_repeated_split" and variant == "log_clip":
        return "Signal weakens under project-level repeated splits."
    if delta_mean < -0.05:
        return "Material drop under this stress variant."
    if flip_mean > 0.3:
        return "Prediction instability without a large BA drop."
    return "Limited or no BA drop."


def write_markdown(path: Path, rows: list[dict[str, object]]) -> None:
    fixed = [row for row in rows if row["layer"] == "fixed_split_seed_sweep"]
    grouped = [row for row in rows if row["layer"] == "group_aware_repeated_split"]
    lines = [
        "# Figure 4 Source Data 2026-08-10",
        "",
        "Purpose: freeze the 4TU HOG counterfactual stress-test source data before plotting.",
        "",
        "Main claim: fixed-split 4TU HOG counterfactuals show strong rendering sensitivity, but project-level repeated splits weaken the evidence.",
        "",
        "Boundary: Figure 4 is stress-test evidence. It is not final causal proof, not a full 4TU five-model matrix and not blind external validation.",
        "",
        "## Fixed-Split Seed Sweep",
        "",
        "| variant | n | BA mean | delta BA mean | flip mean | interpretation |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in fixed:
        lines.append(
            f"| {row['variant']} | {row['n_replicates']} | "
            f"{row['test_balanced_accuracy_mean']:.4f} | {row['delta_balanced_accuracy_mean']:.4f} | "
            f"{row['prediction_flip_rate_mean']:.4f} | {row['interpretation']} |"
        )
    lines.extend(
        [
            "",
            "## Group-Aware Repeated Split",
            "",
            "| variant | n | BA mean | delta BA mean | flip mean | interpretation |",
            "| --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for row in grouped:
        lines.append(
            f"| {row['variant']} | {row['n_replicates']} | "
            f"{row['test_balanced_accuracy_mean']:.4f} | {row['delta_balanced_accuracy_mean']:.4f} | "
            f"{row['prediction_flip_rate_mean']:.4f} | {row['interpretation']} |"
        )
    lines.extend(
        [
            "",
            "## Plotting Notes",
            "",
            "1. Show fixed-split and group-aware bars side by side for the same variants.",
            "2. Use delta balanced accuracy as the primary axis and flip rate as a secondary annotation, not a second y-axis.",
            "3. Highlight `log_clip` because it is the strongest fixed-split signal and the clearest weakened group-aware comparison.",
            "4. Avoid claiming robust 4TU confirmation; the group-aware layer is explicitly weaker.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def build_evidence_layer_rows(extension_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for row in extension_rows:
        out.append(
            {
                "panel": "Figure 4 boundary inset",
                "evidence_layer": row["evidence_layer"],
                "model_family": row["model_family"],
                "aggregate_rows": row["aggregate_rows"],
                "strongest_target": row["strongest_target"],
                "strongest_variant": row["strongest_variant"],
                "strongest_delta_mean": row["strongest_delta_mean"],
                "claim_use": row["claim_use"],
                "upgrade_to_main_confirmation": row["upgrade_to_main_confirmation"],
                "figure4_allowed_role": "stress-test boundary layer",
                "boundary_note": row["reason"],
            }
        )
    return out


def update_markdown_with_extension(path: Path, evidence_rows: list[dict[str, object]]) -> None:
    text = path.read_text(encoding="utf-8").rstrip()
    lines = [
        text,
        "",
        "## 4TU Evidence-Layer Extension Audit",
        "",
        "The updated Figure 4 source package also imports the 4TU model-family extension audit. These rows are boundary metadata for plotting or captioning, not a new main confirmation layer.",
        "",
        "| evidence layer | model family | aggregate rows | strongest target | strongest variant | strongest delta | allowed role |",
        "| --- | --- | ---: | --- | --- | ---: | --- |",
    ]
    for row in evidence_rows:
        lines.append(
            f"| {row['evidence_layer']} | {row['model_family']} | {row['aggregate_rows']} | "
            f"{row['strongest_target']} | {row['strongest_variant']} | {float(row['strongest_delta_mean']):.4f} | "
            f"{row['figure4_allowed_role']} |"
        )
    lines.extend(
        [
            "",
            "Caption boundary: 4TU can be described as a multi-layer counterfactual stress test, but not as a main five-model confirmation layer and not as blind external validation.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def update_desktop_plan(section: str) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    text = DESKTOP_PLAN.read_text(encoding="utf-8")
    marker = "### 18.70 Figure 4 source package extension 更新"
    if marker in text:
        start = text.index(marker)
        next_start = text.find("\n### ", start + len(marker))
        if next_start == -1:
            text = text[:start].rstrip()
            updated = text + "\n\n" + section.strip() + "\n"
        else:
            text_before = text[:start].rstrip()
            text_after = text[next_start:].lstrip("\n")
            updated = text_before + "\n\n" + section.strip() + "\n\n" + text_after
    else:
        updated = text.rstrip() + "\n\n" + section.strip() + "\n"
    DESKTOP_PLAN.write_text(updated, encoding="utf-8", newline="\n")
    return True


def main() -> int:
    fixed_summary = read_json(FIXED_SUMMARY)
    group_summary = read_json(GROUP_SUMMARY)
    extension_summary = read_json(EXTENSION_SUMMARY)
    extension_decisions = read_csv(EXTENSION_DECISIONS)
    source_rows = aggregate_rows(fixed_summary["aggregate"], "fixed_split_seed_sweep") + aggregate_rows(
        group_summary["aggregate"],
        "group_aware_repeated_split",
    )
    evidence_layer_rows = build_evidence_layer_rows(extension_decisions)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fields = [
        "panel",
        "layer",
        "target",
        "feature",
        "model",
        "variant",
        "n_replicates",
        "test_balanced_accuracy_mean",
        "test_balanced_accuracy_std",
        "delta_balanced_accuracy_mean",
        "delta_balanced_accuracy_std",
        "prediction_flip_rate_mean",
        "prediction_flip_rate_std",
        "interpretation",
    ]
    write_csv(OUT_DIR / "figure4_counterfactual_source_data.csv", source_rows, fields)
    write_csv(
        OUT_DIR / "figure4_evidence_layer_boundary.csv",
        evidence_layer_rows,
        [
            "panel",
            "evidence_layer",
            "model_family",
            "aggregate_rows",
            "strongest_target",
            "strongest_variant",
            "strongest_delta_mean",
            "claim_use",
            "upgrade_to_main_confirmation",
            "figure4_allowed_role",
            "boundary_note",
        ],
    )
    markdown_path = OUT_DIR / "figure4_source_summary.md"
    write_markdown(markdown_path, source_rows)
    update_markdown_with_extension(markdown_path, evidence_layer_rows)
    result = {
        "run_id": "20260810_figure4_sources",
        "source_rows": len(source_rows),
        "evidence_layer_boundary_rows": len(evidence_layer_rows),
        "fixed_aggregate_rows": len(fixed_summary["aggregate"]),
        "group_aggregate_rows": len(group_summary["aggregate"]),
        "extension_matrix_rows": extension_summary["matrix_rows"],
        "source_inputs": [
            rel(FIXED_SUMMARY),
            rel(GROUP_SUMMARY),
            rel(EXTENSION_MATRIX),
            rel(EXTENSION_DECISIONS),
            rel(EXTENSION_SUMMARY),
        ],
        "figure4_allowed_role": "multi-layer stress-test and feasibility-boundary evidence",
        "upgrade_to_main_confirmation": False,
        "external_validation_closed": False,
        "submission_ready": False,
        "boundary": "Source data only; stress-test evidence, not main five-model confirmation or external validation.",
    }
    desktop_section = f"""### 18.70 Figure 4 source package extension 更新

已更新 Figure 4 source package，把 18.69 的 4TU model-family extension audit 接入 Figure 4 源数据层。Figure 4 现在不仅保留原来的 HOG fixed-split / group-aware 14 行 counterfactual source data，还新增 evidence-layer boundary 文件，用于 caption 或 inset 中说明 4TU 的五层证据边界。

新增/更新目录：
`{OUT_DIR}`

新增/更新材料：
1. `figure4_counterfactual_source_data.csv`
2. `figure4_evidence_layer_boundary.csv`
3. `figure4_source_summary.md`
4. `figure4_source_summary.json`

当前结果：
1. source_rows = {len(source_rows)}
2. evidence_layer_boundary_rows = {len(evidence_layer_rows)}
3. extension_matrix_rows = {extension_summary['matrix_rows']}
4. upgrade_to_main_confirmation = false
5. external_validation_closed = false
6. submission_ready = false

边界：
1. Figure 4 可以写成 multi-layer 4TU stress-test / feasibility-boundary 图。
2. Figure 4 不能写成 4TU 主五模型确认。
3. Figure 4 不能写成 held-label blind external validation。
4. 这一步仍未渲染正式 figure。
"""
    result["desktop_plan_updated"] = update_desktop_plan(desktop_section)
    (OUT_DIR / "figure4_source_summary.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
