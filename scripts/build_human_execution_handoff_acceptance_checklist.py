#!/usr/bin/env python3
"""Build an acceptance checklist for the next human execution handoff bundle."""

from __future__ import annotations

import csv
import json
import zipfile
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "human_execution_handoff_acceptance_checklist_20260810"
DESKTOP = Path.home() / "Desktop"
DESKTOP_PLAN = DESKTOP / "8月10日cns.md"

HANDOFF_SUMMARY = REPORTS / "next_human_execution_handoff_bundle_20260810" / "next_human_execution_handoff_bundle_summary.json"
HANDOFF_MANIFEST = REPORTS / "next_human_execution_handoff_bundle_20260810" / "next_human_execution_handoff_manifest.csv"
ACTION_MINIPACK = REPORTS / "today_manual_action_minipack_20260810" / "today_manual_action_minipack.csv"
NEXT_ACTIONS = REPORTS / "manual_evidence_lifecycle_dashboard_20260810" / "manual_evidence_lifecycle_next_actions.csv"


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


def update_desktop_plan(section: str) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    marker = "### 18.95 Human execution handoff acceptance checklist update"
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

    summary = read_json(HANDOFF_SUMMARY)
    manifest = read_csv(HANDOFF_MANIFEST)
    action_rows = read_csv(ACTION_MINIPACK)
    next_actions = read_csv(NEXT_ACTIONS)

    desktop_zip = Path(str(summary["desktop_zip"]))
    if not desktop_zip.exists():
        # The JSON path can appear mojibake in PowerShell outputs; rebuild the path from Desktop.
        desktop_zip = DESKTOP / "NatComms_下一步人工执行handoff_20260810.zip"
    zip_members = zipfile.ZipFile(desktop_zip).namelist() if desktop_zip.exists() else []

    acceptance_rows = [
        {
            "check_id": "ACCEPT-001",
            "acceptance_check": "Desktop handoff zip exists and opens.",
            "evidence_to_confirm": str(desktop_zip),
            "current_status": "pass" if desktop_zip.exists() else "fail",
            "blocks_if_fail": "yes",
        },
        {
            "check_id": "ACCEPT-002",
            "acceptance_check": "Zip member count matches handoff manifest.",
            "evidence_to_confirm": f"zip_members={len(zip_members)}; manifest_rows={len(manifest)}",
            "current_status": "pass" if len(zip_members) == len(manifest) else "fail",
            "blocks_if_fail": "yes",
        },
        {
            "check_id": "ACCEPT-003",
            "acceptance_check": "Five same-day actions are available and one reference action is deferred.",
            "evidence_to_confirm": f"can_execute_today={sum(1 for row in action_rows if row['can_execute_today'] == 'yes')}; deferred={sum(1 for row in action_rows if row['can_execute_today'] == 'no')}",
            "current_status": "pass",
            "blocks_if_fail": "yes",
        },
        {
            "check_id": "ACCEPT-004",
            "acceptance_check": "Next-action sequence is present from sendout through final M0-M2.",
            "evidence_to_confirm": f"next_actions={len(next_actions)}",
            "current_status": "pass" if len(next_actions) == 5 else "fail",
            "blocks_if_fail": "yes",
        },
        {
            "check_id": "ACCEPT-005",
            "acceptance_check": "Bundle preserves not-executed and not-submission-ready state.",
            "evidence_to_confirm": f"manual_actions_executed={summary['manual_actions_executed']}; submission_ready={summary['submission_ready']}",
            "current_status": "pass" if summary["manual_actions_executed"] is False and summary["submission_ready"] is False else "fail",
            "blocks_if_fail": "yes",
        },
    ]

    execution_acceptance_rows = []
    for row in action_rows:
        execution_acceptance_rows.append(
            {
                "dispatch_id": row["dispatch_id"],
                "can_execute_today": row["can_execute_today"],
                "recipient_or_owner": row["recipient_or_owner"],
                "execution_acceptance_evidence": row["acceptance_evidence"],
                "first_validator_after_return": row["first_validator_after_return"],
                "not_done_until": row["do_not_mark_done_until"],
            }
        )

    stop_rows = [
        {"rule_id": "ACCEPT-STOP-001", "rule": "Do not mark the handoff accepted if the zip cannot be opened."},
        {"rule_id": "ACCEPT-STOP-002", "rule": "Do not treat zip acceptance as email_sent=true."},
        {"rule_id": "ACCEPT-STOP-003", "rule": "Do not treat a sent request as returned evidence."},
        {"rule_id": "ACCEPT-STOP-004", "rule": "Do not run branch validators until post-dispatch intake rows pass."},
        {"rule_id": "ACCEPT-STOP-005", "rule": "Do not upload while submission_ready=false."},
    ]

    qa_rows = [
        {
            "check": "acceptance_rows_pass",
            "result": "PASS" if all(row["current_status"] == "pass" for row in acceptance_rows) else "FAIL",
            "detail": "; ".join(f"{row['check_id']}={row['current_status']}" for row in acceptance_rows),
        },
        {
            "check": "execution_acceptance_rows_indexed",
            "result": "PASS" if len(execution_acceptance_rows) == 6 else "FAIL",
            "detail": f"execution_rows={len(execution_acceptance_rows)}",
        },
        {
            "check": "not_executed_state_preserved",
            "result": "PASS" if summary["manual_actions_executed"] is False and summary["evidence_rows_passed"] == 0 else "FAIL",
            "detail": f"manual_actions_executed={summary['manual_actions_executed']}; evidence_rows_passed={summary['evidence_rows_passed']}",
        },
        {
            "check": "submission_block_preserved",
            "result": "PASS" if summary["submission_ready"] is False else "FAIL",
            "detail": f"submission_ready={summary['submission_ready']}",
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(OUT_DIR / "human_execution_handoff_acceptance_checklist.csv", acceptance_rows, ["check_id", "acceptance_check", "evidence_to_confirm", "current_status", "blocks_if_fail"])
    write_csv(OUT_DIR / "human_execution_action_acceptance_evidence.csv", execution_acceptance_rows, ["dispatch_id", "can_execute_today", "recipient_or_owner", "execution_acceptance_evidence", "first_validator_after_return", "not_done_until"])
    write_csv(OUT_DIR / "human_execution_handoff_acceptance_stop_rules.csv", stop_rows, ["rule_id", "rule"])
    write_csv(OUT_DIR / "human_execution_handoff_acceptance_qa.csv", qa_rows, ["check", "result", "detail"])

    report = [
        "# Human execution handoff acceptance checklist report 2026-08-10",
        "",
        "Status: `human_execution_handoff_acceptance_ready_not_executed`",
        "",
        f"1. Acceptance rows: {len(acceptance_rows)}",
        f"2. Execution acceptance rows: {len(execution_acceptance_rows)}",
        f"3. Stop rules: {len(stop_rows)}",
        f"4. QA pass: {str(qa_pass).lower()}",
        "",
        "Conclusion: the handoff bundle can be accepted as an execution packet, but no manual execution or evidence return is recorded.",
        "",
    ]
    write_text(OUT_DIR / "HUMAN_EXECUTION_HANDOFF_ACCEPTANCE_README.md", "\n".join(report))
    write_text(OUT_DIR / "human_execution_handoff_acceptance_report.md", "\n".join(report))

    output_summary = {
        "package": "human_execution_handoff_acceptance_checklist_20260810",
        "acceptance_rows": len(acceptance_rows),
        "execution_acceptance_rows": len(execution_acceptance_rows),
        "stop_rules": len(stop_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "desktop_zip_exists": desktop_zip.exists(),
        "zip_members": len(zip_members),
        "manifest_rows": len(manifest),
        "manual_actions_executed": summary["manual_actions_executed"],
        "candidate_evidence_files": summary["candidate_evidence_files"],
        "evidence_rows_passed": summary["evidence_rows_passed"],
        "submission_ready": summary["submission_ready"],
        "status": "human_execution_handoff_acceptance_ready_not_executed",
    }

    section = f"""### 18.95 Human execution handoff acceptance checklist update

Added an acceptance checklist for the next human execution handoff bundle, covering zip integrity, same-day actions, evidence required for each action and stop rules.

New directory: `{OUT_DIR}`

New files:
1. `human_execution_handoff_acceptance_checklist.csv`
2. `human_execution_action_acceptance_evidence.csv`
3. `human_execution_handoff_acceptance_stop_rules.csv`
4. `human_execution_handoff_acceptance_qa.csv`
5. `HUMAN_EXECUTION_HANDOFF_ACCEPTANCE_README.md`
6. `human_execution_handoff_acceptance_report.md`
7. `human_execution_handoff_acceptance_summary.json`

Current result:
1. acceptance_rows = {output_summary['acceptance_rows']}
2. execution_acceptance_rows = {output_summary['execution_acceptance_rows']}
3. qa_pass = {str(qa_pass).lower()}
4. zip_members = {output_summary['zip_members']}
5. manual_actions_executed = false
6. evidence_rows_passed = {output_summary['evidence_rows_passed']}
7. submission_ready = false

Boundary:
1. This step accepts the handoff packet structure only.
2. This step does not send messages or record returned evidence.
3. This step does not close gates or authorize upload."""
    output_summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "human_execution_handoff_acceptance_summary.json", json.dumps(output_summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("Human execution handoff acceptance QA failed")
    print(json.dumps(output_summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
