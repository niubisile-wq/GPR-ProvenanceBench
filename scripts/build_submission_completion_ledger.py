#!/usr/bin/env python3
"""Build a master ledger for the remaining path to submission readiness."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "submission_completion_ledger_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"

OPEN_GATE_QUEUE = REPORTS / "submission_readiness_dashboard_20260810" / "open_gate_priority_queue.csv"
SUBMISSION_DASHBOARD = REPORTS / "submission_readiness_dashboard_20260810" / "submission_readiness_dashboard_summary.json"
FINALIZATION_DASHBOARD = REPORTS / "natcomms_finalization_command_dashboard_v3_20260810" / "finalization_command_dashboard_v3_summary.json"
CRITICAL_PATH = REPORTS / "natcomms_finalization_command_dashboard_v3_20260810" / "critical_path_command_queue.csv"
GATE_BINDER = REPORTS / "natcomms_gate_closure_evidence_binder_20260810" / "gate_closure_evidence_binder_summary.json"
DISPATCH_QUEUE = REPORTS / "manual_dispatch_master_packet_20260810" / "manual_dispatch_master_queue.csv"
DISPATCH_SUMMARY = REPORTS / "manual_dispatch_master_packet_20260810" / "manual_dispatch_master_packet_summary.json"

HANDOFF_SUMMARIES = {
    "figure_backend_scope": REPORTS / "figure_backend_scope_decision_handoff_20260810" / "figure_backend_scope_decision_handoff_summary.json",
    "external_asset": REPORTS / "external_asset_triage_register_20260810" / "external_asset_triage_register_summary.json",
    "repository_predeposit": REPORTS / "repository_predeposit_handoff_20260810" / "repository_predeposit_handoff_summary.json",
    "rights_licence": REPORTS / "rights_licence_completion_handoff_20260810" / "rights_licence_completion_handoff_summary.json",
    "reporting_summary": REPORTS / "reporting_summary_completion_handoff_20260810" / "reporting_summary_completion_handoff_summary.json",
    "references": REPORTS / "reference_completion_handoff_20260810" / "reference_completion_handoff_summary.json",
}


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
    marker = "### 18.80 Submission completion ledger update"
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


def gate_to_handoff(gate: str) -> str:
    mapping = {
        "Real blind external validation": "external_asset",
        "Main figure rendering": "figure_backend_scope",
        "Repository identifiers": "repository_predeposit; rights_licence",
        "Reporting Summary": "reporting_summary",
        "Third-party rights": "rights_licence",
        "Final reference numbering": "references",
    }
    return mapping.get(gate, "")


def gate_to_final_validation(gate: str) -> str:
    mapping = {
        "Real blind external validation": "validate_external_blind_intake.py --strict-sha and evaluate_external_blind_submission.py --main-claim after label unlock",
        "Main figure rendering": "figure backend validator, figure rendering workflow, visual QA, figure source-data lock, full M0-M2",
        "Repository identifiers": "repository DOI/code DOI landing-page checks plus release readiness and availability prelock rerun",
        "Reporting Summary": "reporting_summary_finalization_prelock and reporting_summary_completion_handoff rerun",
        "Third-party rights": "rights_licence_completion_handoff and release readiness audit rerun",
        "Final reference numbering": "reference_completion_handoff rerun after final prose and marker replacement",
    }
    return mapping.get(gate, "full M0-M2 rerun")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    open_gate_rows = read_csv(OPEN_GATE_QUEUE)
    submission_summary = read_json(SUBMISSION_DASHBOARD)
    finalization_summary = read_json(FINALIZATION_DASHBOARD)
    binder_summary = read_json(GATE_BINDER)
    dispatch_rows = read_csv(DISPATCH_QUEUE)
    dispatch_summary = read_json(DISPATCH_SUMMARY)
    critical_rows = read_csv(CRITICAL_PATH)
    handoff_summaries = {name: read_json(path) for name, path in HANDOFF_SUMMARIES.items()}

    ledger_rows = []
    for row in open_gate_rows:
        gate = row["gate"]
        ledger_rows.append(
            {
                "priority": row["priority"],
                "gate": gate,
                "current_status": row["status"],
                "required_evidence_to_close": row["required_evidence_to_close"],
                "current_best_action": row["current_best_action"],
                "current_handoff_package": gate_to_handoff(gate),
                "final_validation_to_run": gate_to_final_validation(gate),
                "closure_state": "open",
            }
        )

    dispatch_link_rows = []
    for row in dispatch_rows:
        dispatch_link_rows.append(
            {
                "dispatch_id": row["dispatch_id"],
                "priority": row["priority"],
                "recipient_or_owner": row["recipient_or_owner"],
                "action": row["action"],
                "linked_gate_or_gates": "author/admin; figure; external; rights; reporting; references",
                "current_status": row["current_status"],
                "acceptance_evidence": row["acceptance_evidence"],
            }
        )

    final_verification_rows = [
        {
            "order": 1,
            "verification": "manual sendout and author reply validators",
            "required_state": "email_sent=true, all required replies returned, author reply ingestion allowed",
            "current_state": "not satisfied",
        },
        {
            "order": 2,
            "verification": "figure backend validator plus rendered figure visual QA",
            "required_state": "backend_selected=true, scope_confirmed=true, rendered figures and source-data QA pass",
            "current_state": "not satisfied",
        },
        {
            "order": 3,
            "verification": "external blind strict-SHA intake and locked one-shot evaluation",
            "required_state": "real asset, held labels, frozen prediction, one locked evaluation",
            "current_state": "not satisfied",
        },
        {
            "order": 4,
            "verification": "repository/release/rights availability chain",
            "required_state": "repository DOI, code DOI, licence, rights review, release readiness pass",
            "current_state": "not satisfied",
        },
        {
            "order": 5,
            "verification": "Reporting Summary and reference finalization",
            "required_state": "final Reporting Summary, final numbered references, final RIS/ENW",
            "current_state": "not satisfied",
        },
        {
            "order": 6,
            "verification": "full .\\scripts\\run_m0_m2_checks.ps1 and portal upload readiness",
            "required_state": "M0-M2 checks completed, gate_closure_allowed=true, portal_upload_ready=true, submission_ready=true",
            "current_state": "not satisfied",
        },
    ]

    no_go_rows = [
        {
            "no_go_id": "SUBMIT-NOGO-001",
            "shortcut": "Treat handoff packets as closed gates",
            "reason": "Handoff packets organize work; they do not provide the required external or author evidence.",
            "decision": "forbidden",
        },
        {
            "no_go_id": "SUBMIT-NOGO-002",
            "shortcut": "Use green M0-M2 checks as proof of submission readiness",
            "reason": "Current checks prove consistency of the not-ready state, not final gate closure.",
            "decision": "forbidden",
        },
        {
            "no_go_id": "SUBMIT-NOGO-003",
            "shortcut": "Submit Track B text without final figures, DOI/rights and Reporting Summary",
            "reason": "Nature Communications submission package requires final companion materials and upload files.",
            "decision": "forbidden",
        },
        {
            "no_go_id": "SUBMIT-NOGO-004",
            "shortcut": "Upgrade 4TU or template external validation into main confirmation",
            "reason": "Current evidence boundaries explicitly forbid this upgrade.",
            "decision": "forbidden",
        },
    ]

    handoff_rows = [
        {
            "handoff": name,
            "status": summary.get("status"),
            "qa_pass": summary.get("qa_pass"),
            "submission_ready": summary.get("submission_ready"),
        }
        for name, summary in handoff_summaries.items()
    ]

    qa_rows = [
        {
            "check": "open_gate_count_preserved",
            "result": "PASS" if len(open_gate_rows) == submission_summary.get("open_gates") == 6 else "FAIL",
            "detail": f"ledger_open_gates={len(open_gate_rows)}; dashboard_open_gates={submission_summary.get('open_gates')}",
        },
        {
            "check": "finalization_commands_remain_blocked",
            "result": "PASS" if finalization_summary.get("blocked_commands") == finalization_summary.get("command_rows") else "FAIL",
            "detail": f"blocked={finalization_summary.get('blocked_commands')}; total={finalization_summary.get('command_rows')}",
        },
        {
            "check": "gate_binder_keeps_all_requirements_open",
            "result": "PASS" if binder_summary.get("open_evidence_requirements") == binder_summary.get("artifact_evidence_requirements") else "FAIL",
            "detail": f"open={binder_summary.get('open_evidence_requirements')}; total={binder_summary.get('artifact_evidence_requirements')}",
        },
        {
            "check": "dispatch_packet_ready_but_not_done",
            "result": "PASS" if dispatch_summary.get("qa_pass") is True and dispatch_summary.get("email_sent") is False and dispatch_summary.get("submission_ready") is False else "FAIL",
            "detail": f"dispatch_actions={dispatch_summary.get('dispatch_actions')}; email_sent={dispatch_summary.get('email_sent')}",
        },
        {
            "check": "submission_not_claimed_ready",
            "result": "PASS" if submission_summary.get("submission_ready") is False else "FAIL",
            "detail": f"submission_ready={submission_summary.get('submission_ready')}",
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(
        OUT_DIR / "submission_completion_gate_ledger.csv",
        ledger_rows,
        ["priority", "gate", "current_status", "required_evidence_to_close", "current_best_action", "current_handoff_package", "final_validation_to_run", "closure_state"],
    )
    write_csv(
        OUT_DIR / "submission_dispatch_to_gate_crosswalk.csv",
        dispatch_link_rows,
        ["dispatch_id", "priority", "recipient_or_owner", "action", "linked_gate_or_gates", "current_status", "acceptance_evidence"],
    )
    write_csv(OUT_DIR / "submission_final_verification_queue.csv", final_verification_rows, ["order", "verification", "required_state", "current_state"])
    write_csv(OUT_DIR / "submission_handoff_status_register.csv", handoff_rows, ["handoff", "status", "qa_pass", "submission_ready"])
    write_csv(OUT_DIR / "submission_no_go_shortcuts.csv", no_go_rows, ["no_go_id", "shortcut", "reason", "decision"])
    write_csv(OUT_DIR / "submission_completion_ledger_qa.csv", qa_rows, ["check", "result", "detail"])

    readme = """# Submission Completion Ledger 2026-08-10

This ledger maps the current not-ready submission state to the evidence required for final gate closure.

It is a control index over open gates, manual dispatch actions, handoff packages, final verification commands and forbidden shortcuts.

Boundary: this ledger does not close gates, execute manual actions, generate final figures, create DOI records, finalize Reporting Summary/references or submit the manuscript.
"""
    write_text(OUT_DIR / "SUBMISSION_COMPLETION_LEDGER_README.md", readme)

    report = [
        "# Submission completion ledger report 2026-08-10",
        "",
        "Status: `submission_completion_ledger_ready_gates_open`",
        "",
        f"- Open gate rows: {len(ledger_rows)}",
        f"- Dispatch crosswalk rows: {len(dispatch_link_rows)}",
        f"- Final verification rows: {len(final_verification_rows)}",
        f"- Handoff status rows: {len(handoff_rows)}",
        f"- No-go shortcuts: {len(no_go_rows)}",
        f"- QA pass: {qa_pass}",
        "",
        "Conclusion: completion evidence is now indexed, but all finalization gates remain open.",
        "",
    ]
    write_text(OUT_DIR / "submission_completion_ledger_report.md", "\n".join(report))

    summary = {
        "package": "submission_completion_ledger_20260810",
        "open_gate_rows": len(ledger_rows),
        "dispatch_crosswalk_rows": len(dispatch_link_rows),
        "final_verification_rows": len(final_verification_rows),
        "handoff_status_rows": len(handoff_rows),
        "no_go_shortcuts": len(no_go_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "gate_closure_allowed": False,
        "portal_upload_ready": False,
        "submission_ready": False,
        "status": "submission_completion_ledger_ready_gates_open",
    }

    section = f"""### 18.80 Submission completion ledger update

Added a submission completion ledger. This maps the six open gates to current handoff packages, manual dispatch actions, required closing evidence and final verification commands.

New directory: `{OUT_DIR}`

New files:
1. `submission_completion_gate_ledger.csv`
2. `submission_dispatch_to_gate_crosswalk.csv`
3. `submission_final_verification_queue.csv`
4. `submission_handoff_status_register.csv`
5. `submission_no_go_shortcuts.csv`
6. `submission_completion_ledger_qa.csv`
7. `SUBMISSION_COMPLETION_LEDGER_README.md`
8. `submission_completion_ledger_report.md`
9. `submission_completion_ledger_summary.json`

Current result:
1. open_gate_rows = {summary['open_gate_rows']}
2. dispatch_crosswalk_rows = {summary['dispatch_crosswalk_rows']}
3. final_verification_rows = {summary['final_verification_rows']}
4. handoff_status_rows = {summary['handoff_status_rows']}
5. no_go_shortcuts = {summary['no_go_shortcuts']}
6. qa_pass = {str(qa_pass).lower()}
7. gate_closure_allowed = false
8. portal_upload_ready = false
9. submission_ready = false
10. status = `submission_completion_ledger_ready_gates_open`

Boundary:
1. This step does not close any gate.
2. This step does not execute manual actions.
3. This step does not create final figures, DOI records, final Reporting Summary or final references.
4. This step does not submit the manuscript."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "submission_completion_ledger_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("Submission completion ledger QA failed")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
