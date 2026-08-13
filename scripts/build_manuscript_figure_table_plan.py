#!/usr/bin/env python3
"""Build the manuscript figure/table blueprint from frozen report artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "manuscript_figure_table_plan_20260810"

FIVE_MODEL_JSON = REPORTS / "five_model_synthesis_20260810" / "five_model_synthesis_summary.json"
FOUR_TU_GROUP_JSON = REPORTS / "4tu_group_feasibility_20260810" / "4tu_group_feasibility_summary.json"
EXTERNAL_READY_JSON = REPORTS / "external_validation_readiness_20260810" / "external_validation_readiness_summary.json"
BLIND_EVAL_JSON = REPORTS / "external_blind_locked_evaluation_20260810" / "external_blind_locked_evaluation_summary.json"


def read_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def claim_line(claim: dict) -> str:
    dataset = claim["dataset"]
    contrast = claim["contrast"]
    directional = f"{claim['directional_support_count']}/{claim['n_model_families']}"
    material = f"{claim['material_support_count']}/{claim['n_model_families']}"
    delta = claim["delta_mean_across_models"]
    status = claim["claim_status"]
    return (
        f"{dataset} {contrast}: directional={directional}, "
        f"material={material}, mean_delta={delta:.4f}, status={status}"
    )


def build_items() -> list[dict[str, str]]:
    five_model = read_json(FIVE_MODEL_JSON)
    four_tu = read_json(FOUR_TU_GROUP_JSON)
    external = read_json(EXTERNAL_READY_JSON)
    blind_eval = read_json(BLIND_EVAL_JSON)

    claims = {item["contrast"]: item for item in five_model["claim_summary"]}
    res_sam_r2s = claims["within_minus_transfer_real_world_to_synthetic"]
    res_sam_s2r = claims["within_minus_transfer_synthetic_to_real_world"]
    mojahid = claims["random_minus_grouped_balanced_accuracy"]

    four_tu_targets = four_tu["targets"]
    four_tu_status = "; ".join(
        f"{item['target']}={item['status']}" for item in four_tu_targets
    )
    external_tracks = "; ".join(
        f"{track['track_id']}={track['current_status']}" for track in external["tracks"]
    )

    return [
        {
            "item_id": "Figure 1",
            "role": "Study design and evidence gates",
            "claim": "The project separates executable local evidence from unresolved confirmation gates.",
            "evidence": (
                "Asset inventory, unified manifests, TIGPR local NO-GO, Res-SAM local manifest, "
                "4TU metadata/groupholdout feasibility, external validation readiness gate."
            ),
            "source_artifacts": (
                "data_manifests/*_unified_samples_20260810.csv; "
                "reports/tigpr_local_asset_audit_20260810.md; "
                "reports/external_validation_readiness_20260810/external_validation_readiness_summary.md"
            ),
            "status": "ready_for_schematic",
            "boundary": "This figure is a protocol/asset map, not a performance result.",
            "next_action": "Draw workflow schematic after finalizing visual style.",
        },
        {
            "item_id": "Figure 2",
            "role": "Five-model cross-model result matrix",
            "claim": "Res-SAM environment transfer is the strongest current cross-model signal.",
            "evidence": (
                f"{claim_line(res_sam_r2s)}; {claim_line(res_sam_s2r)}; "
                f"{claim_line(mojahid)}."
            ),
            "source_artifacts": (
                "reports/five_model_synthesis_20260810/five_model_synthesis_summary.md; "
                "reports/five_model_synthesis_20260810/five_model_synthesis_model_rows.csv"
            ),
            "status": "ready_for_plot",
            "boundary": "Scope is Mojahid and Res-SAM only; 4TU and blind external assets are not included in this matrix.",
            "next_action": "Plot model-family deltas and claim-level support counts.",
        },
        {
            "item_id": "Figure 3",
            "role": "Mojahid split inflation baseline",
            "claim": "Mojahid random-minus-grouped performance inflation is directionally consistent but modest/model-dependent.",
            "evidence": claim_line(mojahid),
            "source_artifacts": (
                "reports/mojahid_hog_rbf_svm_seed_sweep_20260810/seed_sweep_summary.md; "
                "reports/five_model_synthesis_20260810/five_model_synthesis_claim_summary.csv"
            ),
            "status": "ready_with_caution",
            "boundary": "Do not frame as a universal leakage effect; only 1/5 model families reaches material support.",
            "next_action": "Use as secondary panel or combine with Figure 2 rather than lead result.",
        },
        {
            "item_id": "Figure 4",
            "role": "4TU raw-trace counterfactual stress test",
            "claim": "4TU multi-layer counterfactual stress-test evidence remains a feasibility-boundary layer rather than main confirmation.",
            "evidence": (
                "HOG fixed-split Land type ExtraTrees log_clip BA_mean=0.0905, "
                "delta_mean=-0.3429, flip_mean=0.8583; group-aware selected ExtraTrees "
                "appears in 2/5 splits with log_clip delta_mean=-0.0422; the five-layer "
                "4TU extension audit keeps all 4TU evidence as stress-test/feasibility-boundary evidence."
            ),
            "source_artifacts": (
                "reports/4tu_counterfactual_hog_seed_sweep_20260810/hog_seed_sweep_summary.md; "
                "reports/4tu_counterfactual_hog_group_splits_20260810/hog_group_split_summary.md; "
                "reports/4tu_model_family_extension_audit_20260810/4tu_model_family_extension_audit.md"
            ),
            "status": "ready_with_caution",
            "boundary": "This is stress-test and feasibility-boundary evidence, not final causal proof, main confirmation or blind external validation.",
            "next_action": "Plot fixed-split versus group-aware sensitivity side by side and add a five-layer evidence-boundary inset.",
        },
        {
            "item_id": "Figure 5",
            "role": "4TU feasibility and failure-mode map",
            "claim": "Current 4TU labels are insufficient for the main cross-model confirmation layer.",
            "evidence": four_tu_status,
            "source_artifacts": (
                "reports/4tu_group_feasibility_20260810/4tu_group_feasibility_summary.md; "
                "reports/4tu_group_feasibility_20260810/4tu_group_feasibility_targets.csv"
            ),
            "status": "ready_for_table_or_supplement",
            "boundary": "This is a gate/failure-mode result; it supports study design decisions, not model superiority.",
            "next_action": "Consider moving to Extended Data if main text is too crowded.",
        },
        {
            "item_id": "Figure 6",
            "role": "External blind validation gate",
            "claim": "Blind external validation remains unavailable under the frozen protocol.",
            "evidence": (
                f"External readiness gate={external['gate']['status']}; tracks: {external_tracks}; "
                f"locked evaluation mode={blind_eval['evaluation_mode']} with status={blind_eval['status']}."
            ),
            "source_artifacts": (
                "reports/external_validation_readiness_20260810/external_validation_readiness_summary.md; "
                "reports/external_blind_locked_evaluation_20260810/external_blind_locked_evaluation_summary.md"
            ),
            "status": "gate_open_not_result",
            "boundary": "The locked evaluation is template dry-run only; no manuscript claim can call it real blind external validation.",
            "next_action": "Replace with real external result only after strict-sha manifest, frozen prediction and label unlock.",
        },
        {
            "item_id": "Table 1",
            "role": "Dataset and asset audit",
            "claim": "Only Mojahid, 4TU and Res-SAM are executable local assets at this checkpoint; TIGPR is supporting-only.",
            "evidence": "Mojahid=2524 rows; 4TU=99 rows; Res-SAM=1050 rows; TIGPR=0 local executable rows.",
            "source_artifacts": "data_manifests/*_unified_samples_20260810.csv; reports/tigpr_local_asset_audit_20260810.md",
            "status": "ready_for_table",
            "boundary": "Counts are local executable rows, not global dataset sizes.",
            "next_action": "Render as dataset audit table.",
        },
        {
            "item_id": "Table 2",
            "role": "Model-family support summary",
            "claim": "Cross-model material support is strong for Res-SAM transfer and weak for Mojahid split inflation.",
            "evidence": "; ".join(claim_line(item) for item in five_model["claim_summary"]),
            "source_artifacts": "reports/five_model_synthesis_20260810/five_model_synthesis_claim_summary.csv",
            "status": "ready_for_table",
            "boundary": "Summary excludes 4TU and true blind external validation.",
            "next_action": "Use as main or extended table depending on Figure 2 density.",
        },
        {
            "item_id": "Table 3",
            "role": "Gate status and remaining requirements",
            "claim": "The Nature Communications route remains conditional rather than submission-ready.",
            "evidence": "External validation NO-GO; TIGPR NO-GO; 4TU not main confirmation; blind intake/evaluation template-ready only.",
            "source_artifacts": "checkpoints/gate_status_20260810.md; checkpoints/checkpoint_20260810.md",
            "status": "ready_for_internal_decision_table",
            "boundary": "May be internal planning material unless the manuscript is framed as a benchmark/resource paper.",
            "next_action": "Keep in checkpoint; decide later whether it becomes supplement.",
        },
    ]


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fields = ["item_id", "role", "claim", "evidence", "source_artifacts", "status", "boundary", "next_action"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_md(path: Path, rows: list[dict[str, str]]) -> None:
    lines = [
        "# Manuscript Figure/Table Plan 2026-08-10",
        "",
        "Purpose: freeze the current claim-evidence-boundary map before making figures.",
        "",
        "One-sentence argument: current evidence shows that GPR recognition performance is strongly affected by data source and environment transfer, with the strongest reproducible signal in Res-SAM cross-environment transfer; Mojahid and 4TU provide supporting or stress-test evidence, while blind external validation remains open.",
        "",
        "## Main Figure Logic",
        "",
        "1. Establish what assets are executable and what gates remain open.",
        "2. Lead with the strongest cross-model result rather than the most convenient dataset.",
        "3. Keep 4TU counterfactuals as stress-test evidence unless stronger grouped validation is added.",
        "4. Report external blind validation as an open gate until a real asset passes the frozen protocol.",
        "",
        "## Figure and Table Blueprint",
        "",
        "| item | role | status | claim | boundary |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['item_id']} | {row['role']} | {row['status']} | "
            f"{row['claim']} | {row['boundary']} |"
        )
    lines.extend(["", "## Claim-Evidence Details", ""])
    for row in rows:
        lines.extend(
            [
                f"### {row['item_id']}: {row['role']}",
                "",
                f"Claim: {row['claim']}",
                "",
                f"Evidence: {row['evidence']}",
                "",
                f"Source artifacts: `{row['source_artifacts']}`",
                "",
                f"Status: `{row['status']}`",
                "",
                f"Boundary: {row['boundary']}",
                "",
                f"Next action: {row['next_action']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Manuscript Boundary",
            "",
            "Do not write that the study has completed blind external validation. Do not present 4TU grouped results as a confirmed main-effect replication. Do not overstate Mojahid split inflation because material support is only 1/5 model families. The current main result should be framed around Res-SAM environment-transfer fragility, supported by secondary split and counterfactual stress-test evidence.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = build_items()
    result = {
        "run_id": "20260810_manuscript_figure_table_plan",
        "n_items": len(rows),
        "items": rows,
    }
    (OUT_DIR / "figure_table_plan_summary.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_csv(OUT_DIR / "figure_table_claim_evidence_map.csv", rows)
    write_md(OUT_DIR / "figure_table_plan_summary.md", rows)
    print(json.dumps({"n_items": len(rows), "out_dir": str(OUT_DIR)}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
