#!/usr/bin/env python3
"""Build a Nature-style Reporting Summary draft from current checkpoint evidence."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "reporting_summary_draft_20260810"
CHECKLIST = BENCH_ROOT / "reports" / "companion_artifacts_skeleton_20260810" / "reporting_summary_checklist.csv"
METHODS = BENCH_ROOT / "reports" / "methods_section_skeleton_20260810" / "methods_module_map.csv"
DASHBOARD = BENCH_ROOT / "reports" / "submission_readiness_dashboard_20260810" / "open_gate_priority_queue.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    checklist = read_csv(CHECKLIST)
    methods = read_csv(METHODS)
    open_gates = read_csv(DASHBOARD)
    method_lookup = {row["module_id"]: row for row in methods}

    draft_rows = [
        {
            "reporting_item": "Study design",
            "draft_answer": "The current checkpoint is a provenance-aware benchmark workflow for GPR recognition. It separates executable local asset evidence from unresolved confirmation gates and reports split, environment-transfer and counterfactual stress-test contrasts.",
            "evidence_anchor": "M1; M2; M6; manuscript assembly skeleton",
            "current_status": "draft_answer_ready_not_final",
            "missing_before_submission": "Final article framing and final figure/table set.",
            "risk": "medium",
        },
        {
            "reporting_item": "Sample size and exclusions",
            "draft_answer": "Local executable rows are Mojahid 2524, 4TU 99 and Res-SAM 1050. TIGPR has 0 local executable rows and is supporting-only at this checkpoint.",
            "evidence_anchor": "M1; Table 1; unified manifests",
            "current_status": "draft_answer_ready_not_final",
            "missing_before_submission": "Final inclusion/exclusion criteria and third-party licence boundaries for each asset.",
            "risk": "medium",
        },
        {
            "reporting_item": "Randomization and split strategy",
            "draft_answer": "The benchmark distinguishes random stratified, grouped and environment-transfer protocols. Mojahid compares random and grouped splits; Res-SAM compares within-environment and cross-environment transfer; 4TU stress tests include fixed-split and project-level repeated-split layers.",
            "evidence_anchor": "M2; M4; Figure 2; Figure 3; Figure 4",
            "current_status": "draft_answer_ready_not_final",
            "missing_before_submission": "Frozen split manifests and exact seed table for every final figure.",
            "risk": "medium",
        },
        {
            "reporting_item": "Blinding",
            "draft_answer": "No completed blind external validation exists. A protocol, analyst-facing manifest template, label-holdout template, one-shot submission template, intake validator and locked evaluator are available, but no real external asset has passed strict intake.",
            "evidence_anchor": "M6; external validation readiness; blind external acquisition package",
            "current_status": "protocol_only_not_final",
            "missing_before_submission": "Real external asset, strict-SHA manifest, label holdout, frozen prediction submission, label unlock and one-shot locked evaluation.",
            "risk": "high",
        },
        {
            "reporting_item": "Statistical analysis",
            "draft_answer": "Current analyses report balanced accuracy, delta balanced accuracy, directional support, material support counts, feasibility states and stress-test sensitivity summaries. The material-support threshold is 0.05 delta balanced accuracy in the five-model synthesis.",
            "evidence_anchor": "M3; M4; M5; Figure 2-5 source data",
            "current_status": "draft_answer_ready_not_final",
            "missing_before_submission": "Final uncertainty interval policy, final statistical test plan and multiple-comparison policy if inferential tests are added.",
            "risk": "medium",
        },
        {
            "reporting_item": "Software and code availability",
            "draft_answer": "Current scripts regenerate checkpoint artifacts through run_m0_m2_checks.ps1 using the local Python environment. Public code repository URL, release tag, archive DOI and software licence are not yet available.",
            "evidence_anchor": "M7; repository metadata package; code availability draft",
            "current_status": "local_only_not_final",
            "missing_before_submission": "Public repository URL, release tag, archive DOI, software licence and final figure-generation backend.",
            "risk": "high",
        },
        {
            "reporting_item": "Data availability",
            "draft_answer": "Derived manifests, source-data tables, protocol files and audit artifacts exist locally and in sanitized staging preview. Data repository DOI/accession, final Source Data, licence decision and third-party rights review are not yet complete.",
            "evidence_anchor": "source-data deposit package; repository metadata package; release readiness audit",
            "current_status": "local_only_not_final",
            "missing_before_submission": "Repository DOI/accession, dataset README, licence, final source-data mapping and third-party data source citations.",
            "risk": "high",
        },
        {
            "reporting_item": "External validation",
            "draft_answer": "External validation readiness remains NO-GO. Existing external-blind scripts and templates validate structure only and do not constitute a real blind external result.",
            "evidence_anchor": "external validation readiness; Figure 6 source data; blind external acquisition package",
            "current_status": "not_ready",
            "missing_before_submission": "Acquire or restore a separate blind external asset and run the locked evaluation after label unlock.",
            "risk": "high",
        },
    ]
    write_csv(
        OUT_DIR / "reporting_summary_draft_answers.csv",
        draft_rows,
        ["reporting_item", "draft_answer", "evidence_anchor", "current_status", "missing_before_submission", "risk"],
    )

    unresolved_rows = [
        {
            "priority": row["priority"],
            "unresolved_item": row["gate"],
            "status": row["status"],
            "required_evidence": row["required_evidence_to_close"],
            "reporting_summary_impact": "Must remain open in Reporting Summary until closed.",
        }
        for row in open_gates
    ]
    write_csv(
        OUT_DIR / "reporting_summary_unresolved_items.csv",
        unresolved_rows,
        ["priority", "unresolved_item", "status", "required_evidence", "reporting_summary_impact"],
    )

    method_trace_rows = []
    for row in draft_rows:
        anchors = [part.strip() for part in row["evidence_anchor"].split(";")]
        method_ids = [anchor for anchor in anchors if anchor in method_lookup]
        method_trace_rows.append(
            {
                "reporting_item": row["reporting_item"],
                "method_modules": ";".join(method_ids) if method_ids else "not_method_specific",
                "trace_status": "has_method_anchor" if method_ids else "uses_report_or_gate_artifact",
            }
        )
    write_csv(
        OUT_DIR / "reporting_summary_method_trace.csv",
        method_trace_rows,
        ["reporting_item", "method_modules", "trace_status"],
    )

    md_lines = [
        "# Reporting Summary draft 2026-08-10",
        "",
        "Draft boundary: this is a pre-submission draft based on current checkpoint artifacts. It is not a final Nature Reporting Summary because blind external validation, rendered figures, repository identifiers, licence, rights and final source-data mapping remain open.",
        "",
        "## Draft answers",
        "",
    ]
    for row in draft_rows:
        md_lines.extend(
            [
                f"### {row['reporting_item']}",
                "",
                row["draft_answer"],
                "",
                f"Evidence anchor: {row['evidence_anchor']}.",
                "",
                f"Status: `{row['current_status']}`. Risk: `{row['risk']}`.",
                "",
                f"Missing before submission: {row['missing_before_submission']}",
                "",
            ]
        )
    md_lines.extend(
        [
            "## Chinese check",
            "",
            "这份 Reporting Summary 只能作为预填草案。不能把 protocol_only、local_only 或 not_ready 项写成 final ready。尤其是 blinding/external validation、Data Availability、Code Availability 仍是高风险未闭合项。",
            "",
        ]
    )
    (OUT_DIR / "reporting_summary_draft.md").write_text("\n".join(md_lines), encoding="utf-8")

    summary = {
        "run_id": "20260810_reporting_summary_draft",
        "draft_items": len(draft_rows),
        "high_risk_items": sum(row["risk"] == "high" for row in draft_rows),
        "unresolved_items": len(unresolved_rows),
        "method_trace_rows": len(method_trace_rows),
        "final_reporting_summary_ready": False,
        "status": "reporting_summary_draft_ready_not_final",
        "boundary": "Draft answers are mapped to current evidence, but final Reporting Summary cannot be locked before external validation, figures, repository identifiers, licence and rights are resolved.",
    }
    (OUT_DIR / "reporting_summary_draft_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    report = [
        "# Reporting Summary draft report 2026-08-10",
        "",
        f"- Draft items: {summary['draft_items']}",
        f"- High-risk items: {summary['high_risk_items']}",
        f"- Unresolved items: {summary['unresolved_items']}",
        f"- Final Reporting Summary ready: {str(summary['final_reporting_summary_ready']).lower()}",
        "",
        "Boundary: this package reduces Reporting Summary drafting risk but does not close any high-risk submission gate.",
        "",
    ]
    (OUT_DIR / "reporting_summary_draft_report.md").write_text("\n".join(report), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
