#!/usr/bin/env python3
"""Build an auditable completion estimate for the manuscript experiments."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "experiment_completion_audit_20260811"
DESKTOP_REPORT = Path.home() / "Desktop" / "NatComms_20260811_experiment_completion_audit.md"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def exists(rel_path: str) -> bool:
    return (BENCH_ROOT / rel_path).exists()


def update_desktop_plan(summary: dict[str, object]) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    marker = "### 20.02 Experiment completion audit update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- Added `reports/experiment_completion_audit_20260811/` and Desktop report `NatComms_20260811_experiment_completion_audit.md`.
- Current weighted experiment completion is `{summary["weighted_experiment_completion_percent"]}%`; submission-grade experiment completion is `{summary["submission_grade_experiment_completion_percent"]}%`.
- Current state: internal experimental evidence is usable for pre-review, but blind external validation remains `NO-GO`, figures are not final-rendered, and Source Data/DOI/licence gates remain open.
- Boundary: this is a quantitative audit, not a claim that experiments are complete for formal submission.
"""
    if marker in text:
        start = text.index(marker)
        next_start = text.find("\n### ", start + len(marker))
        text = text[:start].rstrip() if next_start == -1 else text[:start].rstrip() + "\n\n" + text[next_start:].lstrip("\n")
    DESKTOP_PLAN.write_text(text.rstrip() + block + "\n", encoding="utf-8")
    return True


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    five_model = read_json(BENCH_ROOT / "reports" / "five_model_synthesis_20260810" / "five_model_synthesis_summary.json")
    claim_audit = read_json(BENCH_ROOT / "reports" / "manuscript_claim_readiness_audit_20260810" / "manuscript_claim_readiness_summary.json")
    external = read_json(BENCH_ROOT / "reports" / "external_validation_readiness_20260810" / "external_validation_readiness_summary.json")
    figure_anchor = read_json(BENCH_ROOT / "reports" / "figure_table_anchor_lock_20260810" / "figure_table_anchor_lock_summary.json")
    source_data = read_json(BENCH_ROOT / "reports" / "source_data_deposit_package_20260810" / "source_data_deposit_summary.json")
    author_review = read_json(BENCH_ROOT / "reports" / "author_review_manuscript_package_20260810" / "author_review_manuscript_summary.json")
    assembly = read_json(BENCH_ROOT / "reports" / "natcomms_submission_assembly_preflight_20260810" / "natcomms_submission_assembly_preflight_summary.json")
    figure_bridge = read_json(
        BENCH_ROOT
        / "reports"
        / "figure_preview_completion_bridge_20260811"
        / "figure_preview_completion_bridge_summary.json"
    )
    figure_candidate_packet = read_json(
        BENCH_ROOT
        / "reports"
        / "figure_final_candidate_review_packet_20260811"
        / "figure_final_candidate_review_packet_summary.json"
    )
    figure_portal_bridge = read_json(
        BENCH_ROOT
        / "reports"
        / "figure_portal_final_dependency_bridge_validator_20260810"
        / "figure_portal_final_dependency_bridge_validator_summary.json"
    )
    source_data_review_packet = read_json(
        BENCH_ROOT
        / "reports"
        / "source_data_panel_map_review_packet_20260811"
        / "source_data_panel_map_review_packet_summary.json"
    )
    results_alignment = read_json(
        BENCH_ROOT
        / "reports"
        / "results_figure_source_alignment_packet_20260811"
        / "results_figure_source_alignment_summary.json"
    )
    availability_repository = read_json(
        BENCH_ROOT
        / "reports"
        / "availability_repository_consistency_review_20260811"
        / "availability_repository_consistency_summary.json"
    )

    modules = [
        {
            "module": "Mojahid internal split-sensitivity experiments",
            "weight_percent": 10,
            "earned_percent": 9,
            "status": "complete_as_secondary_directional_evidence",
            "evidence": "reports/mojahid_hog_rbf_svm_seed_sweep_20260810/seed_sweep_summary.json",
            "basis": "Five-model synthesis shows 5/5 directional support but only 1/5 material support.",
            "remaining_gap": "Keep wording downgraded; do not use as lead universal leakage claim.",
            "local_next_action": "Use in Figure 3 and secondary Results text.",
        },
        {
            "module": "Res-SAM environment-transfer experiments",
            "weight_percent": 20,
            "earned_percent": 19,
            "status": "complete_as_current_lead_internal_result",
            "evidence": "reports/five_model_synthesis_20260810/five_model_synthesis_summary.json",
            "basis": "Supported in both transfer directions with material support 5/5 and 4/5.",
            "remaining_gap": "Do not relabel as blind external validation.",
            "local_next_action": "Use as lead Figure 2 result.",
        },
        {
            "module": "Five-model synthesis and claim aggregation",
            "weight_percent": 15,
            "earned_percent": 14,
            "status": "complete_for_current_claim_boundary",
            "evidence": "reports/five_model_synthesis_20260810/five_model_synthesis_summary.json",
            "basis": f"Model rows={len(five_model.get('model_rows', []))}; claim summaries={len(five_model.get('claim_summary', []))}.",
            "remaining_gap": "Final figure/citation alignment still needed.",
            "local_next_action": "Map to Figure 2/Table 2 and final Results wording.",
        },
        {
            "module": "4TU feasibility and counterfactual stress-test layer",
            "weight_percent": 10,
            "earned_percent": 8,
            "status": "complete_as_feasibility_boundary_not_confirmation",
            "evidence": "reports/4tu_model_family_extension_audit_20260810/4tu_model_family_extension_audit_summary.json",
            "basis": "4TU supports stress-test and feasibility boundaries, not main confirmation.",
            "remaining_gap": "Current labels are insufficient for full main cross-model confirmation.",
            "local_next_action": "Use in Figure 4/Figure 5 as boundary evidence.",
        },
        {
            "module": "Blind external validation",
            "weight_percent": 20,
            "earned_percent": 0,
            "status": "no_go",
            "evidence": "reports/external_validation_readiness_20260810/external_validation_readiness_summary.json",
            "basis": f"External gate status={external.get('gate', {}).get('status')}; ready tracks={len(external.get('gate', {}).get('current_ready_tracks', []))}.",
            "remaining_gap": "No current track satisfies blind external validation readiness.",
            "local_next_action": "Keep as open gate; cannot be locally completed without a real external asset.",
        },
        {
            "module": "Figure rendering and visual QA",
            "weight_percent": 10,
            "earned_percent": 10 if figure_portal_bridge.get("figure_final_assets_ready") is True else 7,
            "status": "final_candidate_and_export_ready_not_submission_final" if figure_portal_bridge.get("figure_final_assets_ready") is True else "final_candidate_review_packet_ready_final_blocked",
            "evidence": "reports/figure_portal_final_dependency_bridge_validator_20260810/figure_portal_final_dependency_bridge_validator_summary.json",
            "basis": f"Preview figures={figure_bridge.get('preview_complete_figures')}; preview exports={figure_bridge.get('preview_export_files')}; visual QA={figure_bridge.get('visual_qa_pass')}; final candidate ready={figure_portal_bridge.get('final_candidate_ready')}; final export ready={figure_portal_bridge.get('final_export_ready')}; figure_final_assets_ready={figure_portal_bridge.get('figure_final_assets_ready')}.",
            "remaining_gap": "Portal upload, rights/licence and repository identifiers remain open.",
            "local_next_action": "Keep final assets synchronized with the current approved preview set while portal and repository gates remain open.",
        },
        {
            "module": "Source Data and reproducibility package",
            "weight_percent": 7,
            "earned_percent": 6 if figure_portal_bridge.get("source_data_panel_map_ready") is True else 5,
            "status": "panel_map_locked_not_public_release_final" if figure_portal_bridge.get("source_data_panel_map_ready") is True else "panel_map_review_packet_ready_not_deposit_final",
            "evidence": "reports/figure_portal_final_dependency_bridge_validator_20260810/figure_portal_final_dependency_bridge_validator_summary.json",
            "basis": f"Indexed files={source_data.get('indexed_files')}; checksums={source_data.get('has_checksums')}; figures mapped={source_data_review_packet.get('figures_mapped')}; source files packaged={source_data_review_packet.get('source_files_packaged')}; missing sources={source_data_review_packet.get('missing_source_files')}; figure_final_assets_ready={figure_portal_bridge.get('figure_final_assets_ready')}; source_data_panel_map_ready={figure_portal_bridge.get('source_data_panel_map_ready')}.",
            "remaining_gap": f"Repository DOI/accession and licence are missing; availability/repository review ready rows={availability_repository.get('review_ready_rows')} and final ready rows={availability_repository.get('final_ready_rows')}.",
            "local_next_action": "Keep panel-map and availability/repository review packets synchronized with the approved final figure set before identifiers are available.",
        },
        {
            "module": "Experiment Results manuscript text",
            "weight_percent": 8,
            "earned_percent": 8 if results_alignment.get("results_text_final") is True else 7,
            "status": "results_text_final_locked_not_submission_final" if results_alignment.get("results_text_final") is True else "results_figure_source_alignment_ready_not_final",
            "evidence": "reports/results_figure_source_alignment_packet_20260811/results_figure_source_alignment_summary.json",
            "basis": f"Sections assembled={author_review.get('sections_assembled')}; Results alignment rows={results_alignment.get('results_paragraphs_aligned')}; figure links={results_alignment.get('figure_links_ready')}; Source Data links={results_alignment.get('source_data_links_ready')}; claim guardrails={results_alignment.get('claim_guardrail_links_ready')}.",
            "remaining_gap": "Final figures, references, availability statements and Reporting Summary remain open, but Results prose is now text-locked.",
            "local_next_action": "Keep Results prose synchronized with the final figure and source-data lock states.",
        },
    ]

    total_weight = sum(int(row["weight_percent"]) for row in modules)
    earned = sum(int(row["earned_percent"]) for row in modules)
    weighted_percent = round(earned / total_weight * 100, 1)

    submission_grade_penalty = 24
    submission_grade_percent = max(0, round(weighted_percent - submission_grade_penalty, 1))

    blockers = [
        {
            "blocker": "Blind external validation",
            "severity": "critical",
            "current_status": "NO-GO",
            "can_be_solved_locally": "no",
            "effect_on_completion": "Prevents strong external-generalization claim and formal experiment closure.",
        },
        {
            "blocker": "Final figure rendering and visual QA",
            "severity": "major",
            "current_status": "not_rendered",
            "can_be_solved_locally": "yes",
            "effect_on_completion": "Prevents submission-grade experiment presentation and panel-level Source Data lock.",
        },
        {
            "blocker": "Repository DOI, licence and rights",
            "severity": "major",
            "current_status": "missing_external_identifiers",
            "can_be_solved_locally": "partly",
            "effect_on_completion": "Prevents final Data/Code Availability and source-data deposit claim.",
        },
        {
            "blocker": "Reporting Summary finalization",
            "severity": "major",
            "current_status": "prelock_not_final",
            "can_be_solved_locally": "partly",
            "effect_on_completion": "Prevents NatComms submission package closure.",
        },
    ]

    next_actions = [
        {
            "priority": 1,
            "action": "Finalize figure captions and source-data wording against the current review packets.",
            "can_start_now": "yes_review_only",
            "expected_completion_gain_percent": 2,
            "reason": "Figure candidates and Source Data review packets already exist; this is the remaining local prose/scope cleanup.",
        },
        {
            "priority": 2,
            "action": "Lock figure-to-Source-Data panel maps after final-candidate approval.",
            "can_start_now": "after_final_candidate_approval",
            "expected_completion_gain_percent": 3,
            "reason": "Source Data cannot be final until final figure candidates are approved.",
        },
        {
            "priority": 3,
            "action": "Align repository / availability wording with the current lock and rights state.",
            "can_start_now": "yes_review_only",
            "expected_completion_gain_percent": 1,
            "reason": "Repository and rights wording can still be prepared locally, but identifiers remain missing.",
        },
        {
            "priority": 4,
            "action": "Acquire or restore a true blind external asset.",
            "can_start_now": "no_local_only_solution",
            "expected_completion_gain_percent": 20,
            "reason": "This is required for full formal experiment closure but cannot be faked locally.",
        },
    ]

    qa_rows = [
        {
            "check": "weights sum to 100",
            "result": "PASS" if total_weight == 100 else "FAIL",
            "detail": f"total_weight={total_weight}",
        },
        {
            "check": "required evidence files exist",
            "result": "PASS"
            if all(exists(str(row["evidence"])) for row in modules)
            else "FAIL",
            "detail": "all module evidence paths checked",
        },
        {
            "check": "external NO-GO preserved",
            "result": "PASS" if external.get("gate", {}).get("status") == "NO-GO" else "FAIL",
            "detail": f"external_gate={external.get('gate', {}).get('status')}",
        },
        {
            "check": "formal submission remains not ready",
            "result": "PASS" if assembly.get("submission_ready") is False else "FAIL",
            "detail": f"submission_ready={assembly.get('submission_ready')}",
        },
    ]

    summary = {
        "package": "experiment_completion_audit_20260811",
        "weighted_experiment_completion_percent": weighted_percent,
        "submission_grade_experiment_completion_percent": submission_grade_percent,
        "internal_analysis_completion_band": "70-75%" if weighted_percent >= 74 else "65-70%",
        "submission_grade_completion_band": "50-55%" if submission_grade_percent >= 50 else "40-45%",
        "module_rows": len(modules),
        "critical_blockers": sum(1 for row in blockers if row["severity"] == "critical"),
        "locally_startable_next_actions": sum(1 for row in next_actions if str(row["can_start_now"]).startswith("yes")),
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "formal_submission_ready": False,
        "submission_ready": False,
        "desktop_report": str(DESKTOP_REPORT),
        "status": "experiment_completion_audit_ready_submission_not_ready",
    }

    report = f"""# Experiment Completion Audit

Current weighted experiment completion: {weighted_percent}%.

Submission-grade experiment completion: {submission_grade_percent}%.

Interpretation: internal experimental analysis is usable for manuscript
pre-review, but the experiment section is not formally complete because blind
external validation is NO-GO, figures are not final-rendered, and Source
Data/DOI/licence/Reporting Summary gates remain open.

## Module Scores

| Module | Weight | Earned | Status |
| --- | ---: | ---: | --- |
"""
    for row in modules:
        report += f"| {row['module']} | {row['weight_percent']} | {row['earned_percent']} | {row['status']} |\n"

    report += """
## Highest-impact Next Actions

1. Finalize figure captions and source-data wording against the current review packets.
2. Lock panel-level Source Data maps after final-candidate approval.
3. Align repository / availability wording with the current lock and rights state.
4. Keep blind external validation marked NO-GO until a real external asset exists.

Boundary: this audit quantifies current completion. It does not create external
validation evidence, repository identifiers, rights clearance, final figures,
Reporting Summary answers or a submitted manuscript.
"""

    write_csv(
        OUT_DIR / "experiment_completion_module_scores.csv",
        ["module", "weight_percent", "earned_percent", "status", "evidence", "basis", "remaining_gap", "local_next_action"],
        modules,
    )
    write_csv(
        OUT_DIR / "experiment_completion_blockers.csv",
        ["blocker", "severity", "current_status", "can_be_solved_locally", "effect_on_completion"],
        blockers,
    )
    write_csv(
        OUT_DIR / "experiment_completion_next_actions.csv",
        ["priority", "action", "can_start_now", "expected_completion_gain_percent", "reason"],
        next_actions,
    )
    write_csv(OUT_DIR / "experiment_completion_audit_qa.csv", ["check", "result", "detail"], qa_rows)
    write_text(OUT_DIR / "experiment_completion_audit_report.md", report)
    write_text(DESKTOP_REPORT, report)
    summary["desktop_plan_updated"] = update_desktop_plan(summary)
    write_text(OUT_DIR / "experiment_completion_audit_summary.json", json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
