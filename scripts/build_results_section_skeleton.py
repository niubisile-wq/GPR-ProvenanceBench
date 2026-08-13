#!/usr/bin/env python3
"""Build a Results-section skeleton from frozen figure/table source packages."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "results_section_skeleton_20260810"

TABLE1 = REPORTS / "figure1_table1_sources_20260810" / "table1_asset_audit.csv"
TABLE2 = REPORTS / "figure2_table2_sources_20260810" / "table2_model_family_support.csv"
FIGURE3_BOUNDARY = REPORTS / "figure3_sources_20260810" / "figure3_claim_boundary.csv"
FIGURE4 = REPORTS / "figure4_sources_20260810" / "figure4_counterfactual_source_data.csv"
FIGURE4_BOUNDARY = REPORTS / "figure4_sources_20260810" / "figure4_evidence_layer_boundary.csv"
FIGURE5 = REPORTS / "figure5_figure6_sources_20260810" / "figure5_4tu_feasibility_source_data.csv"
FIGURE6 = REPORTS / "figure5_figure6_sources_20260810" / "figure6_external_gate_source_data.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def find(rows: list[dict[str, str]], **kwargs: str) -> dict[str, str]:
    for row in rows:
        if all(row.get(key) == value for key, value in kwargs.items()):
            return row
    raise KeyError(kwargs)


def build_paragraph_map() -> list[dict[str, object]]:
    table1 = read_csv(TABLE1)
    table2 = read_csv(TABLE2)
    fig3 = read_csv(FIGURE3_BOUNDARY)[0]
    fig4 = read_csv(FIGURE4)
    fig4_boundary = read_csv(FIGURE4_BOUNDARY)
    fig5 = read_csv(FIGURE5)
    fig6 = read_csv(FIGURE6)

    asset_counts = ", ".join(
        f"{row['asset']}={row['local_executable_rows']}" for row in table1
    )
    res_real_syn = find(table2, contrast="Res-SAM: within real - real->synthetic")
    res_syn_real = find(table2, contrast="Res-SAM: within synthetic - synthetic->real")
    mojahid = find(table2, dataset="Mojahid")
    fixed_log = find(fig4, layer="fixed_split_seed_sweep", variant="log_clip")
    group_log = find(fig4, layer="group_aware_repeated_split", variant="log_clip")
    fig4_layers = len(fig4_boundary)
    land_type = find(fig5, target="Land type")
    no_go = find(fig6, gate_component="External validation readiness gate")

    return [
        {
            "paragraph_id": "R1",
            "section_role": "system/workflow validation",
            "topic_sentence": "We first froze the executable evidence boundary rather than treating all nominal datasets as equivalent validation assets.",
            "evidence": f"Table 1 local executable rows: {asset_counts}. TIGPR local rows are 0 and remain supporting-only.",
            "figure_or_table": "Figure 1; Table 1",
            "claim_status": "supported_for_checkpoint",
            "boundary": "This establishes asset/protocol status, not model performance.",
            "draft_cn": "我们首先冻结当前可执行证据边界，而不是把所有名义数据集都等同为可用验证资产。按本地 unified manifest 口径，Mojahid、4TU 和 Res-SAM 分别提供 2524、99 和 1050 个可执行样本；TIGPR 当前本地可执行样本数为 0，因此只能作为 supporting evidence，不能进入当前核心模型矩阵或外部盲评结论。",
        },
        {
            "paragraph_id": "R2",
            "section_role": "main result",
            "topic_sentence": "Across five model families, Res-SAM environment transfer produced the strongest and most reproducible performance drop.",
            "evidence": (
                f"real-to-synthetic: directional={res_real_syn['directional_support']}, "
                f"material={res_real_syn['material_support']}, mean_delta={res_real_syn['mean_delta_balanced_accuracy']}; "
                f"synthetic-to-real: directional={res_syn_real['directional_support']}, "
                f"material={res_syn_real['material_support']}, mean_delta={res_syn_real['mean_delta_balanced_accuracy']}."
            ),
            "figure_or_table": "Figure 2; Table 2",
            "claim_status": "supported_current_main",
            "boundary": "Scope is Mojahid and Res-SAM only; not blind external validation.",
            "draft_cn": "在五类模型家族中，Res-SAM 的环境迁移落差构成当前最强且最一致的主结果。real-to-synthetic 方向达到 5/5 directional support 和 5/5 material support，平均 balanced accuracy delta 为 0.4239；synthetic-to-real 方向达到 4/5 directional support 和 4/5 material support，平均 delta 为 0.3743。这说明当前最稳健的信号不是单一模型现象，而是跨模型家族可重复的环境迁移脆弱性。",
        },
        {
            "paragraph_id": "R3",
            "section_role": "baseline comparison",
            "topic_sentence": "Mojahid random-minus-grouped inflation was directionally consistent but too modest to serve as the lead claim.",
            "evidence": (
                f"directional={fig3['directional_support']}, material={fig3['material_support']}, "
                f"mean_delta={fig3['mean_delta_balanced_accuracy']}; Table 2 status={mojahid['claim_status']}."
            ),
            "figure_or_table": "Figure 3; Table 2",
            "claim_status": "directional_only",
            "boundary": "Do not frame as universal leakage; only 1/5 model families reaches material support.",
            "draft_cn": "Mojahid 的 random-minus-grouped 差异支持同一方向，但证据强度不足以作为主结论。HOG+RBF-SVM 五种子实验中，random split balanced accuracy mean 为 0.9543，grouped split 为 0.8566，delta 为 0.0976；但在五模型综合层面，该差异虽为 5/5 directional support，却只有 1/5 material support，平均 delta 仅为 0.0406。因此 Mojahid 应作为 split-sensitivity 的次级支撑，而不是 universal leakage 的主证据。",
        },
        {
            "paragraph_id": "R4",
            "section_role": "stress test / failure mode",
            "topic_sentence": "4TU multi-layer counterfactual stress tests defined a feasibility-boundary layer rather than a main confirmation result.",
            "evidence": (
                f"fixed log_clip delta={fixed_log['delta_balanced_accuracy_mean']}, flip={fixed_log['prediction_flip_rate_mean']}; "
                f"group log_clip delta={group_log['delta_balanced_accuracy_mean']}, flip={group_log['prediction_flip_rate_mean']}; "
                f"evidence boundary layers={fig4_layers}."
            ),
            "figure_or_table": "Figure 4",
            "claim_status": "stress_test_supported",
            "boundary": "Stress-test and feasibility-boundary evidence only; not final causal proof, main 4TU confirmation or blind external validation.",
            "draft_cn": "4TU 的多层 counterfactual stress-test 结果表明，该资产目前应被定位为 feasibility-boundary 层，而不是主确认结果。Land type ExtraTrees 在 fixed-split seed sweep 中，log_clip 后 BA_mean 为 0.0905，delta_mean 为 -0.3429，flip_mean 为 0.8583；而在 group-aware repeated split 中，同一方向 delta_mean 降至 -0.0422，flip_mean 为 0.4693。进一步的五层扩展审计把 summary-feature、raw-pixel、HOG、small-CNN 和 group-aware HOG 证据统一限定为 stress-test 或 feasibility-boundary evidence。因此 4TU 不能写成 causal proof、blind external validation 或主确认层。",
        },
        {
            "paragraph_id": "R5",
            "section_role": "failure-mode gate",
            "topic_sentence": "A target-level feasibility audit explained why 4TU should not yet be expanded into the main cross-model confirmation matrix.",
            "evidence": (
                f"Land type status={land_type['status']}, feasible_fraction={land_type['test2_val2_feasible_fraction']}; "
                "Land use and Construction workers are not viable; Land cover and groundwater are weak."
            ),
            "figure_or_table": "Figure 5",
            "claim_status": "gate_supported",
            "boundary": "Feasibility/gate result, not model superiority.",
            "draft_cn": "4TU 的 target-level feasibility audit 解释了为什么当前不应强行扩展 4TU 五模型主确认矩阵。Land type 虽为 usable_with_caution，test2/val2 feasible fraction 为 0.9365，但 Land use 和 Construction workers 不适合 grouped holdout，Land cover 和 Relative groundwater level 受 single-project label 限制。因此，4TU 的合理定位是 counterfactual 和 stress-test，而不是当前主确认矩阵。",
        },
        {
            "paragraph_id": "R6",
            "section_role": "external validation boundary",
            "topic_sentence": "The blind external validation gate remains open despite having protocol templates and dry-run evaluators.",
            "evidence": f"External gate status={no_go['status']}; boundary={no_go['blocking_or_boundary']}",
            "figure_or_table": "Figure 6",
            "claim_status": "not_yet_supported",
            "boundary": "No completed blind external validation; protocol readiness is not a positive result.",
            "draft_cn": "尽管项目已经具备 blind intake 模板、prediction submission 模板和 locked-evaluation dry run，真实 blind external validation 仍未完成。当前 external validation readiness gate 为 NO-GO；TIGPR restoration、第三方 blind GPR set 和 4TU-like raw-trace external asset 均未 ready，Res-SAM 也已进入当前模型矩阵，不能再作为独立盲评资产。因此，所有关于外部盲评的表述必须写成 open gate，而不是正结果。",
        },
    ]


def write_markdown(path: Path, rows: list[dict[str, object]]) -> None:
    lines = [
        "# Results Section Skeleton 2026-08-10",
        "",
        "Purpose: convert frozen figure/table source data into a Results-section paragraph map without inventing new claims.",
        "",
        "One-sentence argument: current evidence indicates that GPR recognition performance is sensitive to source and environment transfer, led by Res-SAM cross-environment fragility, with Mojahid and 4TU providing secondary split/stress-test support and blind external validation still open.",
        "",
        "## Results Paragraph Map",
        "",
        "| paragraph | role | figure/table | claim status | topic sentence | boundary |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['paragraph_id']} | {row['section_role']} | {row['figure_or_table']} | "
            f"{row['claim_status']} | {row['topic_sentence']} | {row['boundary']} |"
        )
    lines.extend(["", "## Chinese Draft Paragraphs", ""])
    for row in rows:
        lines.extend(
            [
                f"### {row['paragraph_id']}: {row['section_role']}",
                "",
                row["draft_cn"],
                "",
                f"Evidence: {row['evidence']}",
                "",
                f"Boundary: {row['boundary']}",
                "",
            ]
        )
    lines.extend(["## Claim-Evidence Map", ""])
    for row in rows:
        lines.append(
            f"- Claim: {row['topic_sentence']} | Evidence: {row['evidence']} | Status: {row['claim_status']} | Boundary: {row['boundary']}"
        )
    lines.extend(
        [
            "",
            "## Manuscript Guardrails",
            "",
            "1. Do not claim completed blind external validation.",
            "2. Do not lead with Mojahid split inflation because it is directional_only at five-model level.",
            "3. Do not present 4TU as main confirmation; keep it as stress-test/failure-mode evidence.",
            "4. Lead Results with Res-SAM environment-transfer fragility.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = build_paragraph_map()
    fields = [
        "paragraph_id",
        "section_role",
        "topic_sentence",
        "evidence",
        "figure_or_table",
        "claim_status",
        "boundary",
        "draft_cn",
    ]
    write_csv(OUT_DIR / "results_paragraph_claim_evidence_map.csv", rows, fields)
    write_markdown(OUT_DIR / "results_section_skeleton.md", rows)
    result = {
        "run_id": "20260810_results_section_skeleton",
        "paragraphs": len(rows),
        "lead_claim": "Res-SAM environment-transfer fragility",
        "boundary": "Results skeleton only; no new experiment and no completed blind external validation.",
    }
    (OUT_DIR / "results_section_skeleton.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
