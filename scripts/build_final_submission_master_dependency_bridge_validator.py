#!/usr/bin/env python3
"""Bridge the latest closeout chain to final submission readiness."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "final_submission_master_dependency_bridge_validator_20260810"
AUTHOR_CLOSEOUT_DIR = BENCH_ROOT / "reports" / "author_final_closeout_dependency_bridge_validator_20260810"
LEDGER_DIR = BENCH_ROOT / "reports" / "submission_completion_ledger_20260810"
FINAL_LOCK_DIR = BENCH_ROOT / "reports" / "natcomms_submission_final_lock_validator_20260810"
PORTAL_FILE_DIR = BENCH_ROOT / "reports" / "portal_submission_file_preflight_20260810"
READINESS_DIR = BENCH_ROOT / "reports" / "submission_readiness_dashboard_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"


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


def as_bool(value: object) -> bool:
    return value is True or str(value).strip().lower() in {"true", "yes", "1"}


def update_desktop_plan(summary: dict[str, object]) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    marker = "### 19.47 Final submission master dependency bridge validator update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- 新增 `reports/final_submission_master_dependency_bridge_validator_20260810/`，把 19.46 author/final closeout bridge、submission completion ledger、NatComms submission final lock、portal file preflight 和 submission readiness dashboard 绑定成最终总封口。
- 当前 `author_closeout_allows_submission={str(summary["author_closeout_allows_submission"]).lower()}`，`ledger_allows_submission={str(summary["ledger_allows_submission"]).lower()}`，`natcomms_final_lock_allows_submission={str(summary["natcomms_final_lock_allows_submission"]).lower()}`。
- 当前 `portal_file_preflight_allows_upload={str(summary["portal_file_preflight_allows_upload"]).lower()}`，`dashboard_allows_submission={str(summary["dashboard_allows_submission"]).lower()}`，`final_submission_master_allowed=false`。
- 当前 `open_gate_rows={summary["open_gate_rows"]}`，`open_master_gates={summary["open_master_gates"]}`，`portal_upload_ready_rows={summary["portal_upload_ready_rows"]}`，`portal_file_upload_allowed_rows={summary["portal_file_upload_allowed_rows"]}`。
- 边界：该 bridge 是最终只读总封口，不关闭 gate、不上传 portal 文件、不生成提交号、不声称 manuscript 已投出。
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

    author_closeout = read_json(AUTHOR_CLOSEOUT_DIR / "author_final_closeout_dependency_bridge_validator_summary.json")
    ledger = read_json(LEDGER_DIR / "submission_completion_ledger_summary.json")
    final_lock = read_json(FINAL_LOCK_DIR / "natcomms_submission_final_lock_validator_summary.json")
    portal_file = read_json(PORTAL_FILE_DIR / "portal_submission_file_preflight_summary.json")
    readiness = read_json(READINESS_DIR / "submission_readiness_dashboard_summary.json")

    gate_ledger_rows = read_csv(LEDGER_DIR / "submission_completion_gate_ledger.csv")
    verification_rows = read_csv(LEDGER_DIR / "submission_final_verification_queue.csv")
    final_lock_gates = read_csv(FINAL_LOCK_DIR / "natcomms_submission_final_lock_gate_matrix.csv")
    portal_inventory = read_csv(PORTAL_FILE_DIR / "portal_submission_file_inventory.csv")

    author_closeout_allows_submission = (
        as_bool(author_closeout.get("qa_pass"))
        and as_bool(author_closeout.get("author_final_closeout_allowed"))
        and as_bool(author_closeout.get("submission_ready"))
    )
    ledger_allows_submission = (
        as_bool(ledger.get("qa_pass"))
        and int(ledger.get("open_gate_rows", 1)) == 0
        and as_bool(ledger.get("gate_closure_allowed"))
        and as_bool(ledger.get("portal_upload_ready"))
        and as_bool(ledger.get("submission_ready"))
    )
    natcomms_final_lock_allows_submission = (
        as_bool(final_lock.get("qa_pass"))
        and int(final_lock.get("open_master_gates", 1)) == 0
        and int(final_lock.get("blocked_commands", 1)) == 0
        and int(final_lock.get("portal_upload_ready_rows", 0)) > 0
        and int(final_lock.get("portal_file_upload_allowed_rows", 0)) > 0
        and as_bool(final_lock.get("submission_ready"))
    )
    portal_file_preflight_allows_upload = (
        as_bool(portal_file.get("qa_pass"))
        and as_bool(portal_file.get("upload_allowed_now"))
        and as_bool(portal_file.get("portal_upload_ready"))
        and as_bool(portal_file.get("submission_ready"))
    )
    dashboard_allows_submission = (
        int(readiness.get("open_gates", 1)) == 0
        and int(readiness.get("hard_no_go_or_not_ready_areas", 1)) == 0
        and as_bool(readiness.get("submission_ready"))
    )
    final_submission_master_allowed = (
        author_closeout_allows_submission
        and ledger_allows_submission
        and natcomms_final_lock_allows_submission
        and portal_file_preflight_allows_upload
        and dashboard_allows_submission
    )
    submission_ready = final_submission_master_allowed

    dependency_rows = [
        {
            "dependency": "author_closeout_allows_submission",
            "source": "19.46 author/final closeout dependency bridge",
            "current": author_closeout_allows_submission,
            "required": "true",
            "passes_now": "yes" if author_closeout_allows_submission else "no",
        },
        {
            "dependency": "ledger_allows_submission",
            "source": "submission completion ledger",
            "current": ledger_allows_submission,
            "required": "open_gate_rows=0 and ledger submission_ready=true",
            "passes_now": "yes" if ledger_allows_submission else "no",
        },
        {
            "dependency": "natcomms_final_lock_allows_submission",
            "source": "NatComms submission final lock validator",
            "current": natcomms_final_lock_allows_submission,
            "required": "open_master_gates=0 and portal upload rows ready",
            "passes_now": "yes" if natcomms_final_lock_allows_submission else "no",
        },
        {
            "dependency": "portal_file_preflight_allows_upload",
            "source": "portal submission file preflight",
            "current": portal_file_preflight_allows_upload,
            "required": "upload_allowed_now=true and portal_upload_ready=true",
            "passes_now": "yes" if portal_file_preflight_allows_upload else "no",
        },
        {
            "dependency": "dashboard_allows_submission",
            "source": "submission readiness dashboard",
            "current": dashboard_allows_submission,
            "required": "open_gates=0 and no hard no-go areas",
            "passes_now": "yes" if dashboard_allows_submission else "no",
        },
        {
            "dependency": "final_submission_master_allowed",
            "source": "19.47 bridge decision",
            "current": final_submission_master_allowed,
            "required": "true only after all final submission gates pass",
            "passes_now": "yes" if final_submission_master_allowed else "no",
        },
        {
            "dependency": "submission_ready",
            "source": "19.47 bridge boundary",
            "current": submission_ready,
            "required": "false in current blocked state",
            "passes_now": "yes" if not submission_ready else "no",
        },
    ]

    final_item_rows = []
    for row in gate_ledger_rows:
        final_item_rows.append(
            {
                "item_id": row.get("priority", ""),
                "item": row.get("gate", ""),
                "source": "submission_completion_gate_ledger",
                "current_state": row.get("current_status", row.get("closure_state", "")),
                "bridge_allowed": "yes" if ledger_allows_submission else "no",
                "reason": "Blocked until ledger has zero open gates and final verification passes.",
            }
        )
    for row in verification_rows:
        final_item_rows.append(
            {
                "item_id": row.get("order", ""),
                "item": row.get("verification", ""),
                "source": "submission_final_verification_queue",
                "current_state": row.get("current_state", ""),
                "bridge_allowed": "yes" if final_submission_master_allowed else "no",
                "reason": "Blocked until every final submission dependency passes.",
            }
        )
    for row in final_lock_gates:
        final_item_rows.append(
            {
                "item_id": row.get("gate_id", ""),
                "item": row.get("requirement", ""),
                "source": "natcomms_submission_final_lock_gate_matrix",
                "current_state": row.get("current_state", ""),
                "bridge_allowed": row.get("passes_now", "no") if final_submission_master_allowed else "no",
                "reason": row.get("blocking_reason", "Blocked by final master bridge."),
            }
        )
    for row in portal_inventory:
        final_item_rows.append(
            {
                "item_id": row.get("portal_item", ""),
                "item": row.get("current_source", ""),
                "source": "portal_submission_file_inventory",
                "current_state": row.get("current_state", ""),
                "bridge_allowed": row.get("upload_allowed_now", "no") if portal_file_preflight_allows_upload else "no",
                "reason": row.get("reason_not_allowed", "Blocked by portal file preflight."),
            }
        )

    blocker_rows = [
        {
            "blocker": "19.46 author/final closeout blocks submission",
            "evidence": (
                f"author_final_closeout_allowed={author_closeout.get('author_final_closeout_allowed')}; "
                f"open_master_gates={author_closeout.get('open_master_gates')}"
            ),
            "blocks": "final submission master gate",
        },
        {
            "blocker": "submission completion ledger has open gates",
            "evidence": (
                f"open_gate_rows={ledger.get('open_gate_rows')}; "
                f"gate_closure_allowed={ledger.get('gate_closure_allowed')}"
            ),
            "blocks": "submission completion",
        },
        {
            "blocker": "NatComms final lock remains blocked",
            "evidence": (
                f"open_master_gates={final_lock.get('open_master_gates')}; "
                f"blocked_commands={final_lock.get('blocked_commands')}; "
                f"portal_upload_ready_rows={final_lock.get('portal_upload_ready_rows')}"
            ),
            "blocks": "portal upload and final lock",
        },
        {
            "blocker": "portal file preflight blocks upload",
            "evidence": (
                f"upload_allowed_now={portal_file.get('upload_allowed_now')}; "
                f"portal_file_rows={portal_file.get('portal_file_rows')}"
            ),
            "blocks": "portal file upload",
        },
        {
            "blocker": "submission readiness dashboard still has no-go areas",
            "evidence": (
                f"open_gates={readiness.get('open_gates')}; "
                f"hard_no_go_or_not_ready_areas={readiness.get('hard_no_go_or_not_ready_areas')}"
            ),
            "blocks": "submission-ready state",
        },
    ]

    qa_rows = [
        {
            "check": "all upstream summaries loaded",
            "result": "PASS",
            "detail": "author closeout, ledger, final lock, portal preflight and readiness dashboard summaries loaded.",
        },
        {
            "check": "19.46 closeout bridge remains blocking",
            "result": "PASS" if not author_closeout_allows_submission else "FAIL",
            "detail": f"author_closeout_allows_submission={author_closeout_allows_submission}",
        },
        {
            "check": "NatComms final lock remains blocking",
            "result": "PASS" if not natcomms_final_lock_allows_submission else "FAIL",
            "detail": f"natcomms_final_lock_allows_submission={natcomms_final_lock_allows_submission}",
        },
        {
            "check": "portal upload remains blocked",
            "result": "PASS" if not portal_file_preflight_allows_upload else "FAIL",
            "detail": f"portal_file_preflight_allows_upload={portal_file_preflight_allows_upload}",
        },
        {
            "check": "submission remains false",
            "result": "PASS" if not submission_ready else "FAIL",
            "detail": f"submission_ready={submission_ready}",
        },
    ]

    summary = {
        "package": "final_submission_master_dependency_bridge_validator_20260810",
        "author_closeout_allows_submission": author_closeout_allows_submission,
        "ledger_allows_submission": ledger_allows_submission,
        "natcomms_final_lock_allows_submission": natcomms_final_lock_allows_submission,
        "portal_file_preflight_allows_upload": portal_file_preflight_allows_upload,
        "dashboard_allows_submission": dashboard_allows_submission,
        "final_submission_master_allowed": final_submission_master_allowed,
        "open_gate_rows": ledger.get("open_gate_rows", 0),
        "open_master_gates": final_lock.get("open_master_gates", 0),
        "portal_upload_ready_rows": final_lock.get("portal_upload_ready_rows", 0),
        "portal_file_upload_allowed_rows": final_lock.get("portal_file_upload_allowed_rows", 0),
        "dashboard_open_gates": readiness.get("open_gates", 0),
        "dashboard_hard_no_go_or_not_ready_areas": readiness.get("hard_no_go_or_not_ready_areas", 0),
        "submission_ready": submission_ready,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": "final_submission_master_dependency_bridge_validator_ready_blocked",
    }
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(
        OUT_DIR / "final_submission_master_dependency_bridge_matrix.csv",
        ["dependency", "source", "current", "required", "passes_now"],
        dependency_rows,
    )
    write_csv(
        OUT_DIR / "final_submission_master_item_bridge.csv",
        ["item_id", "item", "source", "current_state", "bridge_allowed", "reason"],
        final_item_rows,
    )
    write_csv(
        OUT_DIR / "final_submission_master_dependency_bridge_blockers.csv",
        ["blocker", "evidence", "blocks"],
        blocker_rows,
    )
    write_csv(
        OUT_DIR / "final_submission_master_dependency_bridge_qa.csv",
        ["check", "result", "detail"],
        qa_rows,
    )

    readme = """# Final Submission Master Dependency Bridge Validator

This validator is the final read-only bridge across the latest author closeout,
submission ledger, NatComms final lock, portal-file preflight and submission
readiness dashboard.

Boundary: read-only. It does not close gates, upload portal files, create a
submission number or claim the manuscript has been submitted.
"""
    write_text(OUT_DIR / "FINAL_SUBMISSION_MASTER_DEPENDENCY_BRIDGE_VALIDATOR_README.md", readme)

    report = f"""# Final Submission Master Dependency Bridge Validator Report

Status: `{summary["status"]}`

Current result:

1. Author closeout allows submission: {str(summary["author_closeout_allows_submission"]).lower()}
2. Ledger allows submission: {str(summary["ledger_allows_submission"]).lower()}
3. NatComms final lock allows submission: {str(summary["natcomms_final_lock_allows_submission"]).lower()}
4. Portal file preflight allows upload: {str(summary["portal_file_preflight_allows_upload"]).lower()}
5. Dashboard allows submission: {str(summary["dashboard_allows_submission"]).lower()}
6. Final submission master allowed: {str(summary["final_submission_master_allowed"]).lower()}
7. Submission ready: {str(summary["submission_ready"]).lower()}

Boundary: this package records the final dependency state only. It cannot
replace real author/external evidence, final artifact generation, portal upload
or a confirmed journal submission receipt.
"""
    write_text(OUT_DIR / "final_submission_master_dependency_bridge_validator_report.md", report)
    write_text(
        OUT_DIR / "final_submission_master_dependency_bridge_validator_summary.json",
        json.dumps(summary, indent=2, ensure_ascii=False),
    )


if __name__ == "__main__":
    main()
