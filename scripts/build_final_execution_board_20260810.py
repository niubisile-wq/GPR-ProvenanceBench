#!/usr/bin/env python3
"""Build a final execution board for the remaining submission blockers."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "final_execution_board_20260810"
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
    marker = "### 19.82 Final execution board update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- Added `reports/final_execution_board_20260810/` to consolidate the remaining route from manual evidence through FMR completion, guarded recheck and final portal decision.
- Current `execution_steps={summary["execution_steps"]}`, `open_execution_steps={summary["open_execution_steps"]}`, `blocked_execution_steps={summary["blocked_execution_steps"]}`.
- Current `allowed_commands_now={summary["allowed_commands_now"]}`, `complete_receipt_rows={summary["complete_receipt_rows"]}`, `submission_ready=false`.
- Boundary: this board is read-only orchestration. It does not send messages, accept placeholders as evidence, run `--execute-writeback`, execute recheck, upload portal files or submit.
"""
    if marker in text:
        start = text.index(marker)
        next_start = text.find("\n### ", start + len(marker))
        if next_start == -1:
            text = text[:start].rstrip()
        else:
            text = text[:start].rstrip() + "\n\n" + text[next_start:].lstrip("\n")
    text = text.rstrip() + block
    DESKTOP_PLAN.write_text(text + "\n", encoding="utf-8")
    return True


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    operator_summary = read_json(
        BENCH_ROOT
        / "reports"
        / "fmr_manual_evidence_operator_packet_20260810"
        / "fmr_manual_evidence_operator_packet_summary.json"
    )
    receipt_summary = read_json(
        BENCH_ROOT
        / "reports"
        / "final_manual_receipt_completion_validator_20260810"
        / "final_manual_receipt_completion_validator_summary.json"
    )
    next_action_summary = read_json(
        BENCH_ROOT
        / "reports"
        / "final_master_next_action_packet_20260810"
        / "final_master_next_action_packet_summary.json"
    )
    completion_ledger = read_json(
        BENCH_ROOT / "reports" / "submission_completion_ledger_20260810" / "submission_completion_ledger_summary.json"
    )
    readiness_dashboard = read_json(
        BENCH_ROOT
        / "reports"
        / "submission_readiness_dashboard_20260810"
        / "submission_readiness_dashboard_summary.json"
    )
    operator_rows = read_csv(
        BENCH_ROOT
        / "reports"
        / "fmr_manual_evidence_operator_packet_20260810"
        / "fmr_manual_evidence_operator_packet.csv"
    )
    receipt_rows = read_csv(
        BENCH_ROOT
        / "reports"
        / "final_manual_receipt_completion_validator_20260810"
        / "final_manual_receipt_completion_status.csv"
    )

    receipts_by_id = {row["receipt_id"]: row for row in receipt_rows}

    board_rows = [
        {
            "step_id": "FEB-001",
            "phase": "external_sendout",
            "required_action": "Send the external dependency packages through the real human channel and capture complete send receipts.",
            "primary_fmr": "FMR-001",
            "evidence_source": "manual_evidence/external_dependency_sendout_20260810",
            "proof_required": "sender, recipient, timestamp, message subject/body hash and attachment SHA256 values",
            "current_status": receipts_by_id.get("FMR-001", {}).get("current_status", "missing"),
            "next_validator": "py scripts/build_external_dependency_sendout_evidence_intake_preflight.py",
            "allowed_now": "manual_only",
            "blocks": "FMR-001 writeback; FMR-006 guarded recheck; portal upload",
        },
        {
            "step_id": "FEB-002",
            "phase": "author_decisions",
            "required_action": "Collect backend, scope and rights/licence decisions from the author or responsible owner.",
            "primary_fmr": "FMR-002",
            "evidence_source": "manual_evidence_inbox_20260810",
            "proof_required": "signed or attributable decision record, date and selected options",
            "current_status": receipts_by_id.get("FMR-002", {}).get("current_status", "missing"),
            "next_validator": "py scripts/build_fmr002_author_decision_writeback_preflight.py",
            "allowed_now": "manual_only",
            "blocks": "FMR-002 writeback; availability wording; final master",
        },
        {
            "step_id": "FEB-003",
            "phase": "returned_files",
            "required_action": "Place returned author reply files and external-blind payloads into the mapped return inbox.",
            "primary_fmr": "FMR-003",
            "evidence_source": "final_return_evidence_inbox_20260810",
            "proof_required": "returned files, source route, checksum manifest and no sensitive label/answer leakage",
            "current_status": receipts_by_id.get("FMR-003", {}).get("current_status", "missing"),
            "next_validator": "py scripts/build_fmr003_returned_evidence_writeback_preflight.py",
            "allowed_now": "manual_only",
            "blocks": "FMR-003 writeback; external-blind closeout; final master",
        },
        {
            "step_id": "FEB-004",
            "phase": "figure_approval",
            "required_action": "Complete figure author review decisions for Figure 1 through Figure 6.",
            "primary_fmr": "FMR-004",
            "evidence_source": "reports/python_figure_author_review_return_inbox_20260810/returned_author_review_files",
            "proof_required": "figure-level approval/revision/rejection decision and attributable comments",
            "current_status": receipts_by_id.get("FMR-004", {}).get("current_status", "missing"),
            "next_validator": "py scripts/build_fmr004_figure_review_writeback_preflight.py",
            "allowed_now": "manual_only",
            "blocks": "FMR-004 writeback; final figure export; portal upload",
        },
        {
            "step_id": "FEB-005",
            "phase": "repository_rights_doi",
            "required_action": "Finalize repositories, DOI records, licence selection and third-party rights clearance.",
            "primary_fmr": "FMR-005",
            "evidence_source": "final_return_evidence_inbox_20260810/04_repository_rights_doi",
            "proof_required": "repository DOI, code DOI if applicable, licence, rights clearance and availability wording",
            "current_status": receipts_by_id.get("FMR-005", {}).get("current_status", "missing"),
            "next_validator": "py scripts/build_fmr005_repository_rights_doi_writeback_preflight.py",
            "allowed_now": "manual_only",
            "blocks": "FMR-005 writeback; data/code availability; final master",
        },
        {
            "step_id": "FEB-006",
            "phase": "receipt_writeback",
            "required_action": "Only after a matching preflight has exactly one allowed candidate, run that FMR guarded writeback with explicit execute flag.",
            "primary_fmr": "FMR-001..FMR-005",
            "evidence_source": "matching FMR preflight candidate directories",
            "proof_required": "candidate_rows=1, writeback_preflight_allowed=true and explicit --execute-writeback command log",
            "current_status": "blocked",
            "next_validator": "py scripts/build_final_manual_receipt_completion_validator.py",
            "allowed_now": "no",
            "blocks": "FMR receipt completion; FMR-006 guarded recheck",
        },
        {
            "step_id": "FEB-007",
            "phase": "guarded_recheck",
            "required_action": "Run the guarded M0-M2 recheck only after FMR-001 through FMR-005 are complete.",
            "primary_fmr": "FMR-006",
            "evidence_source": "reports/latest_run_m0_m2_checks_20260810.log",
            "proof_required": "post-evidence M0-M2 PASS log and changed gate summary",
            "current_status": receipts_by_id.get("FMR-006", {}).get("current_status", "waiting"),
            "next_validator": "py scripts/build_fmr006_guarded_recheck_receipt_writeback_preflight.py",
            "allowed_now": "no",
            "blocks": "FMR-006 writeback; final master re-entry",
        },
        {
            "step_id": "FEB-008",
            "phase": "portal_decision",
            "required_action": "Re-enter final master gate and only then decide whether portal upload is allowed.",
            "primary_fmr": "all",
            "evidence_source": "checkpoints/gate_status_20260810.md",
            "proof_required": "final gate allows portal upload and submission readiness without open evidence blockers",
            "current_status": "blocked",
            "next_validator": "powershell -ExecutionPolicy Bypass -File scripts\\run_m0_m2_checks.ps1",
            "allowed_now": "no",
            "blocks": "portal upload and submission",
        },
    ]

    unlock_rows = []
    for receipt_id in ["FMR-001", "FMR-002", "FMR-003", "FMR-004", "FMR-005", "FMR-006"]:
        matching = [row for row in operator_rows if row["receipt_id"] == receipt_id]
        unlock_rows.append(
            {
                "receipt_id": receipt_id,
                "current_status": receipts_by_id.get(receipt_id, {}).get("current_status", ""),
                "operator_rows": len(matching),
                "primary_inbox": matching[0]["primary_inbox"] if matching else "",
                "first_validator": matching[0]["after_fill_validation"] if matching else "",
                "writeback_allowed_now": "no",
                "unlock_condition": (
                    "all FMR-001 to FMR-005 complete and guarded recheck PASS"
                    if receipt_id == "FMR-006"
                    else "real evidence present and matching preflight emits one allowed candidate"
                ),
            }
        )

    no_go_rows = [
        {
            "rule_id": "FEB-NOGO-001",
            "rule": "Do not run portal upload or mark submitted while submission_ready=false.",
            "current_evidence": f"submission_ready={readiness_dashboard.get('submission_ready')}",
        },
        {
            "rule_id": "FEB-NOGO-002",
            "rule": "Do not run guarded recheck before all six manual receipts are complete.",
            "current_evidence": f"complete_receipt_rows={receipt_summary.get('complete_receipt_rows')}",
        },
        {
            "rule_id": "FEB-NOGO-003",
            "rule": "Do not run any FMR guarded writeback without a preflight-approved candidate and explicit execute flag.",
            "current_evidence": f"commands_allowed_now={operator_summary.get('commands_allowed_now')}",
        },
        {
            "rule_id": "FEB-NOGO-004",
            "rule": "Do not treat support reports, dashboards or local plans as external evidence.",
            "current_evidence": f"candidate_evidence_files={operator_summary.get('candidate_evidence_files')}",
        },
    ]

    open_execution_steps = sum(1 for row in board_rows if row["allowed_now"] == "manual_only")
    blocked_execution_steps = sum(1 for row in board_rows if row["allowed_now"] == "no")
    allowed_commands_now = 0
    qa_rows = [
        {
            "check": "board covers end-to-end remaining route",
            "result": "PASS" if len(board_rows) == 8 else "FAIL",
            "detail": f"execution_steps={len(board_rows)}",
        },
        {
            "check": "all six FMR receipts have unlock rows",
            "result": "PASS" if len(unlock_rows) == 6 else "FAIL",
            "detail": f"unlock_rows={len(unlock_rows)}",
        },
        {
            "check": "no system commands are allowed now",
            "result": "PASS" if allowed_commands_now == 0 else "FAIL",
            "detail": f"allowed_commands_now={allowed_commands_now}",
        },
        {
            "check": "manual receipt completion remains blocked",
            "result": "PASS" if receipt_summary.get("complete_receipt_rows") == 0 else "FAIL",
            "detail": f"complete_receipt_rows={receipt_summary.get('complete_receipt_rows')}",
        },
        {
            "check": "portal upload and submission remain blocked",
            "result": "PASS"
            if not completion_ledger.get("portal_upload_ready") and not completion_ledger.get("submission_ready")
            else "FAIL",
            "detail": (
                f"portal_upload_ready={completion_ledger.get('portal_upload_ready')}; "
                f"submission_ready={completion_ledger.get('submission_ready')}"
            ),
        },
    ]

    summary = {
        "package": "final_execution_board_20260810",
        "execution_steps": len(board_rows),
        "open_execution_steps": open_execution_steps,
        "blocked_execution_steps": blocked_execution_steps,
        "unlock_rows": len(unlock_rows),
        "no_go_rules": len(no_go_rows),
        "allowed_commands_now": allowed_commands_now,
        "complete_receipt_rows": int(receipt_summary.get("complete_receipt_rows", 0) or 0),
        "candidate_evidence_files": int(operator_summary.get("candidate_evidence_files", 0) or 0),
        "portal_upload_allowed": False,
        "submission_ready": False,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": "final_execution_board_ready_manual_only_submission_blocked",
    }
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(
        OUT_DIR / "final_execution_board.csv",
        [
            "step_id",
            "phase",
            "required_action",
            "primary_fmr",
            "evidence_source",
            "proof_required",
            "current_status",
            "next_validator",
            "allowed_now",
            "blocks",
        ],
        board_rows,
    )
    write_csv(
        OUT_DIR / "final_execution_unlock_sequence.csv",
        [
            "receipt_id",
            "current_status",
            "operator_rows",
            "primary_inbox",
            "first_validator",
            "writeback_allowed_now",
            "unlock_condition",
        ],
        unlock_rows,
    )
    write_csv(OUT_DIR / "final_execution_no_go_rules.csv", ["rule_id", "rule", "current_evidence"], no_go_rows)
    write_csv(OUT_DIR / "final_execution_board_qa.csv", ["check", "result", "detail"], qa_rows)

    report = f"""# Final Execution Board

Status: `{summary["status"]}`

Current result:

1. Execution steps: {summary["execution_steps"]}
2. Manual-only open steps: {summary["open_execution_steps"]}
3. Blocked command/submission steps: {summary["blocked_execution_steps"]}
4. FMR unlock rows: {summary["unlock_rows"]}
5. Allowed commands now: {summary["allowed_commands_now"]}
6. Complete receipt rows: {summary["complete_receipt_rows"]}
7. Candidate evidence files: {summary["candidate_evidence_files"]}
8. Portal upload allowed: false
9. Submission ready: false

Boundary: this board is read-only orchestration. It does not send messages,
accept placeholders as evidence, run `--execute-writeback`, execute recheck,
upload portal files or submit.
"""
    write_text(OUT_DIR / "FINAL_EXECUTION_BOARD_README.md", report)
    write_text(OUT_DIR / "final_execution_board_report.md", report)
    write_text(OUT_DIR / "final_execution_board_summary.json", json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
