#!/usr/bin/env python3
"""Build a bounded Nature Communications initial-submission text preassembly."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "natcomms_initial_submission_text_preassembly_20260810"

AUTHOR_REVIEW = (
    BENCH_ROOT
    / "reports"
    / "author_review_manuscript_package_20260810"
    / "author_review_manuscript_v0_1.md"
)
TRACK_B_ABSTRACT = (
    BENCH_ROOT
    / "reports"
    / "track_b_manuscript_branch_prelock_20260810"
    / "track_b_abstract_prelock.md"
)
TRACK_B_TITLES = (
    BENCH_ROOT
    / "reports"
    / "track_b_manuscript_branch_prelock_20260810"
    / "track_b_title_candidates.csv"
)
FIGURE_LOCK = (
    BENCH_ROOT
    / "reports"
    / "figure_source_data_lock_20260810"
    / "figure_panel_claim_lock.csv"
)
SUBMISSION_ITEMS = (
    BENCH_ROOT
    / "reports"
    / "natcomms_submission_assembly_preflight_20260810"
    / "natcomms_submission_item_preflight.csv"
)
COVER_LETTER = (
    BENCH_ROOT
    / "reports"
    / "natcomms_cover_letter_prelock_20260810"
    / "natcomms_cover_letter_prelock.md"
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def word_count(text: str) -> int:
    cleaned = re.sub(r"`[^`]+`", " ", text)
    cleaned = re.sub(r"\[[^\]]+\]", " ", cleaned)
    cleaned = re.sub(r"#+", " ", cleaned)
    cleaned = re.sub(r"https?://\S+", " ", cleaned)
    return len([token for token in cleaned.split() if token.strip()])


def section_text(text: str, heading: str, next_headings: list[str]) -> str:
    start = text.index(heading) + len(heading)
    end_candidates = [text.find(next_heading, start) for next_heading in next_headings]
    end_candidates = [idx for idx in end_candidates if idx != -1]
    end = min(end_candidates) if end_candidates else len(text)
    return text[start:end].strip()


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    manuscript = AUTHOR_REVIEW.read_text(encoding="utf-8")
    title_rows = read_csv(TRACK_B_TITLES)
    figure_rows = read_csv(FIGURE_LOCK)
    submission_rows = read_csv(SUBMISSION_ITEMS)
    cover_letter_text = COVER_LETTER.read_text(encoding="utf-8")

    recommended_title = next(
        row["title"] for row in title_rows if row["recommendation"] == "recommended_current_default"
    )
    abstract_text = TRACK_B_ABSTRACT.read_text(encoding="utf-8").replace(
        "# Track B abstract prelock", ""
    ).strip()

    sections = {
        "Introduction": section_text(manuscript, "## Introduction", ["## Results"]),
        "Results": section_text(manuscript, "## Results", ["## Discussion"]),
        "Discussion": section_text(manuscript, "## Discussion", ["## Methods"]),
        "Methods": section_text(manuscript, "## Methods", ["## Conclusion"]),
        "Conclusion": section_text(manuscript, "## Conclusion", ["## Non-final companion statements"]),
    }

    preassembly = [
        "# Nature Communications initial-submission text preassembly",
        "",
        "Boundary: this is a Track B text preassembly for author and coauthor review. It is not a final submission package. Figures are not rendered, candidate references are not converted to final numbered references, Data/Code Availability is not final, repository identifiers are absent, rights clearance is unresolved, the Reporting Summary is not final and blind external validation remains unavailable.",
        "",
        "## Article type and route",
        "",
        "Article; current route is Track B, a benchmark/resource and evidence-boundary manuscript rather than a completed blind-external-validation claim.",
        "",
        "## Title",
        "",
        recommended_title,
        "",
        "## Abstract",
        "",
        abstract_text,
        "",
    ]
    for heading in ["Introduction", "Results", "Discussion", "Methods", "Conclusion"]:
        preassembly.extend([f"## {heading}", "", sections[heading], ""])

    preassembly.extend(
        [
            "## Statements not yet final",
            "",
            "Data Availability, Code Availability, Author Contributions, Competing Interests, Reporting Summary, final figure legends, Source Data identifiers and final numbered references are intentionally withheld from final wording until the open gates are closed.",
            "",
            "## Cover letter status",
            "",
            "A bounded cover-letter prelock exists, but it still requires final author details and reconciliation with the final title, figures, repository identifiers, Reporting Summary and references.",
            "",
        ]
    )
    preassembly_text = "\n".join(preassembly)
    (OUT_DIR / "natcomms_initial_submission_text_preassembly.md").write_text(
        preassembly_text, encoding="utf-8"
    )

    section_budget_rows = [
        {"section": "Title", "words": str(word_count(recommended_title)), "natcomms_budget": "concise; recommended <=15 words", "status": "preassembled"},
        {"section": "Abstract", "words": str(word_count(abstract_text)), "natcomms_budget": "<=150 words", "status": "preassembled_track_b"},
    ]
    for section, text in sections.items():
        target = {
            "Introduction": "~700",
            "Results": "~2000",
            "Discussion": "~800",
            "Methods": "~1500",
            "Conclusion": "included in body budget",
        }[section]
        section_budget_rows.append(
            {
                "section": section,
                "words": str(word_count(text)),
                "natcomms_budget": target,
                "status": "preassembled_not_final",
            }
        )
    body_words = sum(
        int(row["words"])
        for row in section_budget_rows
        if row["section"] not in {"Title", "Abstract"}
    )
    write_csv(
        OUT_DIR / "natcomms_text_word_budget.csv",
        section_budget_rows,
        ["section", "words", "natcomms_budget", "status"],
    )

    display_rows = []
    for row in figure_rows:
        display_rows.append(
            {
                "display_item": row["figure_id"],
                "citation_label": row["citation_label"],
                "allowed_claim": row["allowed_claim"],
                "source_status": row["source_status"],
                "rendering_status": row["rendering_status"],
                "preassembly_role": "main display item planned; not final until rendered and QA-passed",
                "boundary": row["boundary"],
            }
        )
    write_csv(
        OUT_DIR / "natcomms_display_item_preassembly.csv",
        display_rows,
        [
            "display_item",
            "citation_label",
            "allowed_claim",
            "source_status",
            "rendering_status",
            "preassembly_role",
            "boundary",
        ],
    )

    gate_rows = []
    for row in submission_rows:
        gate_rows.append(
            {
                "submission_item": row["submission_item"],
                "current_status": row["current_status"],
                "assembly_status": row["assembly_status"],
                "blocking_condition": row["blocking_condition"],
                "text_preassembly_effect": "included_as_preassembled_text"
                if row["assembly_status"] == "preassemblable"
                else "kept_as_open_gate",
            }
        )
    write_csv(
        OUT_DIR / "natcomms_text_open_gate_matrix.csv",
        gate_rows,
        [
            "submission_item",
            "current_status",
            "assembly_status",
            "blocking_condition",
            "text_preassembly_effect",
        ],
    )

    companion_rows = [
        {
            "companion_item": "Data Availability",
            "current_action": "Use prelock variants only after DOI/licence/rights are known.",
            "final_status": "not_final",
        },
        {
            "companion_item": "Code Availability",
            "current_action": "Wait for public repository URL, release tag, licence and archive DOI.",
            "final_status": "not_final",
        },
        {
            "companion_item": "Reporting Summary",
            "current_action": "Keep prelock; finalize after Methods, figures, source data and validation status are locked.",
            "final_status": "not_final",
        },
        {
            "companion_item": "References",
            "current_action": "Keep candidate [P#] support locks; convert only after final figure/table calls and prose order are stable.",
            "final_status": "not_final",
        },
        {
            "companion_item": "Cover letter",
            "current_action": "Use prelock text as editor-pitch base; insert final author details later.",
            "final_status": "prelocked_not_final",
        },
    ]
    write_csv(
        OUT_DIR / "natcomms_companion_statement_queue.csv",
        companion_rows,
        ["companion_item", "current_action", "final_status"],
    )

    forbidden_terms = [
        "has completed blind external validation",
        "reports completed blind external validation",
        "repository doi has been created",
        "code doi has been created",
        "final reporting summary is complete",
        "submission-ready package",
        "deployment robustness",
        "demonstrates universal leakage",
    ]
    lower_text = preassembly_text.lower()
    qa_rows = [
        {
            "check": "Track B title selected",
            "result": "PASS" if recommended_title in preassembly_text else "FAIL",
            "detail": recommended_title,
        },
        {
            "check": "Abstract length",
            "result": "PASS" if word_count(abstract_text) <= 150 else "FAIL",
            "detail": f"{word_count(abstract_text)} words; Nature Communications Article limit is 150.",
        },
        {
            "check": "Main body budget",
            "result": "PASS" if body_words <= 5000 else "FAIL",
            "detail": f"{body_words} words excluding title and abstract; Methods included in the Nature Communications body budget.",
        },
        {
            "check": "Display item cap",
            "result": "PASS" if len(display_rows) <= 10 else "FAIL",
            "detail": f"{len(display_rows)} planned display items; cap is 10.",
        },
        {
            "check": "Open-gate boundary present",
            "result": "PASS" if "not a final submission package" in preassembly_text else "FAIL",
            "detail": "Boundary paragraph states unresolved gates.",
        },
        {
            "check": "Forbidden finalization claims absent",
            "result": "PASS" if not any(term in lower_text for term in forbidden_terms) else "FAIL",
            "detail": "Scans for finalization/deployment overclaims.",
        },
        {
            "check": "Cover letter linked",
            "result": "PASS" if "Dear Editors" in cover_letter_text else "FAIL",
            "detail": "Cover-letter prelock exists and is referenced, but not promoted to final.",
        },
    ]
    write_csv(
        OUT_DIR / "natcomms_text_preassembly_qa.csv",
        qa_rows,
        ["check", "result", "detail"],
    )

    readme = [
        "# Nat Comms initial-submission text preassembly",
        "",
        "This package assembles the current Track B title, abstract, manuscript body, display-item plan, companion-statement queue and open-gate matrix into one author-reviewable text package.",
        "",
        "It does not create a final submission package. Figures, repository identifiers, rights, Reporting Summary, final references and blind external validation remain open.",
        "",
        "Primary file: `natcomms_initial_submission_text_preassembly.md`.",
        "",
    ]
    (OUT_DIR / "NATCOMMS_TEXT_PREASSEMBLY_README.md").write_text(
        "\n".join(readme), encoding="utf-8"
    )

    report = [
        "# Nat Comms initial-submission text preassembly report",
        "",
        f"- Body words excluding title/abstract: {body_words}",
        f"- Abstract words: {word_count(abstract_text)}",
        f"- Planned display items: {len(display_rows)}",
        f"- Open submission items tracked: {len(gate_rows)}",
        f"- Companion statement rows: {len(companion_rows)}",
        f"- QA failures: {sum(1 for row in qa_rows if row['result'] == 'FAIL')}",
        "- Status: natcomms_text_preassembly_ready_not_submission_final",
        "",
        "Boundary: this package improves text assembly only; it does not render figures, create DOI identifiers, clear rights, finalize the Reporting Summary, replace references or complete blind external validation.",
        "",
    ]
    (OUT_DIR / "natcomms_text_preassembly_report.md").write_text(
        "\n".join(report), encoding="utf-8"
    )

    summary = {
        "run_id": "20260810_natcomms_initial_submission_text_preassembly",
        "body_words_excluding_title_abstract": body_words,
        "abstract_words": word_count(abstract_text),
        "planned_display_items": len(display_rows),
        "submission_items_tracked": len(gate_rows),
        "companion_statement_rows": len(companion_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] != "FAIL" for row in qa_rows),
        "current_applicable_branch": "TRACK-B",
        "submission_ready": False,
        "status": "natcomms_text_preassembly_ready_not_submission_final",
        "boundary": "Text is preassembled for author review only; final submission remains blocked by figures, repository identifiers, rights, Reporting Summary, references and blind external validation.",
    }
    (OUT_DIR / "natcomms_text_preassembly_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if summary["qa_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
