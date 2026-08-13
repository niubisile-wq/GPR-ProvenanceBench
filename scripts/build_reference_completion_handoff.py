#!/usr/bin/env python3
"""Build a final-reference completion handoff without replacing candidate markers."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "reference_completion_handoff_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"

PRELOCK_DIR = REPORTS / "reference_numbering_prelock_20260810"
PUBLIC_DIR = REPORTS / "reference_public_verification_20260810"
SUPPORT_DIR = REPORTS / "sentence_citation_support_lock_20260810"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def update_desktop_plan(section: str) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    text = DESKTOP_PLAN.read_text(encoding="utf-8")
    marker = "### 18.77 Reference completion handoff update"
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

    prelock_summary = read_json(PRELOCK_DIR / "reference_numbering_prelock_summary.json")
    public_summary = read_json(PUBLIC_DIR / "reference_public_verification_summary.json")
    support_summary = read_json(SUPPORT_DIR / "sentence_citation_support_lock_summary.json")
    numbering_rows = read_csv(PRELOCK_DIR / "reference_numbering_prelock.csv")
    unresolved_rows = read_csv(PRELOCK_DIR / "unresolved_reference_lock_actions.csv")
    verified_order_rows = read_csv(PUBLIC_DIR / "current_manuscript_reference_order_verified_prelock.csv")
    remaining_action_rows = read_csv(PUBLIC_DIR / "reference_final_lock_remaining_actions.csv")
    support_rows = read_csv(SUPPORT_DIR / "sentence_citation_support_lock.csv")
    replacement_rows = read_csv(SUPPORT_DIR / "citation_marker_replacement_plan.csv")
    guardrail_rows = read_csv(SUPPORT_DIR / "citation_overclaim_guardrails.csv")

    verified_by_candidate = {row["candidate_id"]: row for row in verified_order_rows}
    completion_rows: list[dict[str, object]] = []
    for row in numbering_rows:
        candidate_id = row["candidate_id"]
        verified = verified_by_candidate.get(candidate_id, {})
        completion_rows.append(
            {
                "proposed_reference_number": row["proposed_reference_number"],
                "candidate_id": candidate_id,
                "authors_short": row["authors_short"],
                "year": row["year"],
                "title": row["title"],
                "doi": row["doi"],
                "current_marker_count": row["current_marker_count"],
                "metadata_verified": verified.get("metadata_verified", "no"),
                "support_role": row["support_role"],
                "current_lock_state": "prelock_only_final_order_pending",
                "final_lock_requirement": "final prose, figure/table calls, support audit and final RIS/ENW export are all stable",
            }
        )

    marker_rows: list[dict[str, object]] = []
    for index, row in enumerate(replacement_rows, start=1):
        marker_rows.append(
            {
                "replacement_id": f"REF-REPLACE-{index:03d}",
                "marker": row["marker"],
                "candidate_ids": row["candidate_ids"],
                "current_line_number": row["current_line_number"],
                "replacement_allowed_now": row["replacement_allowed_now"],
                "replacement_blocker": row["replacement_blocker"],
                "minimum_replacement_evidence": row["minimum_replacement_evidence"],
                "current_decision": "keep_candidate_marker",
            }
        )

    manual_rows = [
        {
            "manual_check_id": f"REF-MANUAL-{index:03d}",
            "required_action": row.get("remaining_action", row.get("required_action", "")),
            "severity": row["severity"],
            "closure_evidence": row.get("closure_evidence", ""),
            "current_status": "open",
        }
        for index, row in enumerate(remaining_action_rows + unresolved_rows, start=1)
    ]

    export_rows = [
        {
            "export_item": "candidate_references_prelock.ris",
            "current_status": "prelock_export_available",
            "final_export_trigger": "final manuscript citation order is stable and candidate markers are replaced",
            "allowed_now": "no",
        },
        {
            "export_item": "candidate_references_prelock.enw",
            "current_status": "prelock_export_available",
            "final_export_trigger": "final manuscript citation order is stable and candidate markers are replaced",
            "allowed_now": "no",
        },
        {
            "export_item": "final_numbered_reference_list",
            "current_status": "not_created",
            "final_export_trigger": "manual publisher verification and sentence support audit are complete",
            "allowed_now": "no",
        },
    ]

    no_go_rows = [
        {
            "no_go_id": "REF-NOGO-001",
            "shortcut": "Replace [P#] markers before final prose and figure/table calls are stable",
            "reason": "Citation order can change while figures, submission text and references are still moving.",
            "decision": "forbidden",
        },
        {
            "no_go_id": "REF-NOGO-002",
            "shortcut": "Use external references as evidence for this project's internal metrics",
            "reason": "Balanced-accuracy deltas and gate statuses must be supported by internal figures/source data.",
            "decision": "forbidden",
        },
        {
            "no_go_id": "REF-NOGO-003",
            "shortcut": "Treat metadata verification as final support verification",
            "reason": "A DOI/title match does not prove that the cited sentence is appropriately supported.",
            "decision": "forbidden",
        },
        {
            "no_go_id": "REF-NOGO-004",
            "shortcut": "Generate final RIS/ENW before numbering lock",
            "reason": "Reference-manager exports must match final manuscript numbering.",
            "decision": "forbidden",
        },
    ]

    qa_rows = [
        {
            "check": "prelock_numbering_and_public_verification_imported",
            "result": "PASS" if prelock_summary.get("qa_pass") and public_summary.get("metadata_match_failures") == 0 else "FAIL",
            "detail": f"prelock_qa={prelock_summary.get('qa_pass')}; metadata_failures={public_summary.get('metadata_match_failures')}",
        },
        {
            "check": "sentence_support_lock_imported",
            "result": "PASS" if support_summary.get("qa_pass") and support_summary.get("candidate_markers_replaced") is False else "FAIL",
            "detail": f"support_qa={support_summary.get('qa_pass')}; candidate_markers_replaced={support_summary.get('candidate_markers_replaced')}",
        },
        {
            "check": "all_marker_replacements_blocked",
            "result": "PASS" if all(row["replacement_allowed_now"].lower() == "false" for row in replacement_rows) else "FAIL",
            "detail": f"replacement_rows={len(replacement_rows)}",
        },
        {
            "check": "manual_actions_remain_open",
            "result": "PASS" if len(manual_rows) > 0 and all(row["current_status"] == "open" for row in manual_rows) else "FAIL",
            "detail": f"manual_rows={len(manual_rows)}",
        },
        {
            "check": "final_references_not_claimed",
            "result": "PASS",
            "detail": "This handoff does not replace markers or create final numbered references.",
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(
        OUT_DIR / "reference_completion_matrix.csv",
        completion_rows,
        [
            "proposed_reference_number",
            "candidate_id",
            "authors_short",
            "year",
            "title",
            "doi",
            "current_marker_count",
            "metadata_verified",
            "support_role",
            "current_lock_state",
            "final_lock_requirement",
        ],
    )
    write_csv(
        OUT_DIR / "citation_marker_final_replacement_queue.csv",
        marker_rows,
        [
            "replacement_id",
            "marker",
            "candidate_ids",
            "current_line_number",
            "replacement_allowed_now",
            "replacement_blocker",
            "minimum_replacement_evidence",
            "current_decision",
        ],
    )
    write_csv(OUT_DIR / "reference_manual_verification_queue.csv", manual_rows, ["manual_check_id", "required_action", "severity", "closure_evidence", "current_status"])
    write_csv(OUT_DIR / "reference_export_finalization_queue.csv", export_rows, ["export_item", "current_status", "final_export_trigger", "allowed_now"])
    write_csv(OUT_DIR / "reference_no_go_shortcuts.csv", no_go_rows, ["no_go_id", "shortcut", "reason", "decision"])
    write_csv(OUT_DIR / "reference_completion_handoff_qa.csv", qa_rows, ["check", "result", "detail"])

    readme = """# Reference Completion Handoff 2026-08-10

This package turns the reference numbering prelock, public metadata verification and sentence-level support lock into a final-reference handoff.

Boundary: candidate markers are not replaced, final numbering is not locked, final RIS/ENW exports are not created and final references are not submission-ready.
"""
    write_text(OUT_DIR / "REFERENCE_COMPLETION_HANDOFF_README.md", readme)

    report = [
        "# Reference completion handoff report 2026-08-10",
        "",
        "Status: `reference_completion_handoff_ready_final_references_not_locked`",
        "",
        f"- Reference completion rows: {len(completion_rows)}",
        f"- Marker replacement rows: {len(marker_rows)}",
        f"- Manual verification rows: {len(manual_rows)}",
        f"- Export queue rows: {len(export_rows)}",
        f"- Guardrail rows imported: {len(guardrail_rows)}",
        f"- Sentence support rows imported: {len(support_rows)}",
        f"- QA pass: {qa_pass}",
        "",
        "Conclusion: final reference work is now queued, but marker replacement and final numbering remain blocked until final prose and figure/table calls are stable.",
        "",
    ]
    write_text(OUT_DIR / "reference_completion_handoff_report.md", "\n".join(report))

    summary = {
        "package": "reference_completion_handoff_20260810",
        "reference_completion_rows": len(completion_rows),
        "candidate_markers_found": prelock_summary.get("markers_found"),
        "unique_candidate_ids_in_manuscript": prelock_summary.get("unique_candidate_ids_in_manuscript"),
        "marker_replacement_rows": len(marker_rows),
        "marker_replacements_allowed_now": 0,
        "manual_verification_rows": len(manual_rows),
        "manual_verification_rows_closed": 0,
        "export_queue_rows": len(export_rows),
        "guardrail_rows_imported": len(guardrail_rows),
        "sentence_support_rows_imported": len(support_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "candidate_markers_replaced": False,
        "final_references_ready": False,
        "submission_ready": False,
        "status": "reference_completion_handoff_ready_final_references_not_locked",
    }

    section = f"""### 18.77 Reference completion handoff update

Added a reference completion handoff. This connects numbering prelock, public metadata verification and sentence-level support lock into a final-reference execution queue.

New directory: `{OUT_DIR}`

New files:
1. `reference_completion_matrix.csv`
2. `citation_marker_final_replacement_queue.csv`
3. `reference_manual_verification_queue.csv`
4. `reference_export_finalization_queue.csv`
5. `reference_no_go_shortcuts.csv`
6. `reference_completion_handoff_qa.csv`
7. `REFERENCE_COMPLETION_HANDOFF_README.md`
8. `reference_completion_handoff_report.md`
9. `reference_completion_handoff_summary.json`

Current result:
1. reference_completion_rows = {summary['reference_completion_rows']}
2. candidate_markers_found = {summary['candidate_markers_found']}
3. marker_replacement_rows = {summary['marker_replacement_rows']}
4. marker_replacements_allowed_now = 0
5. manual_verification_rows = {summary['manual_verification_rows']}
6. manual_verification_rows_closed = 0
7. export_queue_rows = {summary['export_queue_rows']}
8. qa_pass = {str(qa_pass).lower()}
9. candidate_markers_replaced = false
10. final_references_ready = false
11. submission_ready = false
12. status = `reference_completion_handoff_ready_final_references_not_locked`

Boundary:
1. This step does not replace `[P#]` markers.
2. This step does not lock final numbered references.
3. This step does not create final RIS/ENW exports.
4. This step does not make the manuscript submission-ready."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "reference_completion_handoff_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("Reference completion handoff QA failed")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
