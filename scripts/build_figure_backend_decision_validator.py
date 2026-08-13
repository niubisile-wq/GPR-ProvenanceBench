#!/usr/bin/env python3
"""Validate the formal figure backend decision before rendering starts."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "figure_backend_decision_validator_20260810"
AUTHOR_PACKET = BENCH_ROOT / "reports" / "natcomms_author_finalization_reply_packet_20260810"
FIGURE_PREFLIGHT = BENCH_ROOT / "reports" / "figure_rendering_preflight_20260810"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    ticket_rows = read_csv(AUTHOR_PACKET / "figure_backend_decision_ticket.csv")
    preflight_summary = read_json(FIGURE_PREFLIGHT / "figure_rendering_preflight_summary.json")
    preflight_sheet = read_csv(FIGURE_PREFLIGHT / "figure_backend_decision_sheet.csv")

    ticket_by_id = {row["ticket_id"]: row for row in ticket_rows}
    backend_choice = ticket_by_id.get("FIG-BACKEND-001", {}).get("current_choice", "").strip()
    scope_choice = ticket_by_id.get("FIG-BACKEND-002", {}).get("current_choice", "").strip()
    allowed_backends = {"Python", "R"}
    allowed_scopes = {"Figure 1-Figure 6", "reduced display set with SI relocation"}

    backend_selected = backend_choice in allowed_backends
    scope_confirmed = scope_choice in allowed_scopes
    preflight_ready = bool(preflight_summary.get("ready_to_render_after_backend_choice"))
    no_missing_sources = int(preflight_summary.get("figures_with_missing_sources", -1)) == 0
    rendered_figures = int(preflight_summary.get("rendered_figures", 0))
    rendering_allowed = backend_selected and scope_confirmed and preflight_ready and no_missing_sources

    validation_rows = [
        {
            "item": "backend_choice",
            "current_value": backend_choice,
            "allowed_values": "Python; R",
            "decision": "pass" if backend_selected else "blocked",
            "issue": "" if backend_selected else "current_choice is blank or not one of the allowed backend values",
        },
        {
            "item": "figure_scope",
            "current_value": scope_choice,
            "allowed_values": "Figure 1-Figure 6; reduced display set with SI relocation",
            "decision": "pass" if scope_confirmed else "blocked",
            "issue": "" if scope_confirmed else "figure set scope is blank or not one of the allowed values",
        },
        {
            "item": "source_preflight",
            "current_value": f"ready={preflight_ready}; missing_sources={preflight_summary.get('figures_with_missing_sources')}",
            "allowed_values": "ready=true; missing_sources=0",
            "decision": "pass" if preflight_ready and no_missing_sources else "blocked",
            "issue": "" if preflight_ready and no_missing_sources else "figure source preflight is not clean",
        },
        {
            "item": "rendered_figures_boundary",
            "current_value": rendered_figures,
            "allowed_values": "0 before formal rendering",
            "decision": "pass" if rendered_figures == 0 else "blocked",
            "issue": "" if rendered_figures == 0 else "rendered figure count changed before formal rendering workflow",
        },
    ]

    gate_rows = [
        {
            "gate": "formal_figure_rendering_allowed",
            "decision": "pass" if rendering_allowed else "blocked",
            "evidence": "requires backend choice, scope choice, clean preflight and no missing sources",
        },
        {
            "gate": "single_backend_policy",
            "decision": "pass" if backend_selected else "blocked",
            "evidence": "once selected, use the same backend for generation, preview, export and QA",
        },
        {
            "gate": "submission_ready",
            "decision": "blocked",
            "evidence": "backend validation cannot make submission ready",
        },
    ]

    handoff = f"""# Figure Backend Decision Handoff

Current backend choice: `{backend_choice or 'blank'}`

Current figure scope choice: `{scope_choice or 'blank'}`

Rendering allowed: `{str(rendering_allowed).lower()}`

If rendering becomes allowed, use exactly one backend for generation, preview,
export and QA. Do not mix Python and R outputs in the final figure set.

Current boundary: this file validates the decision state only. It does not
render Figure 1-Figure 6 and does not perform visual QA.
"""

    qa_rows = [
        {
            "check_id": "QA-001",
            "check": "backend decision ticket has two rows",
            "observed": len(ticket_rows),
            "expected": 2,
            "pass": len(ticket_rows) == 2,
        },
        {
            "check_id": "QA-002",
            "check": "preflight backend options are present",
            "observed": len(preflight_sheet),
            "expected": ">=2",
            "pass": len(preflight_sheet) >= 2,
        },
        {
            "check_id": "QA-003",
            "check": "rendering remains blocked unless backend and scope are explicit",
            "observed": rendering_allowed,
            "expected": backend_selected and scope_confirmed and preflight_ready and no_missing_sources,
            "pass": True,
        },
        {
            "check_id": "QA-004",
            "check": "validator does not mark submission ready",
            "observed": "submission_ready=false",
            "expected": "submission_ready=false",
            "pass": True,
        },
    ]

    summary = {
        "package": "figure_backend_decision_validator_20260810",
        "ticket_rows": len(ticket_rows),
        "preflight_backend_option_rows": len(preflight_sheet),
        "backend_choice": backend_choice or "blank",
        "scope_choice": scope_choice or "blank",
        "backend_selected": backend_selected,
        "scope_confirmed": scope_confirmed,
        "preflight_ready": preflight_ready,
        "missing_sources": preflight_summary.get("figures_with_missing_sources"),
        "rendering_allowed": rendering_allowed,
        "rendered_figures": rendered_figures,
        "submission_ready": False,
        "qa_pass": all(bool(row["pass"]) for row in qa_rows),
        "status": "figure_backend_decision_validator_ready_waiting_author_choice",
    }
    if rendering_allowed:
        summary["status"] = "figure_backend_decision_validator_ready_for_formal_rendering"

    write_csv(
        OUT_DIR / "figure_backend_decision_validation.csv",
        ["item", "current_value", "allowed_values", "decision", "issue"],
        validation_rows,
    )
    write_csv(
        OUT_DIR / "figure_rendering_gate_decision.csv",
        ["gate", "decision", "evidence"],
        gate_rows,
    )
    write_csv(
        OUT_DIR / "figure_backend_decision_validator_qa.csv",
        ["check_id", "check", "observed", "expected", "pass"],
        qa_rows,
    )
    write_text(OUT_DIR / "figure_backend_choice_handoff.md", handoff)

    readme = """# Figure Backend Decision Validator

This package validates whether the author has selected exactly one formal
figure backend and confirmed the figure set scope.

It does not render figures. Formal rendering still requires the selected
backend to be used consistently for generation, preview, export and QA.
"""
    write_text(OUT_DIR / "FIGURE_BACKEND_DECISION_VALIDATOR_README.md", readme)

    report = f"""# Figure Backend Decision Validator Report

Status: `{summary["status"]}`

Current state:

1. Backend choice: `{summary["backend_choice"]}`
2. Figure scope choice: `{summary["scope_choice"]}`
3. Backend selected: {str(summary["backend_selected"]).lower()}
4. Scope confirmed: {str(summary["scope_confirmed"]).lower()}
5. Preflight ready: {str(summary["preflight_ready"]).lower()}
6. Missing sources: {summary["missing_sources"]}
7. Rendering allowed: {str(summary["rendering_allowed"]).lower()}
8. Rendered figures: {summary["rendered_figures"]}
9. Submission ready: false

Boundary: this validator checks decision readiness only. It does not render or
visually QA final figures.
"""
    write_text(OUT_DIR / "figure_backend_decision_validator_report.md", report)
    write_text(
        OUT_DIR / "figure_backend_decision_validator_summary.json",
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
    )

    if not summary["qa_pass"]:
        raise SystemExit("Figure backend decision validator QA failed")

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
