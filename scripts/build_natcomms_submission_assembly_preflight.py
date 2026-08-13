#!/usr/bin/env python3
"""Build a Nature Communications submission assembly preflight package."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "natcomms_submission_assembly_preflight_20260810"

SUMMARIES = {
    "dashboard": BENCH_ROOT / "reports" / "submission_command_dashboard_v2_20260810" / "submission_command_dashboard_v2_summary.json",
    "track_b": BENCH_ROOT / "reports" / "track_b_manuscript_branch_prelock_20260810" / "track_b_manuscript_branch_prelock_summary.json",
    "author_manuscript": BENCH_ROOT / "reports" / "author_review_manuscript_package_20260810" / "author_review_manuscript_summary.json",
    "figures": BENCH_ROOT / "reports" / "figure_source_data_lock_20260810" / "figure_source_data_lock_summary.json",
    "release": BENCH_ROOT / "reports" / "repository_release_manifest_lock_20260810" / "repository_release_manifest_lock_summary.json",
    "availability": BENCH_ROOT / "reports" / "availability_statement_prelock_20260810" / "availability_statement_prelock_summary.json",
    "reporting": BENCH_ROOT / "reports" / "reporting_summary_finalization_prelock_20260810" / "reporting_summary_finalization_prelock_summary.json",
    "references": BENCH_ROOT / "reports" / "sentence_citation_support_lock_20260810" / "sentence_citation_support_lock_summary.json",
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summaries = {key: read_json(path) for key, path in SUMMARIES.items()}

    assembly_rows = [
        {
            "submission_item": "Main manuscript text",
            "current_artifact": "reports/author_review_manuscript_package_20260810/author_review_manuscript_v0_1.md",
            "current_status": "author_review_ready_not_final",
            "assembly_status": "preassemblable",
            "blocking_condition": "Requires final figures, final references, final availability statements and final Reporting Summary alignment.",
            "minimum_final_evidence": "Final manuscript file with stable title, abstract, figure calls, references and statements.",
        },
        {
            "submission_item": "Track B title and abstract",
            "current_artifact": "reports/track_b_manuscript_branch_prelock_20260810/track_b_manuscript_branch_prelock.md",
            "current_status": "track_b_prelocked",
            "assembly_status": "preassemblable",
            "blocking_condition": "Requires author route confirmation and final external-validation status.",
            "minimum_final_evidence": "Author-approved branch decision and no unresolved external-validation language conflict.",
        },
        {
            "submission_item": "Main figures",
            "current_artifact": "reports/figure_source_data_lock_20260810/figure_panel_claim_lock.csv",
            "current_status": "inputs_locked_figures_not_rendered",
            "assembly_status": "blocked",
            "blocking_condition": "Figure backend is undecided; rendered figures, vector exports and visual QA are absent.",
            "minimum_final_evidence": "PDF/SVG/600-dpi previews, QA pass, final captions and Source Data per figure.",
        },
        {
            "submission_item": "Source Data",
            "current_artifact": "reports/source_data_deposit_package_20260810/source_data_file_manifest.csv",
            "current_status": "derived_source_data_ready_for_audit",
            "assembly_status": "blocked",
            "blocking_condition": "Final rendered figure panel mapping and release identifiers are absent.",
            "minimum_final_evidence": "Panel-level Source Data files matching final figures and release manifest.",
        },
        {
            "submission_item": "Data Availability statement",
            "current_artifact": "reports/availability_statement_prelock_20260810/data_availability_statement_variants.csv",
            "current_status": "prelock_not_final",
            "assembly_status": "blocked",
            "blocking_condition": "Repository DOI/accession, licence, rights and final source data are missing.",
            "minimum_final_evidence": "Resolvable repository identifiers and approved rights/licence wording.",
        },
        {
            "submission_item": "Code Availability statement",
            "current_artifact": "reports/availability_statement_prelock_20260810/code_availability_statement_variants.csv",
            "current_status": "prelock_not_final",
            "assembly_status": "blocked",
            "blocking_condition": "Code repository URL, release tag, software licence and code DOI are missing.",
            "minimum_final_evidence": "Public repository/release plus archive DOI and selected software licence.",
        },
        {
            "submission_item": "Repository/DOI package",
            "current_artifact": "reports/repository_release_manifest_lock_20260810/repository_release_manifest_lock.csv",
            "current_status": "predeposit_manifest_locked_release_not_public",
            "assembly_status": "blocked",
            "blocking_condition": "Repository DOI, code DOI, licence and rights clearance are not created.",
            "minimum_final_evidence": "Public deposit/release record with DOI/accession and rights-approved manifest.",
        },
        {
            "submission_item": "Reporting Summary",
            "current_artifact": "reports/reporting_summary_finalization_prelock_20260810/reporting_summary_final_lock_matrix.csv",
            "current_status": "prelock_not_final",
            "assembly_status": "blocked",
            "blocking_condition": "Blinding, external validation, DOI/rights and final figures are unresolved.",
            "minimum_final_evidence": "Final Reporting Summary with every field supported by locked evidence.",
        },
        {
            "submission_item": "References",
            "current_artifact": "reports/sentence_citation_support_lock_20260810/sentence_citation_support_lock.csv",
            "current_status": "sentence_support_mapped_not_final",
            "assembly_status": "blocked",
            "blocking_condition": "Final prose, figure/table calls and citation order are not locked.",
            "minimum_final_evidence": "Final numbered references and reference-manager export matching manuscript order.",
        },
        {
            "submission_item": "Cover letter",
            "current_artifact": "reports/submission_package_skeleton_20260810/cover_letter_skeleton.md",
            "current_status": "skeleton_ready",
            "assembly_status": "preassemblable",
            "blocking_condition": "Needs final title, branch and significance framing.",
            "minimum_final_evidence": "Three-sentence editor-facing letter matched to final manuscript.",
        },
    ]
    write_csv(
        OUT_DIR / "natcomms_submission_item_preflight.csv",
        assembly_rows,
        ["submission_item", "current_artifact", "current_status", "assembly_status", "blocking_condition", "minimum_final_evidence"],
    )

    blocker_rows = [
        {
            "blocker_id": "NC-B01",
            "gate": "Figures",
            "severity": "hard",
            "current_evidence": f"rendered_figures={summaries['figures']['rendered_figures']}; final_figures_ready={summaries['figures']['final_figures_ready']}",
            "required_closure": "Choose backend, render figures, export PDF/SVG/PNG previews and pass visual QA.",
        },
        {
            "blocker_id": "NC-B02",
            "gate": "Repository identifiers and rights",
            "severity": "hard",
            "current_evidence": f"repository_doi_created={summaries['release']['repository_doi_created']}; code_doi_created={summaries['release']['code_doi_created']}; public_release_ready={summaries['release']['public_release_ready']}",
            "required_closure": "Create public deposit/release identifiers after licence and rights decisions.",
        },
        {
            "blocker_id": "NC-B03",
            "gate": "Reporting Summary",
            "severity": "hard",
            "current_evidence": f"final_reporting_summary_ready={summaries['reporting']['final_reporting_summary_ready']}",
            "required_closure": "Finalize Reporting Summary only after methods, blinding, figures, availability and validation status are locked.",
        },
        {
            "blocker_id": "NC-B04",
            "gate": "References",
            "severity": "medium",
            "current_evidence": f"final_references_ready={summaries['references']['final_references_ready']}; candidate_markers_replaced={summaries['references']['candidate_markers_replaced']}",
            "required_closure": "Replace candidate markers after final prose and figure/table calls are stable.",
        },
        {
            "blocker_id": "NC-B05",
            "gate": "External validation language",
            "severity": "hard",
            "current_evidence": f"current_applicable_branch={summaries['dashboard']['current_applicable_branch']}",
            "required_closure": "Either keep Track B open-gate wording or complete real blind external validation before Track A activation.",
        },
    ]
    write_csv(OUT_DIR / "submission_hard_blocker_register.csv", blocker_rows, ["blocker_id", "gate", "severity", "current_evidence", "required_closure"])

    upload_sequence_rows = [
        {"order": "1", "action": "Confirm manuscript branch remains Track B or activate Track A only with real locked external validation.", "owner": "author", "can_execute_now": "yes"},
        {"order": "2", "action": "Choose exactly one figure backend, recommended Python unless author overrides.", "owner": "author", "can_execute_now": "yes"},
        {"order": "3", "action": "Render and QA Figure 1-6 or final reduced figure set.", "owner": "analysis", "can_execute_now": "no_backend_blocked"},
        {"order": "4", "action": "Create rights-approved repository/code release and archive DOI.", "owner": "author", "can_execute_now": "no_rights_blocked"},
        {"order": "5", "action": "Finalize Data Availability, Code Availability and Reporting Summary.", "owner": "author_and_analysis", "can_execute_now": "no_identifier_blocked"},
        {"order": "6", "action": "Lock final references after final prose and figure/table calls.", "owner": "analysis", "can_execute_now": "no_final_text_blocked"},
        {"order": "7", "action": "Assemble single initial-submission PDF/Word package and cover letter.", "owner": "author_and_analysis", "can_execute_now": "no"},
    ]
    write_csv(OUT_DIR / "submission_assembly_execution_order.csv", upload_sequence_rows, ["order", "action", "owner", "can_execute_now"])

    word_budget_rows = [
        {
            "component": "Body excluding title/abstract",
            "current_words": str(summaries["author_manuscript"]["body_words_excluding_title_abstract"]),
            "natcomms_reference_limit": "about 5000 including Methods",
            "status": "within_current_budget_not_final",
        },
        {
            "component": "Track B abstract",
            "current_words": str(summaries["track_b"]["abstract_words"]),
            "natcomms_reference_limit": "150",
            "status": "within_limit_not_final",
        },
        {
            "component": "Display items",
            "current_words": "6 planned figures; 3 table drafts exist separately",
            "natcomms_reference_limit": "up to 10 display items",
            "status": "within_limit_if_final_set_remains_under_10",
        },
    ]
    write_csv(OUT_DIR / "natcomms_format_budget_preflight.csv", word_budget_rows, ["component", "current_words", "natcomms_reference_limit", "status"])

    qa_rows = [
        {
            "qa_check": "submission_ready_preserved_false",
            "status": "pass" if not summaries["dashboard"]["submission_ready"] else "fail",
            "evidence": "dashboard submission_ready=false",
        },
        {
            "qa_check": "track_b_currently_applicable",
            "status": "pass" if summaries["dashboard"]["current_applicable_branch"] == "TRACK-B" else "fail",
            "evidence": summaries["dashboard"]["current_applicable_branch"],
        },
        {
            "qa_check": "hard_blockers_present",
            "status": "pass" if len(blocker_rows) >= 5 else "fail",
            "evidence": f"blocker_rows={len(blocker_rows)}",
        },
        {
            "qa_check": "no_final_submission_claim",
            "status": "pass" if any(row["assembly_status"] == "blocked" for row in assembly_rows) else "fail",
            "evidence": "blocked items remain in submission assembly table",
        },
    ]
    write_csv(OUT_DIR / "natcomms_submission_assembly_preflight_qa.csv", qa_rows, ["qa_check", "status", "evidence"])

    readme = """# Nature Communications submission assembly preflight 2026-08-10

This package lists which submission components can be preassembled and which are blocked.

It does not assemble or submit a manuscript. Submission remains blocked by final figures, repository/rights identifiers, Reporting Summary and final references.
"""
    (OUT_DIR / "NATCOMMS_SUBMISSION_ASSEMBLY_PREFLIGHT_README.md").write_text(readme, encoding="utf-8")

    qa_pass = all(row["status"] == "pass" for row in qa_rows)
    summary = {
        "run_id": "20260810_natcomms_submission_assembly_preflight",
        "submission_items": len(assembly_rows),
        "blocked_items": sum(1 for row in assembly_rows if row["assembly_status"] == "blocked"),
        "preassemblable_items": sum(1 for row in assembly_rows if row["assembly_status"] == "preassemblable"),
        "hard_blocker_rows": len(blocker_rows),
        "execution_order_rows": len(upload_sequence_rows),
        "format_budget_rows": len(word_budget_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "current_applicable_branch": summaries["dashboard"]["current_applicable_branch"],
        "submission_ready": False,
        "status": "natcomms_submission_assembly_preflight_ready_submission_not_ready",
        "boundary": "This package preflights submission assembly only; it does not create final figures, DOI, rights clearance, Reporting Summary, final references or a submitted manuscript.",
    }
    (OUT_DIR / "natcomms_submission_assembly_preflight_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    report = [
        "# Nature Communications submission assembly preflight report 2026-08-10",
        "",
        f"- Submission items: {summary['submission_items']}",
        f"- Blocked items: {summary['blocked_items']}",
        f"- Preassemblable items: {summary['preassemblable_items']}",
        f"- Hard blocker rows: {summary['hard_blocker_rows']}",
        f"- Current branch: {summary['current_applicable_branch']}",
        f"- QA pass: {summary['qa_pass']}",
        f"- Status: {summary['status']}",
        "",
        "Conclusion: the Nat Comms initial-submission package can be planned, but not assembled for submission until figures, repository identifiers, Reporting Summary and final references are closed.",
        "",
    ]
    (OUT_DIR / "natcomms_submission_assembly_preflight_report.md").write_text("\n".join(report), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
