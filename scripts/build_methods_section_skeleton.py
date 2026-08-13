#!/usr/bin/env python3
"""Build a Methods-section skeleton from frozen protocols and source packages."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "methods_section_skeleton_20260810"

RESULTS_MAP = REPORTS / "results_section_skeleton_20260810" / "results_paragraph_claim_evidence_map.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def build_methods_modules() -> list[dict[str, object]]:
    return [
        {
            "module_id": "M1",
            "module_title": "Executable asset boundary and unified sample manifests",
            "motivation": "Nominal dataset availability does not prove that an asset is executable, label-safe or suitable for confirmation.",
            "mechanism": "Local assets were represented using dated unified manifests. The current checkpoint counts local executable rows for Mojahid, 4TU, Res-SAM and TIGPR, and separates executable assets from supporting-only assets.",
            "inputs": "data_manifests/*_unified_samples_20260810.csv; reports/tigpr_local_asset_audit_20260810.json",
            "outputs": "reports/figure1_table1_sources_20260810/table1_asset_audit.csv",
            "role_in_results": "Supports R1, Figure 1 and Table 1.",
            "boundary": "This module defines asset status, not model performance.",
            "draft_cn": "我们首先用统一样本 manifest 固定本地可执行资产边界。该步骤不把名义上存在的数据集直接视为可用验证资产，而是按是否存在本地样本、可追踪路径、稳定样本行和可复现审计结果来判定当前可执行性。Mojahid、4TU 和 Res-SAM 被纳入当前本地可执行资产；TIGPR 因本地 sample index 为 0 且缺少完整五类图像根目录，被保留为 supporting-only。",
        },
        {
            "module_id": "M2",
            "module_title": "Split and environment-transfer task construction",
            "motivation": "Random splits can overestimate performance when images share source, augmentation or environment structure.",
            "mechanism": "Mojahid was evaluated under random stratified and grouped splits. Res-SAM was evaluated under within-environment and cross-environment transfer contrasts between real-world and synthetic subsets.",
            "inputs": "reports/mojahid_hog_rbf_svm_seed_sweep_20260810; reports/figure2_table2_sources_20260810",
            "outputs": "reports/figure2_table2_sources_20260810; reports/figure3_sources_20260810",
            "role_in_results": "Supports R2 and R3.",
            "boundary": "Current split/transfer evidence covers Mojahid and Res-SAM, not true blind external validation.",
            "draft_cn": "为区分常规性能估计和来源/环境敏感性，我们构造了两类任务。Mojahid 使用 random stratified split 与 grouped split 比较同一数据资产上的划分敏感性；Res-SAM 使用 real-world 与 synthetic 子集构造 within-environment 和 cross-environment transfer 对比，用于检验环境迁移时的性能落差。",
        },
        {
            "module_id": "M3",
            "module_title": "Five-model family matrix",
            "motivation": "A single model can exaggerate or hide provenance effects, so claims require model-family-level robustness.",
            "mechanism": "Five model families were run or synthesized for the current Mojahid/Res-SAM matrix: HOG+RBF-SVM, LBP+LinearSVM, TinyCNN, ResNet18 frozen embeddings+LinearSVM and EfficientNetB0 frozen embeddings+LinearSVM. Directional support and material support were computed using delta balanced accuracy, with 0.05 as the material-support threshold.",
            "inputs": "reports/five_model_synthesis_20260810/five_model_synthesis_model_rows.csv",
            "outputs": "reports/five_model_synthesis_20260810; reports/figure2_table2_sources_20260810",
            "role_in_results": "Supports main claim R2 and boundary claim R3.",
            "boundary": "The first five-model matrix excludes 4TU and real blind external validation.",
            "draft_cn": "为避免单一模型决定论文结论，我们将当前可执行的 Mojahid 和 Res-SAM 结果汇总到五模型家族矩阵中。模型家族包括 HOG+RBF-SVM、LBP+LinearSVM、TinyCNN、ResNet18 冻结特征+LinearSVM 和 EfficientNetB0 冻结特征+LinearSVM。每个 contrast 以 balanced accuracy delta 作为效应量，并以 0.05 作为 material support 阈值。",
        },
        {
            "module_id": "M4",
            "module_title": "4TU raw-trace counterfactual stress tests",
            "motivation": "Processed GPR images may encode rendering or export choices rather than only subsurface information.",
            "mechanism": "4TU raw traces were rendered into multiple representation layers and subjected to deterministic counterfactual variants. Fixed-split HOG seed sweeps, small-CNN seed sweeps, summary-feature and raw-pixel stress tests were audited together with project-level repeated splits.",
            "inputs": "reports/4tu_counterfactual_hog_seed_sweep_20260810; reports/4tu_counterfactual_hog_group_splits_20260810; reports/4tu_model_family_extension_audit_20260810",
            "outputs": "reports/figure4_sources_20260810",
            "role_in_results": "Supports R4.",
            "boundary": "This is stress-test and feasibility-boundary evidence, not final causal proof, main confirmation or blind validation.",
            "draft_cn": "为检验模型是否依赖 raw-trace 渲染或导出链路，我们在 4TU 上构造了确定性反事实变体。输入由 raw trace 渲染为 64x64 图像并提取 HOG 特征，随后比较 original、log_clip、zscore_clip、time_reverse 以及边带/边框相关变体。固定 split 五种子结果与 project-level repeated split 结果并列报告，以区分强 fixed-split 信号和更弱的 group-aware 证据。",
        },
        {
            "module_id": "M5",
            "module_title": "4TU target-level grouped feasibility audit",
            "motivation": "A counterfactual stress-test asset should not be promoted to main confirmation if target labels cannot support stable grouped holdouts.",
            "mechanism": "Each 4TU metadata target was audited for sample count, project count, label count, singleton labels, rare project support and feasible test2/val2 grouped splits.",
            "inputs": "reports/4tu_group_feasibility_20260810/4tu_group_feasibility_targets.csv",
            "outputs": "reports/figure5_figure6_sources_20260810/figure5_4tu_feasibility_source_data.csv",
            "role_in_results": "Supports R5.",
            "boundary": "This module is a feasibility gate, not a model-comparison result.",
            "draft_cn": "为避免把 4TU 的 stress-test 结果过度解释为主确认，我们对每个 metadata target 做了 grouped feasibility audit。审计指标包括样本数、项目数、标签数、singleton labels、rare project support，以及 test2/val2 项目级划分的可行组合数。该模块用于决定哪些 target 只能进入可行性或失败模式分析。",
        },
        {
            "module_id": "M6",
            "module_title": "Blind external validation protocol and locked evaluation template",
            "motivation": "External-looking held-out data are not equivalent to blind external validation if the asset has been used during model development or labels are visible before prediction freezing.",
            "mechanism": "A blind external protocol was defined with analyst-facing manifest templates, label-holdout templates, one-shot prediction submission, strict SHA validation and a locked evaluator to be run only after label unlock.",
            "inputs": "protocols/blind_external_validation_protocol_20260810.md; data_manifests/external_blind_*_template_20260810.csv",
            "outputs": "reports/external_blind_intake_20260810; reports/external_blind_locked_evaluation_20260810; reports/figure5_figure6_sources_20260810/figure6_external_gate_source_data.csv",
            "role_in_results": "Supports R6 as an open gate.",
            "boundary": "Protocol/template readiness does not constitute completed blind external validation.",
            "draft_cn": "为防止外部验证中的标签泄漏和重复提交，我们定义了独立的 blind external validation protocol。该协议包括 analyst-facing manifest、label-holdout 文件、一次性 prediction submission、strict SHA 校验，以及标签解锁后才能运行的 locked evaluator。当前这些文件只证明协议入口可执行；在真实外部资产到位前，不能将其写成已完成的 blind external validation。",
        },
        {
            "module_id": "M7",
            "module_title": "Reproducibility checks and dated checkpoints",
            "motivation": "A benchmark-style manuscript requires each main artifact to be regenerated by a single audit path rather than by manual file collection.",
            "mechanism": "The PowerShell runbook executes manifest validation, schema audits, asset readiness checks, source-package generation, Results/Methods skeleton generation and required-artifact checks.",
            "inputs": "scripts/run_m0_m2_checks.ps1",
            "outputs": "checkpoints/checkpoint_20260810.md; checkpoints/gate_status_20260810.md",
            "role_in_results": "Supports reproducibility and gate reporting across all Results modules.",
            "boundary": "Passing M0-M2 checks proves current artifacts regenerate; it does not close future G1-G6 scientific gates.",
            "draft_cn": "所有当前产物通过 dated checkpoint 和统一检查脚本维护。run_m0_m2_checks.ps1 负责执行 manifest validation、schema audit、TIGPR/4TU/external readiness 检查、主图源数据生成、Results/Methods skeleton 生成和必备文件存在性检查。该检查证明当前 M0-M2 产物可重新生成，但不代表后续 G1-G6 科学 gate 已经完成。",
        },
    ]


def write_markdown(path: Path, rows: list[dict[str, object]], results_rows: list[dict[str, str]]) -> None:
    lines = [
        "# Methods Section Skeleton 2026-08-10",
        "",
        "Purpose: map the current Results claims to auditable Methods modules without inventing unperformed work.",
        "",
        "One-sentence methods argument: the study uses dated asset manifests, split/transfer contrasts, a five-model matrix, 4TU raw-trace counterfactual stress tests, target-level feasibility gates and a blind external validation protocol to separate executable evidence from open confirmation gates.",
        "",
        "## Methods Module Map",
        "",
        "| module | title | role in results | boundary |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['module_id']} | {row['module_title']} | {row['role_in_results']} | {row['boundary']} |"
        )
    lines.extend(["", "## Module Details", ""])
    for row in rows:
        lines.extend(
            [
                f"### {row['module_id']}: {row['module_title']}",
                "",
                f"Motivation: {row['motivation']}",
                "",
                f"Mechanism: {row['mechanism']}",
                "",
                f"Inputs: `{row['inputs']}`",
                "",
                f"Outputs: `{row['outputs']}`",
                "",
                f"Role in Results: {row['role_in_results']}",
                "",
                f"Boundary: {row['boundary']}",
                "",
                row["draft_cn"],
                "",
            ]
        )
    lines.extend(
        [
            "## Results-to-Methods Traceability",
            "",
            "| results paragraph | claim status | figure/table | method modules |",
            "| --- | --- | --- | --- |",
        ]
    )
    trace = {
        "R1": "M1, M7",
        "R2": "M2, M3, M7",
        "R3": "M2, M3, M7",
        "R4": "M4, M7",
        "R5": "M5, M7",
        "R6": "M6, M7",
    }
    for row in results_rows:
        lines.append(
            f"| {row['paragraph_id']} | {row['claim_status']} | {row['figure_or_table']} | {trace[row['paragraph_id']]} |"
        )
    lines.extend(
        [
            "",
            "## Methods Guardrails",
            "",
            "1. Do not describe blind external evaluation as completed.",
            "2. Do not imply 4TU has a full five-model confirmation matrix.",
            "3. Do not describe TIGPR as locally executable until source media and the 7169-row sample index are restored.",
            "4. Specify split and transfer contrasts explicitly; avoid vague phrases such as randomly assigned or standard validation.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    modules = build_methods_modules()
    results_rows = read_csv(RESULTS_MAP)
    fields = [
        "module_id",
        "module_title",
        "motivation",
        "mechanism",
        "inputs",
        "outputs",
        "role_in_results",
        "boundary",
        "draft_cn",
    ]
    write_csv(OUT_DIR / "methods_module_map.csv", modules, fields)
    write_markdown(OUT_DIR / "methods_section_skeleton.md", modules, results_rows)
    result = {
        "run_id": "20260810_methods_section_skeleton",
        "modules": len(modules),
        "results_paragraphs_traced": len(results_rows),
        "boundary": "Methods skeleton only; no new experiment and no completed blind external validation.",
    }
    (OUT_DIR / "methods_section_skeleton.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
