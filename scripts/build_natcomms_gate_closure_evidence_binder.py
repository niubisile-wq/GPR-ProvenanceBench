#!/usr/bin/env python3
"""Bind Nat Comms finalization gates to concrete closure evidence artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "natcomms_gate_closure_evidence_binder_20260810"

MASTER_CHECKLIST = BENCH_ROOT / "reports" / "natcomms_finalization_master_checklist_20260810" / "finalization_master_checklist.csv"
AUTHOR_INGESTION = BENCH_ROOT / "reports" / "natcomms_author_reply_ingestion_validator_20260810" / "gate_closure_from_author_replies.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def artifact_exists(rel_path: str) -> str:
    return "yes" if (BENCH_ROOT / rel_path).exists() else "no"


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    master_rows = read_csv(MASTER_CHECKLIST)
    author_gate_rows = {row["gate_id"]: row for row in read_csv(AUTHOR_INGESTION)}

    artifact_requirements = [
        {
            "gate_id": "FM-001",
            "requirement_id": "FM001-AUTHOR-REPLY",
            "requirement": "Filled author/admin replies for title page, author order, affiliations, contributions, interests, funding, acknowledgements, ethics and reviewer/policy choices.",
            "evidence_artifact": "reports/natcomms_author_reply_ingestion_validator_20260810/gate_closure_from_author_replies.csv",
            "current_evidence_status": "missing_author_replies",
            "closure_allowed": "no",
        },
        {
            "gate_id": "FM-001",
            "requirement_id": "FM001-ADMIN-FINAL",
            "requirement": "Final title page and declaration wording generated from confirmed author replies.",
            "evidence_artifact": "not_created/final_title_page_and_declarations",
            "current_evidence_status": "not_created",
            "closure_allowed": "no",
        },
        {
            "gate_id": "FM-002",
            "requirement_id": "FM002-BRANCH-REPLY",
            "requirement": "Author confirms Track B route or supplies a real blind external validation holder for Track A.",
            "evidence_artifact": "reports/natcomms_author_reply_ingestion_validator_20260810/gate_closure_from_author_replies.csv",
            "current_evidence_status": "missing_author_reply",
            "closure_allowed": "no",
        },
        {
            "gate_id": "FM-002",
            "requirement_id": "FM002-TRACKA-EVIDENCE",
            "requirement": "If Track A is used, strict blind-intake manifest and one locked external evaluation must exist.",
            "evidence_artifact": "external_blind/no_real_filled_blind_asset_available",
            "current_evidence_status": "not_available",
            "closure_allowed": "no",
        },
        {
            "gate_id": "FM-003",
            "requirement_id": "FM003-BACKEND-CHOICE",
            "requirement": "Single figure rendering backend is explicitly selected.",
            "evidence_artifact": "reports/natcomms_author_reply_ingestion_validator_20260810/gate_closure_from_author_replies.csv",
            "current_evidence_status": "missing_backend_reply",
            "closure_allowed": "no",
        },
        {
            "gate_id": "FM-003",
            "requirement_id": "FM003-FIGURE-EXPORTS",
            "requirement": "Final Figure 1-Figure 6 or reduced display set rendered with visual QA and final captions.",
            "evidence_artifact": "reports/figure_rendering_preflight_20260810/figure_rendering_preflight_summary.json",
            "current_evidence_status": "preflight_only_rendered_figures_0",
            "closure_allowed": "no",
        },
        {
            "gate_id": "FM-004",
            "requirement_id": "FM004-RIGHTS-LICENCE",
            "requirement": "Author/institution confirms code and derived-data licences plus third-party rights route.",
            "evidence_artifact": "reports/natcomms_author_reply_ingestion_validator_20260810/gate_closure_from_author_replies.csv",
            "current_evidence_status": "missing_licence_reply",
            "closure_allowed": "no",
        },
        {
            "gate_id": "FM-004",
            "requirement_id": "FM004-DOI-RELEASE",
            "requirement": "Repository DOI/accession and code DOI/archive exist, with Source Data manifest ready for publication.",
            "evidence_artifact": "reports/repository_release_manifest_lock_20260810/repository_release_manifest_lock_summary.json",
            "current_evidence_status": "predeposit_only_no_doi",
            "closure_allowed": "no",
        },
        {
            "gate_id": "FM-005",
            "requirement_id": "FM005-AUTHOR-CONFIRM",
            "requirement": "Author confirms Reporting Summary items, ethics/governance, blinding/randomization and availability answers.",
            "evidence_artifact": "reports/natcomms_author_reply_ingestion_validator_20260810/gate_closure_from_author_replies.csv",
            "current_evidence_status": "missing_reporting_replies",
            "closure_allowed": "no",
        },
        {
            "gate_id": "FM-005",
            "requirement_id": "FM005-FINAL-SUMMARY",
            "requirement": "Final Reporting Summary file is generated from locked Methods, figures, validation status, Source Data and availability statements.",
            "evidence_artifact": "reports/reporting_summary_finalization_prelock_20260810/reporting_summary_finalization_prelock_summary.json",
            "current_evidence_status": "prelock_only_not_final",
            "closure_allowed": "no",
        },
        {
            "gate_id": "FM-006",
            "requirement_id": "FM006-REFERENCE-LOCK",
            "requirement": "All [P#] markers are replaced by final Nature-style numbered references in final prose order.",
            "evidence_artifact": "reports/sentence_citation_support_lock_20260810/sentence_citation_support_lock_summary.json",
            "current_evidence_status": "support_lock_only_candidate_markers_remain",
            "closure_allowed": "no",
        },
        {
            "gate_id": "FM-006",
            "requirement_id": "FM006-SUPPORT-AUDIT",
            "requirement": "Every final citation supports the sentence-level claim it is attached to.",
            "evidence_artifact": "reports/reference_public_verification_20260810/reference_public_verification_summary.json",
            "current_evidence_status": "metadata_prelock_only",
            "closure_allowed": "no",
        },
        {
            "gate_id": "FM-007",
            "requirement_id": "FM007-FINAL-FILES",
            "requirement": "Final manuscript and SI files are generated after author/admin, branch, figures, Source Data, Reporting Summary and references are locked.",
            "evidence_artifact": "reports/natcomms_initial_submission_text_preassembly_20260810/natcomms_text_preassembly_summary.json",
            "current_evidence_status": "text_preassembly_only_not_final",
            "closure_allowed": "no",
        },
        {
            "gate_id": "FM-007",
            "requirement_id": "FM007-SI-FINAL",
            "requirement": "Final Supplementary Information file is generated with final figure/source-data/references crosswalk.",
            "evidence_artifact": "reports/natcomms_supplementary_info_preassembly_20260810/supplementary_info_preassembly_summary.json",
            "current_evidence_status": "si_preassembly_only_not_final",
            "closure_allowed": "no",
        },
        {
            "gate_id": "FM-008",
            "requirement_id": "FM008-PORTAL-METADATA",
            "requirement": "Corresponding author confirms portal entries, author metadata, reviewer/policy choices and final file order.",
            "evidence_artifact": "reports/natcomms_author_reply_ingestion_validator_20260810/gate_closure_from_author_replies.csv",
            "current_evidence_status": "missing_author_replies",
            "closure_allowed": "no",
        },
        {
            "gate_id": "FM-008",
            "requirement_id": "FM008-UPLOAD-PACKAGE",
            "requirement": "Every portal upload item is marked upload-ready with final files and identifiers.",
            "evidence_artifact": "reports/natcomms_portal_upload_manifest_prelock_20260810/portal_upload_manifest_summary.json",
            "current_evidence_status": "zero_upload_ready_rows",
            "closure_allowed": "no",
        },
    ]
    for row in artifact_requirements:
        row["artifact_exists"] = artifact_exists(row["evidence_artifact"])

    write_csv(
        OUT_DIR / "gate_artifact_evidence_requirements.csv",
        artifact_requirements,
        ["gate_id", "requirement_id", "requirement", "evidence_artifact", "artifact_exists", "current_evidence_status", "closure_allowed"],
    )

    gate_binder_rows = []
    for master in master_rows:
        gate = master["gate_id"]
        requirements = [row for row in artifact_requirements if row["gate_id"] == gate]
        open_artifact_reqs = [row["requirement_id"] for row in requirements if row["closure_allowed"] != "yes"]
        author_status = author_gate_rows.get(gate, {}).get("reply_evidence_status", "not_mapped")
        gate_binder_rows.append(
            {
                "gate_id": gate,
                "gate": master["gate"],
                "master_current_state": master["current_state"],
                "master_closed_status": master["closed"],
                "author_reply_status": author_status,
                "artifact_requirements": "; ".join(row["requirement_id"] for row in requirements),
                "open_artifact_requirements": "; ".join(open_artifact_reqs),
                "closure_recommendation": "keep_open",
                "next_evidence_needed": "Resolve author replies and artifact requirements listed in gate_artifact_evidence_requirements.csv.",
            }
        )
    write_csv(
        OUT_DIR / "gate_closure_evidence_binder.csv",
        gate_binder_rows,
        ["gate_id", "gate", "master_current_state", "master_closed_status", "author_reply_status", "artifact_requirements", "open_artifact_requirements", "closure_recommendation", "next_evidence_needed"],
    )

    closure_order_rows = [
        {"order": "1", "gate_id": "FM-001", "action": "Collect and validate author/admin replies; generate final declarations only after replies are complete.", "blocked_by": "blank author replies"},
        {"order": "2", "gate_id": "FM-002", "action": "Confirm Track B or supply real Track A blind external asset evidence.", "blocked_by": "blank branch reply; no blind external asset"},
        {"order": "3", "gate_id": "FM-003", "action": "Select backend, render figures, run visual QA and lock captions.", "blocked_by": "blank backend reply; rendered_figures=0"},
        {"order": "4", "gate_id": "FM-004", "action": "Finalize rights/licences, Source Data and repository/code DOI records.", "blocked_by": "blank licence reply; no DOI"},
        {"order": "5", "gate_id": "FM-005", "action": "Finalize Reporting Summary from locked Methods, figures, availability and validation status.", "blocked_by": "Reporting Summary prelock only"},
        {"order": "6", "gate_id": "FM-006", "action": "Replace citation markers and lock final numbered bibliography.", "blocked_by": "final prose and figure/table call order not locked"},
        {"order": "7", "gate_id": "FM-007", "action": "Generate final manuscript and SI files.", "blocked_by": "all prior gates open"},
        {"order": "8", "gate_id": "FM-008", "action": "Confirm portal metadata and upload-ready package.", "blocked_by": "final files and metadata missing"},
    ]
    write_csv(OUT_DIR / "gate_closure_execution_order.csv", closure_order_rows, ["order", "gate_id", "action", "blocked_by"])

    forbidden_shortcut_rows = [
        {"shortcut": "Treat recommended defaults as author approval", "why_forbidden": "Defaults are suggestions, not explicit author replies.", "affected_gates": "FM-001; FM-002; FM-003; FM-004; FM-005; FM-008"},
        {"shortcut": "Render figures before backend choice", "why_forbidden": "Formal figure gate requires one backend and visual QA.", "affected_gates": "FM-003; FM-004; FM-005; FM-007; FM-008"},
        {"shortcut": "Use prelock text as final manuscript", "why_forbidden": "Preassembly text excludes final figures, references, declarations, Reporting Summary and Source Data.", "affected_gates": "FM-007; FM-008"},
        {"shortcut": "Claim repository readiness before DOI/rights", "why_forbidden": "Repository package is predeposit only; no public release or DOI exists.", "affected_gates": "FM-004; FM-005; FM-008"},
        {"shortcut": "Claim Track A without blind external evidence", "why_forbidden": "No filled strict-intake external asset or locked evaluation exists.", "affected_gates": "FM-002"},
    ]
    write_csv(OUT_DIR / "gate_closure_forbidden_shortcuts.csv", forbidden_shortcut_rows, ["shortcut", "why_forbidden", "affected_gates"])

    open_requirements = sum(1 for row in artifact_requirements if row["closure_allowed"] != "yes")
    qa_rows = [
        {"check": "All master gates bound", "result": "PASS" if len(gate_binder_rows) == 8 else "FAIL", "detail": f"{len(gate_binder_rows)} gates."},
        {"check": "Artifact requirements exist", "result": "PASS" if len(artifact_requirements) >= 16 else "FAIL", "detail": f"{len(artifact_requirements)} requirements."},
        {"check": "No false gate closure", "result": "PASS" if all(row["closure_recommendation"] == "keep_open" for row in gate_binder_rows) else "FAIL", "detail": "Every gate remains keep_open."},
        {"check": "Open requirements detected", "result": "PASS" if open_requirements == len(artifact_requirements) else "FAIL", "detail": f"{open_requirements} open requirements."},
        {"check": "Forbidden shortcuts recorded", "result": "PASS" if len(forbidden_shortcut_rows) == 5 else "FAIL", "detail": f"{len(forbidden_shortcut_rows)} shortcuts."},
    ]
    write_csv(OUT_DIR / "gate_closure_evidence_binder_qa.csv", qa_rows, ["check", "result", "detail"])

    readme = [
        "# Nat Comms gate closure evidence binder",
        "",
        "Purpose: bind each finalization master gate to author replies and concrete non-author evidence artifacts needed before closure.",
        "",
        "Current checkpoint: all gates remain open because author replies, rendered figures, DOI/rights, final Reporting Summary, final references, final files and portal readiness are missing.",
        "",
        "Boundary: this binder does not close gates; it lists evidence requirements and prevents shortcut closure.",
        "",
    ]
    (OUT_DIR / "NATCOMMS_GATE_CLOSURE_EVIDENCE_BINDER_README.md").write_text("\n".join(readme), encoding="utf-8")

    report = [
        "# Gate closure evidence binder report",
        "",
        f"- Master gates bound: {len(gate_binder_rows)}",
        f"- Artifact/evidence requirements: {len(artifact_requirements)}",
        f"- Open evidence requirements: {open_requirements}",
        f"- Closure order rows: {len(closure_order_rows)}",
        f"- Forbidden shortcuts: {len(forbidden_shortcut_rows)}",
        f"- QA failures: {sum(1 for row in qa_rows if row['result'] == 'FAIL')}",
        "- Status: natcomms_gate_closure_evidence_binder_ready_all_gates_keep_open",
        "",
    ]
    (OUT_DIR / "gate_closure_evidence_binder_report.md").write_text("\n".join(report), encoding="utf-8")

    summary = {
        "run_id": "20260810_natcomms_gate_closure_evidence_binder",
        "master_gates_bound": len(gate_binder_rows),
        "artifact_evidence_requirements": len(artifact_requirements),
        "open_evidence_requirements": open_requirements,
        "closure_order_rows": len(closure_order_rows),
        "forbidden_shortcuts": len(forbidden_shortcut_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] != "FAIL" for row in qa_rows),
        "gate_closure_allowed": False,
        "submission_ready": False,
        "status": "natcomms_gate_closure_evidence_binder_ready_all_gates_keep_open",
        "boundary": "Binder maps required evidence only; every finalization gate remains open until author replies and concrete artifacts are reviewed.",
    }
    (OUT_DIR / "gate_closure_evidence_binder_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if summary["qa_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
