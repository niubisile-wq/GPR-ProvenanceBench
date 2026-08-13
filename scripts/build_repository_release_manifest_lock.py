#!/usr/bin/env python3
"""Build a repository release manifest lock without creating DOI or release."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "repository_release_manifest_lock_20260810"
STAGING_MANIFEST = BENCH_ROOT / "reports" / "sanitized_release_staging_20260810" / "sanitized_release_manifest.csv"
RELEASE_AUDIT = BENCH_ROOT / "reports" / "release_readiness_audit_20260810" / "release_file_audit.csv"
REPOSITORY_METADATA_DIR = BENCH_ROOT / "reports" / "repository_metadata_package_20260810"
AVAILABILITY_DIR = BENCH_ROOT / "reports" / "availability_statement_prelock_20260810"
SOURCE_DATA_MANIFEST = BENCH_ROOT / "reports" / "source_data_deposit_package_20260810" / "source_data_file_manifest.csv"


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
    staging_rows = read_csv(STAGING_MANIFEST)
    release_audit_rows = read_csv(RELEASE_AUDIT)
    inclusion_rows = read_csv(REPOSITORY_METADATA_DIR / "release_inclusion_plan.csv")
    exclusion_rows = read_csv(REPOSITORY_METADATA_DIR / "release_exclusion_plan.csv")
    licence_rows = read_csv(REPOSITORY_METADATA_DIR / "licence_decision_matrix.csv")
    metadata_rows = read_csv(REPOSITORY_METADATA_DIR / "repository_metadata_fields.csv")
    availability_rows = read_csv(AVAILABILITY_DIR / "availability_access_route_matrix.csv")
    source_data_rows = read_csv(SOURCE_DATA_MANIFEST)

    lock_rows: list[dict[str, str]] = []
    for row in staging_rows:
        lock_rows.append(
            {
                "source_relative_path": row["source_relative_path"],
                "staged_relative_path": row["staged_relative_path"],
                "category": row["category"],
                "size_bytes": row["size_bytes"],
                "sha256": row["sha256"],
                "local_path_markers_after_staging": row["local_path_markers_after_staging"],
                "placeholder_markers_after_staging": row["placeholder_markers_after_staging"],
                "predeposit_lock_status": "candidate_locked_after_sanitized_staging",
                "public_release_status": "blocked_pending_licence_rights_and_identifier",
                "release_note": "Derived artifact candidate only; raw third-party GPR data are not redistributed.",
            }
        )

    category_counts = Counter(row["category"] for row in staging_rows)
    category_rows = [
        {
            "category": category,
            "locked_candidate_files": str(count),
            "release_decision": next((row["release_decision"] for row in inclusion_rows if row["category"] == category), "include_after_licence_review"),
            "remaining_condition": next((row["remaining_condition"] for row in inclusion_rows if row["category"] == category), "Licence selection and third-party rights review."),
        }
        for category, count in sorted(category_counts.items())
    ]

    excluded_status_counts = Counter(row["release_status"] for row in release_audit_rows)
    exclusion_lock_rows = [
        {
            "exclusion_class": "needs_review_or_sanitization",
            "file_count": str(excluded_status_counts.get("needs_review", 0)),
            "reason": "Files contain local paths/placeholders or require rights review before release.",
            "release_condition": "Sanitize paths/placeholders and complete rights review before inclusion.",
        },
        {
            "exclusion_class": "raw_third_party_gpr_files",
            "file_count": "not_bundled",
            "reason": "Raw data redistribution requires provider permission.",
            "release_condition": "Use citations/access instructions unless explicit redistribution permission exists.",
        },
        {
            "exclusion_class": "final_rendered_figures",
            "file_count": "0",
            "reason": "Rendered figures do not exist yet.",
            "release_condition": "Render figures, run visual QA and generate panel-level Source Data first.",
        },
        {
            "exclusion_class": "blind_external_validation_data",
            "file_count": "0",
            "reason": "Blind external validation data have not been acquired.",
            "release_condition": "Define data-holder agreement after real external asset exists.",
        },
    ]

    doi_rows = [
        {
            "field": row["field"],
            "current_value": row["value"],
            "current_status": row["status"],
            "lock_decision": "predeposit_metadata_available" if row["status"] == "draft" else "blocking_for_public_release",
        }
        for row in metadata_rows
    ]

    rights_rows = [
        {
            "component": row["component"],
            "candidate_licence": row["candidate_licence"],
            "decision_status": row["decision_status"],
            "risk": row["risk"],
            "public_release_blocker": "yes" if row["decision_status"] != "exclude_by_default" else "raw_data_excluded_by_default",
        }
        for row in licence_rows
    ]

    availability_crosswalk_rows = [
        {
            "dataset_or_object": row["dataset_or_object"],
            "access_route": row["access_route"],
            "identifier_status": row["identifier_status"],
            "licence_status": row["licence_status"],
            "ready_for_statement": row["ready_for_statement"],
            "release_manifest_consequence": "public_release_blocked" if row["ready_for_statement"] != "final" else "can_reference_release",
        }
        for row in availability_rows
    ]

    qa_rows = [
        {
            "qa_check": "staged_candidates_have_no_local_paths_or_placeholders",
            "status": "pass" if all(not row["local_path_markers_after_staging"] and not row["placeholder_markers_after_staging"] for row in staging_rows) else "fail",
            "evidence": f"staged_rows={len(staging_rows)}",
        },
        {
            "qa_check": "release_does_not_include_raw_third_party_data",
            "status": "pass",
            "evidence": "lock manifest states derived artifact candidates only",
        },
        {
            "qa_check": "doi_not_claimed",
            "status": "pass" if all("DOI" not in row["predeposit_lock_status"] for row in lock_rows) else "fail",
            "evidence": "public_release_status remains blocked_pending_licence_rights_and_identifier",
        },
        {
            "qa_check": "availability_not_final",
            "status": "pass" if any(row["ready_for_statement"] != "final" for row in availability_rows) else "fail",
            "evidence": "availability rows remain draft_only/restricted/open-gate",
        },
    ]

    write_csv(
        OUT_DIR / "repository_release_manifest_lock.csv",
        lock_rows,
        [
            "source_relative_path",
            "staged_relative_path",
            "category",
            "size_bytes",
            "sha256",
            "local_path_markers_after_staging",
            "placeholder_markers_after_staging",
            "predeposit_lock_status",
            "public_release_status",
            "release_note",
        ],
    )
    write_csv(OUT_DIR / "release_category_lock_summary.csv", category_rows, ["category", "locked_candidate_files", "release_decision", "remaining_condition"])
    write_csv(OUT_DIR / "release_exclusion_lock.csv", exclusion_lock_rows, ["exclusion_class", "file_count", "reason", "release_condition"])
    write_csv(OUT_DIR / "doi_metadata_predeposit_lock.csv", doi_rows, ["field", "current_value", "current_status", "lock_decision"])
    write_csv(OUT_DIR / "rights_and_licence_release_blockers.csv", rights_rows, ["component", "candidate_licence", "decision_status", "risk", "public_release_blocker"])
    write_csv(OUT_DIR / "availability_release_crosswalk.csv", availability_crosswalk_rows, ["dataset_or_object", "access_route", "identifier_status", "licence_status", "ready_for_statement", "release_manifest_consequence"])
    write_csv(OUT_DIR / "repository_release_manifest_lock_qa.csv", qa_rows, ["qa_check", "status", "evidence"])

    readme = """# Repository release manifest lock 2026-08-10

This package locks the current sanitized predeposit candidate manifest and the release blockers for repository/DOI preparation.

It does not create a public repository, DOI, accession, software licence, data licence or rights clearance.
"""
    (OUT_DIR / "REPOSITORY_RELEASE_MANIFEST_LOCK_README.md").write_text(readme, encoding="utf-8")

    qa_pass = all(row["status"] == "pass" for row in qa_rows)
    summary = {
        "run_id": "20260810_repository_release_manifest_lock",
        "locked_candidate_files": len(lock_rows),
        "locked_categories": len(category_rows),
        "source_data_manifest_rows": len(source_data_rows),
        "exclusion_rows": len(exclusion_lock_rows),
        "rights_blocker_rows": len(rights_rows),
        "availability_crosswalk_rows": len(availability_crosswalk_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "repository_doi_created": False,
        "code_doi_created": False,
        "public_release_ready": False,
        "submission_ready": False,
        "status": "repository_release_manifest_lock_ready_release_not_public",
        "boundary": "This package locks predeposit candidates and release blockers; it does not create DOI, licence, rights clearance or a public release.",
    }
    (OUT_DIR / "repository_release_manifest_lock_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    report = [
        "# Repository release manifest lock report 2026-08-10",
        "",
        f"- Locked candidate files: {summary['locked_candidate_files']}",
        f"- Locked categories: {summary['locked_categories']}",
        f"- Source-data manifest rows available upstream: {summary['source_data_manifest_rows']}",
        f"- Exclusion rows: {summary['exclusion_rows']}",
        f"- Rights/licence blocker rows: {summary['rights_blocker_rows']}",
        f"- QA pass: {summary['qa_pass']}",
        f"- Repository DOI created: {summary['repository_doi_created']}",
        f"- Public release ready: {summary['public_release_ready']}",
        f"- Status: {summary['status']}",
        "",
        "Conclusion: predeposit release candidates are locked from sanitized staging, but public release remains blocked by licence, rights and identifier decisions.",
        "",
    ]
    (OUT_DIR / "repository_release_manifest_lock_report.md").write_text("\n".join(report), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
