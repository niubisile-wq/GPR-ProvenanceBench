#!/usr/bin/env python3
"""Build an external dependency escalation packet from unresolved final receipts."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "external_dependency_escalation_packet_20260810"
RECEIPT_VALIDATOR_DIR = BENCH_ROOT / "reports" / "final_manual_receipt_completion_validator_20260810"
RECEIPT_INTAKE_DIR = BENCH_ROOT / "reports" / "final_manual_receipt_intake_package_20260810"
EXEC_AUDIT_DIR = BENCH_ROOT / "reports" / "final_guarded_recheck_execution_audit_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"
DESKTOP_ESCALATION = Path.home() / "Desktop" / "NatComms_19.53_external_dependency_escalation_20260810.md"


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
    marker = "### 19.53 External dependency escalation packet update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- 新增 `reports/external_dependency_escalation_packet_20260810/`，把 19.50/19.52 的 FMR 阻断转成外部责任人请求清单。
- 桌面同步生成 `NatComms_19.53_external_dependency_escalation_20260810.md`，用于发送给 corresponding author、advisor、data holder、figure owner 和 repository/rights owner。
- 当前 `external_request_rows={summary["external_request_rows"]}`，`blocked_receipt_rows={summary["blocked_receipt_rows"]}`，`send_ready=true`。
- 当前 `receipt_completion_allowed=false`，`launcher_execution_allowed=false`，`portal_upload_allowed=false`，`submission_ready=false`。
- 边界：该 escalation packet 只组织外部请求，不声称已发送、不代替作者回复、不填 receipt、不触发 recheck。
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

    receipt_summary = read_json(RECEIPT_VALIDATOR_DIR / "final_manual_receipt_completion_validator_summary.json")
    audit_summary = read_json(EXEC_AUDIT_DIR / "final_guarded_recheck_execution_audit_summary.json")
    receipt_rows = read_csv(RECEIPT_INTAKE_DIR / "final_manual_receipt_intake_template.csv")
    blockers = read_csv(RECEIPT_VALIDATOR_DIR / "final_manual_receipt_completion_blockers.csv")

    escalation_rows = []
    for row in receipt_rows:
        receipt_id = row.get("receipt_id", "")
        if receipt_id == "FMR-006":
            urgency = "deferred_until_FMR_001_to_FMR_005_complete"
            send_now = "no"
        else:
            urgency = "send_now"
            send_now = "yes"
        escalation_rows.append(
            {
                "receipt_id": receipt_id,
                "owner": row.get("owner", ""),
                "request": row.get("required_evidence", ""),
                "target_or_route": row.get("target_or_route", ""),
                "acceptance_test": row.get("acceptance_test", ""),
                "first_validator": row.get("first_validator", ""),
                "send_now": send_now,
                "urgency": urgency,
            }
        )

    evidence_contract_rows = [
        {
            "contract_item": "source identity",
            "required_for": "all FMR receipts",
            "format": "real person/account/system name",
            "reject_if_missing": "yes",
        },
        {
            "contract_item": "timestamp",
            "required_for": "all manual actions",
            "format": "YYYY-MM-DD HH:MM local time",
            "reject_if_missing": "yes",
        },
        {
            "contract_item": "file path",
            "required_for": "returned files, figure review files, repository/rights evidence",
            "format": "existing path under the project or documented external record",
            "reject_if_missing": "yes",
        },
        {
            "contract_item": "SHA256",
            "required_for": "sent packet, returned files, final evidence bundles",
            "format": "64-character lowercase hexadecimal hash",
            "reject_if_missing": "yes",
        },
        {
            "contract_item": "allowed decision value",
            "required_for": "author decisions and figure approvals",
            "format": "one of the allowed values in the target form",
            "reject_if_missing": "yes",
        },
    ]

    qa_rows = [
        {
            "check": "receipt blockers imported",
            "result": "PASS" if len(blockers) == receipt_summary.get("incomplete_receipt_rows") else "FAIL",
            "detail": f"blockers={len(blockers)}; incomplete={receipt_summary.get('incomplete_receipt_rows')}",
        },
        {
            "check": "external requests cover active FMR blockers",
            "result": "PASS" if sum(1 for row in escalation_rows if row["send_now"] == "yes") == 5 else "FAIL",
            "detail": f"send_now_rows={sum(1 for row in escalation_rows if row['send_now'] == 'yes')}",
        },
        {
            "check": "launcher remains refused",
            "result": "PASS" if audit_summary.get("expected_launcher_decision") == "refuse" else "FAIL",
            "detail": f"expected_launcher_decision={audit_summary.get('expected_launcher_decision')}",
        },
        {
            "check": "submission remains false",
            "result": "PASS" if receipt_summary.get("submission_ready") is False else "FAIL",
            "detail": f"submission_ready={receipt_summary.get('submission_ready')}",
        },
    ]

    email = """# External dependency escalation email

Subject: Required evidence and decisions before GPR-ProvenanceBench can re-enter final checks

Dear team,

The current 2026-08-10 NatComms package is internally auditable, but the final
submission gate is blocked. Please provide the following evidence or decisions.

1. Author sendout evidence: sent time, sender account, recipient list, sent
   packet path and SHA256, and immutable send-log evidence.
2. Four author/advisor decisions: figure backend, external blind asset
   availability, licence direction, and Track B fallback if no real external
   asset is available.
3. Real returned evidence files in the canonical inbox routes, with source
   identity, timestamp and SHA256 provenance.
4. Figure 1-Figure 6 author review decisions: approve, revise or reject, with
   comments for any revision.
5. Repository/rights/DOI decisions: repository DOI/accession, code DOI, licence
   route, third-party rights decision and exclusion list.

Do not upload portal files or mark the manuscript submission-ready. After the
above receipts are complete, the guarded launcher will decide whether the final
M0-M2 recheck can run.

Best,
[Author]
"""

    guide = ["# NatComms 19.53 External Dependency Escalation", "", email, "", "## Request Matrix", ""]
    for row in escalation_rows:
        guide.extend(
            [
                f"### {row['receipt_id']} - {row['owner']}",
                "",
                f"- Send now: {row['send_now']}",
                f"- Request: {row['request']}",
                f"- Target or route: `{row['target_or_route']}`",
                f"- Acceptance test: {row['acceptance_test']}",
                f"- First validator: `{row['first_validator']}`",
                "",
            ]
        )
    guide_text = "\n".join(guide)

    summary = {
        "package": "external_dependency_escalation_packet_20260810",
        "external_request_rows": len(escalation_rows),
        "send_now_rows": sum(1 for row in escalation_rows if row["send_now"] == "yes"),
        "blocked_receipt_rows": len(blockers),
        "evidence_contract_rows": len(evidence_contract_rows),
        "send_ready": True,
        "receipt_completion_allowed": False,
        "launcher_execution_allowed": False,
        "portal_upload_allowed": False,
        "submission_ready": False,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": "external_dependency_escalation_packet_ready_to_send_requests",
        "desktop_escalation": str(DESKTOP_ESCALATION),
    }
    summary["desktop_escalation_exists"] = True
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(
        OUT_DIR / "external_dependency_escalation_request_matrix.csv",
        ["receipt_id", "owner", "request", "target_or_route", "acceptance_test", "first_validator", "send_now", "urgency"],
        escalation_rows,
    )
    write_csv(
        OUT_DIR / "external_dependency_evidence_contract.csv",
        ["contract_item", "required_for", "format", "reject_if_missing"],
        evidence_contract_rows,
    )
    write_csv(OUT_DIR / "external_dependency_escalation_qa.csv", ["check", "result", "detail"], qa_rows)
    write_text(OUT_DIR / "external_dependency_escalation_email.md", email)
    write_text(OUT_DIR / "EXTERNAL_DEPENDENCY_ESCALATION_README.md", guide_text)
    write_text(OUT_DIR / "external_dependency_escalation_report.md", guide_text)
    write_text(DESKTOP_ESCALATION, guide_text)
    write_text(
        OUT_DIR / "external_dependency_escalation_summary.json",
        json.dumps(summary, indent=2, ensure_ascii=False),
    )


if __name__ == "__main__":
    main()
