#!/usr/bin/env python3
"""Build a Nature Communications cover-letter prelock package."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "natcomms_cover_letter_prelock_20260810"
TRACK_B_SUMMARY = BENCH_ROOT / "reports" / "track_b_manuscript_branch_prelock_20260810" / "track_b_manuscript_branch_prelock_summary.json"
ASSEMBLY_SUMMARY = BENCH_ROOT / "reports" / "natcomms_submission_assembly_preflight_20260810" / "natcomms_submission_assembly_preflight_summary.json"
FORBIDDEN = BENCH_ROOT / "reports" / "track_b_manuscript_branch_prelock_20260810" / "track_b_forbidden_upgrade_ledger.csv"


COVER_LETTER = """Dear Editors,

We submit our manuscript, "Environment transfer exposes fragile generalization in ground-penetrating-radar recognition", for consideration as an Article in Nature Communications.

The manuscript introduces GPR-ProvenanceBench, an auditable workflow for evaluating how acquisition, environment and processing provenance affect ground-penetrating radar (GPR) recognition rather than relying on random-split performance alone.

At the current checkpoint, the strongest evidence is a Res-SAM real-world/synthetic environment-transfer drop across five model families: real-to-synthetic transfer showed directional and material balanced-accuracy drops in all five families, and synthetic-to-real transfer showed directional and material drops in four of five families.

We believe the work will interest readers in geophysics, infrastructure sensing and machine-learning evaluation because it provides a reproducible way to separate benchmark trust, provenance sensitivity and unresolved validation gates in a field where deployment claims can otherwise outpace available evidence.

This submission route is deliberately bounded: blind external validation, final repository identifiers, final figure rendering, the Reporting Summary and final numbered references remain to be locked before any submission-final package is claimed.

Sincerely,

[Corresponding author name and affiliation to be inserted]
"""


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?", text))


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    track_b = json.loads(TRACK_B_SUMMARY.read_text(encoding="utf-8"))
    assembly = json.loads(ASSEMBLY_SUMMARY.read_text(encoding="utf-8"))
    forbidden_rows = read_csv(FORBIDDEN)

    (OUT_DIR / "natcomms_cover_letter_prelock.md").write_text("# Nat Comms cover letter prelock\n\n" + COVER_LETTER, encoding="utf-8")

    pitch_rows = [
        {
            "pitch_job": "what_the_finding_is",
            "sentence": "GPR-ProvenanceBench shows that source and environment structure can substantially reshape apparent GPR recognition generalization, with the strongest current evidence from Res-SAM real-world/synthetic transfer across five model families.",
            "status": "allowed_track_b",
            "boundary": "Do not call this completed blind external validation.",
        },
        {
            "pitch_job": "what_is_new",
            "sentence": "The work links dated asset manifests, grouped split logic, environment-transfer tests, model-family comparisons, counterfactual 4TU stress tests and explicit validation gates in one auditable workflow.",
            "status": "allowed_track_b",
            "boundary": "Do not claim repository DOI or final public release.",
        },
        {
            "pitch_job": "why_it_matters",
            "sentence": "The paper should interest geophysics, infrastructure sensing and machine-learning evaluation readers because it separates benchmark trust from dataset-source or processing-chain shortcuts.",
            "status": "allowed_track_b",
            "boundary": "Do not claim deployment robustness across all GPR settings.",
        },
    ]
    write_csv(OUT_DIR / "editor_pitch_sentence_map.csv", pitch_rows, ["pitch_job", "sentence", "status", "boundary"])

    finalization_rows = [
        {"field": "Corresponding author name and affiliation", "current_status": "placeholder", "required_before_submission": "yes"},
        {"field": "Final title", "current_status": "Track B prelock", "required_before_submission": "yes"},
        {"field": "Final manuscript branch", "current_status": track_b["current_applicable_branch"], "required_before_submission": "yes"},
        {"field": "Final figure status", "current_status": "not rendered", "required_before_submission": "yes"},
        {"field": "Repository/DOI statement", "current_status": "not final", "required_before_submission": "yes"},
        {"field": "Reporting Summary", "current_status": "not final", "required_before_submission": "yes"},
        {"field": "Final references", "current_status": "not final", "required_before_submission": "yes"},
    ]
    write_csv(OUT_DIR / "cover_letter_finalization_checklist.csv", finalization_rows, ["field", "current_status", "required_before_submission"])

    no_go_rows = [
        {
            "forbidden_statement": row["forbidden_statement"],
            "why_forbidden": row["reason"],
            "cover_letter_replacement": row["track_b_replacement"],
        }
        for row in forbidden_rows
    ]
    write_csv(OUT_DIR / "cover_letter_forbidden_language.csv", no_go_rows, ["forbidden_statement", "why_forbidden", "cover_letter_replacement"])

    qa_rows = [
        {
            "qa_check": "current_branch_track_b",
            "status": "pass" if track_b["current_applicable_branch"] == "TRACK-B" else "fail",
            "evidence": track_b["current_applicable_branch"],
        },
        {
            "qa_check": "submission_not_ready_preserved",
            "status": "pass" if not assembly["submission_ready"] else "fail",
            "evidence": "assembly summary submission_ready=false",
        },
        {
            "qa_check": "no_completed_blind_validation_claim",
            "status": "pass" if "completed blind external validation" not in COVER_LETTER.lower() else "fail",
            "evidence": "cover letter states bounded route",
        },
        {
            "qa_check": "placeholder_corresponding_author_visible",
            "status": "pass" if "[Corresponding author" in COVER_LETTER else "fail",
            "evidence": "placeholder retained for author completion",
        },
    ]
    write_csv(OUT_DIR / "natcomms_cover_letter_prelock_qa.csv", qa_rows, ["qa_check", "status", "evidence"])

    readme = """# Nat Comms cover letter prelock 2026-08-10

This package drafts a bounded Track B cover letter and maps each editor-facing pitch sentence to its evidence boundary.

It is not final because author identity, final figures, repository identifiers, Reporting Summary and references remain open.
"""
    (OUT_DIR / "NATCOMMS_COVER_LETTER_PRELOCK_README.md").write_text(readme, encoding="utf-8")

    qa_pass = all(row["status"] == "pass" for row in qa_rows)
    summary = {
        "run_id": "20260810_natcomms_cover_letter_prelock",
        "cover_letter_words": word_count(COVER_LETTER),
        "pitch_rows": len(pitch_rows),
        "finalization_rows": len(finalization_rows),
        "forbidden_language_rows": len(no_go_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "current_applicable_branch": track_b["current_applicable_branch"],
        "cover_letter_final": False,
        "submission_ready": False,
        "status": "natcomms_cover_letter_prelock_ready_not_final",
        "boundary": "This package drafts a bounded cover letter only; it does not finalize author details, figures, DOI, rights, Reporting Summary, references or submission.",
    }
    (OUT_DIR / "natcomms_cover_letter_prelock_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    report = [
        "# Nat Comms cover letter prelock report 2026-08-10",
        "",
        f"- Cover letter words: {summary['cover_letter_words']}",
        f"- Pitch rows: {summary['pitch_rows']}",
        f"- Finalization rows: {summary['finalization_rows']}",
        f"- Forbidden-language rows: {summary['forbidden_language_rows']}",
        f"- Current branch: {summary['current_applicable_branch']}",
        f"- QA pass: {summary['qa_pass']}",
        f"- Status: {summary['status']}",
        "",
        "Conclusion: a bounded Track B cover letter is ready for author review, but it is not final and cannot be submitted until the remaining hard gates close.",
        "",
    ]
    (OUT_DIR / "natcomms_cover_letter_prelock_report.md").write_text("\n".join(report), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
