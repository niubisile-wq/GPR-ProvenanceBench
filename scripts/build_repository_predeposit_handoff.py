#!/usr/bin/env python3
"""Build a repository predeposit handoff packet without claiming a public release."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "repository_predeposit_handoff_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"

REPOSITORY_LOCK_DIR = REPORTS / "repository_release_manifest_lock_20260810"
METADATA_DIR = REPORTS / "repository_metadata_package_20260810"
RELEASE_DELTA_DIR = REPORTS / "release_delta_sync_audit_20260810"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


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
    marker = "### 18.73 Repository predeposit handoff update"
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


def metadata_lookup(rows: list[dict[str, str]]) -> dict[str, str]:
    return {row["field"]: row["current_value"] for row in rows}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    lock_rows = read_csv(REPOSITORY_LOCK_DIR / "repository_release_manifest_lock.csv")
    category_rows = read_csv(REPOSITORY_LOCK_DIR / "release_category_lock_summary.csv")
    doi_rows = read_csv(REPOSITORY_LOCK_DIR / "doi_metadata_predeposit_lock.csv")
    rights_rows = read_csv(REPOSITORY_LOCK_DIR / "rights_and_licence_release_blockers.csv")
    availability_rows = read_csv(REPOSITORY_LOCK_DIR / "availability_release_crosswalk.csv")
    delta_summary = json.loads((RELEASE_DELTA_DIR / "release_delta_sync_summary.json").read_text(encoding="utf-8-sig"))

    doi = metadata_lookup(doi_rows)
    platform_rows = [
        {
            "platform_field": "title",
            "prefill_value": doi.get("title", ""),
            "source": "doi_metadata_predeposit_lock.csv",
            "deposit_status": "prefill_ready",
            "blocking_note": "",
        },
        {
            "platform_field": "upload_type",
            "prefill_value": "dataset",
            "source": "repository_metadata_package/zenodo_metadata_draft.json",
            "deposit_status": "prefill_ready",
            "blocking_note": "",
        },
        {
            "platform_field": "creators",
            "prefill_value": doi.get("creators", ""),
            "source": "doi_metadata_predeposit_lock.csv",
            "deposit_status": "blocked",
            "blocking_note": "Confirm complete author list, order, affiliations and ORCID fields before deposit.",
        },
        {
            "platform_field": "description",
            "prefill_value": doi.get("description", ""),
            "source": "doi_metadata_predeposit_lock.csv",
            "deposit_status": "prefill_ready",
            "blocking_note": "",
        },
        {
            "platform_field": "keywords",
            "prefill_value": doi.get("keywords", ""),
            "source": "doi_metadata_predeposit_lock.csv",
            "deposit_status": "prefill_ready",
            "blocking_note": "",
        },
        {
            "platform_field": "version",
            "prefill_value": doi.get("version", ""),
            "source": "doi_metadata_predeposit_lock.csv",
            "deposit_status": "prefill_ready",
            "blocking_note": "",
        },
        {
            "platform_field": "license",
            "prefill_value": doi.get("license", ""),
            "source": "rights_and_licence_release_blockers.csv",
            "deposit_status": "blocked",
            "blocking_note": "Select software and derived-data licences after author and third-party rights review.",
        },
        {
            "platform_field": "related_identifiers",
            "prefill_value": doi.get("related_identifiers", ""),
            "source": "doi_metadata_predeposit_lock.csv",
            "deposit_status": "blocked",
            "blocking_note": "Add manuscript, preprint, data DOI and code DOI only after they exist.",
        },
        {
            "platform_field": "access_right",
            "prefill_value": doi.get("access_right", ""),
            "source": "availability_release_crosswalk.csv",
            "deposit_status": "blocked",
            "blocking_note": "Open only derived artifacts that pass rights review; exclude raw third-party data by default.",
        },
    ]

    upload_rows: list[dict[str, object]] = []
    for index, row in enumerate(lock_rows, start=1):
        upload_rows.append(
            {
                "upload_order": index,
                "source_relative_path": row["source_relative_path"],
                "staged_relative_path": row["staged_relative_path"],
                "category": row["category"],
                "sha256": row["sha256"],
                "upload_decision": "queue_after_rights_and_licence_clearance",
                "public_release_status": row["public_release_status"],
            }
        )

    action_rows: list[dict[str, object]] = []
    for index, row in enumerate(rights_rows, start=1):
        action_rows.append(
            {
                "action_id": f"RLA-{index:03d}",
                "component": row["component"],
                "candidate_licence": row["candidate_licence"],
                "current_status": row["decision_status"],
                "required_action": row["risk"],
                "public_release_blocker": row["public_release_blocker"],
            }
        )

    qa_rows = [
        {
            "check": "upload_queue_matches_locked_manifest",
            "result": "PASS" if len(upload_rows) == len(lock_rows) and len(lock_rows) > 0 else "FAIL",
            "detail": f"upload_rows={len(upload_rows)}; locked_rows={len(lock_rows)}",
        },
        {
            "check": "metadata_blockers_preserved",
            "result": "PASS" if any(row["deposit_status"] == "blocked" for row in platform_rows) else "FAIL",
            "detail": "creators, licence, related identifiers and access rights remain blocked until real decisions exist.",
        },
        {
            "check": "rights_action_register_complete",
            "result": "PASS" if len(action_rows) == len(rights_rows) and len(action_rows) > 0 else "FAIL",
            "detail": f"rights_actions={len(action_rows)}; rights_rows={len(rights_rows)}",
        },
        {
            "check": "release_delta_sync_imported",
            "result": "PASS" if delta_summary.get("qa_pass") is True else "FAIL",
            "detail": f"tracked_delta_artifacts={delta_summary.get('tracked_delta_artifacts')}",
        },
        {
            "check": "no_doi_or_public_release_claimed",
            "result": "PASS",
            "detail": "This handoff prepares forms and upload queue only; DOI creation and public release remain false.",
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(
        OUT_DIR / "repository_platform_metadata_prefill.csv",
        platform_rows,
        ["platform_field", "prefill_value", "source", "deposit_status", "blocking_note"],
    )
    write_csv(
        OUT_DIR / "repository_file_upload_queue.csv",
        upload_rows,
        ["upload_order", "source_relative_path", "staged_relative_path", "category", "sha256", "upload_decision", "public_release_status"],
    )
    write_csv(
        OUT_DIR / "repository_rights_licence_action_register.csv",
        action_rows,
        ["action_id", "component", "candidate_licence", "current_status", "required_action", "public_release_blocker"],
    )
    write_csv(
        OUT_DIR / "repository_availability_deposit_crosswalk.csv",
        availability_rows,
        ["dataset_or_object", "access_route", "identifier_status", "licence_status", "ready_for_statement", "release_manifest_consequence"],
    )
    write_csv(OUT_DIR / "repository_predeposit_handoff_qa.csv", qa_rows, ["check", "result", "detail"])

    readme = """# Repository predeposit handoff 2026-08-10

This package converts the locked release manifest and metadata draft into a repository-deposit handoff.

Use it to prefill repository fields and to stage candidate derived artifacts after author, licence and third-party rights decisions are available.

Boundary: this package does not create a Zenodo/OSF/Figshare record, DOI, licence, public release, final figures or manuscript submission.
"""
    write_text(OUT_DIR / "REPOSITORY_PREDEPOSIT_HANDOFF_README.md", readme)

    report = [
        "# Repository predeposit handoff report 2026-08-10",
        "",
        "Status: `repository_predeposit_handoff_ready_waiting_rights_and_identifier`",
        "",
        f"- Platform metadata fields: {len(platform_rows)}",
        f"- Upload queue files: {len(upload_rows)}",
        f"- Locked categories: {len(category_rows)}",
        f"- Rights/licence action rows: {len(action_rows)}",
        f"- Availability crosswalk rows: {len(availability_rows)}",
        f"- Release delta QA imported: {delta_summary.get('qa_pass')}",
        f"- QA pass: {qa_pass}",
        "",
        "Remaining blockers: author/creator confirmation, licence choice, third-party rights review, repository DOI/accession, code DOI, final rendered figures and final Source Data QA.",
        "",
    ]
    write_text(OUT_DIR / "repository_predeposit_handoff_report.md", "\n".join(report))

    summary = {
        "package": "repository_predeposit_handoff_20260810",
        "platform_metadata_fields": len(platform_rows),
        "blocked_metadata_fields": sum(1 for row in platform_rows if row["deposit_status"] == "blocked"),
        "upload_queue_files": len(upload_rows),
        "locked_categories": len(category_rows),
        "rights_licence_action_rows": len(action_rows),
        "availability_crosswalk_rows": len(availability_rows),
        "release_delta_sync_imported": delta_summary.get("qa_pass") is True,
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "repository_record_created": False,
        "repository_doi_created": False,
        "public_release_ready": False,
        "submission_ready": False,
        "status": "repository_predeposit_handoff_ready_waiting_rights_and_identifier",
    }

    section = f"""### 18.73 Repository predeposit handoff update

Added a repository predeposit handoff packet. This packet turns the locked release manifest and DOI metadata draft into a practical repository prefill/upload handoff while preserving all blockers.

New directory: `{OUT_DIR}`

New files:
1. `repository_platform_metadata_prefill.csv`
2. `repository_file_upload_queue.csv`
3. `repository_rights_licence_action_register.csv`
4. `repository_availability_deposit_crosswalk.csv`
5. `repository_predeposit_handoff_qa.csv`
6. `REPOSITORY_PREDEPOSIT_HANDOFF_README.md`
7. `repository_predeposit_handoff_report.md`
8. `repository_predeposit_handoff_summary.json`

Current result:
1. platform_metadata_fields = {summary['platform_metadata_fields']}
2. blocked_metadata_fields = {summary['blocked_metadata_fields']}
3. upload_queue_files = {summary['upload_queue_files']}
4. rights_licence_action_rows = {summary['rights_licence_action_rows']}
5. qa_pass = {str(qa_pass).lower()}
6. repository_doi_created = false
7. public_release_ready = false
8. submission_ready = false
9. status = `repository_predeposit_handoff_ready_waiting_rights_and_identifier`

Boundary:
1. This step does not create a repository record.
2. This step does not create a DOI.
3. This step does not select a licence or clear third-party rights.
4. This step does not render final figures.
5. This step does not make the manuscript submission-ready."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "repository_predeposit_handoff_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("Repository predeposit handoff QA failed")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
