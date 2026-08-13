#!/usr/bin/env python3
"""Bridge RB-001 closeout dependencies across return tracker, hash readiness and receipt completion."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "rb001_closeout_dependency_bridge_validator_20260810"
CROSSWALK_DIR = BENCH_ROOT / "reports" / "natcomms_return_tracker_to_rb001_crosswalk_validator_20260810"
HASH_READY_DIR = BENCH_ROOT / "reports" / "rb001_hash_manifest_readiness_validator_20260810"
RECEIPT_VALIDATOR_DIR = BENCH_ROOT / "reports" / "rb001_receipt_completion_validator_20260810"
CLOSEOUT_DIR = BENCH_ROOT / "reports" / "rb001_closeout_dashboard_20260810"
RB002_DIR = BENCH_ROOT / "reports" / "rb002_writeback_readiness_dashboard_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


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
    marker = "### 19.40 RB-001 closeout dependency bridge validator update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- 新增 `reports/rb001_closeout_dependency_bridge_validator_20260810/`，把 19.38 return-to-RB001 crosswalk、19.39 hash manifest readiness、RB-001 receipt completion、RB-001 closeout dashboard 和 RB-002 readiness 串成一个总前置门。
- 当前 `return_tracker_to_rb001_ready={str(summary["return_tracker_to_rb001_ready"]).lower()}`，`hash_manifest_ready={str(summary["hash_manifest_ready"]).lower()}`，`receipt_complete={str(summary["receipt_complete"]).lower()}`。
- 当前 `rb001_closeout_allowed={str(summary["rb001_closeout_allowed"]).lower()}`，`writeback_preflight_allowed={str(summary["writeback_preflight_allowed"]).lower()}`，`rb002_entry_allowed={str(summary["rb002_entry_allowed"]).lower()}`。
- 当前 `candidate_return_files=0`，`writeback_allowed_rows=0`，`submission_ready=false`。
- 边界：该 bridge 只读依赖状态，不复制文件、不计算 hash、不填写 receipt、不关闭 RB-001、不写回 RB-002。
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

    crosswalk = read_json(CROSSWALK_DIR / "return_tracker_to_rb001_crosswalk_validator_summary.json")
    hash_ready = read_json(HASH_READY_DIR / "rb001_hash_manifest_readiness_validator_summary.json")
    receipt = read_json(RECEIPT_VALIDATOR_DIR / "rb001_receipt_completion_validator_summary.json")
    closeout = read_json(CLOSEOUT_DIR / "rb001_closeout_dashboard_summary.json")
    rb002 = read_json(RB002_DIR / "rb002_writeback_readiness_dashboard_summary.json")

    return_tracker_to_rb001_ready = crosswalk.get("return_tracker_to_rb001_ready") is True
    rb001_drop_allowed = crosswalk.get("rb001_drop_allowed") is True
    hash_manifest_ready = hash_ready.get("hash_manifest_ready") is True
    receipt_closeout_allowed = hash_ready.get("receipt_closeout_allowed") is True
    receipt_complete = receipt.get("receipt_complete") is True
    receipt_validator_allows_writeback_preflight = receipt.get("writeback_preflight_entry_allowed") is True
    rb001_closed = closeout.get("rb001_closed") is True
    rb001_closeout_allowed = (
        return_tracker_to_rb001_ready
        and rb001_drop_allowed
        and hash_manifest_ready
        and receipt_closeout_allowed
        and receipt_complete
    )
    writeback_preflight_allowed = (
        rb001_closeout_allowed
        and receipt_validator_allows_writeback_preflight
        and rb001_closed
    )
    rb002_entry_allowed = writeback_preflight_allowed and rb002.get("rb002_ready") is True

    dependency_rows = [
        {
            "dependency": "return_tracker_to_rb001_ready",
            "source": "19.38 crosswalk",
            "current": return_tracker_to_rb001_ready,
            "required": "true",
            "passes_now": "yes" if return_tracker_to_rb001_ready else "no",
        },
        {
            "dependency": "rb001_drop_allowed",
            "source": "19.38 crosswalk",
            "current": rb001_drop_allowed,
            "required": "true",
            "passes_now": "yes" if rb001_drop_allowed else "no",
        },
        {
            "dependency": "hash_manifest_ready",
            "source": "19.39 hash readiness",
            "current": hash_manifest_ready,
            "required": "true",
            "passes_now": "yes" if hash_manifest_ready else "no",
        },
        {
            "dependency": "receipt_closeout_allowed",
            "source": "19.39 hash readiness",
            "current": receipt_closeout_allowed,
            "required": "true",
            "passes_now": "yes" if receipt_closeout_allowed else "no",
        },
        {
            "dependency": "receipt_complete",
            "source": "RB-001 receipt validator",
            "current": receipt_complete,
            "required": "true",
            "passes_now": "yes" if receipt_complete else "no",
        },
        {
            "dependency": "receipt_validator_allows_writeback_preflight",
            "source": "RB-001 receipt validator",
            "current": receipt_validator_allows_writeback_preflight,
            "required": "true",
            "passes_now": "yes" if receipt_validator_allows_writeback_preflight else "no",
        },
        {
            "dependency": "rb001_closed",
            "source": "RB-001 closeout dashboard",
            "current": rb001_closed,
            "required": "true",
            "passes_now": "yes" if rb001_closed else "no",
        },
        {
            "dependency": "rb001_closeout_allowed",
            "source": "bridge decision",
            "current": rb001_closeout_allowed,
            "required": "true",
            "passes_now": "yes" if rb001_closeout_allowed else "no",
        },
        {
            "dependency": "writeback_preflight_allowed",
            "source": "bridge decision",
            "current": writeback_preflight_allowed,
            "required": "true",
            "passes_now": "yes" if writeback_preflight_allowed else "no",
        },
        {
            "dependency": "rb002_entry_allowed",
            "source": "bridge decision",
            "current": rb002_entry_allowed,
            "required": "true",
            "passes_now": "yes" if rb002_entry_allowed else "no",
        },
        {
            "dependency": "submission_ready",
            "source": "bridge boundary",
            "current": False,
            "required": "false",
            "passes_now": "yes",
        },
    ]

    blocker_rows = [
        {
            "blocker": "real returned files absent",
            "evidence": f"candidate_return_files={closeout.get('candidate_return_files')}; returned_rows={crosswalk.get('returned_rows')}",
            "blocks": "return_tracker_to_rb001_ready; hash_manifest_ready",
        },
        {
            "blocker": "hash manifest still template",
            "evidence": f"filled_manifest_rows={hash_ready.get('filled_manifest_rows')}; scanner_file_rows={hash_ready.get('scanner_file_rows')}",
            "blocks": "hash_manifest_ready; receipt_closeout_allowed",
        },
        {
            "blocker": "manual receipt incomplete",
            "evidence": f"completed_receipt_rows={receipt.get('completed_receipt_rows')}; receipt_complete={receipt.get('receipt_complete')}",
            "blocks": "rb001_closeout_allowed; writeback_preflight_allowed",
        },
        {
            "blocker": "RB-001 not closed",
            "evidence": f"rb001_closed={closeout.get('rb001_closed')}",
            "blocks": "writeback_preflight_allowed; rb002_entry_allowed",
        },
        {
            "blocker": "RB-002 not ready",
            "evidence": f"rb002_ready={rb002.get('rb002_ready')}; writeback_allowed_rows={rb002.get('writeback_allowed_rows')}",
            "blocks": "rb002_entry_allowed",
        },
    ]

    qa_rows = [
        {
            "check": "all upstream summaries loaded",
            "result": "PASS",
            "detail": "crosswalk, hash readiness, receipt, closeout and rb002 summaries loaded.",
        },
        {
            "check": "bridge keeps closeout blocked when upstream is blocked",
            "result": "PASS" if not rb001_closeout_allowed else "FAIL",
            "detail": f"rb001_closeout_allowed={rb001_closeout_allowed}",
        },
        {
            "check": "bridge keeps writeback blocked",
            "result": "PASS" if not writeback_preflight_allowed else "FAIL",
            "detail": f"writeback_preflight_allowed={writeback_preflight_allowed}",
        },
        {
            "check": "bridge keeps rb002 blocked",
            "result": "PASS" if not rb002_entry_allowed else "FAIL",
            "detail": f"rb002_entry_allowed={rb002_entry_allowed}",
        },
        {
            "check": "submission remains false",
            "result": "PASS",
            "detail": "bridge cannot make submission ready.",
        },
    ]

    summary = {
        "package": "rb001_closeout_dependency_bridge_validator_20260810",
        "return_tracker_to_rb001_ready": return_tracker_to_rb001_ready,
        "rb001_drop_allowed": rb001_drop_allowed,
        "hash_manifest_ready": hash_manifest_ready,
        "receipt_closeout_allowed": receipt_closeout_allowed,
        "receipt_complete": receipt_complete,
        "receipt_validator_allows_writeback_preflight": receipt_validator_allows_writeback_preflight,
        "rb001_closed": rb001_closed,
        "rb001_closeout_allowed": rb001_closeout_allowed,
        "writeback_preflight_allowed": writeback_preflight_allowed,
        "rb002_entry_allowed": rb002_entry_allowed,
        "candidate_return_files": closeout.get("candidate_return_files", 0),
        "writeback_allowed_rows": closeout.get("writeback_allowed_rows", 0),
        "submission_ready": False,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": "rb001_closeout_dependency_bridge_validator_ready_blocked_upstream_missing",
    }
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(
        OUT_DIR / "rb001_closeout_dependency_bridge_matrix.csv",
        ["dependency", "source", "current", "required", "passes_now"],
        dependency_rows,
    )
    write_csv(
        OUT_DIR / "rb001_closeout_dependency_bridge_blockers.csv",
        ["blocker", "evidence", "blocks"],
        blocker_rows,
    )
    write_csv(
        OUT_DIR / "rb001_closeout_dependency_bridge_qa.csv",
        ["check", "result", "detail"],
        qa_rows,
    )

    readme = """# RB-001 Closeout Dependency Bridge Validator

This validator bridges the returned-file crosswalk, hash manifest readiness,
manual receipt completion, RB-001 closeout dashboard and RB-002 readiness before
any closeout or writeback preflight can be considered.

Boundary: it is read-only. It does not copy files, calculate hashes, fill
receipts, close RB-001, write protected targets, enter RB-002 or make the
manuscript submission-ready.
"""
    write_text(OUT_DIR / "RB001_CLOSEOUT_DEPENDENCY_BRIDGE_VALIDATOR_README.md", readme)

    report = f"""# RB-001 Closeout Dependency Bridge Validator Report

Status: `{summary["status"]}`

Current result:

1. Return tracker to RB-001 ready: {str(summary["return_tracker_to_rb001_ready"]).lower()}
2. Hash manifest ready: {str(summary["hash_manifest_ready"]).lower()}
3. Receipt complete: {str(summary["receipt_complete"]).lower()}
4. RB-001 closed: {str(summary["rb001_closed"]).lower()}
5. RB-001 closeout allowed: {str(summary["rb001_closeout_allowed"]).lower()}
6. Writeback preflight allowed: {str(summary["writeback_preflight_allowed"]).lower()}
7. RB-002 entry allowed: {str(summary["rb002_entry_allowed"]).lower()}
8. Candidate return files: {summary["candidate_return_files"]}
9. Writeback allowed rows: {summary["writeback_allowed_rows"]}
10. Submission ready: false

Interpretation: RB-001 closeout now has an explicit dependency bridge across
return intake, hash manifest readiness and manual receipt completion. Current
state remains blocked because real returned files and completed manifest/receipt
evidence are absent.
"""
    write_text(OUT_DIR / "rb001_closeout_dependency_bridge_validator_report.md", report)
    write_text(
        OUT_DIR / "rb001_closeout_dependency_bridge_validator_summary.json",
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
    )

    if not summary["qa_pass"]:
        raise SystemExit("RB-001 closeout dependency bridge validator QA failed")

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
