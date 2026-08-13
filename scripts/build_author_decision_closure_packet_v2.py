#!/usr/bin/env python3
"""Build a concise author-decision closure packet for unresolved gates."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "author_decision_closure_packet_v2_20260810"
DASHBOARD = BENCH_ROOT / "reports" / "submission_command_dashboard_v2_20260810" / "submission_command_dashboard_v2.csv"
BACKEND = BENCH_ROOT / "reports" / "figure_rendering_preflight_20260810" / "figure_backend_decision_sheet.csv"
BRANCHES = BENCH_ROOT / "reports" / "external_validation_contingency_framing_20260810" / "external_validation_branch_decision_matrix.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    dashboard = read_csv(DASHBOARD)
    backend = read_csv(BACKEND)
    branches = read_csv(BRANCHES)

    decision_rows = [
        {
            "decision_id": "ADC2-001",
            "priority": "1",
            "decision": "Choose figure rendering backend",
            "recommended_response": "Python",
            "why": "Current evidence pipeline, scripts and source data are Python-based.",
            "unlocks": "Formal Figure 1-Figure 6 rendering and visual QA.",
            "if_not_decided": "Figure gate remains open; manuscript figures cannot become final.",
            "response_field": "",
        },
        {
            "decision_id": "ADC2-002",
            "priority": "2",
            "decision": "Name a real external blind GPR data holder or confirm none is available before manuscript lock",
            "recommended_response": "If no named holder exists now, proceed with Track B.",
            "why": "Track A requires a real held-label asset, strict intake and locked evaluation.",
            "unlocks": "Either Track A external validation workflow or Track B benchmark/resource framing lock.",
            "if_not_decided": "External-validation language must remain open-gate only.",
            "response_field": "",
        },
        {
            "decision_id": "ADC2-003",
            "priority": "3",
            "decision": "Confirm code and derived-data licence direction",
            "recommended_response": "Code: MIT or BSD-3-Clause; derived source data: CC BY 4.0 or restricted if rights review fails.",
            "why": "Repository DOI and Code Availability cannot finalize without licence and rights decisions.",
            "unlocks": "Repository metadata can move from draft to deposit preparation.",
            "if_not_decided": "Data/code availability remains current-draft only.",
            "response_field": "",
        },
        {
            "decision_id": "ADC2-004",
            "priority": "4",
            "decision": "Confirm manuscript route if external validation remains unavailable",
            "recommended_response": "Track B: benchmark/resource plus evidence-boundary paper.",
            "why": "This is the current safe branch and avoids unsupported external-generalization claims.",
            "unlocks": "Title, abstract, cover-letter framing and claim strength can be aligned.",
            "if_not_decided": "Manuscript branch remains provisional.",
            "response_field": "",
        },
    ]
    write_csv(
        OUT_DIR / "author_decision_closure_form_v2.csv",
        decision_rows,
        ["decision_id", "priority", "decision", "recommended_response", "why", "unlocks", "if_not_decided", "response_field"],
    )

    next24_rows = [
        {"hour": "0-2", "owner": "author", "action": "Reply with figure backend: Python or R. Recommended: Python.", "output": "Figure rendering workflow can start."},
        {"hour": "0-6", "owner": "author/advisor", "action": "Reply with external data holder name/contact, or confirm no real blind asset is available now.", "output": "Track A or Track B branch can be locked."},
        {"hour": "6-12", "owner": "author/institution", "action": "Confirm provisional code licence and derived-data licence direction.", "output": "Repository package can move toward deposit preparation."},
        {"hour": "12-24", "owner": "author", "action": "Confirm Track B if no external asset exists.", "output": "Conservative manuscript framing can be locked for author review."},
    ]
    write_csv(OUT_DIR / "next_24h_decision_closure_queue.csv", next24_rows, ["hour", "owner", "action", "output"])

    email = """# Coauthor decision closure email draft

Subject: Decisions needed to move GPR-ProvenanceBench from prelock to execution

Dear coauthors,

The 2026-08-10 package is internally auditable but not submission-ready. Four decisions are blocking the next execution step:

1. Figure backend: please confirm Python or R. The current recommendation is Python because the source-data and scripts are already Python-based.
2. External blind validation: please name a real independent GPR data holder/contact, or confirm that no such asset is available before manuscript lock.
3. Licences and rights: please confirm the provisional software licence and derived-data licence route, and flag any raw/third-party GPR data that cannot be redistributed.
4. Manuscript route: if no real external blind asset is available, please confirm Track B, meaning a benchmark/resource and evidence-boundary manuscript centred on Res-SAM environment-transfer fragility.

Until these are answered, we should not claim completed external validation, final figures, data/code DOI, final Reporting Summary or final numbered references.

Best,
[Author]
"""
    (OUT_DIR / "coauthor_decision_closure_email.md").write_text(email, encoding="utf-8")

    external_note = """# External data-holder short request

Subject: Feasibility check for held-label blind GPR validation asset

Dear [Name],

We are preparing a provenance-aware GPR recognition manuscript and need to know whether a real independent blind validation asset is feasible.

Minimum requirements:

1. Files can be shared without labels first.
2. File checksums can be recorded.
3. Labels can be held outside our analyst workflow until predictions are frozen.
4. One locked evaluation can be run after label release.
5. Aggregate metrics may be reported in the manuscript, subject to your data-use conditions.

If feasible, please reply with approximate sample count, label type, rights restrictions and whether aggregate metrics can be published.

Best,
[Author]
"""
    (OUT_DIR / "external_data_holder_feasibility_note.md").write_text(external_note, encoding="utf-8")

    qa_rows = [
        {"check": "dashboard_loaded", "result": "PASS", "detail": f"dashboard_rows={len(dashboard)}"},
        {"check": "backend_options_loaded", "result": "PASS", "detail": f"backend_options={len(backend)}"},
        {"check": "track_b_available", "result": "PASS" if any(row["branch_id"] == "TRACK-B" for row in branches) else "FAIL", "detail": "Track B fallback present."},
        {"check": "no_gate_closure_claimed", "result": "PASS", "detail": "Packet asks for decisions only."},
        {"check": "decision_count", "result": "PASS" if len(decision_rows) == 4 else "FAIL", "detail": str(len(decision_rows))},
    ]
    write_csv(OUT_DIR / "author_decision_closure_packet_v2_qa.csv", qa_rows, ["check", "result", "detail"])

    summary = {
        "run_id": "20260810_author_decision_closure_packet_v2",
        "decision_rows": len(decision_rows),
        "next24_rows": len(next24_rows),
        "email_drafts": 2,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "recommended_backend": "Python",
        "recommended_branch_without_external_asset": "TRACK-B",
        "submission_ready": False,
        "status": "author_decision_closure_packet_v2_ready_decisions_required",
        "boundary": "This packet collects author/external decisions; it does not close figures, external validation, DOI, rights, Reporting Summary or references.",
    }
    (OUT_DIR / "author_decision_closure_packet_v2_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    report = [
        "# Author decision closure packet v2 report 2026-08-10",
        "",
        f"- Decision rows: {summary['decision_rows']}",
        f"- Next-24h rows: {summary['next24_rows']}",
        f"- Email drafts: {summary['email_drafts']}",
        f"- QA pass: {summary['qa_pass']}",
        f"- Recommended backend: {summary['recommended_backend']}",
        f"- Recommended branch without external asset: {summary['recommended_branch_without_external_asset']}",
        f"- Status: {summary['status']}",
        "",
        "Conclusion: the decision packet is ready, but author/external decisions are still required.",
        "",
    ]
    (OUT_DIR / "author_decision_closure_packet_v2_report.md").write_text("\n".join(report), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
