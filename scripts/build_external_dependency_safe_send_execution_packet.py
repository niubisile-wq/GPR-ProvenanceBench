#!/usr/bin/env python3
"""Build a manual-only safe-send execution packet for external dependency escalation."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "external_dependency_safe_send_execution_packet_20260810"
ESCALATION_DIR = BENCH_ROOT / "reports" / "external_dependency_escalation_packet_20260810"
SEND_RECEIPT_DIR = BENCH_ROOT / "reports" / "external_dependency_escalation_sendout_receipt_validator_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"
DESKTOP_GUIDE = Path.home() / "Desktop" / "NatComms_19.55_external_dependency_safe_send_20260810.md"


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


def _obsolete_update_desktop_plan(summary: dict[str, object]) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    marker = "### 19.55 External dependency safe-send execution packet update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- 新增 `reports/external_dependency_safe_send_execution_packet_20260810/`，把 19.53 邮件和 19.54 EDS 回执模板合并为人工安全发送清单。
- 桌面同步生成 `NatComms_19.55_external_dependency_safe_send_20260810.md`，用于人工发送前核对和发送后回填。
- 当前 `send_task_rows={summary["send_task_rows"]}`，`manual_send_allowed_rows={summary["manual_send_allowed_rows"]}`，`automatic_send_allowed=false`。
- 当前 `send_receipt_complete=false`，`fmr001_unlock_allowed=false`，`portal_upload_allowed=false`，`submission_ready=false`。
- 边界：该 packet 不发送邮件、不调用外部客户端、不伪造 SHA256、不回填 EDS/FMR，只给人工执行和回填路径。
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


def update_desktop_plan(summary: dict[str, object]) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    marker = "### 19.55 External dependency safe-send execution packet update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- Added `reports/external_dependency_safe_send_execution_packet_20260810/`, combining the 19.53 email draft and 19.54 EDS receipt template into a manual-only safe-send checklist.
- Desktop guide generated: `NatComms_19.55_external_dependency_safe_send_20260810.md`.
- Current `send_task_rows={summary["send_task_rows"]}`, `manual_send_allowed_rows={summary["manual_send_allowed_rows"]}`, `automatic_send_allowed=false`.
- Current `send_receipt_complete={str(summary["send_receipt_complete"]).lower()}`, `fmr001_unlock_allowed={str(summary["fmr001_unlock_allowed"]).lower()}`, `portal_upload_allowed=false`, `submission_ready=false`.
- Boundary: this packet does not send email, call an external client, fabricate SHA256 values, or fill EDS/FMR rows; it only gives the human execution and writeback route.
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

    escalation_summary = read_json(ESCALATION_DIR / "external_dependency_escalation_summary.json")
    send_summary = read_json(SEND_RECEIPT_DIR / "external_dependency_escalation_sendout_receipt_validator_summary.json")
    request_rows = read_csv(ESCALATION_DIR / "external_dependency_escalation_request_matrix.csv")
    send_receipts = read_csv(SEND_RECEIPT_DIR / "external_dependency_escalation_sendout_receipt_template.csv")
    email_text = (ESCALATION_DIR / "external_dependency_escalation_email.md").read_text(encoding="utf-8-sig")

    send_task_rows = []
    receipt_by_id = {row.get("receipt_id", ""): row for row in send_receipts}
    for row in request_rows:
        if row.get("send_now") != "yes":
            continue
        receipt = receipt_by_id.get(row.get("receipt_id", ""), {})
        send_task_rows.append(
            {
                "task_id": f"SEND-{len(send_task_rows) + 1:03d}",
                "receipt_id": row.get("receipt_id", ""),
                "send_receipt_id": receipt.get("send_receipt_id", ""),
                "owner": row.get("owner", ""),
                "send_channel": "manual_email_or_institutional_message",
                "message_source": "reports/external_dependency_escalation_packet_20260810/external_dependency_escalation_email.md",
                "required_after_send_fields": receipt.get("required_send_evidence", ""),
                "after_send_receipt_target": "reports/external_dependency_escalation_sendout_receipt_validator_20260810/external_dependency_escalation_sendout_receipt_template.csv",
                "manual_send_allowed": "yes",
                "automatic_send_allowed": "no",
                "post_send_validator": "py scripts/build_external_dependency_escalation_sendout_receipt_validator.py",
            }
        )

    pre_send_check_rows = [
        {
            "check": "message source exists",
            "expected": "external_dependency_escalation_email.md exists",
            "current": str((ESCALATION_DIR / "external_dependency_escalation_email.md").exists()),
            "passes_now": "yes" if (ESCALATION_DIR / "external_dependency_escalation_email.md").exists() else "no",
        },
        {
            "check": "send receipt template exists",
            "expected": "5 EDS rows",
            "current": f"sendout_receipt_rows={send_summary.get('sendout_receipt_rows')}",
            "passes_now": "yes" if send_summary.get("sendout_receipt_rows") == 5 else "no",
        },
        {
            "check": "automatic send is disabled",
            "expected": "automatic_send_allowed=false",
            "current": "automatic_send_allowed=false",
            "passes_now": "yes",
        },
        {
            "check": "submission remains blocked",
            "expected": "submission_ready=false",
            "current": f"submission_ready={send_summary.get('submission_ready')}",
            "passes_now": "yes" if send_summary.get("submission_ready") is False else "no",
        },
    ]

    forbidden_rows = [
        {
            "forbidden_action": "Send automatically from scripts or this agent.",
            "reason": "No mail client/session authority is configured and send evidence must be generated by a real human account.",
        },
        {
            "forbidden_action": "Mark EDS rows sent before real send evidence exists.",
            "reason": "EDS fields still contain FILL_AFTER_SEND placeholders.",
        },
        {
            "forbidden_action": "Unlock FMR-001 from the safe-send packet alone.",
            "reason": "Only 19.54 can validate sendout receipts after manual evidence is filled.",
        },
        {
            "forbidden_action": "Run guarded recheck after sending but before receiving/recording required evidence.",
            "reason": "FMR-001 through FMR-005 must be completed before FMR-006.",
        },
    ]

    qa_rows = [
        {
            "check": "19.53 send-ready state imported",
            "result": "PASS" if escalation_summary.get("send_ready") is True else "FAIL",
            "detail": f"send_ready={escalation_summary.get('send_ready')}",
        },
        {
            "check": "five manual send tasks generated",
            "result": "PASS" if len(send_task_rows) == 5 else "FAIL",
            "detail": f"send_task_rows={len(send_task_rows)}",
        },
        {
            "check": "19.54 still has zero sent receipts",
            "result": "PASS" if send_summary.get("sent_receipt_rows") == 0 else "FAIL",
            "detail": f"sent_receipt_rows={send_summary.get('sent_receipt_rows')}",
        },
        {
            "check": "automatic send remains disabled",
            "result": "PASS",
            "detail": "automatic_send_allowed=false",
        },
    ]

    guide_lines = [
        "# NatComms 19.55 External Dependency Safe-send Execution",
        "",
        "This is a manual-only send checklist. It does not send email.",
        "",
        "## Message Source",
        "",
        "`reports/external_dependency_escalation_packet_20260810/external_dependency_escalation_email.md`",
        "",
        "## Email Draft",
        "",
        email_text,
        "",
        "## Send Tasks",
        "",
    ]
    for row in send_task_rows:
        guide_lines.extend(
            [
                f"### {row['task_id']} / {row['receipt_id']} / {row['send_receipt_id']}",
                "",
                f"- Owner: {row['owner']}",
                f"- Send channel: {row['send_channel']}",
                f"- Required after-send fields: {row['required_after_send_fields']}",
                f"- Receipt target: `{row['after_send_receipt_target']}`",
                f"- Post-send validator: `{row['post_send_validator']}`",
                "",
            ]
        )
    guide_lines.extend(["## Forbidden", ""])
    for row in forbidden_rows:
        guide_lines.append(f"- {row['forbidden_action']} Reason: {row['reason']}")
    guide = "\n".join(guide_lines) + "\n"

    summary = {
        "package": "external_dependency_safe_send_execution_packet_20260810",
        "send_task_rows": len(send_task_rows),
        "manual_send_allowed_rows": sum(1 for row in send_task_rows if row["manual_send_allowed"] == "yes"),
        "automatic_send_allowed": False,
        "sent_receipt_rows": send_summary.get("sent_receipt_rows", 0),
        "missing_send_receipts": send_summary.get("missing_send_receipts", 0),
        "send_receipt_complete": send_summary.get("escalation_sent") is True,
        "fmr001_unlock_allowed": send_summary.get("fmr001_unlock_allowed") is True,
        "receipt_completion_allowed": send_summary.get("receipt_completion_allowed") is True,
        "portal_upload_allowed": False,
        "submission_ready": False,
        "desktop_guide": str(DESKTOP_GUIDE),
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": "external_dependency_safe_send_execution_packet_ready_manual_send_only",
    }
    write_csv(
        OUT_DIR / "external_dependency_safe_send_task_list.csv",
        [
            "task_id",
            "receipt_id",
            "send_receipt_id",
            "owner",
            "send_channel",
            "message_source",
            "required_after_send_fields",
            "after_send_receipt_target",
            "manual_send_allowed",
            "automatic_send_allowed",
            "post_send_validator",
        ],
        send_task_rows,
    )
    write_csv(
        OUT_DIR / "external_dependency_safe_send_preflight.csv",
        ["check", "expected", "current", "passes_now"],
        pre_send_check_rows,
    )
    write_csv(
        OUT_DIR / "external_dependency_safe_send_forbidden_actions.csv",
        ["forbidden_action", "reason"],
        forbidden_rows,
    )
    write_csv(OUT_DIR / "external_dependency_safe_send_execution_qa.csv", ["check", "result", "detail"], qa_rows)
    write_text(OUT_DIR / "EXTERNAL_DEPENDENCY_SAFE_SEND_EXECUTION_README.md", guide)
    write_text(OUT_DIR / "external_dependency_safe_send_execution_report.md", guide)
    write_text(DESKTOP_GUIDE, guide)
    summary["desktop_guide_exists"] = DESKTOP_GUIDE.exists()
    summary["desktop_plan_updated"] = update_desktop_plan(summary)
    write_text(
        OUT_DIR / "external_dependency_safe_send_execution_summary.json",
        json.dumps(summary, indent=2, ensure_ascii=False),
    )


if __name__ == "__main__":
    main()
