#!/usr/bin/env python3
"""Validate whether candidate citation markers can be converted to final references."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "reference_final_lock_validator_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"

HANDOFF_DIR = BENCH_ROOT / "reports" / "reference_completion_handoff_20260810"
PUBLIC_DIR = BENCH_ROOT / "reports" / "reference_public_verification_20260810"
SUPPORT_DIR = BENCH_ROOT / "reports" / "sentence_citation_support_lock_20260810"

HANDOFF_SUMMARY = HANDOFF_DIR / "reference_completion_handoff_summary.json"
PUBLIC_SUMMARY = PUBLIC_DIR / "reference_public_verification_summary.json"
SUPPORT_SUMMARY = SUPPORT_DIR / "sentence_citation_support_lock_summary.json"
REPLACEMENT_QUEUE = HANDOFF_DIR / "citation_marker_final_replacement_queue.csv"
MANUAL_QUEUE = HANDOFF_DIR / "reference_manual_verification_queue.csv"
COMPLETION_MATRIX = HANDOFF_DIR / "reference_completion_matrix.csv"
EXPORT_QUEUE = HANDOFF_DIR / "reference_export_finalization_queue.csv"
NO_GO = HANDOFF_DIR / "reference_no_go_shortcuts.csv"
PUBLIC_METADATA = PUBLIC_DIR / "public_reference_metadata_verification.csv"
SUPPORT_LOCK = SUPPORT_DIR / "sentence_citation_support_lock.csv"
SUPPORT_GUARDS = SUPPORT_DIR / "citation_overclaim_guardrails.csv"


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
    marker = "### 19.08 Reference final lock validator update"
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

    handoff_summary = read_json(HANDOFF_SUMMARY)
    public_summary = read_json(PUBLIC_SUMMARY)
    support_summary = read_json(SUPPORT_SUMMARY)
    replacement_rows = read_csv(REPLACEMENT_QUEUE)
    manual_rows = read_csv(MANUAL_QUEUE)
    completion_rows = read_csv(COMPLETION_MATRIX)
    export_rows = read_csv(EXPORT_QUEUE)
    no_go_rows = read_csv(NO_GO)
    public_rows = read_csv(PUBLIC_METADATA)
    support_rows = read_csv(SUPPORT_LOCK)
    guard_rows = read_csv(SUPPORT_GUARDS)

    replacements_allowed = [row for row in replacement_rows if row.get("replacement_allowed_now") == "true"]
    manual_closed = [row for row in manual_rows if row.get("current_status") == "closed"]
    public_ready = [row for row in public_rows if row.get("final_reference_ready") == "true"]
    export_allowed = [row for row in export_rows if row.get("allowed_now") == "yes"]

    gate_rows = [
        {
            "gate_id": "REF-FINAL-001",
            "requirement": "All candidate marker replacements are allowed",
            "current_state": f"allowed={len(replacements_allowed)} of {len(replacement_rows)}",
            "passes_now": "no",
            "blocking_reason": "Final prose, figure/table calls and final citation order are not locked.",
        },
        {
            "gate_id": "REF-FINAL-002",
            "requirement": "Manual DOI/title/support verification is closed",
            "current_state": f"closed={len(manual_closed)} of {len(manual_rows)}",
            "passes_now": "no",
            "blocking_reason": "Manual publisher/support verification queue remains open.",
        },
        {
            "gate_id": "REF-FINAL-003",
            "requirement": "Public metadata rows are final-reference ready",
            "current_state": f"ready={len(public_ready)} of {len(public_rows)}; metadata_failures={public_summary.get('metadata_match_failures')}",
            "passes_now": "no",
            "blocking_reason": "Metadata verification passes, but final_reference_ready remains false until final sentence support and numbering are locked.",
        },
        {
            "gate_id": "REF-FINAL-004",
            "requirement": "Sentence support lock is final, not prelock",
            "current_state": f"sentence_rows={len(support_rows)}; final_references_ready={support_summary.get('final_references_ready')}",
            "passes_now": "no",
            "blocking_reason": "Sentence support mapping is prelock only and candidate markers have not been replaced.",
        },
        {
            "gate_id": "REF-FINAL-005",
            "requirement": "Final reference exports are allowed",
            "current_state": f"allowed_exports={len(export_allowed)} of {len(export_rows)}",
            "passes_now": "no",
            "blocking_reason": "Final numbered reference list and exports require stable citation order and replaced markers.",
        },
    ]

    blocker_rows = [
        {
            "blocker_id": "REF-BLOCK-001",
            "blocker": "final_prose_not_locked",
            "evidence": "citation_marker_final_replacement_queue.csv keeps all replacement_allowed_now=false",
            "next_required_evidence": "Stable final manuscript with final figure/table calls.",
        },
        {
            "blocker_id": "REF-BLOCK-002",
            "blocker": "manual_reference_checks_open",
            "evidence": "reference_manual_verification_queue.csv has zero closed rows",
            "next_required_evidence": "Manual verification rows closed with publisher DOI/title/support evidence.",
        },
        {
            "blocker_id": "REF-BLOCK-003",
            "blocker": "support_lock_prelock_only",
            "evidence": "sentence_citation_support_lock_summary.json has final_references_ready=false",
            "next_required_evidence": "Final sentence-to-reference support audit after prose freeze.",
        },
        {
            "blocker_id": "REF-BLOCK-004",
            "blocker": "final_exports_not_allowed",
            "evidence": "reference_export_finalization_queue.csv has zero allowed_now=yes rows",
            "next_required_evidence": "Final numbered list and RIS/ENW regenerated from locked order.",
        },
    ]

    command_rows = [
        {"order": 1, "command": "py scripts\\build_reference_public_verification.py", "run_now": "yes", "purpose": "Refresh public metadata prelock."},
        {"order": 2, "command": "py scripts\\build_sentence_citation_support_lock.py", "run_now": "yes", "purpose": "Refresh sentence support prelock."},
        {"order": 3, "command": "py scripts\\build_reference_completion_handoff.py", "run_now": "yes", "purpose": "Refresh replacement and manual verification queues."},
        {"order": 4, "command": "py scripts\\build_reference_final_lock_validator.py", "run_now": "yes", "purpose": "Refresh this final-lock validator."},
        {"order": 5, "command": "Replace [P#] markers and export final numbered references", "run_now": "no", "purpose": "Allowed only after all final reference gates pass."},
    ]

    qa_rows = [
        {
            "check": "replacement_rows_blocked",
            "result": "PASS" if len(replacements_allowed) == 0 and len(replacement_rows) == 5 else "FAIL",
            "detail": f"replacement_rows={len(replacement_rows)}; replacements_allowed={len(replacements_allowed)}",
        },
        {
            "check": "manual_checks_open",
            "result": "PASS" if len(manual_closed) == 0 and len(manual_rows) == 8 else "FAIL",
            "detail": f"manual_rows={len(manual_rows)}; manual_closed={len(manual_closed)}",
        },
        {
            "check": "metadata_verified_but_not_final",
            "result": "PASS" if public_summary.get("metadata_match_failures") == 0 and len(public_ready) == 0 else "FAIL",
            "detail": f"metadata_failures={public_summary.get('metadata_match_failures')}; public_ready={len(public_ready)}",
        },
        {
            "check": "support_guards_active",
            "result": "PASS" if len(guard_rows) == 4 and all(row.get("status") == "active" for row in guard_rows) else "FAIL",
            "detail": f"guard_rows={len(guard_rows)}",
        },
        {
            "check": "final_references_not_ready",
            "result": "PASS" if handoff_summary.get("final_references_ready") is False and support_summary.get("final_references_ready") is False else "FAIL",
            "detail": f"handoff_final={handoff_summary.get('final_references_ready')}; support_final={support_summary.get('final_references_ready')}",
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(OUT_DIR / "reference_final_lock_gate_matrix.csv", gate_rows, ["gate_id", "requirement", "current_state", "passes_now", "blocking_reason"])
    write_csv(OUT_DIR / "reference_final_lock_blockers.csv", blocker_rows, ["blocker_id", "blocker", "evidence", "next_required_evidence"])
    write_csv(OUT_DIR / "reference_final_lock_command_queue.csv", command_rows, ["order", "command", "run_now", "purpose"])
    write_csv(OUT_DIR / "reference_final_lock_no_go_rules.csv", no_go_rows, list(no_go_rows[0].keys()))
    write_csv(OUT_DIR / "reference_final_lock_validator_qa.csv", qa_rows, ["check", "result", "detail"])

    report = [
        "# Reference final lock validator 2026-08-10",
        "",
        "Status: `reference_final_lock_validator_ready_blocked`",
        "",
        f"1. Replacement rows: {len(replacement_rows)}",
        f"2. Replacements allowed now: {len(replacements_allowed)}",
        f"3. Manual verification rows closed: {len(manual_closed)} of {len(manual_rows)}",
        f"4. Public metadata match failures: {public_summary.get('metadata_match_failures')}",
        f"5. Final-reference-ready public rows: {len(public_ready)}",
        f"6. QA pass: {str(qa_pass).lower()}",
        "",
        "Boundary: this validator does not replace citation markers or create final numbered references.",
        "",
    ]
    write_text(OUT_DIR / "REFERENCE_FINAL_LOCK_VALIDATOR_README.md", "\n".join(report))
    write_text(OUT_DIR / "reference_final_lock_validator_report.md", "\n".join(report))

    summary = {
        "package": "reference_final_lock_validator_20260810",
        "gate_rows": len(gate_rows),
        "blocker_rows": len(blocker_rows),
        "command_rows": len(command_rows),
        "no_go_rules": len(no_go_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "replacement_rows": len(replacement_rows),
        "marker_replacements_allowed_now": len(replacements_allowed),
        "manual_verification_rows": len(manual_rows),
        "manual_verification_rows_closed": len(manual_closed),
        "metadata_match_failures": public_summary.get("metadata_match_failures"),
        "public_final_reference_ready_rows": len(public_ready),
        "sentence_support_rows": len(support_rows),
        "final_export_allowed_rows": len(export_allowed),
        "candidate_markers_replaced": False,
        "final_references_ready": False,
        "submission_ready": False,
        "status": "reference_final_lock_validator_ready_blocked",
    }

    section = f"""### 19.08 Reference final lock validator update

Added a final-lock validator for candidate citation markers and reference numbering.

New directory: `{OUT_DIR}`

New files:
1. `reference_final_lock_gate_matrix.csv`
2. `reference_final_lock_blockers.csv`
3. `reference_final_lock_command_queue.csv`
4. `reference_final_lock_no_go_rules.csv`
5. `reference_final_lock_validator_qa.csv`
6. `REFERENCE_FINAL_LOCK_VALIDATOR_README.md`
7. `reference_final_lock_validator_report.md`
8. `reference_final_lock_validator_summary.json`

Current result:
1. replacement_rows = {summary['replacement_rows']}
2. marker_replacements_allowed_now = {summary['marker_replacements_allowed_now']}
3. manual_verification_rows_closed = {summary['manual_verification_rows_closed']}
4. metadata_match_failures = {summary['metadata_match_failures']}
5. public_final_reference_ready_rows = {summary['public_final_reference_ready_rows']}
6. final_export_allowed_rows = {summary['final_export_allowed_rows']}
7. final_references_ready = false
8. submission_ready = false

Boundary:
1. This validator checks final reference lock readiness only.
2. It does not replace [P#] markers.
3. It does not create final numbered references or final RIS/ENW exports."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "reference_final_lock_validator_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("Reference final lock validator QA failed")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
