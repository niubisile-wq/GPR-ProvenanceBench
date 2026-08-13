#!/usr/bin/env python3
"""Build Nature Communications administrative declarations prelock package."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "natcomms_admin_declarations_prelock_20260810"

TRACK_B_TITLE = (
    BENCH_ROOT
    / "reports"
    / "track_b_manuscript_branch_prelock_20260810"
    / "track_b_manuscript_branch_prelock.md"
)
COVER_LETTER_CHECKLIST = (
    BENCH_ROOT
    / "reports"
    / "natcomms_cover_letter_prelock_20260810"
    / "cover_letter_finalization_checklist.csv"
)
TEXT_PREASSEMBLY_SUMMARY = (
    BENCH_ROOT
    / "reports"
    / "natcomms_initial_submission_text_preassembly_20260810"
    / "natcomms_text_preassembly_summary.json"
)
SI_SUMMARY = (
    BENCH_ROOT
    / "reports"
    / "natcomms_supplementary_info_preassembly_20260810"
    / "supplementary_info_preassembly_summary.json"
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def extract_recommended_title(text: str) -> str:
    marker = "## Recommended title"
    start = text.index(marker) + len(marker)
    end = text.index("## Abstract", start)
    return text[start:end].strip()


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    title = extract_recommended_title(TRACK_B_TITLE.read_text(encoding="utf-8"))
    cover_rows = read_csv(COVER_LETTER_CHECKLIST)
    text_summary = json.loads(TEXT_PREASSEMBLY_SUMMARY.read_text(encoding="utf-8"))
    si_summary = json.loads(SI_SUMMARY.read_text(encoding="utf-8"))

    official_source_rows = [
        {
            "source_id": "NCOMMS-HOW-SUBMIT",
            "source": "Nature Communications: How to submit",
            "checked_date": "2026-08-10",
            "relevant_requirement": "Cover letter should include corresponding-author affiliation/contact information, work importance, fit for diverse readership, reviewer suggestions/exclusions, prior editor discussions; manuscript text order includes title page, references, acknowledgements, Author Contributions, Competing Interests, figure legends and tables.",
            "url": "https://www.nature.com/ncomms/submit/how-to-submit",
        },
        {
            "source_id": "NCOMMS-AUTHORSHIP",
            "source": "Nature Communications: Authorship",
            "checked_date": "2026-08-10",
            "relevant_requirement": "All authors must approve submission; corresponding author manages communication and competing-interest statement; author contribution statements are required.",
            "url": "https://www.nature.com/ncomms/editorial-policies/authorship",
        },
        {
            "source_id": "SPRINGER-POLICIES",
            "source": "Springer Nature journal policies",
            "checked_date": "2026-08-10",
            "relevant_requirement": "Disclosures should cover funding, financial/non-financial interests, ethics/consent where applicable, data/code availability and author contributions.",
            "url": "https://link.springer.com/brands/springer/journal-policies",
        },
    ]
    write_csv(
        OUT_DIR / "official_submission_admin_source_check.csv",
        official_source_rows,
        ["source_id", "source", "checked_date", "relevant_requirement", "url"],
    )

    title_page_rows = [
        {
            "field": "Manuscript title",
            "current_value": title,
            "status": "track_b_prelocked_not_final",
            "required_before_submission": "yes",
        },
        {
            "field": "Author names and order",
            "current_value": "[AUTHOR LIST TO BE INSERTED]",
            "status": "missing_author_input",
            "required_before_submission": "yes",
        },
        {
            "field": "Affiliations with full institutional addresses",
            "current_value": "[AFFILIATIONS TO BE INSERTED]",
            "status": "missing_author_input",
            "required_before_submission": "yes",
        },
        {
            "field": "Corresponding author email and asterisk marker",
            "current_value": "[CORRESPONDING AUTHOR EMAIL TO BE INSERTED]",
            "status": "missing_author_input",
            "required_before_submission": "yes",
        },
        {
            "field": "ORCID identifiers",
            "current_value": "[ORCID IDS TO BE INSERTED IF AVAILABLE/REQUIRED BY PORTAL]",
            "status": "missing_author_input",
            "required_before_submission": "portal_check",
        },
        {
            "field": "Prior discussion with Nature Communications editor",
            "current_value": "[NONE/DETAILS TO BE CONFIRMED]",
            "status": "missing_author_input",
            "required_before_submission": "yes",
        },
    ]
    write_csv(
        OUT_DIR / "title_page_field_prelock.csv",
        title_page_rows,
        ["field", "current_value", "status", "required_before_submission"],
    )

    title_page_md = [
        "# Title page prelock",
        "",
        f"Title: {title}",
        "",
        "Authors: [AUTHOR LIST TO BE INSERTED]",
        "",
        "Affiliations: [FULL INSTITUTIONAL ADDRESSES TO BE INSERTED]",
        "",
        "Corresponding author: [NAME, EMAIL, AFFILIATION TO BE INSERTED]",
        "",
        "ORCID iDs: [TO BE INSERTED IF AVAILABLE/REQUIRED BY PORTAL]",
        "",
        "Prior editor discussion: [NONE OR DETAILS TO BE CONFIRMED]",
        "",
        "Boundary: this title page is a field prelock only. It does not infer or invent author names, affiliations, order, ORCID iDs or corresponding-author details.",
        "",
    ]
    (OUT_DIR / "title_page_prelock.md").write_text("\n".join(title_page_md), encoding="utf-8")

    contribution_rows = [
        {
            "contribution_area": "Conceptualization and study design",
            "required_author_entry": "[AUTHOR INITIALS]",
            "current_status": "missing_author_input",
            "notes": "Map only authors who substantially contributed to project design.",
        },
        {
            "contribution_area": "Data acquisition or asset restoration",
            "required_author_entry": "[AUTHOR INITIALS]",
            "current_status": "missing_author_input",
            "notes": "Separate public/local asset handling from third-party permission work.",
        },
        {
            "contribution_area": "Data curation and manifest generation",
            "required_author_entry": "[AUTHOR INITIALS]",
            "current_status": "missing_author_input",
            "notes": "Include unified manifests, source-data maps and release-boundary curation.",
        },
        {
            "contribution_area": "Software and reproducibility scripts",
            "required_author_entry": "[AUTHOR INITIALS]",
            "current_status": "missing_author_input",
            "notes": "Include benchmark scripts, checks, validators and package builders.",
        },
        {
            "contribution_area": "Formal analysis",
            "required_author_entry": "[AUTHOR INITIALS]",
            "current_status": "missing_author_input",
            "notes": "Include five-model matrix, 4TU stress tests and synthesis.",
        },
        {
            "contribution_area": "Writing original draft",
            "required_author_entry": "[AUTHOR INITIALS]",
            "current_status": "missing_author_input",
            "notes": "Do not list AI/tooling as author; acknowledge assistance if required by policy.",
        },
        {
            "contribution_area": "Writing review and editing",
            "required_author_entry": "[AUTHOR INITIALS]",
            "current_status": "missing_author_input",
            "notes": "All authors should approve the submitted version.",
        },
        {
            "contribution_area": "Supervision and project administration",
            "required_author_entry": "[AUTHOR INITIALS]",
            "current_status": "missing_author_input",
            "notes": "Include advisor/senior contributors only if authorship criteria are met.",
        },
    ]
    write_csv(
        OUT_DIR / "author_contribution_intake_matrix.csv",
        contribution_rows,
        ["contribution_area", "required_author_entry", "current_status", "notes"],
    )

    declarations_rows = [
        {
            "declaration": "Author Contributions",
            "current_text": "[AUTHOR CONTRIBUTIONS TO BE COMPLETED FROM INTAKE MATRIX]",
            "status": "missing_author_input",
            "finalization_trigger": "Every listed author and contribution role confirmed.",
        },
        {
            "declaration": "Competing Interests",
            "current_text": "[COMPETING INTERESTS STATEMENT TO BE CONFIRMED BY CORRESPONDING AUTHOR]",
            "status": "missing_author_input",
            "finalization_trigger": "Financial and non-financial interests checked for all authors.",
        },
        {
            "declaration": "Acknowledgements",
            "current_text": "[FUNDING, NON-AUTHOR CONTRIBUTIONS AND DATA-PROVIDER ACKNOWLEDGEMENTS TO BE INSERTED]",
            "status": "missing_author_input",
            "finalization_trigger": "Funding, facilities, contributors and data-provider permissions confirmed.",
        },
        {
            "declaration": "Ethics/consent statement",
            "current_text": "Current GPR benchmark package does not include human participants or animal research based on available evidence; confirm no ethics approval is required.",
            "status": "needs_author_confirmation",
            "finalization_trigger": "Author confirms study scope contains no human/animal subject data.",
        },
        {
            "declaration": "Data Availability",
            "current_text": "Use availability prelock only; DOI/accession, rights and final Source Data remain open.",
            "status": "not_final",
            "finalization_trigger": "Repository identifiers, licences, rights and final source-data mapping complete.",
        },
        {
            "declaration": "Code Availability",
            "current_text": "Use availability prelock only; code repository URL, release tag, licence and code DOI remain open.",
            "status": "not_final",
            "finalization_trigger": "Public code release and archive DOI complete.",
        },
    ]
    write_csv(
        OUT_DIR / "admin_declarations_prelock.csv",
        declarations_rows,
        ["declaration", "current_text", "status", "finalization_trigger"],
    )

    declarations_md = [
        "# Administrative declarations prelock",
        "",
        "## Author Contributions",
        "",
        "[AUTHOR CONTRIBUTIONS TO BE COMPLETED FROM `author_contribution_intake_matrix.csv`.]",
        "",
        "## Competing Interests",
        "",
        "[COMPETING INTERESTS STATEMENT TO BE CONFIRMED BY CORRESPONDING AUTHOR ON BEHALF OF ALL AUTHORS.]",
        "",
        "## Acknowledgements",
        "",
        "[FUNDING, NON-AUTHOR CONTRIBUTIONS, FACILITY SUPPORT AND DATA-PROVIDER ACKNOWLEDGEMENTS TO BE INSERTED.]",
        "",
        "## Ethics statement",
        "",
        "Current evidence indicates a non-human, non-animal GPR benchmark and evaluation study. The authors must confirm whether any institutional ethics, consent or data-governance statement is required.",
        "",
        "## Data and Code Availability linkage",
        "",
        "Use the existing availability prelock package only after repository identifiers, licences, rights and final Source Data are resolved.",
        "",
        "Boundary: this declarations file is not final because author identities, funding, interests, acknowledgements, repository identifiers and rights are unresolved.",
        "",
    ]
    (OUT_DIR / "admin_declarations_prelock.md").write_text(
        "\n".join(declarations_md), encoding="utf-8"
    )

    cover_admin_rows = []
    for row in cover_rows:
        cover_admin_rows.append(
            {
                "cover_letter_field": row["field"],
                "current_status": row["current_status"],
                "admin_prelock_action": "mirrored_in_admin_package"
                if row["field"] in {"Corresponding author name and affiliation", "Final title"}
                else "tracked_as_submission_gate",
                "required_before_submission": row["required_before_submission"],
            }
        )
    write_csv(
        OUT_DIR / "cover_letter_admin_crosscheck.csv",
        cover_admin_rows,
        [
            "cover_letter_field",
            "current_status",
            "admin_prelock_action",
            "required_before_submission",
        ],
    )

    reviewer_rows = [
        {
            "field": "Suggested reviewer 1",
            "required_information": "Name, institution, institutional email, expertise, independence/no conflict",
            "current_status": "missing_author_input",
        },
        {
            "field": "Suggested reviewer 2",
            "required_information": "Name, institution, institutional email, expertise, independence/no conflict",
            "current_status": "missing_author_input",
        },
        {
            "field": "Suggested reviewer 3",
            "required_information": "Name, institution, institutional email, expertise, independence/no conflict",
            "current_status": "missing_author_input",
        },
        {
            "field": "Excluded reviewer(s)",
            "required_information": "Name, institution, reason for exclusion if requested",
            "current_status": "optional_missing_author_input",
        },
    ]
    write_csv(
        OUT_DIR / "reviewer_suggestion_intake.csv",
        reviewer_rows,
        ["field", "required_information", "current_status"],
    )

    peer_review_rows = [
        {
            "decision_item": "Transparent peer review",
            "current_default": "[PORTAL DEFAULT/OPTION TO BE CHECKED AT SUBMISSION]",
            "recommended_action": "Make a deliberate author decision rather than leaving this to habit.",
            "status": "needs_author_confirmation",
        },
        {
            "decision_item": "Preprint deposition or prior public posting",
            "current_default": "[UNKNOWN]",
            "recommended_action": "Confirm whether any preprint, thesis chapter, code repository or public plan contains overlapping text/results.",
            "status": "needs_author_confirmation",
        },
        {
            "decision_item": "Previous editor discussion",
            "current_default": "[UNKNOWN]",
            "recommended_action": "State none or provide details in the cover letter.",
            "status": "needs_author_confirmation",
        },
    ]
    write_csv(
        OUT_DIR / "editorial_policy_decision_prelock.csv",
        peer_review_rows,
        ["decision_item", "current_default", "recommended_action", "status"],
    )

    qa_rows = [
        {
            "check": "Official admin sources recorded",
            "result": "PASS" if len(official_source_rows) == 3 else "FAIL",
            "detail": f"{len(official_source_rows)} official/publisher source rows.",
        },
        {
            "check": "Title page does not invent authors",
            "result": "PASS"
            if all(
                (
                    row["field"] not in {"Author names and order", "Affiliations with full institutional addresses"}
                    or row["current_value"].startswith("[")
                )
                for row in title_page_rows
            )
            else "FAIL",
            "detail": "Author and affiliation fields remain placeholders.",
        },
        {
            "check": "Author contribution intake exists",
            "result": "PASS" if len(contribution_rows) >= 6 else "FAIL",
            "detail": f"{len(contribution_rows)} contribution rows.",
        },
        {
            "check": "Declarations remain non-final",
            "result": "PASS" if all(row["status"] != "final" for row in declarations_rows) else "FAIL",
            "detail": "No declaration is marked final.",
        },
        {
            "check": "Reviewer suggestion intake exists",
            "result": "PASS" if len(reviewer_rows) >= 3 else "FAIL",
            "detail": f"{len(reviewer_rows)} reviewer/exclusion rows.",
        },
        {
            "check": "Scientific gates not upgraded",
            "result": "PASS" if not text_summary["submission_ready"] and not si_summary["submission_ready"] else "FAIL",
            "detail": "Text and SI preassemblies remain submission_ready=false.",
        },
    ]
    write_csv(
        OUT_DIR / "admin_declarations_prelock_qa.csv",
        qa_rows,
        ["check", "result", "detail"],
    )

    readme = [
        "# Nat Comms administrative declarations prelock",
        "",
        "This package turns Nature Communications administrative requirements into an author-facing intake and prelock set.",
        "",
        "It does not invent authorship, affiliations, ORCID IDs, competing interests, funding, reviewer suggestions or ethics statements. It does not close figures, DOI/rights, Reporting Summary, references or blind external validation.",
        "",
    ]
    (OUT_DIR / "NATCOMMS_ADMIN_DECLARATIONS_PRELOCK_README.md").write_text(
        "\n".join(readme), encoding="utf-8"
    )

    report = [
        "# Nat Comms administrative declarations prelock report",
        "",
        f"- Title-page fields: {len(title_page_rows)}",
        f"- Author-contribution intake rows: {len(contribution_rows)}",
        f"- Declaration rows: {len(declarations_rows)}",
        f"- Cover-letter crosscheck rows: {len(cover_admin_rows)}",
        f"- Reviewer-suggestion rows: {len(reviewer_rows)}",
        f"- Editorial-policy decision rows: {len(peer_review_rows)}",
        f"- QA failures: {sum(1 for row in qa_rows if row['result'] == 'FAIL')}",
        "- Status: natcomms_admin_declarations_prelock_ready_not_final",
        "",
        "Boundary: this package prepares administrative statements only; it does not finalize author details or close scientific submission gates.",
        "",
    ]
    (OUT_DIR / "admin_declarations_prelock_report.md").write_text(
        "\n".join(report), encoding="utf-8"
    )

    summary = {
        "run_id": "20260810_natcomms_admin_declarations_prelock",
        "official_source_rows": len(official_source_rows),
        "title_page_fields": len(title_page_rows),
        "author_contribution_rows": len(contribution_rows),
        "declaration_rows": len(declarations_rows),
        "cover_letter_crosscheck_rows": len(cover_admin_rows),
        "reviewer_suggestion_rows": len(reviewer_rows),
        "editorial_policy_decision_rows": len(peer_review_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] != "FAIL" for row in qa_rows),
        "admin_declarations_final": False,
        "submission_ready": False,
        "status": "natcomms_admin_declarations_prelock_ready_not_final",
        "boundary": "Administrative declarations are prelocked for author intake only; author details, competing interests, acknowledgements, DOI/rights, Reporting Summary, references, figures and blind external validation remain open.",
    }
    (OUT_DIR / "admin_declarations_prelock_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if summary["qa_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
