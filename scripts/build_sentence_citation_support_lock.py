#!/usr/bin/env python3
"""Build sentence-level citation support locks for the author-review draft."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "sentence_citation_support_lock_20260810"
MANUSCRIPT = BENCH_ROOT / "reports" / "author_review_manuscript_package_20260810" / "author_review_manuscript_v0_1.md"
REF_VERIFY_DIR = BENCH_ROOT / "reports" / "reference_public_verification_20260810"
MARKER_INVENTORY = BENCH_ROOT / "reports" / "reference_numbering_prelock_20260810" / "manuscript_candidate_marker_inventory.csv"


MARKER_PATTERN = re.compile(r"\[P\d+(?:,P\d+)*\]")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def candidate_ids(marker: str) -> list[str]:
    return [part.strip() for part in marker.strip("[]").split(",") if part.strip()]


def sentence_for_marker(line: str, marker: str) -> str:
    idx = line.index(marker)
    before = line[: idx + len(marker)]
    after = line[idx + len(marker) :]
    start_candidates = [before.rfind(". "), before.rfind("? "), before.rfind("! ")]
    start = max(start_candidates)
    start = 0 if start == -1 else start + 2
    end_candidates = [pos for pos in (after.find(". "), after.find("? "), after.find("! ")) if pos != -1]
    end = len(line) if not end_candidates else idx + len(marker) + min(end_candidates) + 1
    return line[start:end].strip()


def claim_type(sentence: str) -> str:
    lowered = sentence.lower()
    if "gpr" in lowered and "curated image collection" in lowered:
        return "field_background"
    if "site conditions" in lowered or "dataset construction" in lowered:
        return "gpr_environment_context"
    if "random" in lowered and "split" in lowered:
        return "leakage_split_background"
    if "generalization claims" in lowered or "audit executable assets" in lowered:
        return "benchmark_design_rationale"
    if "provenance-aware evaluation" in lowered:
        return "conclusion_background_implication"
    return "background_context"


def support_grade(ids: list[str]) -> str:
    if set(ids) == {"P1"}:
        return "background_support"
    if {"P4", "P5"}.issubset(ids):
        return "partial_to_background_support"
    if "P2" in ids:
        return "background_support_for_evaluation_guardrails"
    return "background_support"


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manuscript_lines = MANUSCRIPT.read_text(encoding="utf-8").splitlines()
    metadata_rows = read_csv(REF_VERIFY_DIR / "public_reference_metadata_verification.csv")
    boundary_rows = read_csv(REF_VERIFY_DIR / "reference_support_boundary_audit.csv")
    inventory_rows = read_csv(MARKER_INVENTORY)

    metadata_by_id = {row["candidate_id"]: row for row in metadata_rows}
    boundary_by_id = {row["candidate_id"]: row for row in boundary_rows}

    sentence_rows: list[dict[str, str]] = []
    replacement_rows: list[dict[str, str]] = []
    guard_rows: list[dict[str, str]] = []

    marker_index = 0
    for line_number, line in enumerate(manuscript_lines, start=1):
        for match in MARKER_PATTERN.finditer(line):
            marker_index += 1
            marker = match.group(0)
            ids = candidate_ids(marker)
            sentence = sentence_for_marker(line, marker)
            verified_refs = []
            forbidden_uses = []
            for cid in ids:
                metadata = metadata_by_id[cid]
                boundary = boundary_by_id[cid]
                verified_refs.append(f"{cid}: {metadata['verified_title']} ({metadata['verified_year']})")
                forbidden_uses.append(f"{cid}: {boundary['forbidden_use']}")

            sentence_rows.append(
                {
                    "sentence_citation_id": f"SC{marker_index:03d}",
                    "line_number": str(line_number),
                    "marker": marker,
                    "candidate_ids": ";".join(ids),
                    "sentence": sentence,
                    "claim_type": claim_type(sentence),
                    "support_grade": support_grade(ids),
                    "verified_reference_titles": " | ".join(verified_refs),
                    "allowed_use": "background/context support only; internal measured results require internal figures/source data",
                    "forbidden_use": " | ".join(forbidden_uses),
                    "final_support_lock_status": "prelock_sentence_mapped_not_final",
                }
            )

            replacement_rows.append(
                {
                    "marker": marker,
                    "candidate_ids": ";".join(ids),
                    "current_line_number": str(line_number),
                    "replacement_allowed_now": "false",
                    "replacement_blocker": "final prose, figure/table calls and final citation order are not locked",
                    "minimum_replacement_evidence": "final manuscript with stable sentences plus final numbered reference order",
                }
            )

    guard_rows.extend(
        [
            {
                "guard_id": "CG001",
                "risk": "External papers cited for internal balanced-accuracy deltas.",
                "required_guard": "Balanced-accuracy deltas and support counts must cite internal figures/source data, not P1-P6.",
                "status": "active",
            },
            {
                "guard_id": "CG002",
                "risk": "Background GPR paper used as evidence for this benchmark's main result.",
                "required_guard": "P1 may support GPR/Res-SAM context only; the Res-SAM transfer delta is internal evidence.",
                "status": "active",
            },
            {
                "guard_id": "CG003",
                "risk": "Leakage references overextended into proof of universal GPR leakage.",
                "required_guard": "P4/P5 support split and leakage-risk context only; Mojahid remains directional and modest.",
                "status": "active",
            },
            {
                "guard_id": "CG004",
                "risk": "Citation markers converted before final order.",
                "required_guard": "Keep [P#] markers until final prose, figure/table calls and reference order are locked.",
                "status": "active",
            },
        ]
    )

    write_csv(
        OUT_DIR / "sentence_citation_support_lock.csv",
        sentence_rows,
        [
            "sentence_citation_id",
            "line_number",
            "marker",
            "candidate_ids",
            "sentence",
            "claim_type",
            "support_grade",
            "verified_reference_titles",
            "allowed_use",
            "forbidden_use",
            "final_support_lock_status",
        ],
    )
    write_csv(
        OUT_DIR / "citation_marker_replacement_plan.csv",
        replacement_rows,
        ["marker", "candidate_ids", "current_line_number", "replacement_allowed_now", "replacement_blocker", "minimum_replacement_evidence"],
    )
    write_csv(OUT_DIR / "citation_overclaim_guardrails.csv", guard_rows, ["guard_id", "risk", "required_guard", "status"])

    inventory_markers = sum(1 for _ in inventory_rows)
    qa_rows = [
        {
            "qa_check": "all_inventory_markers_mapped",
            "status": "pass" if inventory_markers == len(sentence_rows) else "fail",
            "evidence": f"inventory={inventory_markers}; sentence_rows={len(sentence_rows)}",
        },
        {
            "qa_check": "all_candidate_ids_have_public_metadata",
            "status": "pass" if all(cid in metadata_by_id for row in sentence_rows for cid in row["candidate_ids"].split(";")) else "fail",
            "evidence": "candidate IDs checked against public metadata verification table",
        },
        {
            "qa_check": "no_replacement_allowed_now",
            "status": "pass" if all(row["replacement_allowed_now"] == "false" for row in replacement_rows) else "fail",
            "evidence": "final prose and citation order remain unlocked",
        },
        {
            "qa_check": "internal_result_guardrails_present",
            "status": "pass" if any("Balanced-accuracy" in row["required_guard"] for row in guard_rows) else "fail",
            "evidence": "internal result guardrail exists",
        },
    ]
    write_csv(OUT_DIR / "sentence_citation_support_lock_qa.csv", qa_rows, ["qa_check", "status", "evidence"])

    qa_pass = all(row["status"] == "pass" for row in qa_rows)
    readme = """# Sentence citation support lock 2026-08-10

This package maps each current author-review manuscript citation marker to the sentence it supports, the verified candidate references and the allowed support boundary.

It does not convert `[P#]` markers into final numbered references. Final numbering remains blocked until final prose, figure/table calls and reference order are locked.
"""
    (OUT_DIR / "SENTENCE_CITATION_SUPPORT_LOCK_README.md").write_text(readme, encoding="utf-8")

    summary = {
        "run_id": "20260810_sentence_citation_support_lock",
        "sentence_citation_rows": len(sentence_rows),
        "replacement_plan_rows": len(replacement_rows),
        "guardrail_rows": len(guard_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "candidate_markers_replaced": False,
        "final_references_ready": False,
        "submission_ready": False,
        "status": "sentence_citation_support_lock_ready_final_references_not_locked",
        "boundary": "This package maps current citation markers to sentence-level support boundaries; it does not finalize numbering or references.",
    }
    (OUT_DIR / "sentence_citation_support_lock_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    report = [
        "# Sentence citation support lock report 2026-08-10",
        "",
        f"- Sentence citation rows: {summary['sentence_citation_rows']}",
        f"- Replacement plan rows: {summary['replacement_plan_rows']}",
        f"- Guardrail rows: {summary['guardrail_rows']}",
        f"- QA pass: {summary['qa_pass']}",
        f"- Candidate markers replaced: {summary['candidate_markers_replaced']}",
        f"- Status: {summary['status']}",
        "",
        "Conclusion: current `[P#]` markers are mapped to sentence-level support boundaries, but final numbered references remain open.",
        "",
    ]
    (OUT_DIR / "sentence_citation_support_lock_report.md").write_text("\n".join(report), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
