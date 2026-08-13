#!/usr/bin/env python3
"""Build a master checklist for Nat Comms finalization gates."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "natcomms_finalization_master_checklist_20260810"

SUMMARY_PATHS = {
    "portal": BENCH_ROOT / "reports" / "natcomms_portal_upload_manifest_prelock_20260810" / "portal_upload_manifest_summary.json",
    "figures": BENCH_ROOT / "reports" / "figure_source_data_lock_20260810" / "figure_source_data_lock_summary.json",
    "repository": BENCH_ROOT / "reports" / "repository_release_manifest_lock_20260810" / "repository_release_manifest_lock_summary.json",
    "reporting": BENCH_ROOT / "reports" / "reporting_summary_finalization_prelock_20260810" / "reporting_summary_finalization_prelock_summary.json",
    "references": BENCH_ROOT / "reports" / "sentence_citation_support_lock_20260810" / "sentence_citation_support_lock_summary.json",
    "admin": BENCH_ROOT / "reports" / "natcomms_admin_declarations_prelock_20260810" / "admin_declarations_prelock_summary.json",
    "external": BENCH_ROOT / "reports" / "external_validation_contingency_framing_20260810" / "external_validation_contingency_framing_summary.json",
    "text": BENCH_ROOT / "reports" / "natcomms_initial_submission_text_preassembly_20260810" / "natcomms_text_preassembly_summary.json",
    "si": BENCH_ROOT / "reports" / "natcomms_supplementary_info_preassembly_20260810" / "supplementary_info_preassembly_summary.json",
}

AUTHOR_DECISIONS = BENCH_ROOT / "reports" / "author_decision_closure_packet_v2_20260810" / "author_decision_closure_form_v2.csv"
PORTAL_ORDER = BENCH_ROOT / "reports" / "natcomms_portal_upload_manifest_prelock_20260810" / "portal_upload_finalization_order.csv"
FORBIDDEN = BENCH_ROOT / "reports" / "submission_command_dashboard_v2_20260810" / "global_forbidden_claims_dashboard.csv"


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
    summaries = {key: read_json(path) for key, path in SUMMARY_PATHS.items()}
    author_decisions = read_csv(AUTHOR_DECISIONS)
    portal_order = read_csv(PORTAL_ORDER)
    forbidden_rows = read_csv(FORBIDDEN)

    master_rows = [
        {
            "gate_id": "FM-001",
            "gate": "Author/admin declarations",
            "current_state": "prelocked_not_final",
            "owner": "author/corresponding author",
            "control_artifact": "natcomms_admin_declarations_prelock_20260810",
            "minimum_closure_evidence": "Author-confirmed title page, author order, affiliations, corresponding author, ORCID if required, contributions, interests, funding, acknowledgements, ethics/policy choices and reviewer suggestions.",
            "can_close_locally": "no_author_input_required",
            "blocks": "cover letter; initial manuscript file; portal metadata",
            "closed": "no",
        },
        {
            "gate_id": "FM-002",
            "gate": "Manuscript branch",
            "current_state": str(summaries["external"]["current_applicable_branch"]),
            "owner": "author/advisor",
            "control_artifact": "external_validation_contingency_framing_20260810; track_b_manuscript_branch_prelock_20260810",
            "minimum_closure_evidence": "Either real blind external validation activates Track A, or author confirms Track B no-external-validation route.",
            "can_close_locally": "no_if_track_a; yes_for_track_b_wording_after_author_confirmation",
            "blocks": "title; abstract; cover letter; discussion limitation wording",
            "closed": "no",
        },
        {
            "gate_id": "FM-003",
            "gate": "Formal figures",
            "current_state": f"backend={summaries['figures']['backend_choice']}; rendered_figures={summaries['figures']['rendered_figures']}",
            "owner": "author/analysis",
            "control_artifact": "figure_rendering_preflight_20260810; figure_source_data_lock_20260810",
            "minimum_closure_evidence": "Single backend chosen, Figure 1-Figure 6 or reduced final set rendered, vector/raster exports produced, visual QA passed and final captions locked.",
            "can_close_locally": "after_author_backend_choice",
            "blocks": "main manuscript; Source Data; Reporting Summary; portal upload",
            "closed": "yes" if summaries["figures"]["final_figures_ready"] else "no",
        },
        {
            "gate_id": "FM-004",
            "gate": "Source Data and repository/code release",
            "current_state": f"repository_doi={summaries['repository']['repository_doi_created']}; code_doi={summaries['repository']['code_doi_created']}; public_release={summaries['repository']['public_release_ready']}",
            "owner": "author/institution/repository lead",
            "control_artifact": "repository_release_manifest_lock_20260810; availability_statement_prelock_20260810",
            "minimum_closure_evidence": "Rights-approved Source Data, repository DOI/accession, code archive DOI, selected licences and public/restricted access route.",
            "can_close_locally": "no_rights_and_repository_actions_required",
            "blocks": "Data Availability; Code Availability; Reporting Summary; portal upload",
            "closed": "yes" if summaries["repository"]["public_release_ready"] else "no",
        },
        {
            "gate_id": "FM-005",
            "gate": "Reporting Summary",
            "current_state": "prelock_not_final",
            "owner": "author/analysis",
            "control_artifact": "reporting_summary_finalization_prelock_20260810",
            "minimum_closure_evidence": "Every Reporting Summary field has a final answer supported by frozen Methods, figure set, Source Data, availability statements and validation status.",
            "can_close_locally": "after_other_gates",
            "blocks": "submission package; portal upload",
            "closed": "yes" if summaries["reporting"]["final_reporting_summary_ready"] else "no",
        },
        {
            "gate_id": "FM-006",
            "gate": "Final references",
            "current_state": f"candidate_markers_replaced={summaries['references']['candidate_markers_replaced']}",
            "owner": "author/reference lead",
            "control_artifact": "sentence_citation_support_lock_20260810; reference_public_verification_20260810",
            "minimum_closure_evidence": "No [P#] markers remain, Nature-style numbered references match final prose order and every citation supports the sentence claim.",
            "can_close_locally": "after_final_text_and_figure_calls",
            "blocks": "final manuscript file; portal upload",
            "closed": "yes" if summaries["references"]["final_references_ready"] else "no",
        },
        {
            "gate_id": "FM-007",
            "gate": "Final manuscript and SI files",
            "current_state": f"text_submission_ready={summaries['text']['submission_ready']}; si_submission_ready={summaries['si']['submission_ready']}",
            "owner": "writing lead/author",
            "control_artifact": "natcomms_initial_submission_text_preassembly_20260810; natcomms_supplementary_info_preassembly_20260810",
            "minimum_closure_evidence": "Final Word/PDF manuscript and final SI file generated from locked text, figures, references, statements and Source Data.",
            "can_close_locally": "after_all_prior_gates",
            "blocks": "portal upload",
            "closed": "no",
        },
        {
            "gate_id": "FM-008",
            "gate": "Portal upload readiness",
            "current_state": f"upload_ready_rows={summaries['portal']['upload_ready_rows']}; blocked_upload_rows={summaries['portal']['blocked_upload_rows']}",
            "owner": "corresponding author",
            "control_artifact": "natcomms_portal_upload_manifest_prelock_20260810",
            "minimum_closure_evidence": "Every portal upload row is upload-ready with final files and metadata; corresponding author confirms portal entries.",
            "can_close_locally": "no_corresponding_author_required",
            "blocks": "actual submission",
            "closed": "yes" if summaries["portal"]["portal_upload_ready"] else "no",
        },
    ]
    write_csv(
        OUT_DIR / "finalization_master_checklist.csv",
        master_rows,
        ["gate_id", "gate", "current_state", "owner", "control_artifact", "minimum_closure_evidence", "can_close_locally", "blocks", "closed"],
    )

    owner_rows = []
    for decision in author_decisions:
        owner_rows.append(
            {
                "queue_id": decision["decision_id"],
                "priority": decision["priority"],
                "owner": "author",
                "action": decision["decision"],
                "recommended_response": decision["recommended_response"],
                "unlocks": decision["unlocks"],
                "if_not_done": decision["if_not_decided"],
            }
        )
    for row in portal_order:
        owner_rows.append(
            {
                "queue_id": f"PORTAL-{row['order']}",
                "priority": row["order"],
                "owner": "author_and_analysis",
                "action": row["action"],
                "recommended_response": row["dependency"],
                "unlocks": "Portal upload row readiness",
                "if_not_done": "Portal upload package remains not ready.",
            }
        )
    write_csv(
        OUT_DIR / "owner_action_master_queue.csv",
        owner_rows,
        ["queue_id", "priority", "owner", "action", "recommended_response", "unlocks", "if_not_done"],
    )

    dependency_rows = [
        {"upstream_gate": "FM-001 Author/admin declarations", "downstream_gate": "FM-007 Final manuscript and SI files", "dependency_type": "metadata_text_lock"},
        {"upstream_gate": "FM-002 Manuscript branch", "downstream_gate": "FM-007 Final manuscript and SI files", "dependency_type": "claim_scope_lock"},
        {"upstream_gate": "FM-003 Formal figures", "downstream_gate": "FM-004 Source Data and repository/code release", "dependency_type": "panel_source_data_mapping"},
        {"upstream_gate": "FM-003 Formal figures", "downstream_gate": "FM-005 Reporting Summary", "dependency_type": "figure_set_lock"},
        {"upstream_gate": "FM-004 Source Data and repository/code release", "downstream_gate": "FM-005 Reporting Summary", "dependency_type": "availability_lock"},
        {"upstream_gate": "FM-005 Reporting Summary", "downstream_gate": "FM-007 Final manuscript and SI files", "dependency_type": "statement_alignment"},
        {"upstream_gate": "FM-006 Final references", "downstream_gate": "FM-007 Final manuscript and SI files", "dependency_type": "bibliography_lock"},
        {"upstream_gate": "FM-007 Final manuscript and SI files", "downstream_gate": "FM-008 Portal upload readiness", "dependency_type": "final_file_generation"},
    ]
    write_csv(
        OUT_DIR / "finalization_dependency_graph.csv",
        dependency_rows,
        ["upstream_gate", "downstream_gate", "dependency_type"],
    )

    forbidden_master_rows = []
    for row in forbidden_rows:
        forbidden_master_rows.append(
            {
                "category": row["category"],
                "forbidden_claim": row["forbidden_claim"],
                "safe_current_wording": row["safe_current_wording"],
                "master_gate_that_must_close_first": {
                    "external_validation": "FM-002 or real Track A validation",
                    "repository": "FM-004",
                    "figures": "FM-003",
                    "reporting_summary": "FM-005",
                    "references": "FM-006",
                }.get(row["category"], "FM-007"),
            }
        )
    write_csv(
        OUT_DIR / "finalization_forbidden_claims_master.csv",
        forbidden_master_rows,
        ["category", "forbidden_claim", "safe_current_wording", "master_gate_that_must_close_first"],
    )

    open_gate_count = sum(1 for row in master_rows if row["closed"] != "yes")
    local_after_author_count = sum(1 for row in master_rows if "after_author" in row["can_close_locally"])
    fully_external_count = sum(1 for row in master_rows if row["can_close_locally"].startswith("no"))
    qa_rows = [
        {"check": "Master gates exist", "result": "PASS" if len(master_rows) == 8 else "FAIL", "detail": f"{len(master_rows)} master gates."},
        {"check": "No false closure", "result": "PASS" if open_gate_count == 8 else "FAIL", "detail": f"{open_gate_count} gates remain open."},
        {"check": "Owner queue exists", "result": "PASS" if len(owner_rows) >= 10 else "FAIL", "detail": f"{len(owner_rows)} owner actions."},
        {"check": "Dependency graph exists", "result": "PASS" if len(dependency_rows) >= 8 else "FAIL", "detail": f"{len(dependency_rows)} dependencies."},
        {"check": "Forbidden claims mapped", "result": "PASS" if len(forbidden_master_rows) >= 5 else "FAIL", "detail": f"{len(forbidden_master_rows)} forbidden rows."},
    ]
    write_csv(OUT_DIR / "finalization_master_checklist_qa.csv", qa_rows, ["check", "result", "detail"])

    md = [
        "# Nat Comms finalization master checklist",
        "",
        "Boundary: this is a master control checklist for finalization work. It does not close any gate, create final files, render figures, create DOI records, finalize references or submit the manuscript.",
        "",
        f"- Master gates: {len(master_rows)}",
        f"- Open gates: {open_gate_count}",
        f"- Gates locally actionable after author choice: {local_after_author_count}",
        f"- Gates requiring author/external/institutional action: {fully_external_count}",
        "",
        "## Current critical path",
        "",
        "1. Confirm author/admin fields and Track B/Track A branch.",
        "2. Choose figure backend and render final figures.",
        "3. Finalize Source Data, repository identifiers and rights.",
        "4. Finalize Reporting Summary.",
        "5. Lock final numbered references.",
        "6. Generate final manuscript/SI files and portal upload package.",
        "",
    ]
    (OUT_DIR / "finalization_master_checklist.md").write_text("\n".join(md), encoding="utf-8")

    readme = [
        "# Nat Comms finalization master checklist",
        "",
        "Use this package as the single control layer for remaining Nature Communications finalization work.",
        "",
        "All master gates remain open at this checkpoint. This is expected and prevents accidental claims of submission readiness.",
        "",
    ]
    (OUT_DIR / "NATCOMMS_FINALIZATION_MASTER_CHECKLIST_README.md").write_text("\n".join(readme), encoding="utf-8")

    report = [
        "# Finalization master checklist report",
        "",
        f"- Master gates: {len(master_rows)}",
        f"- Open gates: {open_gate_count}",
        f"- Owner actions: {len(owner_rows)}",
        f"- Dependency edges: {len(dependency_rows)}",
        f"- Forbidden-claim rows: {len(forbidden_master_rows)}",
        f"- QA failures: {sum(1 for row in qa_rows if row['result'] == 'FAIL')}",
        "- Status: natcomms_finalization_master_checklist_ready_all_gates_open",
        "",
    ]
    (OUT_DIR / "finalization_master_checklist_report.md").write_text("\n".join(report), encoding="utf-8")

    summary = {
        "run_id": "20260810_natcomms_finalization_master_checklist",
        "master_gates": len(master_rows),
        "open_gates": open_gate_count,
        "owner_action_rows": len(owner_rows),
        "dependency_rows": len(dependency_rows),
        "forbidden_claim_rows": len(forbidden_master_rows),
        "local_after_author_choice_gates": local_after_author_count,
        "external_or_author_required_gates": fully_external_count,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] != "FAIL" for row in qa_rows),
        "submission_ready": False,
        "status": "natcomms_finalization_master_checklist_ready_all_gates_open",
        "boundary": "Master checklist consolidates remaining gates only; it does not close author/admin, branch, figure, repository, Reporting Summary, reference, final-file or portal-upload gates.",
    }
    (OUT_DIR / "finalization_master_checklist_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if summary["qa_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
