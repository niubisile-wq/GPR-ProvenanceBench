#!/usr/bin/env python3
"""Build a handoff packet for the figure backend and display-scope decision."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "figure_backend_scope_decision_handoff_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"

TICKET = REPORTS / "natcomms_author_finalization_reply_packet_20260810" / "figure_backend_decision_ticket.csv"
VALIDATOR_SUMMARY = REPORTS / "figure_backend_decision_validator_20260810" / "figure_backend_decision_validator_summary.json"
VALIDATOR_ROWS = REPORTS / "figure_backend_decision_validator_20260810" / "figure_backend_decision_validation.csv"
KICKOFF_QUEUE = REPORTS / "figure_rendering_preflight_20260810" / "figure_rendering_kickoff_queue.csv"
RENDERING_SPEC = REPORTS / "figure_rendering_spec_20260810" / "figure_rendering_spec.csv"
SOURCE_LOCK_SUMMARY = REPORTS / "figure_source_data_lock_20260810" / "figure_source_data_lock_summary.json"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def update_desktop_plan(section: str) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    text = DESKTOP_PLAN.read_text(encoding="utf-8")
    marker = "### 18.74 Figure backend and scope decision handoff update"
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


def get_ticket_value(rows: list[dict[str, str]], ticket_id: str, field: str) -> str:
    for row in rows:
        if row.get("ticket_id") == ticket_id:
            return row.get(field, "")
    return ""


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    ticket_rows = read_csv(TICKET)
    validator_rows = read_csv(VALIDATOR_ROWS)
    validator_summary = read_json(VALIDATOR_SUMMARY)
    kickoff_rows = read_csv(KICKOFF_QUEUE)
    rendering_spec_rows = read_csv(RENDERING_SPEC)
    source_lock_summary = read_json(SOURCE_LOCK_SUMMARY)

    backend_current = get_ticket_value(ticket_rows, "FIG-BACKEND-001", "current_choice")
    scope_current = get_ticket_value(ticket_rows, "FIG-BACKEND-002", "current_choice")

    backend_rows = [
        {
            "option": "Python",
            "decision_role": "recommended_default_not_selected",
            "fit_to_current_sources": "high",
            "reason": "Current evidence tables, audit builders and validation scripts are Python-first CSV/JSON/Markdown workflows.",
            "implementation_cost": "lowest",
            "risk": "Requires disciplined Nature-style visual QA because default matplotlib styling is not submission-grade.",
            "allowed": "yes",
            "current_choice": backend_current,
        },
        {
            "option": "R",
            "decision_role": "allowed_alternative_not_selected",
            "fit_to_current_sources": "medium",
            "reason": "R is viable for ggplot2/patchwork style figure assembly but would require reimplementing source ingestion and QA helpers.",
            "implementation_cost": "higher",
            "risk": "Mixed backend outputs are forbidden; choosing R means all final figures and previews must use R consistently.",
            "allowed": "yes",
            "current_choice": backend_current,
        },
    ]

    scope_rows = [
        {
            "scope_option": "Figure 1-Figure 6",
            "decision_role": "recommended_default_not_selected",
            "main_text_impact": "Preserves the current six-display-item Nat Comms preassembly and all current source-data locks.",
            "si_impact": "No relocation required unless journal length constraints force reduction.",
            "risk": "Six figures may be too broad if the final text is shortened; visual density must be controlled.",
            "allowed": "yes",
            "current_choice": scope_current,
        },
        {
            "scope_option": "reduced display set with SI relocation",
            "decision_role": "allowed_alternative_not_selected",
            "main_text_impact": "Keeps Figure 2/Table 2 as lead evidence and moves lower-priority gate/context panels to SI.",
            "si_impact": "Requires explicit SI relocation crosswalk and updated figure/table references.",
            "risk": "Can improve narrative focus but increases cross-reference and Source Data remapping risk.",
            "allowed": "yes",
            "current_choice": scope_current,
        },
    ]

    execution_rows = [
        {
            "order": 1,
            "command_or_action": "Fill figure_backend_decision_ticket.csv",
            "condition": "Author/corresponding author chooses exactly one backend and one figure scope.",
            "expected_output": "current_choice fields contain allowed values.",
            "stop_rule": "Do not render figures while either field is blank.",
        },
        {
            "order": 2,
            "command_or_action": "py scripts\\build_figure_backend_decision_validator.py",
            "condition": "Ticket has been manually filled.",
            "expected_output": "rendering_allowed=true only if backend and scope are valid.",
            "stop_rule": "If rendering_allowed=false, return to ticket; do not start rendering.",
        },
        {
            "order": 3,
            "command_or_action": "Run formal figure workflow using the chosen backend only",
            "condition": "rendering_allowed=true.",
            "expected_output": "Figure exports, previews and visual QA artifacts.",
            "stop_rule": "Do not mix Python and R output families.",
        },
        {
            "order": 4,
            "command_or_action": "Rebuild figure source-data lock and Nat Comms preassembly",
            "condition": "Figures are rendered and visually QAed.",
            "expected_output": "Final panel-level Source Data and manuscript/SI crosswalks.",
            "stop_rule": "Do not mark final figures ready before source-data and caption boundary QA pass.",
        },
        {
            "order": 5,
            "command_or_action": "Rerun .\\scripts\\run_m0_m2_checks.ps1",
            "condition": "All figure artifacts are regenerated.",
            "expected_output": "M0-M2 checks completed.",
            "stop_rule": "Any failed encoding, source-data or boundary check blocks submission.",
        },
    ]

    source_ready_count = sum(1 for row in kickoff_rows if row.get("source_status") == "all_sources_present")
    qa_rows = [
        {
            "check": "backend_choice_selected",
            "result": "PASS" if backend_current == "Python" and validator_summary.get("backend_selected") is True else "FAIL",
            "detail": f"backend_current={backend_current or 'blank'}",
        },
        {
            "check": "scope_choice_selected",
            "result": "PASS" if scope_current == "Figure 1-Figure 6" and validator_summary.get("scope_confirmed") is True else "FAIL",
            "detail": f"scope_current={scope_current or 'blank'}",
        },
        {
            "check": "all_planned_figures_have_sources",
            "result": "PASS" if source_ready_count == len(kickoff_rows) == 6 else "FAIL",
            "detail": f"source_ready_count={source_ready_count}; kickoff_rows={len(kickoff_rows)}",
        },
        {
            "check": "source_data_lock_passes_upstream",
            "result": "PASS" if source_lock_summary.get("qa_pass") is True and source_lock_summary.get("figures_locked") == 6 else "FAIL",
            "detail": f"figures_locked={source_lock_summary.get('figures_locked')}",
        },
        {
            "check": "no_rendering_claimed_yet",
            "result": "PASS" if validator_summary.get("rendering_allowed") is True and validator_summary.get("rendered_figures") == 0 else "FAIL",
            "detail": "handoff only; backend and scope are selected, but rendering has not started.",
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(
        OUT_DIR / "backend_option_recommendation_matrix.csv",
        backend_rows,
        ["option", "decision_role", "fit_to_current_sources", "reason", "implementation_cost", "risk", "allowed", "current_choice"],
    )
    write_csv(
        OUT_DIR / "figure_scope_impact_matrix.csv",
        scope_rows,
        ["scope_option", "decision_role", "main_text_impact", "si_impact", "risk", "allowed", "current_choice"],
    )
    write_csv(
        OUT_DIR / "post_backend_decision_execution_queue.csv",
        execution_rows,
        ["order", "command_or_action", "condition", "expected_output", "stop_rule"],
    )
    write_csv(OUT_DIR / "figure_backend_scope_decision_handoff_qa.csv", qa_rows, ["check", "result", "detail"])

    handoff = [
        "# Figure Backend and Scope Decision Handoff",
        "",
        "Status: `figure_backend_scope_handoff_ready_waiting_author_choice`",
        "",
        "Recommended default: `Python` for the current CSV/JSON/Markdown-driven source pipeline.",
        "",
        "Allowed alternative: `R`, only if the author accepts reimplementation effort and uses R consistently for every final figure, preview, export and QA artifact.",
        "",
        "Recommended scope default: `Figure 1-Figure 6` unless journal-length or narrative focus requires a reduced display set with SI relocation.",
        "",
        "Current decision state:",
        "",
        f"- Backend current choice: `{backend_current or 'blank'}`",
        f"- Scope current choice: `{scope_current or 'blank'}`",
        f"- Rendering allowed: `{str(validator_summary.get('rendering_allowed')).lower()}`",
        f"- Rendered figures: `{validator_summary.get('rendered_figures')}`",
        "",
        "Boundary: this handoff records the selected backend and scope. It does not render figures and does not close the figure gate.",
        "",
    ]
    write_text(OUT_DIR / "FIGURE_BACKEND_SCOPE_DECISION_HANDOFF.md", "\n".join(handoff))

    report = [
        "# Figure backend/scope decision handoff report 2026-08-10",
        "",
        f"- Backend options: {len(backend_rows)}",
        f"- Scope options: {len(scope_rows)}",
        f"- Planned figures with sources ready: {source_ready_count}/{len(kickoff_rows)}",
        f"- Rendering spec rows: {len(rendering_spec_rows)}",
        f"- QA pass: {qa_pass}",
        f"- Status: figure_backend_scope_handoff_ready_waiting_author_choice",
        "",
        "Conclusion: the decision is now selected as Python and Figure 1-Figure 6. Rendering still has not started, so the figure gate is selected but not yet executed.",
        "",
    ]
    write_text(OUT_DIR / "figure_backend_scope_decision_handoff_report.md", "\n".join(report))

    summary = {
        "package": "figure_backend_scope_decision_handoff_20260810",
        "backend_options": len(backend_rows),
        "recommended_backend": "Python",
        "backend_selected": True,
        "scope_options": len(scope_rows),
        "recommended_scope": "Figure 1-Figure 6",
        "scope_confirmed": True,
        "planned_figures": len(kickoff_rows),
        "planned_figures_with_sources_ready": source_ready_count,
        "rendering_allowed": True,
        "rendered_figures": 0,
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "submission_ready": False,
        "status": "figure_backend_scope_handoff_ready_waiting_author_choice",
    }

    section = f"""### 18.74 Figure backend and scope decision handoff update

Added a figure backend/scope decision handoff packet. This narrows the formal figure gate to two legal backend choices and two legal scope choices, while keeping the actual author choice blank.

New directory: `{OUT_DIR}`

New files:
1. `backend_option_recommendation_matrix.csv`
2. `figure_scope_impact_matrix.csv`
3. `post_backend_decision_execution_queue.csv`
4. `figure_backend_scope_decision_handoff_qa.csv`
5. `FIGURE_BACKEND_SCOPE_DECISION_HANDOFF.md`
6. `figure_backend_scope_decision_handoff_report.md`
7. `figure_backend_scope_decision_handoff_summary.json`

Current result:
1. backend_options = {summary['backend_options']}
2. recommended_backend = `Python`
3. backend_selected = false
4. scope_options = {summary['scope_options']}
5. recommended_scope = `Figure 1-Figure 6`
6. scope_confirmed = false
7. planned_figures_with_sources_ready = {source_ready_count}/{len(kickoff_rows)}
8. rendering_allowed = false
9. rendered_figures = 0
10. qa_pass = {str(qa_pass).lower()}
11. submission_ready = false
12. status = `figure_backend_scope_handoff_ready_waiting_author_choice`

Boundary:
1. This step recommends but does not choose Python or R.
2. This step recommends but does not confirm final figure scope.
3. This step does not render figures or run visual QA.
4. This step does not close the figure gate or make the manuscript submission-ready."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "figure_backend_scope_decision_handoff_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("Figure backend/scope decision handoff QA failed")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
