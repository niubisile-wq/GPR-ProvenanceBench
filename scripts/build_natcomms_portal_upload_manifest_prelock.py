#!/usr/bin/env python3
"""Build Nature Communications portal upload manifest prelock package."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "natcomms_portal_upload_manifest_prelock_20260810"

SUBMISSION_PREFLIGHT = (
    BENCH_ROOT
    / "reports"
    / "natcomms_submission_assembly_preflight_20260810"
    / "natcomms_submission_item_preflight.csv"
)
TEXT_SUMMARY = (
    BENCH_ROOT
    / "reports"
    / "natcomms_initial_submission_text_preassembly_20260810"
    / "natcomms_text_preassembly_summary.json"
)
SI_SUMMARY = (
    BENCH_ROOT
    / "reports"
    / "natcomms_supplementary_info_preassembly_20260810"
    / "supplementary_info_preassembly_summary.json"
)
ADMIN_SUMMARY = (
    BENCH_ROOT
    / "reports"
    / "natcomms_admin_declarations_prelock_20260810"
    / "admin_declarations_prelock_summary.json"
)
FIGURE_SUMMARY = (
    BENCH_ROOT
    / "reports"
    / "figure_source_data_lock_20260810"
    / "figure_source_data_lock_summary.json"
)
REPORTING_SUMMARY = (
    BENCH_ROOT
    / "reports"
    / "reporting_summary_finalization_prelock_20260810"
    / "reporting_summary_finalization_prelock_summary.json"
)
REFERENCE_SUMMARY = (
    BENCH_ROOT
    / "reports"
    / "sentence_citation_support_lock_20260810"
    / "sentence_citation_support_lock_summary.json"
)
REPOSITORY_SUMMARY = (
    BENCH_ROOT
    / "reports"
    / "repository_release_manifest_lock_20260810"
    / "repository_release_manifest_lock_summary.json"
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    submission_rows = read_csv(SUBMISSION_PREFLIGHT)
    text_summary = read_json(TEXT_SUMMARY)
    si_summary = read_json(SI_SUMMARY)
    admin_summary = read_json(ADMIN_SUMMARY)
    figure_summary = read_json(FIGURE_SUMMARY)
    reporting_summary = read_json(REPORTING_SUMMARY)
    reference_summary = read_json(REFERENCE_SUMMARY)
    repository_summary = read_json(REPOSITORY_SUMMARY)

    upload_rows = [
        {
            "portal_item": "Initial manuscript single file",
            "current_artifact": "reports/natcomms_initial_submission_text_preassembly_20260810/natcomms_initial_submission_text_preassembly.md",
            "current_status": "preassembled_text_not_final",
            "portal_role": "Main text plus embedded or grouped figures for first submission if converted to Word/PDF.",
            "blocking_condition": "Final figures, references, availability statements, Reporting Summary alignment and author/admin fields are not final.",
            "minimum_final_evidence": "Single Word/PDF or equivalent with final title page, text, figure calls, references, statements, figure legends and tables.",
            "upload_ready": "no",
        },
        {
            "portal_item": "Supplementary Information file",
            "current_artifact": "reports/natcomms_supplementary_info_preassembly_20260810/supplementary_information_preassembly.md",
            "current_status": "si_preassembled_not_final",
            "portal_role": "Separate Supplementary Information file.",
            "blocking_condition": "Final SI PDF/Word, rendered supplementary material, Source Data and open gates are not final.",
            "minimum_final_evidence": "Final SI file with stable Supplementary Methods, Tables, Notes and Supplementary Data references.",
            "upload_ready": "no",
        },
        {
            "portal_item": "Cover letter",
            "current_artifact": "reports/natcomms_cover_letter_prelock_20260810/natcomms_cover_letter_prelock.md",
            "current_status": "cover_letter_prelocked_not_final",
            "portal_role": "Separate cover letter upload or portal text.",
            "blocking_condition": "Corresponding-author contact, final title, branch, figures, DOI/rights, Reporting Summary and references are not final.",
            "minimum_final_evidence": "Final editor-facing letter with corresponding-author details and reviewer suggestions/exclusions as appropriate.",
            "upload_ready": "no",
        },
        {
            "portal_item": "Administrative declarations",
            "current_artifact": "reports/natcomms_admin_declarations_prelock_20260810/admin_declarations_prelock.md",
            "current_status": "admin_prelocked_not_final",
            "portal_role": "Title page fields, Author Contributions, Competing Interests, acknowledgements and policy choices.",
            "blocking_condition": "Author names, order, affiliations, contributions, interests, funding, ethics and reviewer suggestions need author input.",
            "minimum_final_evidence": "Author-confirmed title page and declaration statements.",
            "upload_ready": "no",
        },
        {
            "portal_item": "Main figure files",
            "current_artifact": "reports/figure_source_data_lock_20260810/figure_panel_claim_lock.csv",
            "current_status": "inputs_locked_figures_not_rendered",
            "portal_role": "Embedded in first-submission single file or uploaded as individual files for revision/final package.",
            "blocking_condition": "Backend choice is undecided and rendered figure files do not exist.",
            "minimum_final_evidence": "Final PDF/SVG/TIFF/JPEG exports, panel labels, caption boundaries and visual QA pass.",
            "upload_ready": "no",
        },
        {
            "portal_item": "Source Data / Supplementary Data",
            "current_artifact": "reports/source_data_deposit_package_20260810/source_data_file_manifest.csv",
            "current_status": "derived_source_data_ready_for_audit_not_final",
            "portal_role": "Source Data files and/or public repository records supporting final figures.",
            "blocking_condition": "Final rendered figure panel mapping, repository identifiers and rights clearance are absent.",
            "minimum_final_evidence": "Panel-level Source Data matching final figures and rights-approved release manifest.",
            "upload_ready": "no",
        },
        {
            "portal_item": "Reporting Summary",
            "current_artifact": "reports/reporting_summary_finalization_prelock_20260810/reporting_summary_final_lock_matrix.csv",
            "current_status": "prelock_not_final",
            "portal_role": "Nature Portfolio Reporting Summary attachment/portal form.",
            "blocking_condition": "Blinding, external validation, figures, availability statements and DOI/rights are unresolved.",
            "minimum_final_evidence": "Every Reporting Summary item has a final answer tied to locked evidence.",
            "upload_ready": "no",
        },
        {
            "portal_item": "References / bibliography",
            "current_artifact": "reports/sentence_citation_support_lock_20260810/sentence_citation_support_lock.csv",
            "current_status": "sentence_support_mapped_not_final",
            "portal_role": "Nature-style numbered references inside manuscript file.",
            "blocking_condition": "Final prose, figure/table calls and citation order are not locked.",
            "minimum_final_evidence": "No [P#] candidate markers remain; numbered references are verified and exported.",
            "upload_ready": "no",
        },
        {
            "portal_item": "Data and code repository identifiers",
            "current_artifact": "reports/repository_release_manifest_lock_20260810/repository_release_manifest_lock.csv",
            "current_status": "predeposit_manifest_locked_release_not_public",
            "portal_role": "Repository URLs/DOIs in Data Availability and Code Availability statements.",
            "blocking_condition": "Repository DOI, code DOI, licence and rights clearance are not created.",
            "minimum_final_evidence": "Resolvable repository/accession records, code release tag, archive DOI and licence/rights approvals.",
            "upload_ready": "no",
        },
    ]
    write_csv(
        OUT_DIR / "portal_upload_item_manifest.csv",
        upload_rows,
        [
            "portal_item",
            "current_artifact",
            "current_status",
            "portal_role",
            "blocking_condition",
            "minimum_final_evidence",
            "upload_ready",
        ],
    )

    stage_rows = [
        {
            "stage": "Initial submission",
            "allowed_package_logic": "Nature Communications allows first submissions to combine manuscript text and figures into one Word/LaTeX/PDF file up to the stated size limit, while Supplementary Information is supplied separately.",
            "current_project_action": "Keep text/SI/admin/cover-letter preassemblies separate until author inputs and figures are final; do not generate final PDF yet.",
            "status": "planned_not_ready",
        },
        {
            "stage": "Revision or final production",
            "allowed_package_logic": "Text, figures and other files may need separate upload according to revision-stage instructions.",
            "current_project_action": "Use the same manifest but switch figure rows from embedded to individual file uploads after rendering and QA.",
            "status": "future",
        },
        {
            "stage": "Submission portal metadata",
            "allowed_package_logic": "Portal metadata must align with the manuscript title page, author list, declarations, reviewer suggestions and cover letter.",
            "current_project_action": "Use admin declarations prelock as the author input source; do not infer missing author metadata.",
            "status": "author_input_required",
        },
    ]
    write_csv(
        OUT_DIR / "portal_stage_upload_strategy.csv",
        stage_rows,
        ["stage", "allowed_package_logic", "current_project_action", "status"],
    )

    blocker_rows = []
    for row in submission_rows:
        blocker_rows.append(
            {
                "submission_item": row["submission_item"],
                "current_status": row["current_status"],
                "assembly_status": row["assembly_status"],
                "blocking_condition": row["blocking_condition"],
                "portal_manifest_effect": "upload_row_created_but_not_ready",
            }
        )
    write_csv(
        OUT_DIR / "portal_blocker_crosswalk.csv",
        blocker_rows,
        [
            "submission_item",
            "current_status",
            "assembly_status",
            "blocking_condition",
            "portal_manifest_effect",
        ],
    )

    finalization_rows = [
        {
            "order": "1",
            "action": "Confirm author/title page and declarations.",
            "dependency": "Author input from admin declarations prelock.",
            "can_execute_now": "partially",
        },
        {
            "order": "2",
            "action": "Choose one figure backend and render final figure set.",
            "dependency": "Author confirms Python or R; recommended Python.",
            "can_execute_now": "requires_author_backend_choice",
        },
        {
            "order": "3",
            "action": "Finalize Source Data and repository/DOI records.",
            "dependency": "Rendered figure panel mapping, licence and rights decisions.",
            "can_execute_now": "no",
        },
        {
            "order": "4",
            "action": "Finalize Reporting Summary.",
            "dependency": "Figures, validation status, availability and Methods locked.",
            "can_execute_now": "no",
        },
        {
            "order": "5",
            "action": "Replace candidate references and lock numbered bibliography.",
            "dependency": "Final prose and figure/table call order.",
            "can_execute_now": "no",
        },
        {
            "order": "6",
            "action": "Generate final initial-submission file and SI file.",
            "dependency": "Steps 1-5 complete.",
            "can_execute_now": "no",
        },
    ]
    write_csv(
        OUT_DIR / "portal_upload_finalization_order.csv",
        finalization_rows,
        ["order", "action", "dependency", "can_execute_now"],
    )

    source_rows = [
        {
            "source_id": "NCOMMS-HOW-SUBMIT",
            "source": "Nature Communications How to submit",
            "checked_date": "2026-08-10",
            "rule_used": "First submissions may combine manuscript text and figures into a single file; Supplementary Information should be supplied as a separate file; manuscript text order includes title page, references, acknowledgements, Author Contributions, Competing Interests, Figure Legends and Tables.",
            "url": "https://www.nature.com/ncomms/submit/how-to-submit",
        },
        {
            "source_id": "NCOMMS-AUTHORSHIP",
            "source": "Nature Communications Authorship",
            "checked_date": "2026-08-10",
            "rule_used": "Submission implies all listed authors agree to the content, author list and contribution statements; corresponding author manages communication and competing-interest statement.",
            "url": "https://www.nature.com/ncomms/editorial-policies/authorship",
        },
    ]
    write_csv(
        OUT_DIR / "portal_upload_official_rule_sources.csv",
        source_rows,
        ["source_id", "source", "checked_date", "rule_used", "url"],
    )

    upload_ready_count = sum(1 for row in upload_rows if row["upload_ready"] == "yes")
    hard_blocked_count = len(upload_rows) - upload_ready_count
    qa_rows = [
        {
            "check": "Portal upload rows exist",
            "result": "PASS" if len(upload_rows) >= 8 else "FAIL",
            "detail": f"{len(upload_rows)} portal upload rows.",
        },
        {
            "check": "No upload-ready false positive",
            "result": "PASS" if upload_ready_count == 0 else "FAIL",
            "detail": f"{upload_ready_count} rows marked upload_ready=yes.",
        },
        {
            "check": "Final blockers preserved",
            "result": "PASS"
            if not text_summary["submission_ready"]
            and not si_summary["submission_ready"]
            and not admin_summary["submission_ready"]
            and not figure_summary["final_figures_ready"]
            and not reporting_summary["final_reporting_summary_ready"]
            and not reference_summary["final_references_ready"]
            and not repository_summary["public_release_ready"]
            else "FAIL",
            "detail": "Text, SI, admin, figures, Reporting Summary, references and repository release remain non-final.",
        },
        {
            "check": "Official rule source rows exist",
            "result": "PASS" if len(source_rows) == 2 else "FAIL",
            "detail": f"{len(source_rows)} official Nature rows.",
        },
        {
            "check": "Finalization order exists",
            "result": "PASS" if len(finalization_rows) == 6 else "FAIL",
            "detail": f"{len(finalization_rows)} finalization actions.",
        },
    ]
    write_csv(
        OUT_DIR / "portal_upload_manifest_qa.csv",
        qa_rows,
        ["check", "result", "detail"],
    )

    manifest_md = [
        "# Nature Communications portal upload manifest prelock",
        "",
        "Boundary: this manifest maps current preassembled artifacts to likely Nature Communications portal upload items. It is not a final upload package, does not create Word/PDF files, does not render figures, does not create repository identifiers and does not submit the manuscript.",
        "",
        "## Current upload state",
        "",
        f"- Portal upload rows: {len(upload_rows)}",
        f"- Upload-ready rows: {upload_ready_count}",
        f"- Blocked/not-ready rows: {hard_blocked_count}",
        "- Current branch: Track B",
        "",
        "## Main blockers",
        "",
        "1. Author/title-page/declaration fields require author confirmation.",
        "2. Figure backend is not chosen and final figures are not rendered.",
        "3. Source Data and repository/code DOI records are not final.",
        "4. Reporting Summary is not final.",
        "5. Candidate references are not converted to final numbered references.",
        "6. Blind external validation remains unavailable.",
        "",
    ]
    (OUT_DIR / "portal_upload_manifest_prelock.md").write_text(
        "\n".join(manifest_md), encoding="utf-8"
    )

    readme = [
        "# Nat Comms portal upload manifest prelock",
        "",
        "This package maps current manuscript, SI, cover-letter, admin, figure, Source Data, Reporting Summary, reference and repository artifacts to portal upload items.",
        "",
        "It is a prelock/checklist only. No row is currently upload-ready, because submission-critical author, figure, repository, Reporting Summary, reference and validation gates remain open.",
        "",
    ]
    (OUT_DIR / "NATCOMMS_PORTAL_UPLOAD_MANIFEST_PRELOCK_README.md").write_text(
        "\n".join(readme), encoding="utf-8"
    )

    report = [
        "# Nat Comms portal upload manifest prelock report",
        "",
        f"- Portal upload rows: {len(upload_rows)}",
        f"- Upload-ready rows: {upload_ready_count}",
        f"- Blocked/not-ready rows: {hard_blocked_count}",
        f"- Stage strategy rows: {len(stage_rows)}",
        f"- Blocker crosswalk rows: {len(blocker_rows)}",
        f"- Finalization-order rows: {len(finalization_rows)}",
        f"- Official source rows: {len(source_rows)}",
        f"- QA failures: {sum(1 for row in qa_rows if row['result'] == 'FAIL')}",
        "- Status: natcomms_portal_upload_manifest_prelock_ready_not_upload_ready",
        "",
        "Boundary: this package maps upload work only; it does not assemble, render, deposit, finalize or submit.",
        "",
    ]
    (OUT_DIR / "portal_upload_manifest_report.md").write_text(
        "\n".join(report), encoding="utf-8"
    )

    summary = {
        "run_id": "20260810_natcomms_portal_upload_manifest_prelock",
        "portal_upload_rows": len(upload_rows),
        "upload_ready_rows": upload_ready_count,
        "blocked_upload_rows": hard_blocked_count,
        "stage_strategy_rows": len(stage_rows),
        "blocker_crosswalk_rows": len(blocker_rows),
        "finalization_order_rows": len(finalization_rows),
        "official_source_rows": len(source_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] != "FAIL" for row in qa_rows),
        "current_applicable_branch": "TRACK-B",
        "portal_upload_ready": False,
        "submission_ready": False,
        "status": "natcomms_portal_upload_manifest_prelock_ready_not_upload_ready",
        "boundary": "Portal upload manifest is prelocked for planning only; author details, figures, Source Data, DOI/rights, Reporting Summary, references and blind external validation remain open.",
    }
    (OUT_DIR / "portal_upload_manifest_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if summary["qa_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
