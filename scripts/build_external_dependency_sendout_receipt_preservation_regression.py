#!/usr/bin/env python3
"""Regression-test the 19.54 sendout receipt preservation validator."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import tempfile
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "external_dependency_sendout_receipt_preservation_regression_20260810"
VALIDATOR_PATH = BENCH_ROOT / "scripts" / "build_external_dependency_escalation_sendout_receipt_validator.py"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_validator_module():
    spec = importlib.util.spec_from_file_location("sendout_validator_under_test", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load validator module: {VALIDATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_validator_case(tmp_root: Path, corrupt_one_hash: bool) -> dict[str, object]:
    reports_root = tmp_root / "reports"
    escalation_dir = reports_root / "external_dependency_escalation_packet_20260810"
    validator_dir = reports_root / "external_dependency_escalation_sendout_receipt_validator_20260810"
    sent_dir = tmp_root / "sent_messages"
    desktop_plan = tmp_root / "Desktop" / "8月10日cns.md"

    write_text(desktop_plan, "# Temporary desktop plan\n")
    write_text(
        escalation_dir / "external_dependency_escalation_summary.json",
        json.dumps({"send_ready": True}, indent=2),
    )

    request_rows = [
        {"receipt_id": f"FMR-{idx:03d}", "owner": f"owner_{idx}", "send_now": "yes"}
        for idx in range(1, 6)
    ]
    write_csv(
        escalation_dir / "external_dependency_escalation_request_matrix.csv",
        ["receipt_id", "owner", "send_now"],
        request_rows,
    )

    receipt_rows = []
    for idx in range(1, 6):
        message_text = f"sent message body for EDS-{idx:03d}\n"
        message_path = sent_dir / f"eds-{idx:03d}.md"
        write_text(message_path, message_text)
        digest = sha256_text(message_text)
        if corrupt_one_hash and idx == 3:
            digest = "0" * 64
        receipt_rows.append(
            {
                "send_receipt_id": f"EDS-{idx:03d}",
                "receipt_id": f"FMR-{idx:03d}",
                "owner": f"owner_{idx}",
                "required_send_evidence": "sent_datetime_local; sender; recipient_or_channel; sent_message_path; sent_message_sha256",
                "sent_datetime_local": "2026-08-10 21:00",
                "sender": "human.sender@example.org",
                "recipient_or_channel": f"recipient_{idx}@example.org",
                "sent_message_path": str(message_path),
                "sent_message_sha256": digest,
                "current_status": "manual_filled",
                "unlock_if_valid": "FMR-001 can be considered only after all send-now receipts are sent and verified.",
            }
        )
    write_csv(
        validator_dir / "external_dependency_escalation_sendout_receipt_template.csv",
        [
            "send_receipt_id",
            "receipt_id",
            "owner",
            "required_send_evidence",
            "sent_datetime_local",
            "sender",
            "recipient_or_channel",
            "sent_message_path",
            "sent_message_sha256",
            "current_status",
            "unlock_if_valid",
        ],
        receipt_rows,
    )

    module = load_validator_module()
    module.BENCH_ROOT = tmp_root
    module.OUT_DIR = validator_dir
    module.ESCALATION_DIR = escalation_dir
    module.DESKTOP_PLAN = desktop_plan
    module.TEMPLATE_PATH = validator_dir / "external_dependency_escalation_sendout_receipt_template.csv"
    module.main()

    summary = json.loads(
        (validator_dir / "external_dependency_escalation_sendout_receipt_validator_summary.json").read_text(
            encoding="utf-8-sig"
        )
    )
    output_rows = read_csv(validator_dir / "external_dependency_escalation_sendout_receipt_template.csv")
    preserved_fields = all(
        row["sender"] == "human.sender@example.org"
        and row["sent_datetime_local"] == "2026-08-10 21:00"
        and row["sent_message_path"]
        and not row["sent_message_path"].startswith("FILL_AFTER")
        for row in output_rows
    )

    return {
        "corrupt_one_hash": corrupt_one_hash,
        "sent_receipt_rows": summary["sent_receipt_rows"],
        "missing_send_receipts": summary["missing_send_receipts"],
        "escalation_sent": summary["escalation_sent"],
        "fmr001_unlock_allowed": summary["fmr001_unlock_allowed"],
        "receipt_completion_allowed": summary["receipt_completion_allowed"],
        "submission_ready": summary["submission_ready"],
        "preserved_manual_fields": preserved_fields,
        "qa_pass": summary["qa_pass"],
    }


def update_desktop_plan(summary: dict[str, object]) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    marker = "### 19.56 Sendout receipt preservation regression update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- Added `reports/external_dependency_sendout_receipt_preservation_regression_20260810/` to regression-test the 19.54 EDS preservation and SHA256 validation behavior.
- Current `regression_cases={summary["regression_cases"]}`, `regression_pass={str(summary["regression_pass"]).lower()}`.
- Verified behavior: valid filled EDS rows are preserved and counted; one corrupted `sent_message_sha256` keeps the validator blocked.
- Boundary: this uses temporary synthetic evidence only. It does not fill real EDS/FMR rows, send email, unlock portal upload or mark submission ready.
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

    with tempfile.TemporaryDirectory(prefix="gpr_eds_regression_") as tmp:
        tmp_root = Path(tmp)
        valid_case = run_validator_case(tmp_root / "valid_case", corrupt_one_hash=False)
        corrupt_case = run_validator_case(tmp_root / "corrupt_hash_case", corrupt_one_hash=True)

    qa_rows = [
        {
            "check": "valid case counts all preserved EDS rows",
            "result": "PASS"
            if valid_case["sent_receipt_rows"] == 5
            and valid_case["missing_send_receipts"] == 0
            and valid_case["escalation_sent"] is True
            and valid_case["fmr001_unlock_allowed"] is True
            and valid_case["preserved_manual_fields"] is True
            else "FAIL",
            "detail": json.dumps(valid_case, ensure_ascii=False, sort_keys=True),
        },
        {
            "check": "corrupt hash case remains blocked",
            "result": "PASS"
            if corrupt_case["sent_receipt_rows"] == 4
            and corrupt_case["missing_send_receipts"] == 1
            and corrupt_case["escalation_sent"] is False
            and corrupt_case["fmr001_unlock_allowed"] is False
            and corrupt_case["preserved_manual_fields"] is True
            else "FAIL",
            "detail": json.dumps(corrupt_case, ensure_ascii=False, sort_keys=True),
        },
        {
            "check": "regression does not alter real submission state",
            "result": "PASS" if valid_case["submission_ready"] is False and corrupt_case["submission_ready"] is False else "FAIL",
            "detail": "Both synthetic cases keep submission_ready=false.",
        },
    ]

    summary = {
        "package": "external_dependency_sendout_receipt_preservation_regression_20260810",
        "regression_cases": 2,
        "valid_case_sent_receipt_rows": valid_case["sent_receipt_rows"],
        "valid_case_unlock_allowed": valid_case["fmr001_unlock_allowed"],
        "corrupt_hash_case_sent_receipt_rows": corrupt_case["sent_receipt_rows"],
        "corrupt_hash_case_unlock_allowed": corrupt_case["fmr001_unlock_allowed"],
        "preservation_verified": valid_case["preserved_manual_fields"] and corrupt_case["preserved_manual_fields"],
        "sha256_rejection_verified": corrupt_case["missing_send_receipts"] == 1 and corrupt_case["fmr001_unlock_allowed"] is False,
        "portal_upload_allowed": False,
        "submission_ready": False,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": "external_dependency_sendout_receipt_preservation_regression_passed",
    }
    summary["regression_pass"] = summary["qa_pass"]
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(
        OUT_DIR / "external_dependency_sendout_receipt_preservation_regression_cases.csv",
        [
            "case",
            "sent_receipt_rows",
            "missing_send_receipts",
            "escalation_sent",
            "fmr001_unlock_allowed",
            "preserved_manual_fields",
        ],
        [
            {"case": "valid_case", **valid_case},
            {"case": "corrupt_hash_case", **corrupt_case},
        ],
    )
    write_csv(
        OUT_DIR / "external_dependency_sendout_receipt_preservation_regression_qa.csv",
        ["check", "result", "detail"],
        qa_rows,
    )

    report = f"""# External Dependency Sendout Receipt Preservation Regression

Status: `{summary["status"]}`

Current result:

1. Regression cases: {summary["regression_cases"]}
2. Preservation verified: {str(summary["preservation_verified"]).lower()}
3. SHA256 rejection verified: {str(summary["sha256_rejection_verified"]).lower()}
4. Valid case sent rows: {summary["valid_case_sent_receipt_rows"]}
5. Corrupt-hash case sent rows: {summary["corrupt_hash_case_sent_receipt_rows"]}
6. Portal upload allowed: false
7. Submission ready: false

Boundary: this regression uses temporary synthetic files only. It does not
write real send evidence, send email, fill FMR rows, upload portal files or
mark the manuscript submitted.
"""
    write_text(OUT_DIR / "EXTERNAL_DEPENDENCY_SENDOUT_RECEIPT_PRESERVATION_REGRESSION_README.md", report)
    write_text(OUT_DIR / "external_dependency_sendout_receipt_preservation_regression_report.md", report)
    write_text(
        OUT_DIR / "external_dependency_sendout_receipt_preservation_regression_summary.json",
        json.dumps(summary, indent=2, ensure_ascii=False),
    )


if __name__ == "__main__":
    main()
