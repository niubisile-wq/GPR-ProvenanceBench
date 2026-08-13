#!/usr/bin/env python3
"""Validate final Data/Code Availability and repository-release readiness."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "availability_repository_finalization_validator_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"

AVAIL_DIR = BENCH_ROOT / "reports" / "availability_statement_prelock_20260810"
RIGHTS_DIR = BENCH_ROOT / "reports" / "rights_licence_completion_handoff_20260810"
PREDEPOSIT_DIR = BENCH_ROOT / "reports" / "repository_predeposit_handoff_20260810"
RELEASE_LOCK_DIR = BENCH_ROOT / "reports" / "repository_release_manifest_lock_20260810"

AVAIL_SUMMARY = AVAIL_DIR / "availability_statement_prelock_summary.json"
RIGHTS_SUMMARY = RIGHTS_DIR / "rights_licence_completion_handoff_summary.json"
PREDEPOSIT_SUMMARY = PREDEPOSIT_DIR / "repository_predeposit_handoff_summary.json"
RELEASE_SUMMARY = RELEASE_LOCK_DIR / "repository_release_manifest_lock_summary.json"

AVAIL_GATES = AVAIL_DIR / "availability_statement_gate_requirements.csv"
AVAIL_ROUTES = AVAIL_DIR / "availability_access_route_matrix.csv"
DATA_VARIANTS = AVAIL_DIR / "data_availability_statement_variants.csv"
CODE_VARIANTS = AVAIL_DIR / "code_availability_statement_variants.csv"
RIGHTS_DECISIONS = RIGHTS_DIR / "rights_licence_decision_matrix.csv"
RIGHTS_DEP = RIGHTS_DIR / "rights_availability_dependency_map.csv"
RIGHTS_COMMANDS = RIGHTS_DIR / "rights_completion_command_queue.csv"
PREDEPOSIT_METADATA = PREDEPOSIT_DIR / "repository_platform_metadata_prefill.csv"
UPLOAD_QUEUE = PREDEPOSIT_DIR / "repository_file_upload_queue.csv"
PREDEPOSIT_CROSSWALK = PREDEPOSIT_DIR / "repository_availability_deposit_crosswalk.csv"
RELEASE_BLOCKERS = RELEASE_LOCK_DIR / "rights_and_licence_release_blockers.csv"
DOI_LOCK = RELEASE_LOCK_DIR / "doi_metadata_predeposit_lock.csv"
RELEASE_CROSSWALK = RELEASE_LOCK_DIR / "availability_release_crosswalk.csv"


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
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    marker = "### 19.09 Availability/repository finalization validator update"
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

    avail_summary = read_json(AVAIL_SUMMARY)
    rights_summary = read_json(RIGHTS_SUMMARY)
    predeposit_summary = read_json(PREDEPOSIT_SUMMARY)
    release_summary = read_json(RELEASE_SUMMARY)

    avail_gates = read_csv(AVAIL_GATES)
    avail_routes = read_csv(AVAIL_ROUTES)
    data_variants = read_csv(DATA_VARIANTS)
    code_variants = read_csv(CODE_VARIANTS)
    rights_decisions = read_csv(RIGHTS_DECISIONS)
    rights_dep = read_csv(RIGHTS_DEP)
    rights_commands = read_csv(RIGHTS_COMMANDS)
    predeposit_metadata = read_csv(PREDEPOSIT_METADATA)
    upload_queue = read_csv(UPLOAD_QUEUE)
    predeposit_crosswalk = read_csv(PREDEPOSIT_CROSSWALK)
    release_blockers = read_csv(RELEASE_BLOCKERS)
    doi_lock = read_csv(DOI_LOCK)
    release_crosswalk = read_csv(RELEASE_CROSSWALK)

    open_avail_gates = [row for row in avail_gates if row.get("current_state") == "open"]
    blocked_metadata = [row for row in predeposit_metadata if row.get("deposit_status") == "blocked" or row.get("current_status") == "blocking"]
    queued_uploads = [row for row in upload_queue if row.get("upload_decision") == "queue_after_rights_and_licence_clearance"]
    public_blockers = [row for row in release_blockers if row.get("public_release_blocker") in {"yes", "raw_data_excluded_by_default"}]
    draft_data_variants = [row for row in data_variants if row.get("status") != "not_usable_yet"]
    draft_code_variants = [row for row in code_variants if row.get("status") != "not_usable_yet"]

    gate_rows = [
        {
            "gate_id": "AVAIL-REPO-001",
            "requirement": "Repository DOI/accession exists and resolves",
            "current_state": f"repository_doi_created={release_summary.get('repository_doi_created')}; repository_record_created={predeposit_summary.get('repository_record_created')}",
            "passes_now": "no",
            "blocking_reason": "No repository record or DOI/accession exists.",
        },
        {
            "gate_id": "AVAIL-REPO-002",
            "requirement": "Code DOI and software licence are selected",
            "current_state": f"code_doi_created={release_summary.get('code_doi_created')}; licence_selected={rights_summary.get('licence_selected')}",
            "passes_now": "no",
            "blocking_reason": "Software licence and code archive DOI require author confirmation and repository release.",
        },
        {
            "gate_id": "AVAIL-REPO-003",
            "requirement": "Third-party rights and raw-data exclusion policy are closed",
            "current_state": f"third_party_rights_cleared={rights_summary.get('third_party_rights_cleared')}; raw_public_allowed={rights_summary.get('raw_third_party_data_public_release_allowed')}",
            "passes_now": "no",
            "blocking_reason": "Third-party rights are not cleared; raw third-party GPR data remain excluded by default.",
        },
        {
            "gate_id": "AVAIL-REPO-004",
            "requirement": "Final rendered figure Source Data is available",
            "current_state": "final figure Source Data and panel-level mapping remain blocked by figure finalization",
            "passes_now": "no",
            "blocking_reason": "Final figures and panel-level Source Data are not locked.",
        },
        {
            "gate_id": "AVAIL-REPO-005",
            "requirement": "Final availability wording can be used",
            "current_state": f"open_availability_gates={len(open_avail_gates)}; public_release_ready={release_summary.get('public_release_ready')}",
            "passes_now": "no",
            "blocking_reason": "Availability wording remains draft while DOI, rights, licence, final Source Data and blind external data gates are open.",
        },
    ]

    blocker_rows = [
        {
            "blocker_id": "AVAIL-BLOCK-001",
            "blocker": "repository_identifier_missing",
            "evidence": "repository_doi_created=false and repository_record_created=false",
            "next_required_evidence": "Repository landing page, DOI/accession, file list, README, licence and version.",
        },
        {
            "blocker_id": "AVAIL-BLOCK-002",
            "blocker": "licence_and_rights_not_cleared",
            "evidence": "licence_selected=false and third_party_rights_cleared=false",
            "next_required_evidence": "Author-selected software/data licences and rights lead clearance.",
        },
        {
            "blocker_id": "AVAIL-BLOCK-003",
            "blocker": "upload_queue_blocked",
            "evidence": f"{len(queued_uploads)} files are queued only after rights and identifier clearance",
            "next_required_evidence": "Release upload queue with public_release_status allowed after DOI/rights closure.",
        },
        {
            "blocker_id": "AVAIL-BLOCK-004",
            "blocker": "final_source_data_not_locked",
            "evidence": "final rendered figures and panel-level Source Data remain blocked",
            "next_required_evidence": "Final figure exports, visual QA and panel-level Source Data manifest.",
        },
        {
            "blocker_id": "AVAIL-BLOCK-005",
            "blocker": "blind_external_data_open",
            "evidence": "blind external validation data are not acquired",
            "next_required_evidence": "Data-holder agreement, manifest, label-holdout route and shareability decision.",
        },
    ]

    wording_rows = []
    for row in data_variants:
        wording_rows.append(
            {
                "statement_type": "data_availability",
                "variant_id": row.get("variant_id"),
                "status": row.get("status"),
                "usable_now": "yes" if row.get("status") == "author_review_only" else "no",
                "reason": row.get("when_to_use"),
            }
        )
    for row in code_variants:
        wording_rows.append(
            {
                "statement_type": "code_availability",
                "variant_id": row.get("variant_id"),
                "status": row.get("status"),
                "usable_now": "yes" if row.get("status") == "author_review_only" else "no",
                "reason": row.get("when_to_use"),
            }
        )

    command_rows = [
        {"order": 1, "command": "py scripts\\build_rights_licence_completion_handoff.py", "run_now": "yes", "purpose": "Refresh rights/licence queues."},
        {"order": 2, "command": "py scripts\\build_repository_release_manifest_lock.py", "run_now": "yes", "purpose": "Refresh release manifest and DOI metadata locks."},
        {"order": 3, "command": "py scripts\\build_repository_predeposit_handoff.py", "run_now": "yes", "purpose": "Refresh repository predeposit queues."},
        {"order": 4, "command": "py scripts\\build_availability_statement_prelock_package.py", "run_now": "yes", "purpose": "Refresh availability wording prelock."},
        {"order": 5, "command": "py scripts\\build_availability_repository_finalization_validator.py", "run_now": "yes", "purpose": "Refresh this finalization validator."},
        {"order": 6, "command": "Create public repository/DOI and final availability statements", "run_now": "no", "purpose": "Allowed only after rights, licence, DOI and final Source Data gates close."},
    ]

    qa_rows = [
        {
            "check": "availability_gates_open",
            "result": "PASS" if len(open_avail_gates) == 5 else "FAIL",
            "detail": f"open_availability_gates={len(open_avail_gates)}",
        },
        {
            "check": "rights_not_cleared_truthful",
            "result": "PASS" if rights_summary.get("licence_selected") is False and rights_summary.get("third_party_rights_cleared") is False else "FAIL",
            "detail": f"licence_selected={rights_summary.get('licence_selected')}; third_party_rights_cleared={rights_summary.get('third_party_rights_cleared')}",
        },
        {
            "check": "repository_not_created_truthful",
            "result": "PASS" if predeposit_summary.get("repository_record_created") is False and release_summary.get("repository_doi_created") is False else "FAIL",
            "detail": f"repository_record_created={predeposit_summary.get('repository_record_created')}; repository_doi_created={release_summary.get('repository_doi_created')}",
        },
        {
            "check": "upload_queue_blocked",
            "result": "PASS" if len(queued_uploads) == predeposit_summary.get("upload_queue_files") else "FAIL",
            "detail": f"queued_uploads={len(queued_uploads)}; upload_queue_files={predeposit_summary.get('upload_queue_files')}",
        },
        {
            "check": "final_availability_not_ready",
            "result": "PASS" if avail_summary.get("submission_ready") is False and release_summary.get("public_release_ready") is False else "FAIL",
            "detail": f"availability_submission_ready={avail_summary.get('submission_ready')}; public_release_ready={release_summary.get('public_release_ready')}",
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(OUT_DIR / "availability_repository_final_gate_matrix.csv", gate_rows, ["gate_id", "requirement", "current_state", "passes_now", "blocking_reason"])
    write_csv(OUT_DIR / "availability_repository_blockers.csv", blocker_rows, ["blocker_id", "blocker", "evidence", "next_required_evidence"])
    write_csv(OUT_DIR / "availability_statement_usable_variant_matrix.csv", wording_rows, ["statement_type", "variant_id", "status", "usable_now", "reason"])
    write_csv(OUT_DIR / "availability_repository_command_queue.csv", command_rows, ["order", "command", "run_now", "purpose"])
    write_csv(OUT_DIR / "availability_repository_finalization_validator_qa.csv", qa_rows, ["check", "result", "detail"])

    report = [
        "# Availability/repository finalization validator 2026-08-10",
        "",
        "Status: `availability_repository_finalization_validator_ready_blocked`",
        "",
        f"1. Open availability gates: {len(open_avail_gates)}",
        f"2. Blocked metadata fields: {len(blocked_metadata)}",
        f"3. Upload queue files blocked pending rights/identifier: {len(queued_uploads)}",
        f"4. Release blockers: {len(public_blockers)}",
        f"5. Author-review-only statement variants: {len(draft_data_variants) + len(draft_code_variants)}",
        f"6. QA pass: {str(qa_pass).lower()}",
        "",
        "Boundary: this validator does not create DOI records, select licences, clear rights, upload files or finalize availability wording.",
        "",
    ]
    write_text(OUT_DIR / "AVAILABILITY_REPOSITORY_FINALIZATION_VALIDATOR_README.md", "\n".join(report))
    write_text(OUT_DIR / "availability_repository_finalization_validator_report.md", "\n".join(report))

    summary = {
        "package": "availability_repository_finalization_validator_20260810",
        "gate_rows": len(gate_rows),
        "blocker_rows": len(blocker_rows),
        "wording_variant_rows": len(wording_rows),
        "command_rows": len(command_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "open_availability_gates": len(open_avail_gates),
        "blocked_metadata_fields": len(blocked_metadata),
        "upload_queue_files": len(upload_queue),
        "upload_queue_blocked_pending_rights_identifier": len(queued_uploads),
        "release_blocker_rows": len(public_blockers),
        "repository_record_created": False,
        "repository_doi_created": False,
        "code_doi_created": False,
        "licence_selected": False,
        "third_party_rights_cleared": False,
        "public_release_ready": False,
        "final_availability_ready": False,
        "submission_ready": False,
        "status": "availability_repository_finalization_validator_ready_blocked",
    }

    section = f"""### 19.09 Availability/repository finalization validator update

Added a finalization validator for Data Availability, Code Availability, repository DOI and rights/licence gates.

New directory: `{OUT_DIR}`

New files:
1. `availability_repository_final_gate_matrix.csv`
2. `availability_repository_blockers.csv`
3. `availability_statement_usable_variant_matrix.csv`
4. `availability_repository_command_queue.csv`
5. `availability_repository_finalization_validator_qa.csv`
6. `AVAILABILITY_REPOSITORY_FINALIZATION_VALIDATOR_README.md`
7. `availability_repository_finalization_validator_report.md`
8. `availability_repository_finalization_validator_summary.json`

Current result:
1. open_availability_gates = {summary['open_availability_gates']}
2. blocked_metadata_fields = {summary['blocked_metadata_fields']}
3. upload_queue_blocked_pending_rights_identifier = {summary['upload_queue_blocked_pending_rights_identifier']}
4. repository_doi_created = false
5. code_doi_created = false
6. licence_selected = false
7. third_party_rights_cleared = false
8. public_release_ready = false
9. final_availability_ready = false
10. submission_ready = false

Boundary:
1. This validator checks final availability/repository readiness only.
2. It does not create DOI records or upload repository files.
3. It does not select licences, clear rights or finalize Data/Code Availability wording."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "availability_repository_finalization_validator_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("Availability/repository finalization validator QA failed")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
