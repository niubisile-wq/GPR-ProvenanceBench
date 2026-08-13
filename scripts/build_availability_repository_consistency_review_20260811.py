#!/usr/bin/env python3
"""Review consistency across availability wording, repository predeposit and Source Data status."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "availability_repository_consistency_review_20260811"
DESKTOP_REPORT = Path.home() / "Desktop" / "NatComms_20260811_availability_repository_consistency_review.md"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


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


def update_desktop_plan(summary: dict[str, object]) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    marker = "### 20.07 Availability/repository consistency review update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- Added `reports/availability_repository_consistency_review_20260811/` and Desktop report `NatComms_20260811_availability_repository_consistency_review.md`.
- Current availability/repository state: `consistency_rows={summary["consistency_rows"]}`, `review_ready_rows={summary["review_ready_rows"]}`, `final_ready_rows={summary["final_ready_rows"]}`, `prefill_ready_fields={summary["prefill_ready_fields"]}`, `blocked_fields={summary["blocked_fields"]}`, `upload_queue_files={summary["upload_queue_files"]}`.
- Final availability state remains guarded: `repository_doi_created=false`, `code_doi_created=false`, `licence_selected=false`, `third_party_rights_cleared=false`, `submission_ready=false`.
- Boundary: this is a consistency review only; it does not create DOI/accession, select licences, clear rights, publish a repository or finalize availability statements.
"""
    if marker in text:
        start = text.index(marker)
        next_start = text.find("\n### ", start + len(marker))
        text = text[:start].rstrip() if next_start == -1 else text[:start].rstrip() + "\n\n" + text[next_start:].lstrip("\n")
    DESKTOP_PLAN.write_text(text.rstrip() + block + "\n", encoding="utf-8")
    return True


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    availability_summary = read_json(
        BENCH_ROOT
        / "reports"
        / "availability_statement_prelock_20260810"
        / "availability_statement_prelock_summary.json"
    )
    repository_summary = read_json(
        BENCH_ROOT
        / "reports"
        / "repository_predeposit_handoff_20260810"
        / "repository_predeposit_handoff_summary.json"
    )
    rights_summary = read_json(
        BENCH_ROOT
        / "reports"
        / "rights_licence_completion_handoff_20260810"
        / "rights_licence_completion_handoff_summary.json"
    )
    release_summary = read_json(
        BENCH_ROOT
        / "reports"
        / "repository_release_manifest_lock_20260810"
        / "repository_release_manifest_lock_summary.json"
    )
    source_review = read_json(
        BENCH_ROOT
        / "reports"
        / "source_data_panel_map_review_packet_20260811"
        / "source_data_panel_map_review_packet_summary.json"
    )

    metadata_rows = read_csv(
        BENCH_ROOT
        / "reports"
        / "repository_predeposit_handoff_20260810"
        / "repository_platform_metadata_prefill.csv"
    )
    upload_rows = read_csv(
        BENCH_ROOT
        / "reports"
        / "repository_predeposit_handoff_20260810"
        / "repository_file_upload_queue.csv"
    )
    rights_rows = read_csv(
        BENCH_ROOT
        / "reports"
        / "rights_licence_completion_handoff_20260810"
        / "rights_licence_decision_matrix.csv"
    )
    access_rows = read_csv(
        BENCH_ROOT
        / "reports"
        / "availability_statement_prelock_20260810"
        / "availability_access_route_matrix.csv"
    )

    consistency_rows = [
        {
            "component": "Data Availability wording",
            "current_evidence": "availability_statement_prelock_20260810",
            "current_state": f"variants={availability_summary.get('data_statement_variants')}; repository_identifier_created={availability_summary.get('repository_identifier_created')}",
            "ready_for_review": "yes",
            "ready_for_final_submission": "no",
            "blocking_reason": "Repository DOI/accession, rights/licence and final Source Data lock are missing.",
        },
        {
            "component": "Code Availability wording",
            "current_evidence": "availability_statement_prelock_20260810",
            "current_state": f"variants={availability_summary.get('code_statement_variants')}; code_doi_created={availability_summary.get('code_doi_created')}",
            "ready_for_review": "yes",
            "ready_for_final_submission": "no",
            "blocking_reason": "Public code release tag, software licence and code DOI are missing.",
        },
        {
            "component": "Repository metadata prefill",
            "current_evidence": "repository_predeposit_handoff_20260810",
            "current_state": f"fields={repository_summary.get('platform_metadata_fields')}; blocked_fields={repository_summary.get('blocked_metadata_fields')}",
            "ready_for_review": "yes",
            "ready_for_final_submission": "no",
            "blocking_reason": "Author list, licence, related identifiers and access rights are not final.",
        },
        {
            "component": "Repository upload queue",
            "current_evidence": "repository_predeposit_handoff_20260810",
            "current_state": f"upload_queue_files={repository_summary.get('upload_queue_files')}; public_release_ready={repository_summary.get('public_release_ready')}",
            "ready_for_review": "yes",
            "ready_for_final_submission": "no",
            "blocking_reason": "Rights/licence clearance and DOI creation are absent.",
        },
        {
            "component": "Rights and licence",
            "current_evidence": "rights_licence_completion_handoff_20260810",
            "current_state": f"decision_rows={rights_summary.get('decision_rows')}; licence_selected={rights_summary.get('licence_selected')}; third_party_rights_cleared={rights_summary.get('third_party_rights_cleared')}",
            "ready_for_review": "yes",
            "ready_for_final_submission": "no",
            "blocking_reason": "Licence selection and third-party rights clearance remain open.",
        },
        {
            "component": "Figure Source Data",
            "current_evidence": "source_data_panel_map_review_packet_20260811",
            "current_state": f"figures_mapped={source_review.get('figures_mapped')}; source_files_packaged={source_review.get('source_files_packaged')}; source_data_panel_map_locked={source_review.get('source_data_panel_map_locked')}",
            "ready_for_review": "yes",
            "ready_for_final_submission": "no",
            "blocking_reason": "Final figure exports and panel-level Source Data lock are absent.",
        },
        {
            "component": "Release manifest",
            "current_evidence": "repository_release_manifest_lock_20260810",
            "current_state": f"locked_candidate_files={release_summary.get('locked_candidate_files')}; repository_doi_created={release_summary.get('repository_doi_created')}; public_release_ready={release_summary.get('public_release_ready')}",
            "ready_for_review": "yes",
            "ready_for_final_submission": "no",
            "blocking_reason": "Repository DOI, code DOI, licence and rights clearance are missing.",
        },
    ]

    blocked_metadata = [row for row in metadata_rows if row["deposit_status"] == "blocked"]
    prefill_ready = [row for row in metadata_rows if row["deposit_status"] == "prefill_ready"]
    release_blockers = [
        {
            "blocker": "repository DOI/accession",
            "current_state": f"repository_doi_created={release_summary.get('repository_doi_created')}",
            "required_to_close": "Create public repository/deposit record after rights and licence clearance.",
            "can_be_done_locally": "no",
        },
        {
            "blocker": "code DOI",
            "current_state": f"code_doi_created={release_summary.get('code_doi_created')}",
            "required_to_close": "Create code release/archive DOI after software licence selection.",
            "can_be_done_locally": "no",
        },
        {
            "blocker": "licence selection",
            "current_state": f"licence_selected={rights_summary.get('licence_selected')}",
            "required_to_close": "Author/rights lead selects software and derived-data licences.",
            "can_be_done_locally": "no",
        },
        {
            "blocker": "third-party rights",
            "current_state": f"third_party_rights_cleared={rights_summary.get('third_party_rights_cleared')}",
            "required_to_close": "Confirm derived artifacts expose no prohibited raw third-party data or label hints.",
            "can_be_done_locally": "partly_review_only",
        },
        {
            "blocker": "final Source Data lock",
            "current_state": f"source_data_panel_map_locked={source_review.get('source_data_panel_map_locked')}",
            "required_to_close": "Lock panel-level Source Data after final figures and final export QA.",
            "can_be_done_locally": "after_final_figures",
        },
    ]

    qa_rows = [
        {
            "check": "all consistency components review-ready",
            "result": "PASS" if all(row["ready_for_review"] == "yes" for row in consistency_rows) else "FAIL",
            "detail": f"review_ready={sum(1 for row in consistency_rows if row['ready_for_review'] == 'yes')}",
        },
        {
            "check": "final submission remains blocked",
            "result": "PASS" if all(row["ready_for_final_submission"] == "no" for row in consistency_rows) else "FAIL",
            "detail": "no component is marked final-submission ready",
        },
        {
            "check": "metadata blocked fields preserved",
            "result": "PASS" if len(blocked_metadata) == int(repository_summary.get("blocked_metadata_fields", -1)) else "FAIL",
            "detail": f"blocked_metadata={len(blocked_metadata)}",
        },
        {
            "check": "upload queue preserved",
            "result": "PASS" if len(upload_rows) == int(repository_summary.get("upload_queue_files", -1)) else "FAIL",
            "detail": f"upload_rows={len(upload_rows)}",
        },
        {
            "check": "rights/licence blockers preserved",
            "result": "PASS" if rights_summary.get("public_release_ready") is False else "FAIL",
            "detail": f"public_release_ready={rights_summary.get('public_release_ready')}",
        },
    ]

    summary = {
        "package": "availability_repository_consistency_review_20260811",
        "consistency_rows": len(consistency_rows),
        "review_ready_rows": sum(1 for row in consistency_rows if row["ready_for_review"] == "yes"),
        "final_ready_rows": sum(1 for row in consistency_rows if row["ready_for_final_submission"] == "yes"),
        "prefill_ready_fields": len(prefill_ready),
        "blocked_fields": len(blocked_metadata),
        "upload_queue_files": len(upload_rows),
        "rights_decision_rows": len(rights_rows),
        "availability_access_routes": len(access_rows),
        "release_blockers": len(release_blockers),
        "repository_doi_created": False,
        "code_doi_created": False,
        "licence_selected": False,
        "third_party_rights_cleared": False,
        "public_release_ready": False,
        "submission_ready": False,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "desktop_report": str(DESKTOP_REPORT),
        "status": "availability_repository_consistency_review_ready_not_final",
    }

    report = f"""# Availability / Repository Consistency Review

This packet aligns availability wording, repository predeposit fields, upload
queue, rights/licence status and Source Data review state.

Current state:

1. `consistency_rows={summary["consistency_rows"]}`.
2. `review_ready_rows={summary["review_ready_rows"]}`.
3. `final_ready_rows={summary["final_ready_rows"]}`.
4. `prefill_ready_fields={summary["prefill_ready_fields"]}`.
5. `blocked_fields={summary["blocked_fields"]}`.
6. `upload_queue_files={summary["upload_queue_files"]}`.
7. `repository_doi_created=false`.
8. `code_doi_created=false`.
9. `licence_selected=false`.
10. `third_party_rights_cleared=false`.
11. `submission_ready=false`.

Use: review consistency before final Data Availability, Code Availability and
repository deposit wording.

Boundary: this is a consistency review only. It does not create DOI/accession,
select licences, clear rights, publish a repository or finalize availability
statements.
"""

    write_csv(
        OUT_DIR / "availability_repository_consistency_matrix.csv",
        [
            "component",
            "current_evidence",
            "current_state",
            "ready_for_review",
            "ready_for_final_submission",
            "blocking_reason",
        ],
        consistency_rows,
    )
    write_csv(OUT_DIR / "availability_repository_blockers.csv", ["blocker", "current_state", "required_to_close", "can_be_done_locally"], release_blockers)
    write_csv(OUT_DIR / "availability_repository_metadata_status.csv", ["platform_field", "prefill_value", "source", "deposit_status", "blocking_note"], metadata_rows)
    write_csv(OUT_DIR / "availability_repository_consistency_qa.csv", ["check", "result", "detail"], qa_rows)
    write_text(OUT_DIR / "AVAILABILITY_REPOSITORY_CONSISTENCY_README.md", report)
    write_text(OUT_DIR / "availability_repository_consistency_report.md", report)
    write_text(DESKTOP_REPORT, report)
    summary["desktop_plan_updated"] = update_desktop_plan(summary)
    write_text(OUT_DIR / "availability_repository_consistency_summary.json", json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
