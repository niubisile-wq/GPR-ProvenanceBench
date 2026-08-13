#!/usr/bin/env python3
"""Bridge author decision closure and final human closeout to the latest final gates."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "author_final_closeout_dependency_bridge_validator_20260810"
FIGURE_PORTAL_DIR = BENCH_ROOT / "reports" / "figure_portal_final_dependency_bridge_validator_20260810"
AUTHOR_CLOSURE_DIR = BENCH_ROOT / "reports" / "author_decision_closure_packet_v2_20260810"
HUMAN_CLOSEOUT_DIR = BENCH_ROOT / "reports" / "final_human_execution_closeout_board_20260810"
RESIDUAL_PACKET_DIR = BENCH_ROOT / "reports" / "final_residual_blocker_closure_packet_20260810"
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
    marker = "### 19.46 Author/final closeout dependency bridge validator update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- 新增 `reports/author_final_closeout_dependency_bridge_validator_20260810/`，把 19.45 figure/portal bridge、author decision closure v2、final human execution closeout board 和 final residual blocker closure packet 绑定到作者最终决策闭环。
- 当前 `figure_portal_bridge_allows_closeout={str(summary["figure_portal_bridge_allows_closeout"]).lower()}`，`author_decisions_closed={str(summary["author_decisions_closed"]).lower()}`，`human_closeout_closed={str(summary["human_closeout_closed"]).lower()}`。
- 当前 `residual_blockers_closed={str(summary["residual_blockers_closed"]).lower()}`，`author_final_closeout_allowed={str(summary["author_final_closeout_allowed"]).lower()}`，`submission_ready=false`。
- 当前 `decision_rows={summary["decision_rows"]}`，`closed_action_rows={summary["closed_action_rows"]}`，`ready_to_close_rows={summary["ready_to_close_rows"]}`，`open_master_gates={summary["open_master_gates"]}`。
- 边界：该 bridge 只读，不代替作者回复、不发送邮件、不关闭 residual blockers、不上传 portal 文件、不提交 manuscript。
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

    figure_portal = read_json(FIGURE_PORTAL_DIR / "figure_portal_final_dependency_bridge_validator_summary.json")
    author_closure = read_json(AUTHOR_CLOSURE_DIR / "author_decision_closure_packet_v2_summary.json")
    human_closeout = read_json(HUMAN_CLOSEOUT_DIR / "final_human_execution_closeout_board_summary.json")
    residual_packet = read_json(RESIDUAL_PACKET_DIR / "final_residual_blocker_closure_packet_summary.json")

    decision_rows = read_csv(AUTHOR_CLOSURE_DIR / "author_decision_closure_form_v2.csv")
    next24_rows = read_csv(AUTHOR_CLOSURE_DIR / "next_24h_decision_closure_queue.csv")
    human_actions = read_csv(HUMAN_CLOSEOUT_DIR / "final_human_execution_action_queue.csv")
    residual_rows = read_csv(RESIDUAL_PACKET_DIR / "final_residual_blocker_closure_packet.csv")

    figure_portal_bridge_allows_closeout = (
        as_bool(figure_portal.get("qa_pass"))
        and as_bool(figure_portal.get("figure_portal_upload_allowed"))
        and as_bool(figure_portal.get("portal_upload_ready"))
    )
    author_decisions_closed = (
        as_bool(author_closure.get("qa_pass"))
        and author_closure.get("decision_rows", 0) == 0
        and as_bool(author_closure.get("submission_ready"))
    )
    human_closeout_closed = (
        as_bool(human_closeout.get("qa_pass"))
        and int(human_closeout.get("blocked_action_rows", 1)) == 0
        and int(human_closeout.get("closed_action_rows", 0)) == int(human_closeout.get("action_rows", -1))
        and int(human_closeout.get("open_master_gates", 1)) == 0
        and as_bool(human_closeout.get("submission_ready"))
    )
    residual_blockers_closed = (
        as_bool(residual_packet.get("qa_pass"))
        and int(residual_packet.get("ready_to_close_rows", 0)) == int(residual_packet.get("closure_rows", -1))
        and int(residual_packet.get("blocked_validation_commands", 1)) == 0
        and int(residual_packet.get("open_master_gates", 1)) == 0
        and as_bool(residual_packet.get("submission_ready"))
    )
    author_final_closeout_allowed = (
        figure_portal_bridge_allows_closeout
        and author_decisions_closed
        and human_closeout_closed
        and residual_blockers_closed
    )
    submission_ready = author_final_closeout_allowed and as_bool(figure_portal.get("submission_ready"))

    dependency_rows = [
        {
            "dependency": "figure_portal_bridge_allows_closeout",
            "source": "19.45 figure/portal final dependency bridge",
            "current": figure_portal_bridge_allows_closeout,
            "required": "true",
            "passes_now": "yes" if figure_portal_bridge_allows_closeout else "no",
        },
        {
            "dependency": "author_decisions_closed",
            "source": "author decision closure packet v2",
            "current": author_decisions_closed,
            "required": "all author decisions resolved and accepted",
            "passes_now": "yes" if author_decisions_closed else "no",
        },
        {
            "dependency": "human_closeout_closed",
            "source": "final human execution closeout board",
            "current": human_closeout_closed,
            "required": "all human actions closed, open_master_gates=0",
            "passes_now": "yes" if human_closeout_closed else "no",
        },
        {
            "dependency": "residual_blockers_closed",
            "source": "final residual blocker closure packet",
            "current": residual_blockers_closed,
            "required": "all residual blockers ready to close and validation commands unblocked",
            "passes_now": "yes" if residual_blockers_closed else "no",
        },
        {
            "dependency": "author_final_closeout_allowed",
            "source": "19.46 bridge decision",
            "current": author_final_closeout_allowed,
            "required": "true only after all upstream closeout gates pass",
            "passes_now": "yes" if author_final_closeout_allowed else "no",
        },
        {
            "dependency": "submission_ready",
            "source": "19.46 bridge boundary",
            "current": submission_ready,
            "required": "false in current blocked state",
            "passes_now": "yes" if not submission_ready else "no",
        },
    ]

    action_rows = []
    for row in decision_rows:
        action_rows.append(
            {
                "item_id": row.get("decision_id", ""),
                "item": row.get("decision", ""),
                "source": "author_decision_closure_form_v2",
                "current_status": "decision_required",
                "bridge_allowed": "yes" if author_final_closeout_allowed else "no",
                "reason": "Blocked until author decisions, residual blockers and figure/portal gates all close.",
            }
        )
    for row in next24_rows:
        action_rows.append(
            {
                "item_id": row.get("hour", ""),
                "item": row.get("action", ""),
                "source": "next_24h_decision_closure_queue",
                "current_status": "pending_author_action",
                "bridge_allowed": "yes" if author_final_closeout_allowed else "no",
                "reason": "Blocked as final closeout evidence; manual action remains required.",
            }
        )
    for row in human_actions:
        action_rows.append(
            {
                "item_id": row.get("action_id", ""),
                "item": row.get("action", ""),
                "source": "final_human_execution_action_queue",
                "current_status": row.get("current_status", ""),
                "bridge_allowed": "yes" if human_closeout_closed else "no",
                "reason": "Blocked until all human execution actions are closed.",
            }
        )
    for row in residual_rows:
        action_rows.append(
            {
                "item_id": row.get("blocker_id", ""),
                "item": row.get("closure_item", ""),
                "source": "final_residual_blocker_closure_packet",
                "current_status": row.get("current_blocker", ""),
                "bridge_allowed": "yes" if residual_blockers_closed else "no",
                "reason": "Blocked until every residual blocker is ready to close.",
            }
        )

    blocker_rows = [
        {
            "blocker": "19.45 figure/portal bridge blocks closeout",
            "evidence": (
                f"figure_portal_upload_allowed={figure_portal.get('figure_portal_upload_allowed')}; "
                f"portal_upload_ready={figure_portal.get('portal_upload_ready')}"
            ),
            "blocks": "author final closeout",
        },
        {
            "blocker": "author decisions remain required",
            "evidence": (
                f"decision_rows={author_closure.get('decision_rows')}; "
                f"next24_rows={author_closure.get('next24_rows')}"
            ),
            "blocks": "branch/backend/licence/framing lock",
        },
        {
            "blocker": "human execution actions all blocked",
            "evidence": (
                f"blocked_action_rows={human_closeout.get('blocked_action_rows')}; "
                f"closed_action_rows={human_closeout.get('closed_action_rows')}; "
                f"open_master_gates={human_closeout.get('open_master_gates')}"
            ),
            "blocks": "final closeout board",
        },
        {
            "blocker": "residual blockers not closeable",
            "evidence": (
                f"ready_to_close_rows={residual_packet.get('ready_to_close_rows')}; "
                f"blocked_validation_commands={residual_packet.get('blocked_validation_commands')}; "
                f"candidate_return_files={residual_packet.get('candidate_return_files')}"
            ),
            "blocks": "final submission gate",
        },
    ]

    qa_rows = [
        {
            "check": "all upstream summaries loaded",
            "result": "PASS",
            "detail": "figure/portal bridge, author closure, human closeout and residual packet summaries loaded.",
        },
        {
            "check": "figure/portal bridge remains blocking",
            "result": "PASS" if not figure_portal_bridge_allows_closeout else "FAIL",
            "detail": f"figure_portal_bridge_allows_closeout={figure_portal_bridge_allows_closeout}",
        },
        {
            "check": "author decisions remain open",
            "result": "PASS" if not author_decisions_closed else "FAIL",
            "detail": f"author_decisions_closed={author_decisions_closed}",
        },
        {
            "check": "final human closeout remains open",
            "result": "PASS" if not human_closeout_closed else "FAIL",
            "detail": f"human_closeout_closed={human_closeout_closed}",
        },
        {
            "check": "submission remains false",
            "result": "PASS" if not submission_ready else "FAIL",
            "detail": f"submission_ready={submission_ready}",
        },
    ]

    summary = {
        "package": "author_final_closeout_dependency_bridge_validator_20260810",
        "figure_portal_bridge_allows_closeout": figure_portal_bridge_allows_closeout,
        "author_decisions_closed": author_decisions_closed,
        "human_closeout_closed": human_closeout_closed,
        "residual_blockers_closed": residual_blockers_closed,
        "author_final_closeout_allowed": author_final_closeout_allowed,
        "decision_rows": author_closure.get("decision_rows", 0),
        "next24_rows": author_closure.get("next24_rows", 0),
        "closed_action_rows": human_closeout.get("closed_action_rows", 0),
        "blocked_action_rows": human_closeout.get("blocked_action_rows", 0),
        "ready_to_close_rows": residual_packet.get("ready_to_close_rows", 0),
        "blocked_validation_commands": residual_packet.get("blocked_validation_commands", 0),
        "open_master_gates": residual_packet.get("open_master_gates", human_closeout.get("open_master_gates", 0)),
        "candidate_return_files": residual_packet.get("candidate_return_files", 0),
        "submission_ready": submission_ready,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": "author_final_closeout_dependency_bridge_validator_ready_blocked",
    }
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(
        OUT_DIR / "author_final_closeout_dependency_bridge_matrix.csv",
        ["dependency", "source", "current", "required", "passes_now"],
        dependency_rows,
    )
    write_csv(
        OUT_DIR / "author_final_closeout_action_bridge.csv",
        ["item_id", "item", "source", "current_status", "bridge_allowed", "reason"],
        action_rows,
    )
    write_csv(
        OUT_DIR / "author_final_closeout_dependency_bridge_blockers.csv",
        ["blocker", "evidence", "blocks"],
        blocker_rows,
    )
    write_csv(
        OUT_DIR / "author_final_closeout_dependency_bridge_qa.csv",
        ["check", "result", "detail"],
        qa_rows,
    )

    readme = """# Author/final Closeout Dependency Bridge Validator

This validator bridges author decision closure, final human execution closeout
and residual blocker closure to the latest figure/portal final dependency gate.

Boundary: read-only. It does not replace author replies, send email, close
residual blockers, upload portal files or mark the manuscript submission-ready.
"""
    write_text(OUT_DIR / "AUTHOR_FINAL_CLOSEOUT_DEPENDENCY_BRIDGE_VALIDATOR_README.md", readme)

    report = f"""# Author/final Closeout Dependency Bridge Validator Report

Status: `{summary["status"]}`

Current result:

1. Figure/portal bridge allows closeout: {str(summary["figure_portal_bridge_allows_closeout"]).lower()}
2. Author decisions closed: {str(summary["author_decisions_closed"]).lower()}
3. Human closeout closed: {str(summary["human_closeout_closed"]).lower()}
4. Residual blockers closed: {str(summary["residual_blockers_closed"]).lower()}
5. Author final closeout allowed: {str(summary["author_final_closeout_allowed"]).lower()}
6. Submission ready: {str(summary["submission_ready"]).lower()}

Boundary: this package records closeout dependencies only. It cannot substitute
for real author replies, external evidence, residual-blocker validation or final
submission verification.
"""
    write_text(OUT_DIR / "author_final_closeout_dependency_bridge_validator_report.md", report)
    write_text(
        OUT_DIR / "author_final_closeout_dependency_bridge_validator_summary.json",
        json.dumps(summary, indent=2, ensure_ascii=False),
    )


if __name__ == "__main__":
    main()
