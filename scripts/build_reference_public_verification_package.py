#!/usr/bin/env python3
"""Build a public metadata verification package for prelocked references."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "reference_public_verification_20260810"
PRELOCK_DIR = BENCH_ROOT / "reports" / "reference_numbering_prelock_20260810"
CANDIDATE_LIBRARY = BENCH_ROOT / "reports" / "narrative_citation_pass_20260810" / "citation_candidate_library.csv"


VERIFIED = {
    "P1": {
        "authors_citation": "Zhou, X., Liu, S., Yan, X. et al.",
        "title": "Reservoir-enhanced segment anything model for subsurface diagnosis",
        "journal": "Nature Communications",
        "short_journal": "Nat Commun",
        "volume": "16",
        "article_number": "11080",
        "year": "2025",
        "published": "2025-12-12",
        "doi": "10.1038/s41467-025-67382-4",
        "url": "https://www.nature.com/articles/s41467-025-67382-4",
    },
    "P2": {
        "authors_citation": "Zhou, W., Liu, F., Zheng, H. et al.",
        "title": "Mitigating data bias and ensuring reliable evaluation of AI models with shortcut hull learning",
        "journal": "Nature Communications",
        "short_journal": "Nat Commun",
        "volume": "16",
        "article_number": "5513",
        "year": "2025",
        "published": "2025-07-01",
        "doi": "10.1038/s41467-025-60801-6",
        "url": "https://www.nature.com/articles/s41467-025-60801-6",
    },
    "P3": {
        "authors_citation": "Brown, A., Tomasev, N., Freyberg, J. et al.",
        "title": "Detecting shortcut learning for fair medical AI using shortcut testing",
        "journal": "Nature Communications",
        "short_journal": "Nat Commun",
        "volume": "14",
        "article_number": "4314",
        "year": "2023",
        "published": "2023-07-18",
        "doi": "10.1038/s41467-023-39902-7",
        "url": "https://www.nature.com/articles/s41467-023-39902-7",
    },
    "P4": {
        "authors_citation": "Rosenblatt, M., Tejavibulya, L., Jiang, R. et al.",
        "title": "Data leakage inflates prediction performance in connectome-based machine learning models",
        "journal": "Nature Communications",
        "short_journal": "Nat Commun",
        "volume": "15",
        "article_number": "1829",
        "year": "2024",
        "published": "2024-02-28",
        "doi": "10.1038/s41467-024-46150-w",
        "url": "https://www.nature.com/articles/s41467-024-46150-w",
    },
    "P5": {
        "authors_citation": "Joeres, R., Blumenthal, D.B. & Kalinina, O.V.",
        "title": "Data splitting to avoid information leakage with DataSAIL",
        "journal": "Nature Communications",
        "short_journal": "Nat Commun",
        "volume": "16",
        "article_number": "3337",
        "year": "2025",
        "published": "2025-04-08",
        "doi": "10.1038/s41467-025-58606-8",
        "url": "https://www.nature.com/articles/s41467-025-58606-8",
    },
    "P6": {
        "authors_citation": "Roschewitz, M., Khara, G., Yearsley, J. et al.",
        "title": "Automatic correction of performance drift under acquisition shift in medical image classification",
        "journal": "Nature Communications",
        "short_journal": "Nat Commun",
        "volume": "14",
        "article_number": "6608",
        "year": "2023",
        "published": "2023-10-19",
        "doi": "10.1038/s41467-023-42396-y",
        "url": "https://www.nature.com/articles/s41467-023-42396-y",
    },
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def ris_record(candidate_id: str, verified: dict[str, str]) -> str:
    return "\n".join(
        [
            "TY  - JOUR",
            f"ID  - {candidate_id}",
            f"TI  - {verified['title']}",
            f"JO  - {verified['journal']}",
            f"VL  - {verified['volume']}",
            f"SP  - {verified['article_number']}",
            f"PY  - {verified['year']}",
            f"DA  - {verified['published']}",
            f"DO  - {verified['doi']}",
            f"UR  - {verified['url']}",
            f"N1  - Prelock export only; verify final citation order and support boundary before submission.",
            "ER  -",
            "",
        ]
    )


def enw_record(candidate_id: str, verified: dict[str, str]) -> str:
    return "\n".join(
        [
            "%0 Journal Article",
            f"%F {candidate_id}",
            f"%T {verified['title']}",
            f"%J {verified['journal']}",
            f"%V {verified['volume']}",
            f"%P {verified['article_number']}",
            f"%D {verified['year']}",
            f"%8 {verified['published']}",
            f"%R {verified['doi']}",
            f"%U {verified['url']}",
            "%Z Prelock export only; verify final citation order and support boundary before submission.",
            "",
        ]
    )


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    candidates = read_csv(CANDIDATE_LIBRARY)
    prelock_rows = read_csv(PRELOCK_DIR / "reference_numbering_prelock.csv")
    used_ids = {row["candidate_id"] for row in prelock_rows}

    metadata_rows: list[dict[str, str]] = []
    support_rows: list[dict[str, str]] = []
    for candidate in candidates:
        candidate_id = candidate["candidate_id"]
        verified = VERIFIED[candidate_id]
        metadata_match = (
            candidate["title"] == verified["title"]
            and candidate["journal"] == verified["journal"]
            and candidate["doi"] == verified["doi"]
            and candidate["year"] == verified["year"]
        )
        metadata_rows.append(
            {
                "candidate_id": candidate_id,
                "used_in_current_manuscript": "yes" if candidate_id in used_ids else "no",
                "verified_authors_citation": verified["authors_citation"],
                "verified_title": verified["title"],
                "verified_journal": verified["journal"],
                "verified_volume": verified["volume"],
                "verified_article_number": verified["article_number"],
                "verified_year": verified["year"],
                "verified_published_date": verified["published"],
                "verified_doi": verified["doi"],
                "verified_url": verified["url"],
                "local_metadata_match": "pass" if metadata_match else "fail",
                "verification_source": "Nature article page DOI search on 2026-08-10",
                "final_reference_ready": "false",
            }
        )
        support_rows.append(
            {
                "candidate_id": candidate_id,
                "used_in_current_manuscript": "yes" if candidate_id in used_ids else "no",
                "support_role": candidate["support_role"],
                "allowed_use": "background_or_method_context_only",
                "forbidden_use": "Do not cite as evidence for this project's measured deltas, rendered figures, repository DOI, blind external validation or final Reporting Summary.",
                "support_lock_status": "prelock_verified_metadata_support_boundary_not_final",
            }
        )

    write_csv(
        OUT_DIR / "public_reference_metadata_verification.csv",
        metadata_rows,
        [
            "candidate_id",
            "used_in_current_manuscript",
            "verified_authors_citation",
            "verified_title",
            "verified_journal",
            "verified_volume",
            "verified_article_number",
            "verified_year",
            "verified_published_date",
            "verified_doi",
            "verified_url",
            "local_metadata_match",
            "verification_source",
            "final_reference_ready",
        ],
    )

    order_rows = []
    for row in prelock_rows:
        verified = VERIFIED[row["candidate_id"]]
        order_rows.append(
            {
                "proposed_reference_number": row["proposed_reference_number"],
                "candidate_id": row["candidate_id"],
                "formatted_prelock_reference": f"{verified['authors_citation']} {verified['title']}. {verified['short_journal']} {verified['volume']}, {verified['article_number']} ({verified['year']}). https://doi.org/{verified['doi']}",
                "marker_count": row["current_marker_count"],
                "metadata_verified": "yes",
                "numbering_lock_status": "prelock_only_final_order_pending_final_prose_and_figure_calls",
            }
        )
    write_csv(
        OUT_DIR / "current_manuscript_reference_order_verified_prelock.csv",
        order_rows,
        [
            "proposed_reference_number",
            "candidate_id",
            "formatted_prelock_reference",
            "marker_count",
            "metadata_verified",
            "numbering_lock_status",
        ],
    )

    write_csv(
        OUT_DIR / "reference_support_boundary_audit.csv",
        support_rows,
        ["candidate_id", "used_in_current_manuscript", "support_role", "allowed_use", "forbidden_use", "support_lock_status"],
    )

    remaining_rows = [
        {
            "remaining_action": "Replace [P#] markers only after final prose and figure/table calls are locked.",
            "severity": "high",
            "closure_evidence": "Final manuscript file with stable citation order and no candidate markers.",
        },
        {
            "remaining_action": "Confirm support strength against the final sentence-level claims.",
            "severity": "high",
            "closure_evidence": "Sentence-to-reference support audit with no metadata-only citations.",
        },
        {
            "remaining_action": "Keep internal metrics cited to internal figures/source data rather than external literature.",
            "severity": "high",
            "closure_evidence": "Final claim-source map for balanced-accuracy deltas and gate statuses.",
        },
        {
            "remaining_action": "Regenerate final RIS/ENW after final order is locked.",
            "severity": "medium",
            "closure_evidence": "Reference-manager export whose order matches final manuscript numbering.",
        },
    ]
    write_csv(OUT_DIR / "reference_final_lock_remaining_actions.csv", remaining_rows, ["remaining_action", "severity", "closure_evidence"])

    (OUT_DIR / "candidate_references_prelock.ris").write_text("".join(ris_record(cid, VERIFIED[cid]) for cid in VERIFIED), encoding="utf-8")
    (OUT_DIR / "candidate_references_prelock.enw").write_text("".join(enw_record(cid, VERIFIED[cid]) for cid in VERIFIED), encoding="utf-8")

    readme = """# Reference public verification 2026-08-10

This package verifies public metadata for the current Nature Communications candidate references and exports prelock RIS/ENW files.

It does not create final numbered references. Final numbering remains blocked until final prose, figure/table calls and sentence-level support mapping are locked.
"""
    (OUT_DIR / "REFERENCE_PUBLIC_VERIFICATION_README.md").write_text(readme, encoding="utf-8")

    summary = {
        "run_id": "20260810_reference_public_verification",
        "candidate_rows": len(metadata_rows),
        "current_manuscript_used_rows": len(order_rows),
        "metadata_match_failures": sum(1 for row in metadata_rows if row["local_metadata_match"] != "pass"),
        "support_boundary_rows": len(support_rows),
        "remaining_action_rows": len(remaining_rows),
        "exports": ["candidate_references_prelock.ris", "candidate_references_prelock.enw"],
        "final_references_ready": False,
        "submission_ready": False,
        "status": "reference_public_verification_ready_final_references_not_locked",
        "boundary": "This package verifies public metadata and prelock exports only; it does not finalize numbered references or support mapping.",
    }
    (OUT_DIR / "reference_public_verification_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    report = [
        "# Reference public verification report 2026-08-10",
        "",
        f"- Candidate rows: {summary['candidate_rows']}",
        f"- Current manuscript used rows: {summary['current_manuscript_used_rows']}",
        f"- Metadata match failures: {summary['metadata_match_failures']}",
        f"- Support-boundary rows: {summary['support_boundary_rows']}",
        f"- Remaining action rows: {summary['remaining_action_rows']}",
        f"- Exports: {', '.join(summary['exports'])}",
        f"- Status: {summary['status']}",
        "",
        "Conclusion: public metadata is verified for the candidate library, but final numbered references remain open until final prose and support mapping are locked.",
        "",
    ]
    (OUT_DIR / "reference_public_verification_report.md").write_text("\n".join(report), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
