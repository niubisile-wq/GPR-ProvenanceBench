#!/usr/bin/env python3
"""Build a guarded preflight for FMR-005 repository/rights/DOI writeback."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "fmr005_repository_rights_doi_writeback_preflight_20260810"
FMR_DIR = BENCH_ROOT / "reports" / "final_manual_receipt_intake_package_20260810"
REPOSITORY_DIR = BENCH_ROOT / "reports" / "repository_predeposit_handoff_20260810"
RIGHTS_DIR = BENCH_ROOT / "reports" / "rights_licence_completion_handoff_20260810"
AVAILABILITY_DIR = BENCH_ROOT / "reports" / "availability_repository_finalization_validator_20260810"
METADATA_DIR = BENCH_ROOT / "reports" / "repository_metadata_package_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"


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
    marker = "### 19.68 FMR-005 repository rights DOI writeback preflight update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- Added `reports/fmr005_repository_rights_doi_writeback_preflight_20260810/` to guard future FMR-005 writeback from repository, rights, licence and DOI decisions.
- Current `repository_record_created={str(summary["repository_record_created"]).lower()}`, `repository_doi_created={str(summary["repository_doi_created"]).lower()}`, `code_doi_created={str(summary["code_doi_created"]).lower()}`, `licence_selected={str(summary["licence_selected"]).lower()}`.
- Current `third_party_rights_cleared={str(summary["third_party_rights_cleared"]).lower()}`, `final_availability_ready={str(summary["final_availability_ready"]).lower()}`, `fmr005_writeback_allowed={str(summary["fmr005_writeback_allowed"]).lower()}`.
- Boundary: FMR-005 cannot move from `FILL_AFTER_RIGHTS_DOI/missing` until repository/code identifiers, licences, third-party rights and final availability wording are complete. This preflight does not create a DOI, change licences, upload files, write the FMR intake template or submit.
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

    fmr_rows = read_csv(FMR_DIR / "final_manual_receipt_intake_template.csv")
    metadata_rows = read_csv(REPOSITORY_DIR / "repository_platform_metadata_prefill.csv")
    rights_rows = read_csv(RIGHTS_DIR / "rights_licence_decision_matrix.csv")
    final_gate_rows = read_csv(AVAILABILITY_DIR / "availability_repository_final_gate_matrix.csv")
    zenodo_metadata = read_json(METADATA_DIR / "zenodo_metadata_draft.json")
    repository_summary = read_json(REPOSITORY_DIR / "repository_predeposit_handoff_summary.json")
    rights_summary = read_json(RIGHTS_DIR / "rights_licence_completion_handoff_summary.json")
    availability_summary = read_json(AVAILABILITY_DIR / "availability_repository_finalization_validator_summary.json")

    fmr005_rows = [row for row in fmr_rows if row.get("receipt_id") == "FMR-005"]
    blocked_metadata_fields = int(repository_summary.get("blocked_metadata_fields", 0) or 0)
    upload_queue_files = int(repository_summary.get("upload_queue_files", 0) or 0)
    release_blocker_rows = int(availability_summary.get("release_blocker_rows", 0) or 0)
    open_availability_gates = int(availability_summary.get("open_availability_gates", 0) or 0)
    repository_record_created = repository_summary.get("repository_record_created") is True
    repository_doi_created = availability_summary.get("repository_doi_created") is True
    code_doi_created = availability_summary.get("code_doi_created") is True
    licence_selected = rights_summary.get("licence_selected") is True
    third_party_rights_cleared = rights_summary.get("third_party_rights_cleared") is True
    public_release_ready = availability_summary.get("public_release_ready") is True
    final_availability_ready = availability_summary.get("final_availability_ready") is True
    metadata_license = str(zenodo_metadata.get("license", "")).strip()
    metadata_has_tbd = any("TBD" in str(value) for value in zenodo_metadata.values())

    fmr005_writeback_allowed = (
        len(fmr005_rows) == 1
        and repository_record_created
        and repository_doi_created
        and code_doi_created
        and licence_selected
        and third_party_rights_cleared
        and public_release_ready
        and final_availability_ready
        and blocked_metadata_fields == 0
        and release_blocker_rows == 0
        and open_availability_gates == 0
        and not metadata_has_tbd
    )

    metadata_status_rows = []
    for row in metadata_rows:
        blocked = row.get("deposit_status") == "blocked"
        metadata_status_rows.append(
            {
                "platform_field": row.get("platform_field", ""),
                "deposit_status": row.get("deposit_status", ""),
                "prefill_value": row.get("prefill_value", ""),
                "blocking_note": row.get("blocking_note", ""),
                "blocks_fmr005_now": "yes" if blocked else "no",
            }
        )

    rights_status_rows = []
    for row in rights_rows:
        unresolved = row.get("current_decision", "").strip() in {"open", ""}
        rights_status_rows.append(
            {
                "component": row.get("component", ""),
                "current_status": row.get("current_status", ""),
                "current_decision": row.get("current_decision", ""),
                "candidate_decision": row.get("candidate_decision", ""),
                "required_evidence_to_close": row.get("required_evidence_to_close", ""),
                "blocks_fmr005_now": "yes" if unresolved else "no",
            }
        )

    candidate_rows = []
    if fmr005_writeback_allowed:
        fmr005 = fmr005_rows[0]
        candidate_rows.append(
            {
                "receipt_id": "FMR-005",
                "target_or_route": fmr005.get("target_or_route", ""),
                "current_status_after_writeback": "complete",
                "value_to_fill_after_manual_action": "Repository/data DOI, code DOI, licence, rights clearance and final availability wording complete.",
                "first_validator": fmr005.get("first_validator", ""),
                "writeback_allowed": "yes",
            }
        )

    guard_rows = [
        {
            "guard": "single_FMR_005_row_present",
            "current": len(fmr005_rows),
            "required": 1,
            "passes_now": "yes" if len(fmr005_rows) == 1 else "no",
        },
        {
            "guard": "repository_record_and_data_doi_created",
            "current": f"repository_record_created={repository_record_created}; repository_doi_created={repository_doi_created}",
            "required": "both true",
            "passes_now": "yes" if repository_record_created and repository_doi_created else "no",
        },
        {
            "guard": "code_doi_created",
            "current": code_doi_created,
            "required": "true",
            "passes_now": "yes" if code_doi_created else "no",
        },
        {
            "guard": "licence_and_third_party_rights_cleared",
            "current": f"licence_selected={licence_selected}; third_party_rights_cleared={third_party_rights_cleared}; metadata_license={metadata_license}",
            "required": "licence_selected=true; third_party_rights_cleared=true; no TBD metadata",
            "passes_now": "yes" if licence_selected and third_party_rights_cleared and not metadata_has_tbd else "no",
        },
        {
            "guard": "availability_finalization_ready",
            "current": f"final_availability_ready={final_availability_ready}; public_release_ready={public_release_ready}; open_availability_gates={open_availability_gates}",
            "required": "final_availability_ready=true; public_release_ready=true; open_availability_gates=0",
            "passes_now": "yes" if final_availability_ready and public_release_ready and open_availability_gates == 0 else "no",
        },
        {
            "guard": "no_metadata_or_release_blockers",
            "current": f"blocked_metadata_fields={blocked_metadata_fields}; release_blocker_rows={release_blocker_rows}; upload_queue_files={upload_queue_files}",
            "required": "blocked_metadata_fields=0; release_blocker_rows=0",
            "passes_now": "yes" if blocked_metadata_fields == 0 and release_blocker_rows == 0 else "no",
        },
    ]

    blocker_rows = []
    if not repository_record_created or not repository_doi_created or not code_doi_created:
        blocker_rows.append(
            {
                "blocker": "repository/code identifiers missing",
                "evidence": f"repository_record_created={repository_record_created}; repository_doi_created={repository_doi_created}; code_doi_created={code_doi_created}",
                "blocks": "FMR-005 writeback candidate and availability statement finalization",
            }
        )
    if not licence_selected or not third_party_rights_cleared or metadata_has_tbd:
        blocker_rows.append(
            {
                "blocker": "licence or third-party rights not complete",
                "evidence": f"licence_selected={licence_selected}; third_party_rights_cleared={third_party_rights_cleared}; metadata_has_tbd={metadata_has_tbd}",
                "blocks": "FMR-005 writeback candidate and public release",
            }
        )
    if not final_availability_ready or open_availability_gates:
        blocker_rows.append(
            {
                "blocker": "final availability not ready",
                "evidence": f"final_availability_ready={final_availability_ready}; open_availability_gates={open_availability_gates}",
                "blocks": "FMR-005 writeback candidate and portal file preflight",
            }
        )
    if blocked_metadata_fields or release_blocker_rows:
        blocker_rows.append(
            {
                "blocker": "metadata/release blockers remain",
                "evidence": f"blocked_metadata_fields={blocked_metadata_fields}; release_blocker_rows={release_blocker_rows}",
                "blocks": "FMR-005 writeback candidate",
            }
        )

    qa_rows = [
        {
            "check": "FMR-005 row imported",
            "result": "PASS" if len(fmr005_rows) == 1 else "FAIL",
            "detail": f"fmr005_rows={len(fmr005_rows)}",
        },
        {
            "check": "repository metadata rows imported",
            "result": "PASS" if len(metadata_rows) == int(repository_summary.get("platform_metadata_fields", 0) or 0) else "FAIL",
            "detail": f"metadata_rows={len(metadata_rows)}; expected={repository_summary.get('platform_metadata_fields')}",
        },
        {
            "check": "TBD metadata does not unlock writeback",
            "result": "PASS" if not metadata_has_tbd or not fmr005_writeback_allowed else "FAIL",
            "detail": f"metadata_has_tbd={metadata_has_tbd}; fmr005_writeback_allowed={fmr005_writeback_allowed}",
        },
        {
            "check": "candidate generation follows repository-rights gates",
            "result": "PASS" if len(candidate_rows) == (1 if fmr005_writeback_allowed else 0) else "FAIL",
            "detail": f"candidate_rows={len(candidate_rows)}; fmr005_writeback_allowed={fmr005_writeback_allowed}",
        },
        {
            "check": "submission remains false",
            "result": "PASS",
            "detail": "guarded_recheck_allowed=false; portal_upload_allowed=false; submission_ready=false",
        },
    ]

    summary = {
        "package": "fmr005_repository_rights_doi_writeback_preflight_20260810",
        "fmr005_rows": len(fmr005_rows),
        "metadata_rows": len(metadata_rows),
        "rights_rows": len(rights_rows),
        "final_gate_rows": len(final_gate_rows),
        "blocked_metadata_fields": blocked_metadata_fields,
        "release_blocker_rows": release_blocker_rows,
        "open_availability_gates": open_availability_gates,
        "repository_record_created": repository_record_created,
        "repository_doi_created": repository_doi_created,
        "code_doi_created": code_doi_created,
        "licence_selected": licence_selected,
        "third_party_rights_cleared": third_party_rights_cleared,
        "public_release_ready": public_release_ready,
        "final_availability_ready": final_availability_ready,
        "metadata_has_tbd": metadata_has_tbd,
        "fmr005_candidate_rows": len(candidate_rows),
        "fmr005_writeback_allowed": fmr005_writeback_allowed,
        "real_fmr_template_modified": False,
        "guarded_recheck_allowed": False,
        "portal_upload_allowed": False,
        "submission_ready": False,
        "blocker_rows": len(blocker_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": (
            "fmr005_repository_rights_doi_writeback_preflight_candidate_ready"
            if fmr005_writeback_allowed
            else "fmr005_repository_rights_doi_writeback_preflight_ready_blocked_waiting_rights_doi"
        ),
    }
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(
        OUT_DIR / "fmr005_repository_metadata_status.csv",
        ["platform_field", "deposit_status", "prefill_value", "blocking_note", "blocks_fmr005_now"],
        metadata_status_rows,
    )
    write_csv(
        OUT_DIR / "fmr005_rights_licence_status.csv",
        ["component", "current_status", "current_decision", "candidate_decision", "required_evidence_to_close", "blocks_fmr005_now"],
        rights_status_rows,
    )
    write_csv(
        OUT_DIR / "fmr005_repository_rights_doi_guard_matrix.csv",
        ["guard", "current", "required", "passes_now"],
        guard_rows,
    )
    write_csv(
        OUT_DIR / "fmr005_repository_rights_doi_candidates.csv",
        [
            "receipt_id",
            "target_or_route",
            "current_status_after_writeback",
            "value_to_fill_after_manual_action",
            "first_validator",
            "writeback_allowed",
        ],
        candidate_rows,
    )
    write_csv(
        OUT_DIR / "fmr005_repository_rights_doi_blockers.csv",
        ["blocker", "evidence", "blocks"],
        blocker_rows,
    )
    write_csv(
        OUT_DIR / "fmr005_repository_rights_doi_qa.csv",
        ["check", "result", "detail"],
        qa_rows,
    )

    report = f"""# FMR-005 Repository Rights DOI Writeback Preflight

Status: `{summary["status"]}`

Current result:

1. FMR-005 rows: {summary["fmr005_rows"]}
2. Repository record created: {str(summary["repository_record_created"]).lower()}
3. Repository DOI created: {str(summary["repository_doi_created"]).lower()}
4. Code DOI created: {str(summary["code_doi_created"]).lower()}
5. Licence selected: {str(summary["licence_selected"]).lower()}
6. Third-party rights cleared: {str(summary["third_party_rights_cleared"]).lower()}
7. Public release ready: {str(summary["public_release_ready"]).lower()}
8. Final availability ready: {str(summary["final_availability_ready"]).lower()}
9. Blocked metadata fields: {summary["blocked_metadata_fields"]}
10. Release blocker rows: {summary["release_blocker_rows"]}
11. FMR-005 candidate rows: {summary["fmr005_candidate_rows"]}
12. FMR-005 writeback allowed: {str(summary["fmr005_writeback_allowed"]).lower()}
13. Real FMR template modified: false
14. Guarded recheck allowed: false
15. Portal upload allowed: false
16. Submission ready: false

Boundary: FMR-005 remains blocked until repository and code identifiers exist,
licences are selected, third-party rights are cleared, metadata has no TBD
fields and final availability wording is ready. This preflight does not create
a DOI, change licences, upload files, write the FMR intake template, run
guarded recheck or mark the manuscript submitted.
"""
    write_text(OUT_DIR / "FMR005_REPOSITORY_RIGHTS_DOI_WRITEBACK_PREFLIGHT_README.md", report)
    write_text(OUT_DIR / "fmr005_repository_rights_doi_writeback_preflight_report.md", report)
    write_text(
        OUT_DIR / "fmr005_repository_rights_doi_writeback_preflight_summary.json",
        json.dumps(summary, indent=2, ensure_ascii=False),
    )


if __name__ == "__main__":
    main()
