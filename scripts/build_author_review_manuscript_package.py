#!/usr/bin/env python3
"""Assemble author-review manuscript package v0.1 from conservative drafts."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "author_review_manuscript_package_20260810"
CONSERVATIVE = BENCH_ROOT / "reports" / "conservative_manuscript_draft_20260810" / "conservative_manuscript_draft_v0_1.md"
METHODS = BENCH_ROOT / "reports" / "conservative_methods_draft_20260810" / "methods_draft_v0_1.md"
INTRO = BENCH_ROOT / "reports" / "narrative_cited_drafts_20260810" / "introduction_draft_v1_cited.md"
CONCLUSION = BENCH_ROOT / "reports" / "narrative_cited_drafts_20260810" / "conclusion_draft_v1_cited.md"
CLAIM_AUDIT = BENCH_ROOT / "reports" / "manuscript_claim_readiness_audit_20260810" / "manuscript_claim_readiness_summary.json"
GAP_SUMMARY = BENCH_ROOT / "reports" / "submission_gap_closure_matrix_20260810" / "submission_gap_closure_summary.json"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def extract_between(text: str, start: str, end: str | None = None) -> str:
    start_idx = text.index(start) + len(start)
    if end is None:
        return text[start_idx:].strip()
    end_idx = text.index(end, start_idx)
    return text[start_idx:end_idx].strip()


def word_count(text: str) -> int:
    cleaned = re.sub(r"`[^`]+`", " ", text)
    cleaned = re.sub(r"\[[^\]]+\]", " ", cleaned)
    cleaned = re.sub(r"#+", " ", cleaned)
    return len([token for token in cleaned.split() if token.strip()])


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    conservative_text = CONSERVATIVE.read_text(encoding="utf-8")
    methods_text = METHODS.read_text(encoding="utf-8")
    intro_text = INTRO.read_text(encoding="utf-8").replace("# Introduction Draft v1 cited", "").strip()
    conclusion_text = CONCLUSION.read_text(encoding="utf-8").replace("# Conclusion Draft v1 cited", "").strip()

    title = extract_between(conservative_text, "## Recommended title", "## Abstract draft").strip()
    abstract = extract_between(conservative_text, "## Abstract draft", "# Results draft v0.1").strip()
    results = extract_between(conservative_text, "# Results draft v0.1", "# Discussion draft v0.1").strip()
    discussion = extract_between(conservative_text, "# Discussion draft v0.1", "## Assumptions and missing inputs").strip()
    methods_body = methods_text.replace("# Methods draft v0.1", "").strip()

    full_manuscript = [
        "# Author-review manuscript package v0.1 2026-08-10",
        "",
        "Boundary: this is an author-review manuscript draft assembled from audited local evidence. It is not final submission text. Formal figures, blind external validation, repository identifiers, rights clearance and final Reporting Summary remain open.",
        "",
        "## Title",
        "",
        title,
        "",
        "## Abstract",
        "",
        abstract,
        "",
        "## Introduction",
        "",
        intro_text,
        "",
        "## Results",
        "",
        results,
        "",
        "## Discussion",
        "",
        discussion,
        "",
        "## Methods",
        "",
        methods_body,
        "",
        "## Conclusion",
        "",
        conclusion_text,
        "",
        "## Non-final companion statements",
        "",
        "Data Availability and Code Availability are captured in the repository metadata prelock drafts for this checkpoint, but they remain unfinalized until repository identifiers, rights review, figure-source locking and licence decisions are complete. Reporting Summary, figure legends, source-data deposit identifiers and final reference numbering are likewise not finalized in this draft.",
        "",
    ]
    full_text = "\n".join(full_manuscript)
    (OUT_DIR / "author_review_manuscript_v0_1.md").write_text(full_text, encoding="utf-8")

    section_rows = [
        {
            "section": "Title",
            "source": str(CONSERVATIVE.relative_to(BENCH_ROOT)),
            "word_count": str(word_count(title)),
            "status": "draft_ready_bounded",
        },
        {
            "section": "Abstract",
            "source": str(CONSERVATIVE.relative_to(BENCH_ROOT)),
            "word_count": str(word_count(abstract)),
            "status": "draft_ready_bounded",
        },
        {
            "section": "Introduction",
            "source": str(INTRO.relative_to(BENCH_ROOT)),
            "word_count": str(word_count(intro_text)),
            "status": "citation_markers_not_final",
        },
        {
            "section": "Results",
            "source": str(CONSERVATIVE.relative_to(BENCH_ROOT)),
            "word_count": str(word_count(results)),
            "status": "draft_ready_bounded",
        },
        {
            "section": "Discussion",
            "source": str(CONSERVATIVE.relative_to(BENCH_ROOT)),
            "word_count": str(word_count(discussion)),
            "status": "draft_ready_bounded",
        },
        {
            "section": "Methods",
            "source": str(METHODS.relative_to(BENCH_ROOT)),
            "word_count": str(word_count(methods_body)),
            "status": "draft_ready_bounded",
        },
        {
            "section": "Conclusion",
            "source": str(CONCLUSION.relative_to(BENCH_ROOT)),
            "word_count": str(word_count(conclusion_text)),
            "status": "citation_markers_not_final",
        },
    ]
    write_csv(OUT_DIR / "author_review_section_word_budget.csv", section_rows, ["section", "source", "word_count", "status"])

    total_words = sum(int(row["word_count"]) for row in section_rows if row["section"] not in {"Title", "Abstract"})
    qa_rows = [
        {
            "check": "Nat Comms abstract length",
            "result": "PASS" if word_count(abstract) <= 150 else "FAIL",
            "detail": f"{word_count(abstract)} words; limit 150.",
        },
        {
            "check": "Nat Comms main body budget",
            "result": "PASS" if total_words <= 5000 else "FAIL",
            "detail": f"{total_words} words excluding title/abstract; approximate Article limit is 5000 including Methods.",
        },
        {
            "check": "Blind external validation overclaim",
            "result": "PASS" if "not yet a completed blind external validation claim" in full_text and "not completed" in full_text else "FAIL",
            "detail": "Draft explicitly marks blind external validation as open/not completed.",
        },
        {
            "check": "Repository/Reporting Summary non-final",
            "result": "PASS" if "not finalized" in full_text and "repository identifiers" in full_text else "FAIL",
            "detail": "Draft does not claim final repository identifiers or Reporting Summary.",
        },
        {
            "check": "Citation markers not final",
            "result": "WARN" if "[P" in full_text else "PASS",
            "detail": "Candidate citation markers remain and require final reference conversion.",
        },
    ]
    write_csv(OUT_DIR / "author_review_manuscript_qa.csv", qa_rows, ["check", "result", "detail"])

    open_gate_rows = [
        {
            "gate": "Formal figures",
            "draft_impact": "Figure calls and legends remain non-final.",
            "required_before_submission": "Rendered Figure 1-Figure 6 or final reduced figure set with visual QA.",
        },
        {
            "gate": "Blind external validation",
            "draft_impact": "Generalization wording remains bounded.",
            "required_before_submission": "Real held-label asset, strict SHA manifest, frozen predictions and one locked evaluation.",
        },
        {
            "gate": "Repository identifiers",
            "draft_impact": "Data/Code Availability cannot be final.",
            "required_before_submission": "Data repository DOI/accession and code release DOI.",
        },
        {
            "gate": "Rights clearance",
            "draft_impact": "Public release and source-data scope remain provisional.",
            "required_before_submission": "Licence decisions and third-party redistribution boundaries.",
        },
        {
            "gate": "Reporting Summary",
            "draft_impact": "Reporting Summary remains draft-only.",
            "required_before_submission": "Final answers linked to frozen Methods, figures, data/code and validation status.",
        },
        {
            "gate": "Final references",
            "draft_impact": "Candidate [P#] markers remain.",
            "required_before_submission": "Manual verification and Nature-style numbered references.",
        },
    ]
    write_csv(OUT_DIR / "author_review_open_gate_impact.csv", open_gate_rows, ["gate", "draft_impact", "required_before_submission"])

    claim_summary = json.loads(CLAIM_AUDIT.read_text(encoding="utf-8"))
    gap_summary = json.loads(GAP_SUMMARY.read_text(encoding="utf-8"))
    summary = {
        "run_id": "20260810_author_review_manuscript_package_v0_1",
        "sections_assembled": len(section_rows),
        "body_words_excluding_title_abstract": total_words,
        "abstract_words": word_count(abstract),
        "nat_comms_body_limit_reference": 5000,
        "qa_rows": len(qa_rows),
        "qa_failures": sum(1 for row in qa_rows if row["result"] == "FAIL"),
        "qa_warnings": sum(1 for row in qa_rows if row["result"] == "WARN"),
        "claim_audit_status": claim_summary["status"],
        "gap_matrix_status": gap_summary["status"],
        "submission_ready": False,
        "status": "author_review_manuscript_ready_not_submission_final",
        "boundary": "Assembled manuscript is for author review only; final submission remains blocked by figures, external validation, DOI, rights, Reporting Summary and references.",
    }
    (OUT_DIR / "author_review_manuscript_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    report = [
        "# Author-review manuscript package report 2026-08-10",
        "",
        f"- Sections assembled: {summary['sections_assembled']}",
        f"- Body words excluding title/abstract: {summary['body_words_excluding_title_abstract']}",
        f"- Abstract words: {summary['abstract_words']}",
        f"- QA failures: {summary['qa_failures']}",
        f"- QA warnings: {summary['qa_warnings']}",
        f"- Status: {summary['status']}",
        "",
        "Conclusion: a coherent author-review manuscript draft now exists, but it is not submission-final.",
        "",
    ]
    (OUT_DIR / "author_review_manuscript_report.md").write_text("\n".join(report), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
