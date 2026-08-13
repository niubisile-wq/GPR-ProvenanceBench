#!/usr/bin/env python3
"""Build a portal submission file preflight without assembling final files."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "portal_submission_file_preflight_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"

DASHBOARD = REPORTS / "submission_readiness_dashboard_20260810" / "submission_readiness_dashboard_summary.json"
GATE_LEDGER = REPORTS / "submission_completion_ledger_20260810" / "submission_completion_gate_ledger.csv"
FINAL_VERIFICATION = REPORTS / "submission_completion_ledger_20260810" / "submission_final_verification_queue.csv"
MANUSCRIPT_BLOCKERS = REPORTS / "manuscript_assembly_skeleton_20260810" / "manuscript_blocker_checklist.csv"


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def exists(rel_path: str) -> bool:
    return (BENCH_ROOT / rel_path).exists()


def update_desktop_plan(section: str) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    marker = "### 18.86 Portal submission file preflight update"
    if marker in text:
        start = text.index(marker)
        next_start = text.find("\n### ", start + len(marker))
        if next_start == -1:
            updated = text[:start].rstrip() + "\n\n" + section.strip() + "\n"
        else:
            updated = text[:start].rstrip() + "\n\n" + section.strip() + "\n\n" + text[next_start:].lstrip("\n")
    else:
        updated = text.rstrip() + "\n\n" + section.strip() + "\n"
    DESKTOP_PLAN.write_text(updated, encoding="utf-8", newline="\n")
    return True


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    dashboard = read_json(DASHBOARD)
    gate_rows = read_csv(GATE_LEDGER)
    verification_rows = read_csv(FINAL_VERIFICATION)
    blocker_rows = read_csv(MANUSCRIPT_BLOCKERS)

    portal_items = [
        {
            "portal_item": "main_manuscript_docx_or_pdf",
            "current_source": "reports/manuscript_assembly_skeleton_20260810/manuscript_assembly_skeleton.md",
            "current_state": "skeleton_only",
            "required_unlock_gate": "Main figure rendering; Reporting Summary; final reference numbering; repository identifiers",
            "upload_allowed_now": "no",
            "reason_not_allowed": "Final prose, rendered figures, DOI/accessions and numbered references are not locked.",
        },
        {
            "portal_item": "cover_letter",
            "current_source": "reports/submission_package_skeleton_20260810/cover_letter_skeleton.md",
            "current_state": "skeleton_only",
            "required_unlock_gate": "final manuscript and corresponding-author approval",
            "upload_allowed_now": "no",
            "reason_not_allowed": "Author approval and final manuscript state are missing.",
        },
        {
            "portal_item": "title_abstract_significance",
            "current_source": "reports/submission_package_skeleton_20260810/title_abstract_significance.md",
            "current_state": "draft_skeleton",
            "required_unlock_gate": "final results framing and external-validation boundary",
            "upload_allowed_now": "no",
            "reason_not_allowed": "Abstract must match final figure set and open-gate wording.",
        },
        {
            "portal_item": "display_figures",
            "current_source": "reports/figure_source_data_lock_20260810/figure_panel_claim_lock.csv",
            "current_state": "source_data_locked_not_rendered",
            "required_unlock_gate": "Main figure rendering",
            "upload_allowed_now": "no",
            "reason_not_allowed": "No rendered figure exports or visual QA outputs exist.",
        },
        {
            "portal_item": "source_data_files",
            "current_source": "reports/source_data_deposit_package_20260810/source_data_file_manifest.csv",
            "current_state": "deposit_skeleton",
            "required_unlock_gate": "final figure rendering; repository identifiers; rights clearance",
            "upload_allowed_now": "no",
            "reason_not_allowed": "Panel-level source data must match final rendered figures and licence scope.",
        },
        {
            "portal_item": "data_availability_statement",
            "current_source": "reports/companion_artifacts_skeleton_20260810/data_availability_skeleton.md",
            "current_state": "skeleton_only",
            "required_unlock_gate": "Repository identifiers; third-party rights",
            "upload_allowed_now": "no",
            "reason_not_allowed": "Repository DOI/accession and rights boundaries are missing.",
        },
        {
            "portal_item": "code_availability_statement",
            "current_source": "reports/companion_artifacts_skeleton_20260810/code_availability_skeleton.md",
            "current_state": "skeleton_only",
            "required_unlock_gate": "Repository identifiers; licence",
            "upload_allowed_now": "no",
            "reason_not_allowed": "Public code release, tag, DOI and licence are missing.",
        },
        {
            "portal_item": "reporting_summary",
            "current_source": "reports/reporting_summary_completion_handoff_20260810/reporting_summary_item_completion_matrix.csv",
            "current_state": "handoff_only",
            "required_unlock_gate": "Reporting Summary",
            "upload_allowed_now": "no",
            "reason_not_allowed": "Author confirmations and final Methods/figure references are missing.",
        },
        {
            "portal_item": "references",
            "current_source": "reports/reference_completion_handoff_20260810/citation_marker_final_replacement_queue.csv",
            "current_state": "markers_not_replaced",
            "required_unlock_gate": "Final reference numbering",
            "upload_allowed_now": "no",
            "reason_not_allowed": "Final prose, figure/table calls and reference order are not locked.",
        },
        {
            "portal_item": "supplementary_information",
            "current_source": "reports/manuscript_table_drafts_20260810/manuscript_table_drafts.md",
            "current_state": "candidate_material_only",
            "required_unlock_gate": "final display/SI split and rendered figures",
            "upload_allowed_now": "no",
            "reason_not_allowed": "Display-vs-SI scope has not been selected and figures are unrendered.",
        },
    ]

    for row in portal_items:
        row["current_source_exists"] = exists(str(row["current_source"]))

    gate_to_portal = []
    for gate in gate_rows:
        affected = [item["portal_item"] for item in portal_items if gate["gate"] in item["required_unlock_gate"] or gate["current_handoff_package"] in item["required_unlock_gate"]]
        if not affected:
            affected = [item["portal_item"] for item in portal_items if gate["gate"].split()[0].lower() in item["required_unlock_gate"].lower()]
        gate_to_portal.append(
            {
                "priority": gate["priority"],
                "gate": gate["gate"],
                "closure_state": gate["closure_state"],
                "current_status": gate["current_status"],
                "affected_portal_items": "; ".join(affected) if affected else "cross-cutting",
                "required_evidence_to_close": gate["required_evidence_to_close"],
                "final_validation_to_run": gate["final_validation_to_run"],
            }
        )

    no_upload_rows = [
        {
            "rule_id": "NO-UPLOAD-001",
            "rule": "Do not upload skeletons as final manuscript files.",
            "evidence": "main manuscript, cover letter and availability statements are skeleton/draft only.",
        },
        {
            "rule_id": "NO-UPLOAD-002",
            "rule": "Do not upload unrendered figure source locks as display figures.",
            "evidence": "rendered_figures=0 and backend/scope choices are blank.",
        },
        {
            "rule_id": "NO-UPLOAD-003",
            "rule": "Do not claim public data/code availability before DOI/licence evidence exists.",
            "evidence": "repository identifiers and rights/licence gates are open.",
        },
        {
            "rule_id": "NO-UPLOAD-004",
            "rule": "Do not replace citation markers until final prose and reference order are stable.",
            "evidence": "reference replacement rows remain blocked.",
        },
        {
            "rule_id": "NO-UPLOAD-005",
            "rule": "Do not use full-check pass as portal readiness while submission_ready=false.",
            "evidence": f"dashboard_submission_ready={dashboard.get('submission_ready')}",
        },
    ]

    upload_allowed_now = all(item["upload_allowed_now"] == "yes" for item in portal_items)
    missing_current_sources = [item["portal_item"] for item in portal_items if not item["current_source_exists"]]

    qa_rows = [
        {
            "check": "portal_items_indexed",
            "result": "PASS" if len(portal_items) >= 10 else "FAIL",
            "detail": f"portal_items={len(portal_items)}",
        },
        {
            "check": "open_gates_imported",
            "result": "PASS" if len(gate_rows) == 6 else "FAIL",
            "detail": f"gate_rows={len(gate_rows)}",
        },
        {
            "check": "current_sources_traceable",
            "result": "PASS" if not missing_current_sources else "FAIL",
            "detail": "missing=" + "; ".join(missing_current_sources),
        },
        {
            "check": "upload_block_preserved",
            "result": "PASS" if dashboard.get("submission_ready") is False and not upload_allowed_now else "FAIL",
            "detail": f"submission_ready={dashboard.get('submission_ready')}; upload_allowed_now={upload_allowed_now}",
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(
        OUT_DIR / "portal_submission_file_inventory.csv",
        portal_items,
        ["portal_item", "current_source", "current_source_exists", "current_state", "required_unlock_gate", "upload_allowed_now", "reason_not_allowed"],
    )
    write_csv(
        OUT_DIR / "portal_gate_to_file_gap_matrix.csv",
        gate_to_portal,
        ["priority", "gate", "closure_state", "current_status", "affected_portal_items", "required_evidence_to_close", "final_validation_to_run"],
    )
    write_csv(OUT_DIR / "portal_no_upload_rules.csv", no_upload_rows, ["rule_id", "rule", "evidence"])
    write_csv(
        OUT_DIR / "portal_final_verification_order.csv",
        verification_rows,
        ["order", "verification", "required_state", "current_state"],
    )
    write_csv(
        OUT_DIR / "portal_submission_file_preflight_qa.csv",
        qa_rows,
        ["check", "result", "detail"],
    )

    report = [
        "# Portal submission file preflight report 2026-08-10",
        "",
        "Status: `portal_file_preflight_ready_upload_blocked`",
        "",
        f"1. Portal file rows: {len(portal_items)}",
        f"2. Gate-to-file rows: {len(gate_to_portal)}",
        f"3. No-upload rules: {len(no_upload_rows)}",
        f"4. Final verification rows: {len(verification_rows)}",
        f"5. Manuscript blocker rows imported: {len(blocker_rows)}",
        f"6. QA pass: {str(qa_pass).lower()}",
        "",
        "Conclusion: portal submission file requirements are indexed, but upload is blocked because the six submission gates remain open.",
        "",
    ]
    write_text(OUT_DIR / "PORTAL_SUBMISSION_FILE_PREFLIGHT_README.md", "\n".join(report))
    write_text(OUT_DIR / "portal_submission_file_preflight_report.md", "\n".join(report))

    summary = {
        "package": "portal_submission_file_preflight_20260810",
        "portal_file_rows": len(portal_items),
        "gate_to_file_rows": len(gate_to_portal),
        "no_upload_rules": len(no_upload_rows),
        "final_verification_rows": len(verification_rows),
        "manuscript_blocker_rows_imported": len(blocker_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "upload_allowed_now": upload_allowed_now,
        "portal_upload_ready": False,
        "submission_ready": False,
        "status": "portal_file_preflight_ready_upload_blocked",
    }

    section = f"""### 18.86 Portal submission file preflight update

Added a portal submission file preflight package that maps final upload items to current draft sources and open gates.

New directory: `{OUT_DIR}`

New files:
1. `portal_submission_file_inventory.csv`
2. `portal_gate_to_file_gap_matrix.csv`
3. `portal_no_upload_rules.csv`
4. `portal_final_verification_order.csv`
5. `portal_submission_file_preflight_qa.csv`
6. `PORTAL_SUBMISSION_FILE_PREFLIGHT_README.md`
7. `portal_submission_file_preflight_report.md`
8. `portal_submission_file_preflight_summary.json`

Current result:
1. portal_file_rows = {summary['portal_file_rows']}
2. gate_to_file_rows = {summary['gate_to_file_rows']}
3. no_upload_rules = {summary['no_upload_rules']}
4. qa_pass = {str(qa_pass).lower()}
5. upload_allowed_now = false
6. portal_upload_ready = false
7. submission_ready = false

Boundary:
1. This step does not assemble final portal files.
2. This step does not create DOI/licence evidence.
3. This step does not close submission gates or authorize upload."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "portal_submission_file_preflight_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("Portal submission file preflight QA failed")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
