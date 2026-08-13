#!/usr/bin/env python3
"""Build a non-final reference numbering prelock package from candidate markers."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "reference_numbering_prelock_20260810"
MANUSCRIPT = BENCH_ROOT / "reports" / "author_review_manuscript_package_20260810" / "author_review_manuscript_v0_1.md"
CITATION_DIR = BENCH_ROOT / "reports" / "narrative_citation_pass_20260810"
CANDIDATES = CITATION_DIR / "citation_candidate_library.csv"
MAPPING = CITATION_DIR / "narrative_citation_mapping.csv"
RIS_EXPORT = CITATION_DIR / "references_narrative_citation_pass.ris"
BROWSER = CITATION_DIR / "citation_pass_browser.html"


MARKER_RE = re.compile(r"\[P[0-9](?:,P[0-9])*\]")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def split_marker(marker: str) -> list[str]:
    return marker.strip("[]").split(",")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manuscript = MANUSCRIPT.read_text(encoding="utf-8")
    candidates = read_csv(CANDIDATES)
    mapping = read_csv(MAPPING)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}

    marker_rows: list[dict[str, str]] = []
    candidate_sequence: list[str] = []
    line_starts: list[int] = []
    offset = 0
    for line in manuscript.splitlines(keepends=True):
        line_starts.append(offset)
        offset += len(line)

    for match in MARKER_RE.finditer(manuscript):
        marker = match.group(0)
        line_number = 1
        for idx, start in enumerate(line_starts, start=1):
            if start <= match.start():
                line_number = idx
            else:
                break
        candidate_ids = split_marker(marker)
        candidate_sequence.extend(candidate_ids)
        marker_rows.append(
            {
                "marker": marker,
                "line_number": str(line_number),
                "candidate_ids": ";".join(candidate_ids),
                "context": manuscript[max(0, match.start() - 120) : min(len(manuscript), match.end() + 160)].replace("\n", " "),
                "status": "candidate_marker_not_final_numbered_reference",
            }
        )
    write_csv(OUT_DIR / "manuscript_candidate_marker_inventory.csv", marker_rows, ["marker", "line_number", "candidate_ids", "context", "status"])

    counter = Counter(candidate_sequence)
    first_order: list[str] = []
    for candidate_id in candidate_sequence:
        if candidate_id not in first_order:
            first_order.append(candidate_id)

    prelock_rows: list[dict[str, str]] = []
    for idx, candidate_id in enumerate(first_order, start=1):
        candidate = candidate_by_id.get(candidate_id, {})
        prelock_rows.append(
            {
                "proposed_reference_number": str(idx),
                "candidate_id": candidate_id,
                "current_marker_count": str(counter[candidate_id]),
                "authors_short": candidate.get("authors_short", ""),
                "year": candidate.get("year", ""),
                "title": candidate.get("title", ""),
                "journal": candidate.get("journal", ""),
                "doi": candidate.get("doi", ""),
                "support_role": candidate.get("support_role", ""),
                "prelock_status": "eligible_for_manual_verification" if candidate_id in candidate_by_id else "missing_from_candidate_library",
            }
        )
    write_csv(
        OUT_DIR / "reference_numbering_prelock.csv",
        prelock_rows,
        [
            "proposed_reference_number",
            "candidate_id",
            "current_marker_count",
            "authors_short",
            "year",
            "title",
            "journal",
            "doi",
            "support_role",
            "prelock_status",
        ],
    )

    verification_rows: list[dict[str, str]] = []
    used_ids = set(first_order)
    for row in candidates:
        used = row["candidate_id"] in used_ids
        verification_rows.append(
            {
                "candidate_id": row["candidate_id"],
                "used_in_author_review_manuscript": "yes" if used else "no",
                "authors_short": row["authors_short"],
                "year": row["year"],
                "journal": row["journal"],
                "doi": row["doi"],
                "local_text_exists": row["local_text_exists"],
                "verification_basis": row["verification_basis"],
                "support_role": row["support_role"],
                "manual_check_required": "yes",
                "manual_check_reason": "Confirm bibliography fields, publisher page, local claim support and final prose placement before numbered conversion.",
            }
        )
    write_csv(
        OUT_DIR / "reference_candidate_verification_table.csv",
        verification_rows,
        [
            "candidate_id",
            "used_in_author_review_manuscript",
            "authors_short",
            "year",
            "journal",
            "doi",
            "local_text_exists",
            "verification_basis",
            "support_role",
            "manual_check_required",
            "manual_check_reason",
        ],
    )

    unresolved_rows = [
        {
            "item": "candidate_markers_remain",
            "severity": "high",
            "required_action": "Replace [P#] or [P#,P#] markers only after final prose, figure calls and reference order are locked.",
        },
        {
            "item": "manual_publisher_verification",
            "severity": "high",
            "required_action": "Verify DOI, title, journal, year and support boundary against publisher/Crossref pages before final bibliography.",
        },
        {
            "item": "internal_result_citations",
            "severity": "high",
            "required_action": "Use internal figures/source data for this project's measured deltas; do not cite external papers as evidence for derived metrics.",
        },
        {
            "item": "availability_statement_refs",
            "severity": "medium",
            "required_action": "Do not finalize repository/data/code statements until DOI, licence and rights gates are resolved.",
        },
    ]
    write_csv(OUT_DIR / "unresolved_reference_lock_actions.csv", unresolved_rows, ["item", "severity", "required_action"])

    qa_rows = [
        {
            "check": "all_manuscript_candidate_ids_in_library",
            "result": "PASS" if all(candidate_id in candidate_by_id for candidate_id in first_order) else "FAIL",
            "detail": ";".join(first_order),
        },
        {
            "check": "ris_export_exists",
            "result": "PASS" if RIS_EXPORT.exists() else "FAIL",
            "detail": str(RIS_EXPORT),
        },
        {
            "check": "html_browser_exists",
            "result": "PASS" if BROWSER.exists() else "FAIL",
            "detail": str(BROWSER),
        },
        {
            "check": "final_numbered_references_not_claimed",
            "result": "PASS",
            "detail": "This package is prelock only and does not replace candidate markers.",
        },
        {
            "check": "manual_verification_required",
            "result": "PASS" if all(row["manual_check_required"] == "yes" for row in verification_rows) else "FAIL",
            "detail": "Every candidate row remains marked for manual verification.",
        },
    ]
    write_csv(OUT_DIR / "reference_prelock_qa.csv", qa_rows, ["check", "result", "detail"])

    readme = f"""# Reference numbering prelock package 2026-08-10

This package prepares the current candidate citation markers for final manual reference verification and numbering.

## Inputs

1. Author-review manuscript: `{MANUSCRIPT.relative_to(BENCH_ROOT)}`
2. Candidate library: `{CANDIDATES.relative_to(BENCH_ROOT)}`
3. Citation mapping: `{MAPPING.relative_to(BENCH_ROOT)}`
4. RIS export: `{RIS_EXPORT.relative_to(BENCH_ROOT)}`
5. HTML browser: `{BROWSER.relative_to(BENCH_ROOT)}`

## Current interpretation

The author-review manuscript still contains candidate markers and must not be treated as having final numbered references. The prelock table gives a proposed order based only on first marker appearance in the current author-review draft.

## Stop rules

1. Do not convert `[P#]` markers to final reference numbers until final prose and figure calls are locked.
2. Do not cite external literature as evidence for this project's internally derived metrics.
3. Do not finalize Data Availability or Code Availability references until repository DOI/accession, licence and rights decisions are real.
4. Verify DOI, journal, title and support boundary manually before final bibliography export.
"""
    (OUT_DIR / "REFERENCE_PRELOCK_README.md").write_text(readme, encoding="utf-8")

    summary = {
        "run_id": "20260810_reference_numbering_prelock",
        "markers_found": len(marker_rows),
        "unique_candidate_ids_in_manuscript": len(first_order),
        "candidate_library_rows": len(candidates),
        "mapping_rows": len(mapping),
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "reference_export": str(RIS_EXPORT.relative_to(BENCH_ROOT)),
        "browser": str(BROWSER.relative_to(BENCH_ROOT)),
        "submission_ready": False,
        "status": "reference_numbering_prelock_ready_not_final_references",
        "boundary": "This package prepares reference numbering; it does not finalize references or remove candidate markers.",
    }
    (OUT_DIR / "reference_numbering_prelock_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    report = [
        "# Reference numbering prelock report 2026-08-10",
        "",
        f"- Markers found: {summary['markers_found']}",
        f"- Unique candidate IDs in manuscript: {summary['unique_candidate_ids_in_manuscript']}",
        f"- Candidate library rows: {summary['candidate_library_rows']}",
        f"- Mapping rows: {summary['mapping_rows']}",
        f"- QA pass: {summary['qa_pass']}",
        f"- Status: {summary['status']}",
        "",
        "Conclusion: candidate references are organized for final manual verification, but the manuscript still does not have final numbered references.",
        "",
    ]
    (OUT_DIR / "reference_numbering_prelock_report.md").write_text("\n".join(report), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
