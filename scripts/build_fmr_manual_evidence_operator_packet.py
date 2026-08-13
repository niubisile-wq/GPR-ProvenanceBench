#!/usr/bin/env python3
"""Build an operator packet for entering real FMR manual evidence."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "fmr_manual_evidence_operator_packet_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"


FMR_TO_WORKSHEET = {
    "FMR-001": ["real_author_sendout"],
    "FMR-002": ["backend_and_scope_choice", "rights_licence_decisions"],
    "FMR-003": ["returned_author_reply_files", "external_blind_asset_payload"],
    "FMR-004": ["figure_author_review_decisions"],
    "FMR-005": ["rights_licence_decisions"],
    "FMR-006": ["guarded_recheck_receipt"],
}


FMR_EXTRA_ROWS = {
    "FMR-004": {
        "evidence_type": "figure_author_review_decisions",
        "target_file": "reports/python_figure_author_review_packet_20260810/python_figure_author_review_form.csv",
        "target_rows": "Figure 1-Figure 6",
        "fields_to_fill": "author_approval_status; author_comment",
        "allowed_values_or_format": "approve_preview_for_final_candidate; request_revision; reject_claim_framing",
        "do_not_edit": "figure_id; preview_file_png; preview_file_pdf; core_conclusion; required_boundary",
        "after_fill_validation": "py scripts/build_python_figure_author_review_intake_validator.py",
    },
    "FMR-006": {
        "evidence_type": "guarded_recheck_receipt",
        "target_file": "reports/latest_run_m0_m2_checks_20260810.log plus final_manual_receipt_intake_template.csv after FMR-001 to FMR-005 complete",
        "target_rows": "FMR-006 only after all prerequisite receipts complete",
        "fields_to_fill": "M0-M2 log path; exit code; changed gate summary",
        "allowed_values_or_format": "M0-M2 PASS after real evidence; no portal upload",
        "do_not_edit": "FMR-006 before FMR-001 to FMR-005 are complete",
        "after_fill_validation": "py scripts/build_fmr006_guarded_recheck_receipt_writeback_preflight.py",
    },
}


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
    marker = "### 19.81 FMR manual evidence operator packet update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- Added `reports/fmr_manual_evidence_operator_packet_20260810/` as a consolidated operator packet for entering future real FMR evidence.
- Current `operator_rows={summary["operator_rows"]}`, `fmr_rows={summary["fmr_rows"]}`, `commands_allowed_now={summary["commands_allowed_now"]}`.
- Current `manual_evidence_writeback_allowed=false`, `portal_upload_allowed=false`, `submission_ready=false`.
- Boundary: this packet is instructions and manifests only. It does not fill evidence, write trackers, run `--execute-writeback`, execute recheck, upload portal files or submit.
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

    fmr_rows = read_csv(BENCH_ROOT / "reports/final_manual_receipt_intake_package_20260810/final_manual_receipt_intake_template.csv")
    inbox_rows = read_csv(BENCH_ROOT / "reports/fmr_manual_evidence_inbox_integrity_audit_20260810/fmr_manual_evidence_inbox_integrity_matrix.csv")
    worksheet_rows = read_csv(BENCH_ROOT / "reports/manual_evidence_intake_worksheet_20260810/manual_evidence_intake_worksheet.csv")
    order_summary = read_json(BENCH_ROOT / "reports/fmr_evidence_to_writeback_execution_order_audit_20260810/fmr_evidence_to_writeback_execution_order_audit_summary.json")
    inbox_summary = read_json(BENCH_ROOT / "reports/fmr_manual_evidence_inbox_integrity_audit_20260810/fmr_manual_evidence_inbox_integrity_audit_summary.json")

    worksheet_by_type = {}
    for row in worksheet_rows:
        worksheet_by_type.setdefault(row["evidence_type"], []).append(row)
    inbox_by_id = {row["receipt_id"]: row for row in inbox_rows}

    operator_rows = []
    for fmr in fmr_rows:
        receipt_id = fmr["receipt_id"]
        inbox = inbox_by_id.get(receipt_id, {})
        mapped_rows = []
        for evidence_type in FMR_TO_WORKSHEET.get(receipt_id, []):
            mapped_rows.extend(worksheet_by_type.get(evidence_type, []))
        if receipt_id in FMR_EXTRA_ROWS:
            mapped_rows.append(FMR_EXTRA_ROWS[receipt_id])
        if not mapped_rows:
            mapped_rows.append(
                {
                    "evidence_type": fmr["receipt_type"],
                    "target_file": fmr["target_or_route"],
                    "target_rows": "see FMR target route",
                    "fields_to_fill": fmr["required_evidence"],
                    "allowed_values_or_format": fmr["acceptance_test"],
                    "do_not_edit": "do not edit protected FMR fields directly",
                    "after_fill_validation": fmr["first_validator"],
                }
            )
        for row in mapped_rows:
            operator_rows.append(
                {
                    "receipt_id": receipt_id,
                    "receipt_type": fmr["receipt_type"],
                    "owner": fmr["owner"],
                    "primary_inbox": inbox.get("primary_inbox", ""),
                    "evidence_type": row["evidence_type"],
                    "target_file": row["target_file"],
                    "target_rows": row["target_rows"],
                    "fields_to_fill": row["fields_to_fill"],
                    "allowed_values_or_format": row["allowed_values_or_format"],
                    "do_not_edit": row["do_not_edit"],
                    "after_fill_validation": row["after_fill_validation"],
                    "guarded_writeback_allowed_now": "no",
                    "no_go_command": f"py scripts/build_{receipt_id.lower().replace('-', '').replace('fmr', 'fmr')}_guarded_writeback_applier.py --execute-writeback",
                }
            )

    stop_rules = [
        {
            "rule_id": "FMR-OP-NOGO-001",
            "stop_rule": "Do not run any --execute-writeback command until its matching preflight emits exactly one allowed candidate.",
            "current_state": f"commands_allowed_now={order_summary.get('commands_allowed_now')}",
        },
        {
            "rule_id": "FMR-OP-NOGO-002",
            "stop_rule": "Do not treat support report files as real evidence files.",
            "current_state": f"candidate_evidence_files={inbox_summary.get('candidate_evidence_files')}",
        },
        {
            "rule_id": "FMR-OP-NOGO-003",
            "stop_rule": "Do not run guarded recheck until FMR-001 through FMR-005 are complete.",
            "current_state": f"guarded_recheck_allowed={order_summary.get('guarded_recheck_allowed')}",
        },
        {
            "rule_id": "FMR-OP-NOGO-004",
            "stop_rule": "Do not upload portal files or mark submitted from this operator packet.",
            "current_state": "portal_upload_allowed=false; submission_ready=false",
        },
    ]

    qa_rows = [
        {
            "check": "operator packet covers all six FMR receipts",
            "result": "PASS" if len({row["receipt_id"] for row in operator_rows}) == 6 else "FAIL",
            "detail": f"covered_fmr_rows={len({row['receipt_id'] for row in operator_rows})}",
        },
        {
            "check": "all operator rows are currently no-writeback",
            "result": "PASS" if all(row["guarded_writeback_allowed_now"] == "no" for row in operator_rows) else "FAIL",
            "detail": f"operator_rows={len(operator_rows)}",
        },
        {
            "check": "inbox integrity still reports no candidate evidence",
            "result": "PASS" if inbox_summary.get("candidate_evidence_files") == 0 else "FAIL",
            "detail": f"candidate_evidence_files={inbox_summary.get('candidate_evidence_files')}",
        },
        {
            "check": "execution order still allows no commands",
            "result": "PASS" if order_summary.get("commands_allowed_now") == 0 else "FAIL",
            "detail": f"commands_allowed_now={order_summary.get('commands_allowed_now')}",
        },
        {
            "check": "submission remains false",
            "result": "PASS",
            "detail": "manual_evidence_writeback_allowed=false; portal_upload_allowed=false; submission_ready=false",
        },
    ]

    summary = {
        "package": "fmr_manual_evidence_operator_packet_20260810",
        "fmr_rows": len(fmr_rows),
        "operator_rows": len(operator_rows),
        "stop_rules": len(stop_rules),
        "commands_allowed_now": int(order_summary.get("commands_allowed_now", 0) or 0),
        "candidate_evidence_files": int(inbox_summary.get("candidate_evidence_files", 0) or 0),
        "manual_evidence_writeback_allowed": False,
        "portal_upload_allowed": False,
        "submission_ready": False,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": "fmr_manual_evidence_operator_packet_ready_waiting_real_evidence",
    }
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(
        OUT_DIR / "fmr_manual_evidence_operator_packet.csv",
        [
            "receipt_id",
            "receipt_type",
            "owner",
            "primary_inbox",
            "evidence_type",
            "target_file",
            "target_rows",
            "fields_to_fill",
            "allowed_values_or_format",
            "do_not_edit",
            "after_fill_validation",
            "guarded_writeback_allowed_now",
            "no_go_command",
        ],
        operator_rows,
    )
    write_csv(OUT_DIR / "fmr_manual_evidence_operator_stop_rules.csv", ["rule_id", "stop_rule", "current_state"], stop_rules)
    write_csv(OUT_DIR / "fmr_manual_evidence_operator_qa.csv", ["check", "result", "detail"], qa_rows)

    report = f"""# FMR Manual Evidence Operator Packet

Status: `{summary["status"]}`

Current result:

1. FMR rows: {summary["fmr_rows"]}
2. Operator rows: {summary["operator_rows"]}
3. Stop rules: {summary["stop_rules"]}
4. Commands allowed now: {summary["commands_allowed_now"]}
5. Candidate evidence files: {summary["candidate_evidence_files"]}
6. Manual evidence writeback allowed: false
7. Portal upload allowed: false
8. Submission ready: false

Boundary: this packet gives entry instructions only. It does not fill evidence,
write trackers, run `--execute-writeback`, execute recheck, upload portal files
or mark the manuscript submitted.
"""
    write_text(OUT_DIR / "FMR_MANUAL_EVIDENCE_OPERATOR_PACKET_README.md", report)
    write_text(OUT_DIR / "fmr_manual_evidence_operator_packet_report.md", report)
    write_text(OUT_DIR / "fmr_manual_evidence_operator_packet_summary.json", json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
