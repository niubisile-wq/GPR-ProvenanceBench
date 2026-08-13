#!/usr/bin/env python3
"""Audit release-chain synchronization after recent Figure 4/R4 artifact changes."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "release_delta_sync_audit_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"

SOURCE_MANIFEST = REPORTS / "source_data_deposit_package_20260810" / "source_data_file_manifest.csv"
RELEASE_AUDIT = REPORTS / "release_readiness_audit_20260810" / "release_file_audit.csv"
STAGING_MANIFEST = REPORTS / "sanitized_release_staging_20260810" / "sanitized_release_manifest.csv"
REPOSITORY_LOCK = REPORTS / "repository_release_manifest_lock_20260810" / "repository_release_manifest_lock.csv"
R4_SYNC_SUMMARY = REPORTS / "r4_manuscript_boundary_sync_audit_20260810" / "r4_manuscript_boundary_sync_summary.json"

TRACKED_DELTAS = [
    {
        "artifact_id": "DELTA-F4-001",
        "relative_path": "reports/figure4_sources_20260810/figure4_evidence_layer_boundary.csv",
        "artifact_role": "figure4_source_data_boundary",
        "release_decision": "include_as_derived_source_data_candidate_after_licence",
    },
    {
        "artifact_id": "DELTA-F4-002",
        "relative_path": "reports/figure4_sources_20260810/figure4_source_summary.json",
        "artifact_role": "figure4_source_data_metadata",
        "release_decision": "include_as_derived_source_data_candidate_after_licence",
    },
    {
        "artifact_id": "DELTA-F4-003",
        "relative_path": "reports/figure4_sources_20260810/figure4_source_summary.md",
        "artifact_role": "figure4_source_data_readme",
        "release_decision": "include_as_derived_source_data_candidate_after_licence",
    },
    {
        "artifact_id": "DELTA-R4-001",
        "relative_path": "reports/r4_manuscript_boundary_sync_audit_20260810/r4_manuscript_boundary_sync_audit.csv",
        "artifact_role": "internal_manuscript_qa",
        "release_decision": "exclude_from_source_data_release_keep_internal_qa",
    },
    {
        "artifact_id": "DELTA-R4-002",
        "relative_path": "reports/r4_manuscript_boundary_sync_audit_20260810/r4_manuscript_boundary_sync_summary.json",
        "artifact_role": "internal_manuscript_qa",
        "release_decision": "exclude_from_source_data_release_keep_internal_qa",
    },
]


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


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def update_desktop_plan(section: str) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    text = DESKTOP_PLAN.read_text(encoding="utf-8")
    marker = "### 18.72 Release delta synchronization audit 更新"
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
    source_rows = read_csv(SOURCE_MANIFEST)
    release_rows = read_csv(RELEASE_AUDIT)
    staging_rows = read_csv(STAGING_MANIFEST)
    lock_rows = read_csv(REPOSITORY_LOCK)
    r4_summary = read_json(R4_SYNC_SUMMARY)

    source_set = {row["relative_path"] for row in source_rows}
    release_set = {row["relative_path"] for row in release_rows}
    staging_set = {row["source_relative_path"] for row in staging_rows}
    lock_set = {row["source_relative_path"] for row in lock_rows}

    matrix_rows: list[dict[str, object]] = []
    for item in TRACKED_DELTAS:
        rel_path = item["relative_path"]
        should_include = item["release_decision"].startswith("include_")
        row = {
            "artifact_id": item["artifact_id"],
            "relative_path": rel_path,
            "artifact_role": item["artifact_role"],
            "release_decision": item["release_decision"],
            "exists_in_worktree": (BENCH_ROOT / rel_path).exists(),
            "in_source_data_manifest": rel_path in source_set,
            "in_release_readiness_audit": rel_path in release_set,
            "in_sanitized_staging_manifest": rel_path in staging_set,
            "in_repository_release_lock": rel_path in lock_set,
        }
        if should_include:
            expected_ok = (
                row["exists_in_worktree"]
                and row["in_source_data_manifest"]
                and row["in_release_readiness_audit"]
                and row["in_sanitized_staging_manifest"]
                and row["in_repository_release_lock"]
            )
            status = "pass_included_release_chain" if expected_ok else "fail_missing_from_release_chain"
        else:
            expected_ok = row["exists_in_worktree"] and not row["in_source_data_manifest"] and not row["in_repository_release_lock"]
            status = "pass_internal_qa_excluded_from_source_release" if expected_ok else "fail_internal_qa_release_scope_mismatch"
        row["status"] = status
        matrix_rows.append(row)

    inclusion_rows = [
        {
            "decision_id": "REL-DELTA-001",
            "artifact_group": "Figure 4 evidence-layer boundary files",
            "decision": "include",
            "reason": "These are derived Figure 4 source-data and metadata files needed to reproduce the planned stress-test boundary panel.",
            "remaining_condition": "Licence, repository DOI/accession, final figures and rights review remain unresolved.",
        },
        {
            "decision_id": "REL-DELTA-002",
            "artifact_group": "R4 manuscript boundary sync audit files",
            "decision": "exclude_from_source_data_release",
            "reason": "These files are internal manuscript-QA evidence rather than figure/table source data or public repository metadata.",
            "remaining_condition": "Keep under local reports and checkpoint evidence; include in public release only if authors decide to publish internal QA provenance.",
        },
    ]

    qa_rows = [
        {
            "check": "Tracked Figure 4 source-data deltas are included through repository lock",
            "result": "PASS" if all(row["status"] == "pass_included_release_chain" for row in matrix_rows if str(row["artifact_id"]).startswith("DELTA-F4")) else "FAIL",
            "detail": "Figure 4 boundary artifacts must appear in source manifest, release audit, sanitized staging and repository lock.",
        },
        {
            "check": "Tracked R4 manuscript-QA deltas are intentionally excluded from source-data release",
            "result": "PASS" if all(row["status"] == "pass_internal_qa_excluded_from_source_release" for row in matrix_rows if str(row["artifact_id"]).startswith("DELTA-R4")) else "FAIL",
            "detail": "R4 sync audit is internal QA, not figure/table Source Data.",
        },
        {
            "check": "R4 manuscript sync audit passed upstream",
            "result": "PASS" if r4_summary.get("qa_pass") is True and r4_summary.get("obsolete_marker_hits") == 0 else "FAIL",
            "detail": f"obsolete_marker_hits={r4_summary.get('obsolete_marker_hits')}",
        },
        {
            "check": "No public release asserted",
            "result": "PASS",
            "detail": "This audit does not create DOI, licence, rights clearance or public release.",
        },
    ]

    write_csv(
        OUT_DIR / "release_delta_sync_matrix.csv",
        matrix_rows,
        [
            "artifact_id",
            "relative_path",
            "artifact_role",
            "release_decision",
            "exists_in_worktree",
            "in_source_data_manifest",
            "in_release_readiness_audit",
            "in_sanitized_staging_manifest",
            "in_repository_release_lock",
            "status",
        ],
    )
    write_csv(
        OUT_DIR / "release_delta_inclusion_decisions.csv",
        inclusion_rows,
        ["decision_id", "artifact_group", "decision", "reason", "remaining_condition"],
    )
    write_csv(OUT_DIR / "release_delta_sync_qa.csv", qa_rows, ["check", "result", "detail"])

    qa_pass = all(row["result"] != "FAIL" for row in qa_rows)
    report = [
        "# Release Delta Synchronization Audit",
        "",
        "Status: `release_delta_sync_ready_release_not_public`",
        "",
        "Purpose: verify that recent Figure 4/R4 changes are consistently handled by the release chain.",
        "",
        f"- Tracked delta artifacts: {len(matrix_rows)}",
        f"- Figure 4 release-chain included rows: {sum(1 for row in matrix_rows if row['status'] == 'pass_included_release_chain')}",
        f"- Internal R4 QA excluded rows: {sum(1 for row in matrix_rows if row['status'] == 'pass_internal_qa_excluded_from_source_release')}",
        f"- QA pass: {qa_pass}",
        "",
        "Boundary: this is a synchronization audit only. It does not create DOI records, select a licence, clear third-party rights, render final figures or make the manuscript submission-ready.",
        "",
    ]
    write_text(OUT_DIR / "release_delta_sync_report.md", "\n".join(report))

    summary = {
        "package": "release_delta_sync_audit_20260810",
        "tracked_delta_artifacts": len(matrix_rows),
        "figure4_deltas_included_through_repository_lock": sum(1 for row in matrix_rows if row["status"] == "pass_included_release_chain"),
        "r4_internal_qa_deltas_excluded_from_source_release": sum(1 for row in matrix_rows if row["status"] == "pass_internal_qa_excluded_from_source_release"),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "repository_doi_created": False,
        "public_release_ready": False,
        "submission_ready": False,
        "status": "release_delta_sync_ready_release_not_public",
    }

    section = f"""### 18.72 Release delta synchronization audit 更新

已新增 release delta synchronization audit。这个包专门检查 18.70/18.71 之后新增的 Figure 4 source-data delta 和 R4 manuscript-QA delta 在 release 链条中的处理是否一致。

新增目录：
`{OUT_DIR}`

新增材料：
1. `release_delta_sync_matrix.csv`
2. `release_delta_inclusion_decisions.csv`
3. `release_delta_sync_qa.csv`
4. `release_delta_sync_report.md`
5. `release_delta_sync_summary.json`

当前结果：
1. tracked_delta_artifacts = {len(matrix_rows)}
2. figure4_deltas_included_through_repository_lock = {summary['figure4_deltas_included_through_repository_lock']}
3. r4_internal_qa_deltas_excluded_from_source_release = {summary['r4_internal_qa_deltas_excluded_from_source_release']}
4. qa_pass = {str(qa_pass).lower()}
5. repository_doi_created = false
6. public_release_ready = false
7. submission_ready = false
8. 当前状态：`release_delta_sync_ready_release_not_public`

边界：
1. Figure 4 evidence-layer boundary 文件应进入 Source Data / release candidate。
2. R4 manuscript boundary sync audit 是内部稿件 QA，不自动进入 Source Data release。
3. 这一步不创建 DOI、不选择 licence、不完成 rights clearance、不渲染 final figures。
"""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "release_delta_sync_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("Release delta synchronization audit failed")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
