#!/usr/bin/env python3
"""Build a completion handoff for rights and licence decisions."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "rights_licence_completion_handoff_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"

RELEASE_AUDIT = REPORTS / "release_readiness_audit_20260810" / "licence_and_rights_checklist.csv"
RELEASE_SUMMARY = REPORTS / "release_readiness_audit_20260810" / "release_readiness_summary.json"
REPOSITORY_RIGHTS = REPORTS / "repository_predeposit_handoff_20260810" / "repository_rights_licence_action_register.csv"
REPOSITORY_SUMMARY = REPORTS / "repository_predeposit_handoff_20260810" / "repository_predeposit_handoff_summary.json"
AVAILABILITY_GATES = REPORTS / "availability_statement_prelock_20260810" / "availability_statement_gate_requirements.csv"
AVAILABILITY_SUMMARY = REPORTS / "availability_statement_prelock_20260810" / "availability_statement_prelock_summary.json"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def update_desktop_plan(section: str) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    text = DESKTOP_PLAN.read_text(encoding="utf-8")
    marker = "### 18.78 Rights and licence completion handoff update"
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


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    release_rows = read_csv(RELEASE_AUDIT)
    release_summary = read_json(RELEASE_SUMMARY)
    repository_rows = read_csv(REPOSITORY_RIGHTS)
    repository_summary = read_json(REPOSITORY_SUMMARY)
    availability_rows = read_csv(AVAILABILITY_GATES)
    availability_summary = read_json(AVAILABILITY_SUMMARY)

    repository_by_component = {row["component"]: row for row in repository_rows}
    decision_rows = [
        {
            "component": "Code/scripts",
            "current_status": repository_by_component["Code/scripts"]["current_status"],
            "candidate_decision": repository_by_component["Code/scripts"]["candidate_licence"],
            "required_evidence_to_close": "Corresponding author confirms software licence, public repository URL, release tag and archive DOI.",
            "release_consequence_if_open": "Code availability remains local-only and public release is blocked.",
            "current_decision": "open",
        },
        {
            "component": "Derived source-data CSV/JSON/Markdown",
            "current_status": repository_by_component["Derived source-data CSV/JSON/Markdown"]["current_status"],
            "candidate_decision": repository_by_component["Derived source-data CSV/JSON/Markdown"]["candidate_licence"],
            "required_evidence_to_close": "Rights lead confirms derived metadata can be redistributed and no third-party raw data or label hints are exposed.",
            "release_consequence_if_open": "Derived source-data deposit remains draft/predeposit only.",
            "current_decision": "open",
        },
        {
            "component": "Third-party raw GPR data",
            "current_status": repository_by_component["Third-party raw GPR data"]["current_status"],
            "candidate_decision": "exclude raw files by default; cite providers or access routes",
            "required_evidence_to_close": "Written provider permission is required for any redistribution; otherwise exclusion remains final.",
            "release_consequence_if_open": "Raw files stay excluded; Data Availability uses restricted/provider-controlled wording.",
            "current_decision": "exclude_by_default_not_public_release",
        },
        {
            "component": "Rendered figures and panel Source Data",
            "current_status": repository_by_component["Rendered figures"]["current_status"],
            "candidate_decision": repository_by_component["Rendered figures"]["candidate_licence"],
            "required_evidence_to_close": "Final rendered figures, visual QA and panel-level Source Data mapping exist.",
            "release_consequence_if_open": "Final figure Source Data and public release remain blocked.",
            "current_decision": "open",
        },
    ]

    availability_dependency_rows = [
        {
            "gate": row["gate"],
            "required_evidence": row["required_evidence"],
            "current_state": row["current_state"],
            "rights_licence_dependency": "yes" if row["gate"] in {"third_party_rights", "data_repository_identifier", "code_repository_identifier"} else "partial",
            "completion_consequence": "Availability wording remains draft while this gate is open.",
        }
        for row in availability_rows
    ]

    release_action_rows = [
        {
            "release_item": row["item"],
            "current_status": row["current_status"],
            "required_action": row["required_action"],
            "release_blocker": row["release_blocker"],
            "handoff_status": "open",
        }
        for row in release_rows
    ]

    no_go_rows = [
        {
            "no_go_id": "RIGHTS-NOGO-001",
            "shortcut": "Publish raw third-party GPR files without explicit provider permission",
            "reason": "Raw-file redistribution rights are separate from using aggregate derived metrics.",
            "decision": "forbidden",
        },
        {
            "no_go_id": "RIGHTS-NOGO-002",
            "shortcut": "Treat candidate licence text as selected licence",
            "reason": "MIT/BSD and CC BY/CC0 are candidates only until author and rights confirmation.",
            "decision": "forbidden",
        },
        {
            "no_go_id": "RIGHTS-NOGO-003",
            "shortcut": "Claim public data/code availability before DOI/release tag exists",
            "reason": "Repository identifiers and software/data releases do not exist.",
            "decision": "forbidden",
        },
        {
            "no_go_id": "RIGHTS-NOGO-004",
            "shortcut": "Release final figure Source Data before figures are rendered and QAed",
            "reason": "Panel-level Source Data depends on final figure scope, rendering and visual QA.",
            "decision": "forbidden",
        },
    ]

    command_rows = [
        {
            "order": 1,
            "command_or_action": "Author confirms software licence",
            "condition": "public code repository scope is known",
            "expected_evidence": "licence file and repository release tag",
            "stop_rule": "Do not claim code DOI or public code availability before release exists.",
        },
        {
            "order": 2,
            "command_or_action": "Rights lead reviews derived source-data files",
            "condition": "final source-data scope is locked",
            "expected_evidence": "decision allowing derived CSV/JSON/Markdown release or excluding sensitive rows",
            "stop_rule": "Do not publish derived artifacts that expose raw-data paths, label hints or third-party restricted content.",
        },
        {
            "order": 3,
            "command_or_action": "Raw third-party data exclusion or permission is finalized",
            "condition": "provider licences are checked",
            "expected_evidence": "provider permission or restricted-access wording",
            "stop_rule": "Default is exclusion without written permission.",
        },
        {
            "order": 4,
            "command_or_action": "Final figures and panel Source Data are rendered and QAed",
            "condition": "backend/scope selected and figure workflow completed",
            "expected_evidence": "figure exports, visual QA and panel-level Source Data manifest",
            "stop_rule": "Do not finalize figure/source-data rights before final figure artifacts exist.",
        },
        {
            "order": 5,
            "command_or_action": "Repository DOI/accession and code DOI are created",
            "condition": "licence and rights decisions are recorded",
            "expected_evidence": "repository landing pages and archive identifiers",
            "stop_rule": "Do not mark public_release_ready before identifiers resolve.",
        },
    ]

    qa_rows = [
        {
            "check": "release_readiness_remains_false",
            "result": "PASS" if release_summary.get("release_ready") is False else "FAIL",
            "detail": f"release_ready={release_summary.get('release_ready')}",
        },
        {
            "check": "repository_handoff_not_public",
            "result": "PASS" if repository_summary.get("public_release_ready") is False and repository_summary.get("repository_doi_created") is False else "FAIL",
            "detail": f"public_release_ready={repository_summary.get('public_release_ready')}; repository_doi_created={repository_summary.get('repository_doi_created')}",
        },
        {
            "check": "availability_gates_open",
            "result": "PASS" if all(row["current_state"] == "open" for row in availability_rows) else "FAIL",
            "detail": f"availability_rows={len(availability_rows)}",
        },
        {
            "check": "raw_third_party_default_exclusion_preserved",
            "result": "PASS" if any(row["component"] == "Third-party raw GPR data" and "exclude" in row["current_decision"] for row in decision_rows) else "FAIL",
            "detail": "Raw third-party files must not enter public release without permission.",
        },
        {
            "check": "final_rights_not_claimed",
            "result": "PASS",
            "detail": "This handoff queues decisions only; no licence, DOI, rights clearance or public release is created.",
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(
        OUT_DIR / "rights_licence_decision_matrix.csv",
        decision_rows,
        ["component", "current_status", "candidate_decision", "required_evidence_to_close", "release_consequence_if_open", "current_decision"],
    )
    write_csv(
        OUT_DIR / "rights_availability_dependency_map.csv",
        availability_dependency_rows,
        ["gate", "required_evidence", "current_state", "rights_licence_dependency", "completion_consequence"],
    )
    write_csv(
        OUT_DIR / "rights_release_action_queue.csv",
        release_action_rows,
        ["release_item", "current_status", "required_action", "release_blocker", "handoff_status"],
    )
    write_csv(OUT_DIR / "rights_no_go_shortcuts.csv", no_go_rows, ["no_go_id", "shortcut", "reason", "decision"])
    write_csv(OUT_DIR / "rights_completion_command_queue.csv", command_rows, ["order", "command_or_action", "condition", "expected_evidence", "stop_rule"])
    write_csv(OUT_DIR / "rights_licence_completion_handoff_qa.csv", qa_rows, ["check", "result", "detail"])

    readme = """# Rights and Licence Completion Handoff 2026-08-10

This package consolidates release readiness, repository predeposit and availability prelock evidence into a rights/licence completion handoff.

Boundary: this package does not select a licence, clear third-party rights, create a DOI, create a public release or make the manuscript submission-ready.
"""
    write_text(OUT_DIR / "RIGHTS_LICENCE_COMPLETION_HANDOFF_README.md", readme)

    report = [
        "# Rights and licence completion handoff report 2026-08-10",
        "",
        "Status: `rights_licence_completion_handoff_ready_not_cleared`",
        "",
        f"- Decision rows: {len(decision_rows)}",
        f"- Availability dependency rows: {len(availability_dependency_rows)}",
        f"- Release action rows: {len(release_action_rows)}",
        f"- No-go shortcuts: {len(no_go_rows)}",
        f"- Completion command rows: {len(command_rows)}",
        f"- QA pass: {qa_pass}",
        "",
        "Conclusion: rights/licence decisions are now queued, but public release remains blocked by author licence choice, derived-data rights review, repository identifiers and final figure Source Data.",
        "",
    ]
    write_text(OUT_DIR / "rights_licence_completion_handoff_report.md", "\n".join(report))

    summary = {
        "package": "rights_licence_completion_handoff_20260810",
        "decision_rows": len(decision_rows),
        "availability_dependency_rows": len(availability_dependency_rows),
        "release_action_rows": len(release_action_rows),
        "no_go_shortcuts": len(no_go_rows),
        "completion_command_rows": len(command_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "licence_selected": False,
        "third_party_rights_cleared": False,
        "raw_third_party_data_public_release_allowed": False,
        "repository_doi_created": False,
        "public_release_ready": False,
        "submission_ready": False,
        "status": "rights_licence_completion_handoff_ready_not_cleared",
    }

    section = f"""### 18.78 Rights and licence completion handoff update

Added a rights/licence completion handoff. This consolidates release readiness, repository predeposit and availability prelock evidence into a single decision queue.

New directory: `{OUT_DIR}`

New files:
1. `rights_licence_decision_matrix.csv`
2. `rights_availability_dependency_map.csv`
3. `rights_release_action_queue.csv`
4. `rights_no_go_shortcuts.csv`
5. `rights_completion_command_queue.csv`
6. `rights_licence_completion_handoff_qa.csv`
7. `RIGHTS_LICENCE_COMPLETION_HANDOFF_README.md`
8. `rights_licence_completion_handoff_report.md`
9. `rights_licence_completion_handoff_summary.json`

Current result:
1. decision_rows = {summary['decision_rows']}
2. availability_dependency_rows = {summary['availability_dependency_rows']}
3. release_action_rows = {summary['release_action_rows']}
4. no_go_shortcuts = {summary['no_go_shortcuts']}
5. completion_command_rows = {summary['completion_command_rows']}
6. qa_pass = {str(qa_pass).lower()}
7. licence_selected = false
8. third_party_rights_cleared = false
9. raw_third_party_data_public_release_allowed = false
10. repository_doi_created = false
11. public_release_ready = false
12. submission_ready = false
13. status = `rights_licence_completion_handoff_ready_not_cleared`

Boundary:
1. This step does not select a licence.
2. This step does not clear third-party rights.
3. This step does not create DOI records.
4. This step does not create a public release.
5. This step does not make the manuscript submission-ready."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "rights_licence_completion_handoff_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("Rights/licence completion handoff QA failed")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
