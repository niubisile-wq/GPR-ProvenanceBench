#!/usr/bin/env python3
"""Build the next human-action packet from the final submission master bridge."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "final_master_next_action_packet_20260810"
FINAL_MASTER_DIR = BENCH_ROOT / "reports" / "final_submission_master_dependency_bridge_validator_20260810"
AUTHOR_CLOSURE_DIR = BENCH_ROOT / "reports" / "author_decision_closure_packet_v2_20260810"
RESIDUAL_PACKET_DIR = BENCH_ROOT / "reports" / "final_residual_blocker_closure_packet_20260810"
HUMAN_CLOSEOUT_DIR = BENCH_ROOT / "reports" / "final_human_execution_closeout_board_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"
DESKTOP_GUIDE = Path.home() / "Desktop" / "NatComms_19.48_final_next_actions_20260810.md"


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def update_desktop_plan(summary: dict[str, object]) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    marker = "### 19.48 Final master next-action packet update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- 新增 `reports/final_master_next_action_packet_20260810/`，从 19.47 final submission master bridge 直接生成下一步人工执行包。
- 桌面同步生成 `NatComms_19.48_final_next_actions_20260810.md`，只列允许的人工动作和禁止的最终提交动作。
- 当前 `final_submission_master_allowed=false`，`manual_action_rows={summary["manual_action_rows"]}`，`allowed_human_action_rows={summary["allowed_human_action_rows"]}`，`forbidden_submission_action_rows={summary["forbidden_submission_action_rows"]}`。
- 当前 `submission_ready=false`，`portal_upload_allowed=false`，`system_command_execution_allowed=false`。
- 边界：该 packet 只组织人工下一步，不代替作者回复、不放入真实返回文件、不执行重跑、不上传 portal、不声称完成投稿。
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

    final_master = read_json(FINAL_MASTER_DIR / "final_submission_master_dependency_bridge_validator_summary.json")
    final_blockers = read_csv(FINAL_MASTER_DIR / "final_submission_master_dependency_bridge_blockers.csv")
    final_items = read_csv(FINAL_MASTER_DIR / "final_submission_master_item_bridge.csv")
    author_queue = read_csv(AUTHOR_CLOSURE_DIR / "next_24h_decision_closure_queue.csv")
    residual_rows = read_csv(RESIDUAL_PACKET_DIR / "final_residual_blocker_closure_packet.csv")
    human_actions = read_csv(HUMAN_CLOSEOUT_DIR / "final_human_execution_action_queue.csv")

    final_submission_master_allowed = final_master.get("final_submission_master_allowed") is True
    submission_ready = final_master.get("submission_ready") is True

    manual_actions = [
        {
            "priority": 1,
            "owner": "corresponding_author",
            "action": "Send the author decision closure packet and capture send evidence.",
            "source_evidence": "author_decision_closure_packet_v2",
            "required_input": "Email/message sent to coauthors or advisor with decision packet attached or pasted.",
            "acceptance_test": "email_sent=true, immutable send log recorded, and sent packet checksum retained.",
            "after_completion_validator": "py scripts/build_natcomms_author_response_log_validator.py",
            "allowed_now": "yes",
        },
        {
            "priority": 2,
            "owner": "author_and_advisor",
            "action": "Return four required decisions: figure backend, external asset availability, licence direction and Track B fallback.",
            "source_evidence": "author_decision_closure_form_v2.csv",
            "required_input": "Nonblank accepted values for all four decision rows.",
            "acceptance_test": "decision_rows=0 unresolved and blank_author_reply_fields=0 after intake.",
            "after_completion_validator": "py scripts/build_manual_evidence_final_intake_validator.py",
            "allowed_now": "yes",
        },
        {
            "priority": 3,
            "owner": "author_or_data_holder",
            "action": "Place real returned evidence files into the canonical return/RB-001 inbox routes.",
            "source_evidence": "final_residual_blocker_closure_packet.csv",
            "required_input": "Returned files with source identity, timestamps and SHA256 provenance.",
            "acceptance_test": "candidate_return_files > 0 and scanner/hash manifest reconciliation passes.",
            "after_completion_validator": "py scripts/build_final_return_evidence_intake_scanner.py",
            "allowed_now": "yes",
        },
        {
            "priority": 4,
            "owner": "figure_owner_and_author_team",
            "action": "Collect Figure 1-Figure 6 approve/revise/drop decisions before final candidate generation.",
            "source_evidence": "python_figure_author_review_packet_20260810",
            "required_input": "Six figure review rows with accepted decision values and comments for revisions.",
            "acceptance_test": "approved_rows covers required figures and final_candidate_generation_allowed=true.",
            "after_completion_validator": "py scripts/build_python_figure_author_review_intake_validator.py",
            "allowed_now": "yes",
        },
        {
            "priority": 5,
            "owner": "repository_or_rights_owner",
            "action": "Resolve repository DOI, code DOI, licence and third-party rights direction.",
            "source_evidence": "repository_predeposit_handoff and rights_licence_completion_handoff",
            "required_input": "Repository/accession identifiers, release licence and rights-clearance decisions.",
            "acceptance_test": "final_availability_ready=true and portal files are no longer skeleton-only.",
            "after_completion_validator": "py scripts/build_availability_repository_finalization_validator.py",
            "allowed_now": "yes",
        },
        {
            "priority": 6,
            "owner": "manuscript_operator",
            "action": "After decisions and evidence return, rerun only the guarded validation sequence, not portal upload.",
            "source_evidence": "final_submission_master_dependency_bridge_validator_20260810",
            "required_input": "Completed actions 1-5 plus accepted manual evidence receipts.",
            "acceptance_test": "19.47 changes only after upstream validators report zero open gates.",
            "after_completion_validator": "powershell -ExecutionPolicy Bypass -File scripts/run_m0_m2_checks.ps1",
            "allowed_now": "after manual evidence is present",
        },
    ]

    forbidden_actions = [
        {
            "action": "Upload any file to the Nature Communications portal.",
            "reason": "portal_upload_ready=false and portal_file_upload_allowed_rows=0.",
        },
        {
            "action": "Mark the manuscript submission-ready.",
            "reason": "final_submission_master_allowed=false and submission_ready=false.",
        },
        {
            "action": "Close master gates or residual blockers manually.",
            "reason": "open_master_gates=8 and ready_to_close_rows=0.",
        },
        {
            "action": "Run route/writeback/transition commands as if evidence were present.",
            "reason": "candidate_return_files=0 and writeback/transition remain blocked.",
        },
        {
            "action": "Replace open-gate language with final external-validation claims.",
            "reason": "real blind external validation remains NO-GO.",
        },
    ]

    acceptance_rows = [
        {
            "check": "19.47 remains source of truth",
            "expected_state": "final_submission_master_allowed=false",
            "current_state": f"final_submission_master_allowed={final_master.get('final_submission_master_allowed')}",
            "passes_now": "yes" if not final_submission_master_allowed else "no",
        },
        {
            "check": "manual actions only",
            "expected_state": "allowed human actions are communications, evidence collection and guarded recheck preparation",
            "current_state": "portal upload and submission actions forbidden",
            "passes_now": "yes",
        },
        {
            "check": "no system execution allowed now",
            "expected_state": "system_command_execution_allowed=false",
            "current_state": "all final item bridge rows are bridge_allowed=no",
            "passes_now": "yes" if all(row.get("bridge_allowed") == "no" for row in final_items) else "no",
        },
        {
            "check": "blockers are exposed",
            "expected_state": "at least five final blockers listed",
            "current_state": f"final_blocker_rows={len(final_blockers)}",
            "passes_now": "yes" if len(final_blockers) >= 5 else "no",
        },
    ]

    summary = {
        "package": "final_master_next_action_packet_20260810",
        "final_submission_master_allowed": final_submission_master_allowed,
        "submission_ready": submission_ready,
        "manual_action_rows": len(manual_actions),
        "allowed_human_action_rows": sum(1 for row in manual_actions if row["allowed_now"] == "yes"),
        "forbidden_submission_action_rows": len(forbidden_actions),
        "final_blocker_rows_imported": len(final_blockers),
        "author_queue_rows_imported": len(author_queue),
        "residual_rows_imported": len(residual_rows),
        "human_action_rows_imported": len(human_actions),
        "portal_upload_allowed": False,
        "system_command_execution_allowed": False,
        "qa_rows": len(acceptance_rows),
        "qa_pass": all(row["passes_now"] == "yes" for row in acceptance_rows),
        "status": "final_master_next_action_packet_ready_manual_actions_only",
        "desktop_guide": str(DESKTOP_GUIDE),
    }

    guide_lines = [
        "# NatComms 19.48 Final Next Actions",
        "",
        "Source of truth: `reports/final_submission_master_dependency_bridge_validator_20260810/`.",
        "",
        "Current state: final submission is blocked. Do not upload portal files or mark the manuscript submission-ready.",
        "",
        "## Allowed Human Actions",
        "",
    ]
    for row in manual_actions:
        guide_lines.extend(
            [
                f"### {row['priority']}. {row['action']}",
                "",
                f"- Owner: {row['owner']}",
                f"- Required input: {row['required_input']}",
                f"- Acceptance test: {row['acceptance_test']}",
                f"- Recheck: `{row['after_completion_validator']}`",
                "",
            ]
        )
    guide_lines.extend(["## Forbidden Until 19.47 Passes", ""])
    for row in forbidden_actions:
        guide_lines.append(f"- {row['action']} Reason: {row['reason']}")
    guide_lines.extend(
        [
            "",
            "## Final Recheck",
            "",
            "After real evidence and replies are present, rerun:",
            "",
            "```powershell",
            "powershell -ExecutionPolicy Bypass -File scripts\\run_m0_m2_checks.ps1",
            "```",
            "",
            "Submission is still false unless 19.47 reports `final_submission_master_allowed=true` and `submission_ready=true`.",
        ]
    )
    guide = "\n".join(guide_lines) + "\n"

    write_csv(
        OUT_DIR / "final_master_next_manual_actions.csv",
        ["priority", "owner", "action", "source_evidence", "required_input", "acceptance_test", "after_completion_validator", "allowed_now"],
        manual_actions,
    )
    write_csv(
        OUT_DIR / "final_master_forbidden_submission_actions.csv",
        ["action", "reason"],
        forbidden_actions,
    )
    write_csv(
        OUT_DIR / "final_master_next_action_acceptance_tests.csv",
        ["check", "expected_state", "current_state", "passes_now"],
        acceptance_rows,
    )
    write_text(OUT_DIR / "FINAL_MASTER_NEXT_ACTION_PACKET_README.md", guide)
    write_text(OUT_DIR / "final_master_next_action_packet_report.md", guide)
    write_text(
        OUT_DIR / "final_master_next_action_packet_summary.json",
        json.dumps(summary, indent=2, ensure_ascii=False),
    )
    write_text(DESKTOP_GUIDE, guide)
    summary["desktop_guide_exists"] = DESKTOP_GUIDE.exists()
    summary["desktop_plan_updated"] = update_desktop_plan(summary)
    write_text(
        OUT_DIR / "final_master_next_action_packet_summary.json",
        json.dumps(summary, indent=2, ensure_ascii=False),
    )


if __name__ == "__main__":
    main()
