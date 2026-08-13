#!/usr/bin/env python3
"""Validate whether the Reporting Summary can be finalized."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "reporting_summary_final_lock_validator_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"

DRAFT_DIR = BENCH_ROOT / "reports" / "reporting_summary_draft_20260810"
HANDOFF_DIR = BENCH_ROOT / "reports" / "reporting_summary_completion_handoff_20260810"
PRELOCK_DIR = BENCH_ROOT / "reports" / "reporting_summary_finalization_prelock_20260810"
AVAIL_VALIDATOR_DIR = BENCH_ROOT / "reports" / "availability_repository_finalization_validator_20260810"
REF_VALIDATOR_DIR = BENCH_ROOT / "reports" / "reference_final_lock_validator_20260810"
FIGURE_SD_DIR = BENCH_ROOT / "reports" / "python_figure_source_data_panel_map_preflight_20260810"

DRAFT_SUMMARY = DRAFT_DIR / "reporting_summary_draft_summary.json"
HANDOFF_SUMMARY = HANDOFF_DIR / "reporting_summary_completion_handoff_summary.json"
PRELOCK_SUMMARY = PRELOCK_DIR / "reporting_summary_finalization_prelock_summary.json"
AVAIL_SUMMARY = AVAIL_VALIDATOR_DIR / "availability_repository_finalization_validator_summary.json"
REF_SUMMARY = REF_VALIDATOR_DIR / "reference_final_lock_validator_summary.json"
FIGURE_SD_SUMMARY = FIGURE_SD_DIR / "python_figure_source_data_panel_map_preflight_summary.json"

DRAFT_ANSWERS = DRAFT_DIR / "reporting_summary_draft_answers.csv"
UNRESOLVED = DRAFT_DIR / "reporting_summary_unresolved_items.csv"
ITEM_MATRIX = HANDOFF_DIR / "reporting_summary_item_completion_matrix.csv"
AUTHOR_QUEUE = HANDOFF_DIR / "reporting_summary_author_handoff_queue.csv"
DEPENDENCY_MAP = HANDOFF_DIR / "reporting_summary_gate_dependency_map.csv"
FINAL_LOCK_MATRIX = PRELOCK_DIR / "reporting_summary_final_lock_matrix.csv"
AUTHOR_CHECKLIST = PRELOCK_DIR / "reporting_summary_author_confirmation_checklist.csv"
FORBIDDEN_WORDING = PRELOCK_DIR / "reporting_summary_forbidden_final_wording.csv"
AVAIL_CROSSWALK = PRELOCK_DIR / "reporting_summary_availability_gate_crosswalk.csv"


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
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    marker = "### 19.10 Reporting Summary final lock validator update"
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

    draft_summary = read_json(DRAFT_SUMMARY)
    handoff_summary = read_json(HANDOFF_SUMMARY)
    prelock_summary = read_json(PRELOCK_SUMMARY)
    avail_summary = read_json(AVAIL_SUMMARY)
    ref_summary = read_json(REF_SUMMARY)
    figure_sd_summary = read_json(FIGURE_SD_SUMMARY)

    draft_rows = read_csv(DRAFT_ANSWERS)
    unresolved_rows = read_csv(UNRESOLVED)
    item_rows = read_csv(ITEM_MATRIX)
    author_rows = read_csv(AUTHOR_QUEUE)
    dependency_rows = read_csv(DEPENDENCY_MAP)
    final_lock_rows = read_csv(FINAL_LOCK_MATRIX)
    author_check_rows = read_csv(AUTHOR_CHECKLIST)
    forbidden_rows = read_csv(FORBIDDEN_WORDING)
    avail_crosswalk_rows = read_csv(AVAIL_CROSSWALK)

    lockable_rows = [row for row in final_lock_rows if row.get("can_lock_now") == "yes"]
    author_confirmed = [row for row in author_rows if row.get("current_author_reply_state") not in {"blank", "", "pending"}]
    open_dependencies = [row for row in dependency_rows if row.get("current_state") in {"blocked", "NO-GO", "open"}]
    open_avail_crosswalk = [row for row in avail_crosswalk_rows if row.get("current_state") == "open"]

    gate_rows = [
        {
            "gate_id": "RS-FINAL-001",
            "requirement": "All Reporting Summary rows are lockable",
            "current_state": f"lockable={len(lockable_rows)} of {len(final_lock_rows)}",
            "passes_now": "no",
            "blocking_reason": "Every Reporting Summary item remains draft/prelock or gate-blocked.",
        },
        {
            "gate_id": "RS-FINAL-002",
            "requirement": "Author confirmations are collected",
            "current_state": f"confirmed={len(author_confirmed)} of {len(author_rows)}",
            "passes_now": "no",
            "blocking_reason": "Author confirmation rows remain blank.",
        },
        {
            "gate_id": "RS-FINAL-003",
            "requirement": "Availability/repository gates are closed",
            "current_state": f"open_availability_gates={avail_summary.get('open_availability_gates')}; repository_doi_created={avail_summary.get('repository_doi_created')}",
            "passes_now": "no",
            "blocking_reason": "Repository DOI, code DOI, licence and rights gates remain open.",
        },
        {
            "gate_id": "RS-FINAL-004",
            "requirement": "Final figures and source data are locked",
            "current_state": f"final_figures_ready={figure_sd_summary.get('final_figures_ready')}; source_data_panel_map_locked={figure_sd_summary.get('source_data_panel_map_locked')}",
            "passes_now": "no",
            "blocking_reason": "Final rendered figures and panel-level Source Data are not locked.",
        },
        {
            "gate_id": "RS-FINAL-005",
            "requirement": "Final references are locked",
            "current_state": f"final_references_ready={ref_summary.get('final_references_ready')}; marker_replacements_allowed_now={ref_summary.get('marker_replacements_allowed_now')}",
            "passes_now": "no",
            "blocking_reason": "Candidate citation markers and final reference exports remain blocked.",
        },
        {
            "gate_id": "RS-FINAL-006",
            "requirement": "External/blinding status is resolved",
            "current_state": "blind external validation remains NO-GO or explicitly open-gate Track B",
            "passes_now": "no",
            "blocking_reason": "No real strict-SHA blind external asset and locked held-label evaluation are available.",
        },
    ]

    item_status_rows = []
    final_lock_by_item = {row["reporting_item"]: row for row in final_lock_rows}
    for row in item_rows:
        lock_row = final_lock_by_item.get(row["reporting_item"], {})
        item_status_rows.append(
            {
                "reporting_item": row["reporting_item"],
                "current_status": row.get("current_status"),
                "completion_state": row.get("completion_state"),
                "can_lock_now": lock_row.get("can_lock_now", "no"),
                "owner": row.get("owner"),
                "blocking_reason": row.get("missing_before_submission"),
                "forbidden_final_wording": row.get("forbidden_final_wording"),
            }
        )

    blocker_rows = [
        {
            "blocker_id": "RS-BLOCK-001",
            "blocker": "author_confirmations_missing",
            "evidence": f"{len(author_confirmed)} of {len(author_rows)} author confirmations collected",
            "next_required_evidence": "Returned author confirmation sheet with final figure/statistics/external/repository answers.",
        },
        {
            "blocker_id": "RS-BLOCK-002",
            "blocker": "availability_repository_not_final",
            "evidence": f"open_availability_gates={avail_summary.get('open_availability_gates')}",
            "next_required_evidence": "Repository DOI/accession, code DOI, licence and rights clearance.",
        },
        {
            "blocker_id": "RS-BLOCK-003",
            "blocker": "figures_source_data_not_final",
            "evidence": f"final_figures_ready={figure_sd_summary.get('final_figures_ready')}; source_data_panel_map_locked={figure_sd_summary.get('source_data_panel_map_locked')}",
            "next_required_evidence": "Final figure exports, visual QA and Source Data panel-map lock.",
        },
        {
            "blocker_id": "RS-BLOCK-004",
            "blocker": "external_validation_or_track_b_not_author_confirmed",
            "evidence": "External validation remains open; Track B fallback is prelocked but not final author-confirmed.",
            "next_required_evidence": "Author/external holder decision preserving Track B open-gate wording or real external validation evidence.",
        },
        {
            "blocker_id": "RS-BLOCK-005",
            "blocker": "references_not_final",
            "evidence": f"final_references_ready={ref_summary.get('final_references_ready')}",
            "next_required_evidence": "Final numbered references and manually verified support lock.",
        },
    ]

    command_rows = [
        {"order": 1, "command": "py scripts\\build_reporting_summary_draft.py", "run_now": "yes", "purpose": "Refresh draft answers."},
        {"order": 2, "command": "py scripts\\build_reporting_summary_completion_handoff.py", "run_now": "yes", "purpose": "Refresh author confirmation handoff."},
        {"order": 3, "command": "py scripts\\build_reporting_summary_finalization_prelock.py", "run_now": "yes", "purpose": "Refresh finalization prelock."},
        {"order": 4, "command": "py scripts\\build_reporting_summary_final_lock_validator.py", "run_now": "yes", "purpose": "Refresh this final lock validator."},
        {"order": 5, "command": "Create final Reporting Summary answers", "run_now": "no", "purpose": "Allowed only after all final lock gates pass."},
    ]

    qa_rows = [
        {
            "check": "eight_reporting_items_indexed",
            "result": "PASS" if len(draft_rows) == 8 and len(item_rows) == 8 and len(final_lock_rows) == 8 else "FAIL",
            "detail": f"draft={len(draft_rows)}; item_matrix={len(item_rows)}; final_lock={len(final_lock_rows)}",
        },
        {
            "check": "no_items_lockable_now",
            "result": "PASS" if len(lockable_rows) == 0 else "FAIL",
            "detail": f"lockable_rows={len(lockable_rows)}",
        },
        {
            "check": "author_confirmations_blank",
            "result": "PASS" if len(author_confirmed) == 0 and len(author_rows) == 4 else "FAIL",
            "detail": f"author_rows={len(author_rows)}; confirmed={len(author_confirmed)}",
        },
        {
            "check": "dependencies_open",
            "result": "PASS" if len(open_dependencies) == 3 and len(open_avail_crosswalk) == 5 else "FAIL",
            "detail": f"open_dependencies={len(open_dependencies)}; open_availability_crosswalk={len(open_avail_crosswalk)}",
        },
        {
            "check": "final_reporting_summary_not_ready",
            "result": "PASS" if draft_summary.get("final_reporting_summary_ready") is False and handoff_summary.get("final_reporting_summary_ready") is False and prelock_summary.get("final_reporting_summary_ready") is False else "FAIL",
            "detail": f"draft={draft_summary.get('final_reporting_summary_ready')}; handoff={handoff_summary.get('final_reporting_summary_ready')}; prelock={prelock_summary.get('final_reporting_summary_ready')}",
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(OUT_DIR / "reporting_summary_final_lock_gate_matrix.csv", gate_rows, ["gate_id", "requirement", "current_state", "passes_now", "blocking_reason"])
    write_csv(OUT_DIR / "reporting_summary_item_final_lock_status.csv", item_status_rows, ["reporting_item", "current_status", "completion_state", "can_lock_now", "owner", "blocking_reason", "forbidden_final_wording"])
    write_csv(OUT_DIR / "reporting_summary_final_lock_blockers.csv", blocker_rows, ["blocker_id", "blocker", "evidence", "next_required_evidence"])
    write_csv(OUT_DIR / "reporting_summary_final_lock_command_queue.csv", command_rows, ["order", "command", "run_now", "purpose"])
    write_csv(OUT_DIR / "reporting_summary_final_lock_validator_qa.csv", qa_rows, ["check", "result", "detail"])
    write_csv(OUT_DIR / "reporting_summary_forbidden_final_wording_import.csv", forbidden_rows, list(forbidden_rows[0].keys()))

    report = [
        "# Reporting Summary final lock validator 2026-08-10",
        "",
        "Status: `reporting_summary_final_lock_validator_ready_blocked`",
        "",
        f"1. Reporting Summary items indexed: {len(item_rows)}",
        f"2. Lockable items now: {len(lockable_rows)}",
        f"3. Author confirmations collected: {len(author_confirmed)} of {len(author_rows)}",
        f"4. Unresolved rows imported: {len(unresolved_rows)}",
        f"5. Forbidden final wording rows imported: {len(forbidden_rows)}",
        f"6. QA pass: {str(qa_pass).lower()}",
        "",
        "Boundary: this validator does not create final Reporting Summary answers or close author, figure, repository, reference or external-validation gates.",
        "",
    ]
    write_text(OUT_DIR / "REPORTING_SUMMARY_FINAL_LOCK_VALIDATOR_README.md", "\n".join(report))
    write_text(OUT_DIR / "reporting_summary_final_lock_validator_report.md", "\n".join(report))

    summary = {
        "package": "reporting_summary_final_lock_validator_20260810",
        "gate_rows": len(gate_rows),
        "item_status_rows": len(item_status_rows),
        "blocker_rows": len(blocker_rows),
        "command_rows": len(command_rows),
        "forbidden_wording_rows": len(forbidden_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "reporting_items": len(item_rows),
        "lockable_reporting_items_now": len(lockable_rows),
        "author_confirmation_rows": len(author_rows),
        "author_confirmations_collected": len(author_confirmed),
        "open_dependency_rows": len(open_dependencies),
        "open_availability_crosswalk_rows": len(open_avail_crosswalk),
        "unresolved_items_imported": len(unresolved_rows),
        "high_risk_items": draft_summary.get("high_risk_items"),
        "final_reporting_summary_ready": False,
        "submission_ready": False,
        "status": "reporting_summary_final_lock_validator_ready_blocked",
    }

    section = f"""### 19.10 Reporting Summary final lock validator update

Added a final-lock validator for the Nature Communications Reporting Summary fields.

New directory: `{OUT_DIR}`

New files:
1. `reporting_summary_final_lock_gate_matrix.csv`
2. `reporting_summary_item_final_lock_status.csv`
3. `reporting_summary_final_lock_blockers.csv`
4. `reporting_summary_final_lock_command_queue.csv`
5. `reporting_summary_final_lock_validator_qa.csv`
6. `reporting_summary_forbidden_final_wording_import.csv`
7. `REPORTING_SUMMARY_FINAL_LOCK_VALIDATOR_README.md`
8. `reporting_summary_final_lock_validator_report.md`
9. `reporting_summary_final_lock_validator_summary.json`

Current result:
1. reporting_items = {summary['reporting_items']}
2. lockable_reporting_items_now = {summary['lockable_reporting_items_now']}
3. author_confirmations_collected = {summary['author_confirmations_collected']}
4. open_dependency_rows = {summary['open_dependency_rows']}
5. open_availability_crosswalk_rows = {summary['open_availability_crosswalk_rows']}
6. unresolved_items_imported = {summary['unresolved_items_imported']}
7. high_risk_items = {summary['high_risk_items']}
8. final_reporting_summary_ready = false
9. submission_ready = false

Boundary:
1. This validator checks final Reporting Summary readiness only.
2. It does not create final Reporting Summary answers.
3. It does not close author, figure, repository, reference or external-validation gates."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "reporting_summary_final_lock_validator_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("Reporting Summary final lock validator QA failed")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
