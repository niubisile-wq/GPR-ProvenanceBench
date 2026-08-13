#!/usr/bin/env python3
"""Build a completion handoff for Nature Communications Reporting Summary fields."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "reporting_summary_completion_handoff_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"

DRAFT_DIR = REPORTS / "reporting_summary_draft_20260810"
PRELOCK_DIR = REPORTS / "reporting_summary_finalization_prelock_20260810"
AUTHOR_REPLY = REPORTS / "natcomms_author_finalization_reply_packet_20260810" / "reporting_summary_author_reply_sheet.csv"
FIGURE_HANDOFF = REPORTS / "figure_backend_scope_decision_handoff_20260810" / "figure_backend_scope_decision_handoff_summary.json"
EXTERNAL_TRIAGE = REPORTS / "external_asset_triage_register_20260810" / "external_asset_triage_register_summary.json"
REPOSITORY_HANDOFF = REPORTS / "repository_predeposit_handoff_20260810" / "repository_predeposit_handoff_summary.json"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def update_desktop_plan(section: str) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    text = DESKTOP_PLAN.read_text(encoding="utf-8")
    marker = "### 18.76 Reporting Summary completion handoff update"
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


def reply_blank_count(rows: list[dict[str, str]]) -> int:
    return sum(1 for row in rows if not (row.get("author_reply") or "").strip())


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    draft_rows = read_csv(DRAFT_DIR / "reporting_summary_draft_answers.csv")
    unresolved_rows = read_csv(DRAFT_DIR / "reporting_summary_unresolved_items.csv")
    method_trace_rows = read_csv(DRAFT_DIR / "reporting_summary_method_trace.csv")
    lock_rows = read_csv(PRELOCK_DIR / "reporting_summary_final_lock_matrix.csv")
    confirmation_rows = read_csv(PRELOCK_DIR / "reporting_summary_author_confirmation_checklist.csv")
    availability_rows = read_csv(PRELOCK_DIR / "reporting_summary_availability_gate_crosswalk.csv")
    forbidden_rows = read_csv(PRELOCK_DIR / "reporting_summary_forbidden_final_wording.csv")
    author_reply_rows = read_csv(AUTHOR_REPLY)
    figure_handoff = read_json(FIGURE_HANDOFF)
    external_triage = read_json(EXTERNAL_TRIAGE)
    repository_handoff = read_json(REPOSITORY_HANDOFF)

    draft_by_item = {row["reporting_item"]: row for row in draft_rows}
    trace_by_item = {row["reporting_item"]: row for row in method_trace_rows}

    completion_rows: list[dict[str, object]] = []
    for row in lock_rows:
        item = row["reporting_item"]
        draft = draft_by_item.get(item, {})
        trace = trace_by_item.get(item, {})
        if row["can_lock_now"].lower() == "yes":
            lock_state = "lockable"
        elif row["prelock_level"] == "gate_blocked":
            lock_state = "blocked_by_external_or_repository_gate"
        else:
            lock_state = "draft_ready_waiting_final_artifacts"
        completion_rows.append(
            {
                "reporting_item": item,
                "current_prelock_answer": draft.get("draft_answer", ""),
                "method_modules": trace.get("method_modules", ""),
                "current_status": row["current_status"],
                "completion_state": lock_state,
                "owner": row["owner"],
                "final_lock_trigger": row["final_lock_trigger"],
                "missing_before_submission": row["missing_before_submission"],
                "forbidden_final_wording": row["forbidden_final_wording"],
            }
        )

    author_handoff_rows = [
        {
            "confirmation_id": row["confirmation_id"],
            "owner": row["owner"],
            "question": row["question"],
            "blocks": row["blocks"],
            "current_author_reply_state": "blank",
            "after_reply_validation": "rerun reporting_summary_completion_handoff and full M0-M2 checks",
        }
        for row in confirmation_rows
    ]

    gate_dependency_rows = [
        {
            "dependency": "figure_backend_and_scope",
            "current_state": "blocked" if not figure_handoff.get("backend_selected") else "selected",
            "evidence": "figure_backend_scope_decision_handoff_summary.json",
            "impacted_reporting_items": "Study design; Randomization and split strategy; Data availability",
            "completion_requirement": "backend_selected=true, scope_confirmed=true, rendered figures and panel-level Source Data QA complete",
        },
        {
            "dependency": "blind_external_validation",
            "current_state": "NO-GO" if not external_triage.get("blind_external_gate_closed") else "closed",
            "evidence": "external_asset_triage_register_summary.json",
            "impacted_reporting_items": "Blinding; External validation",
            "completion_requirement": "real_external_asset_acquired=true, strict_sha_manifest_passed=true, one_shot_prediction_frozen=true and locked evaluation complete",
        },
        {
            "dependency": "repository_identifiers_and_rights",
            "current_state": "blocked" if not repository_handoff.get("repository_doi_created") else "identifier_created",
            "evidence": "repository_predeposit_handoff_summary.json",
            "impacted_reporting_items": "Software and code availability; Data availability; Sample size and exclusions",
            "completion_requirement": "repository DOI/accession, code DOI, licences and third-party rights decisions exist",
        },
    ]

    command_rows = [
        {
            "order": 1,
            "command_or_action": "Collect four Reporting Summary author confirmations",
            "condition": "author reply sheet has real replies, not placeholders",
            "expected_output": "reporting_summary_author_reply_sheet.csv completed",
            "stop_rule": "Do not mark final Reporting Summary ready while any reply is blank.",
        },
        {
            "order": 2,
            "command_or_action": "Close figure backend/scope and render final figures",
            "condition": "backend and scope selected by author",
            "expected_output": "rendered figures, visual QA and final Source Data mapping",
            "stop_rule": "Do not fill final figure/source-data answers before visual QA.",
        },
        {
            "order": 3,
            "command_or_action": "Resolve repository DOI/code DOI/licence/rights",
            "condition": "release scope and final Source Data are locked",
            "expected_output": "repository identifiers and availability wording",
            "stop_rule": "Do not write public availability claims without identifiers and rights.",
        },
        {
            "order": 4,
            "command_or_action": "Resolve blind external status",
            "condition": "real external asset exists or Track B fallback remains explicit",
            "expected_output": "completed external validation fields or explicitly open-gate wording",
            "stop_rule": "Do not write completed blinding from templates or dry runs.",
        },
        {
            "order": 5,
            "command_or_action": "Rerun reporting summary finalization prelock and full M0-M2",
            "condition": "all upstream artifacts are updated",
            "expected_output": "QA pass and finalization readiness only if all blockers are closed",
            "stop_rule": "Any unresolved high-risk row blocks final Reporting Summary.",
        },
    ]

    blank_author_reply_rows = reply_blank_count(author_reply_rows)
    qa_rows = [
        {
            "check": "all_draft_items_mapped_to_completion_rows",
            "result": "PASS" if len(completion_rows) == len(draft_rows) == 8 else "FAIL",
            "detail": f"completion_rows={len(completion_rows)}; draft_rows={len(draft_rows)}",
        },
        {
            "check": "blocked_dependencies_preserved",
            "result": "PASS" if any(row["completion_state"] == "blocked_by_external_or_repository_gate" for row in completion_rows) else "FAIL",
            "detail": "Blinding, data/code availability and external validation must remain blocked.",
        },
        {
            "check": "author_confirmations_remain_uncollected",
            "result": "PASS" if blank_author_reply_rows == len(author_reply_rows) else "FAIL",
            "detail": f"blank_author_reply_rows={blank_author_reply_rows}; author_reply_rows={len(author_reply_rows)}",
        },
        {
            "check": "upstream_gate_handoffs_imported",
            "result": "PASS" if figure_handoff.get("qa_pass") and external_triage.get("qa_pass") and repository_handoff.get("qa_pass") else "FAIL",
            "detail": "figure, external and repository handoff summaries imported.",
        },
        {
            "check": "final_reporting_summary_not_claimed",
            "result": "PASS",
            "detail": "This package is a handoff only; final Reporting Summary remains false.",
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(
        OUT_DIR / "reporting_summary_item_completion_matrix.csv",
        completion_rows,
        [
            "reporting_item",
            "current_prelock_answer",
            "method_modules",
            "current_status",
            "completion_state",
            "owner",
            "final_lock_trigger",
            "missing_before_submission",
            "forbidden_final_wording",
        ],
    )
    write_csv(
        OUT_DIR / "reporting_summary_author_handoff_queue.csv",
        author_handoff_rows,
        ["confirmation_id", "owner", "question", "blocks", "current_author_reply_state", "after_reply_validation"],
    )
    write_csv(
        OUT_DIR / "reporting_summary_gate_dependency_map.csv",
        gate_dependency_rows,
        ["dependency", "current_state", "evidence", "impacted_reporting_items", "completion_requirement"],
    )
    write_csv(
        OUT_DIR / "reporting_summary_completion_command_queue.csv",
        command_rows,
        ["order", "command_or_action", "condition", "expected_output", "stop_rule"],
    )
    write_csv(OUT_DIR / "reporting_summary_completion_handoff_qa.csv", qa_rows, ["check", "result", "detail"])

    readme = """# Reporting Summary Completion Handoff 2026-08-10

This package converts the Reporting Summary draft and finalization prelock into a field-level completion handoff.

It maps each item to the current prelock answer, owner, final lock trigger, missing evidence and forbidden final wording.

Boundary: this package does not create a final Nature Communications Reporting Summary and does not close blinding, figure, repository, rights, author-confirmation or external-validation gates.
"""
    write_text(OUT_DIR / "REPORTING_SUMMARY_COMPLETION_HANDOFF_README.md", readme)

    report = [
        "# Reporting Summary completion handoff report 2026-08-10",
        "",
        "Status: `reporting_summary_completion_handoff_ready_not_final`",
        "",
        f"- Reporting Summary items mapped: {len(completion_rows)}",
        f"- Author confirmation rows: {len(author_handoff_rows)}",
        f"- Gate dependency rows: {len(gate_dependency_rows)}",
        f"- Completion command rows: {len(command_rows)}",
        f"- Unresolved upstream items imported: {len(unresolved_rows)}",
        f"- QA pass: {qa_pass}",
        "",
        "Conclusion: every current Reporting Summary field has a completion trigger, but final lock remains blocked by author confirmations, final figures, repository identifiers, rights/licence decisions and blind external status.",
        "",
    ]
    write_text(OUT_DIR / "reporting_summary_completion_handoff_report.md", "\n".join(report))

    summary = {
        "package": "reporting_summary_completion_handoff_20260810",
        "reporting_items_mapped": len(completion_rows),
        "draft_items": len(draft_rows),
        "author_confirmation_rows": len(author_handoff_rows),
        "author_confirmations_collected": 0,
        "gate_dependency_rows": len(gate_dependency_rows),
        "completion_command_rows": len(command_rows),
        "unresolved_items_imported": len(unresolved_rows),
        "high_risk_items": sum(1 for row in draft_rows if row.get("risk") == "high"),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "final_reporting_summary_ready": False,
        "submission_ready": False,
        "status": "reporting_summary_completion_handoff_ready_not_final",
    }

    section = f"""### 18.76 Reporting Summary completion handoff update

Added a Reporting Summary completion handoff. This maps every current Reporting Summary item to its prelock answer, owner, final lock trigger, missing evidence and forbidden final wording.

New directory: `{OUT_DIR}`

New files:
1. `reporting_summary_item_completion_matrix.csv`
2. `reporting_summary_author_handoff_queue.csv`
3. `reporting_summary_gate_dependency_map.csv`
4. `reporting_summary_completion_command_queue.csv`
5. `reporting_summary_completion_handoff_qa.csv`
6. `REPORTING_SUMMARY_COMPLETION_HANDOFF_README.md`
7. `reporting_summary_completion_handoff_report.md`
8. `reporting_summary_completion_handoff_summary.json`

Current result:
1. reporting_items_mapped = {summary['reporting_items_mapped']}
2. author_confirmation_rows = {summary['author_confirmation_rows']}
3. author_confirmations_collected = 0
4. gate_dependency_rows = {summary['gate_dependency_rows']}
5. completion_command_rows = {summary['completion_command_rows']}
6. unresolved_items_imported = {summary['unresolved_items_imported']}
7. high_risk_items = {summary['high_risk_items']}
8. qa_pass = {str(qa_pass).lower()}
9. final_reporting_summary_ready = false
10. submission_ready = false
11. status = `reporting_summary_completion_handoff_ready_not_final`

Boundary:
1. This step does not finalize the Reporting Summary.
2. This step does not collect author confirmations.
3. This step does not close figure, repository, rights or blind external gates.
4. This step does not make the manuscript submission-ready."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "reporting_summary_completion_handoff_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("Reporting Summary completion handoff QA failed")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
