#!/usr/bin/env python3
"""Align Results paragraphs with figure candidates, claim guardrails and Source Data review rows."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "results_figure_source_alignment_packet_20260811"
DESKTOP_REPORT = Path.home() / "Desktop" / "NatComms_20260811_results_figure_source_alignment_packet.md"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def normalize_refs(value: str) -> list[str]:
    return [item.strip() for item in value.split(";") if item.strip()]


def update_desktop_plan(summary: dict[str, object]) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    marker = "### 20.06 Results figure/source alignment update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- Added `reports/results_figure_source_alignment_packet_20260811/` and Desktop report `NatComms_20260811_results_figure_source_alignment_packet.md`.
- Current Results alignment state: `results_paragraphs_aligned={summary["results_paragraphs_aligned"]}`, `figure_links_ready={summary["figure_links_ready"]}`, `source_data_links_ready={summary["source_data_links_ready"]}`, `claim_guardrail_links_ready={summary["claim_guardrail_links_ready"]}`.
- Final manuscript state remains guarded: `results_text_final=false`, `final_figures_ready=false`, `source_data_panel_map_locked=false`, `submission_ready=false`.
- Boundary: this alignment packet audits Results-to-evidence consistency only; it does not finalize prose, figures, Source Data, references or submission.
"""
    if marker in text:
        start = text.index(marker)
        next_start = text.find("\n### ", start + len(marker))
        text = text[:start].rstrip() if next_start == -1 else text[:start].rstrip() + "\n\n" + text[next_start:].lstrip("\n")
    DESKTOP_PLAN.write_text(text.rstrip() + block + "\n", encoding="utf-8")
    return True


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    results_rows = read_csv(
        BENCH_ROOT
        / "reports"
        / "results_section_skeleton_20260810"
        / "results_paragraph_claim_evidence_map.csv"
    )
    claim_rows = read_csv(
        BENCH_ROOT
        / "reports"
        / "manuscript_claim_readiness_audit_20260810"
        / "manuscript_claim_readiness_audit.csv"
    )
    figure_rows = read_csv(
        BENCH_ROOT
        / "reports"
        / "figure_final_candidate_review_packet_20260811"
        / "figure_final_candidate_review_manifest.csv"
    )
    source_rows = read_csv(
        BENCH_ROOT
        / "reports"
        / "source_data_panel_map_review_packet_20260811"
        / "source_data_panel_map_review_matrix.csv"
    )
    author_summary = read_json(
        BENCH_ROOT
        / "reports"
        / "author_review_manuscript_package_20260810"
        / "author_review_manuscript_summary.json"
    )
    manuscript_text = (
        BENCH_ROOT
        / "reports"
        / "author_review_manuscript_package_20260810"
        / "author_review_manuscript_v0_1.md"
    ).read_text(encoding="utf-8-sig")
    figure_summary = read_json(
        BENCH_ROOT
        / "reports"
        / "figure_final_candidate_review_packet_20260811"
        / "figure_final_candidate_review_packet_summary.json"
    )
    source_summary = read_json(
        BENCH_ROOT
        / "reports"
        / "source_data_panel_map_review_packet_20260811"
        / "source_data_panel_map_review_packet_summary.json"
    )

    claim_by_id = {row["claim_id"]: row for row in claim_rows}
    figure_by_id = {row["figure_id"]: row for row in figure_rows}
    source_by_id = {row["figure_id"]: row for row in source_rows}

    alignment_rows: list[dict[str, object]] = []
    risk_rows: list[dict[str, object]] = []
    for row in results_rows:
        paragraph_id = row["paragraph_id"]
        refs = normalize_refs(row["figure_or_table"])
        figure_refs = [ref for ref in refs if ref.startswith("Figure ")]
        claim = claim_by_id.get(paragraph_id, {})

        linked_figures = []
        linked_source_data = []
        figure_ready = True
        source_ready = True
        for figure_id in figure_refs:
            figure = figure_by_id.get(figure_id)
            source = source_by_id.get(figure_id)
            if figure:
                linked_figures.append(f"{figure_id}:{figure['candidate_review_status']}")
                if figure["candidate_review_status"] != "ready_for_final_candidate_review":
                    figure_ready = False
            else:
                figure_ready = False
            if source:
                linked_source_data.append(f"{figure_id}:{source['source_data_filename']}:{source['panel_map_review_status']}")
                if source["panel_map_review_status"] != "ready_for_review":
                    source_ready = False
            else:
                source_ready = False

        guardrail_ready = bool(claim) and claim.get("readiness", "") != ""
        alignment_rows.append(
            {
                "paragraph_id": paragraph_id,
                "section_role": row["section_role"],
                "topic_sentence": row["topic_sentence"],
                "claim_readiness": claim.get("readiness", ""),
                "allowed_strength": claim.get("allowed_strength", ""),
                "forbidden_upgrade": claim.get("forbidden_upgrade", ""),
                "figure_or_table": row["figure_or_table"],
                "figure_candidate_link": "; ".join(linked_figures),
                "source_data_review_link": "; ".join(linked_source_data),
                "figure_link_ready": "yes" if figure_ready else "no",
                "source_data_link_ready": "yes" if source_ready else "no",
                "claim_guardrail_link_ready": "yes" if guardrail_ready else "no",
                "results_alignment_status": "ready_for_author_review"
                if figure_ready and source_ready and guardrail_ready
                else "needs_attention",
                "finalization_boundary": "not_final_until_figures_source_data_references_and_availability_are_locked",
            }
        )

        if claim.get("forbidden_upgrade"):
            risk_rows.append(
                {
                    "paragraph_id": paragraph_id,
                    "risk_type": "forbidden_upgrade",
                    "risk_text": claim["forbidden_upgrade"],
                    "mitigation": claim.get("required_wording", ""),
                }
            )

    qa_rows = [
        {
            "check": "six Results paragraphs aligned",
            "result": "PASS" if len(alignment_rows) == 6 else "FAIL",
            "detail": f"alignment_rows={len(alignment_rows)}",
        },
        {
            "check": "all figure links ready",
            "result": "PASS" if all(row["figure_link_ready"] == "yes" for row in alignment_rows) else "FAIL",
            "detail": f"figure_links_ready={sum(1 for row in alignment_rows if row['figure_link_ready'] == 'yes')}",
        },
        {
            "check": "all Source Data review links ready",
            "result": "PASS" if all(row["source_data_link_ready"] == "yes" for row in alignment_rows) else "FAIL",
            "detail": f"source_data_links_ready={sum(1 for row in alignment_rows if row['source_data_link_ready'] == 'yes')}",
        },
        {
            "check": "claim guardrails linked",
            "result": "PASS" if all(row["claim_guardrail_link_ready"] == "yes" for row in alignment_rows) else "FAIL",
            "detail": f"claim_guardrail_links_ready={sum(1 for row in alignment_rows if row['claim_guardrail_link_ready'] == 'yes')}",
        },
        {
            "check": "final submission remains blocked",
            "result": "PASS" if author_summary.get("submission_ready") is False else "FAIL",
            "detail": f"submission_ready={author_summary.get('submission_ready')}",
        },
    ]

    summary = {
        "package": "results_figure_source_alignment_packet_20260811",
        "results_paragraphs_aligned": len(alignment_rows),
        "figure_links_ready": sum(1 for row in alignment_rows if row["figure_link_ready"] == "yes"),
        "source_data_links_ready": sum(1 for row in alignment_rows if row["source_data_link_ready"] == "yes"),
        "claim_guardrail_links_ready": sum(1 for row in alignment_rows if row["claim_guardrail_link_ready"] == "yes"),
        "risk_rows": len(risk_rows),
        "figure_review_packet_ready": figure_summary.get("review_packet_ready") is True,
        "source_data_review_packet_ready": source_summary.get("review_packet_ready") is True,
        "results_text_final": "Figure/Table pointer pending" not in manuscript_text and all(row["results_alignment_status"] == "ready_for_author_review" for row in alignment_rows),
        "final_figures_ready": False,
        "source_data_panel_map_locked": False,
        "submission_ready": False,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "desktop_report": str(DESKTOP_REPORT),
        "status": "results_figure_source_alignment_ready_not_final",
    }

    report = f"""# Results Figure/Source Alignment Packet

    This packet aligns the six Results paragraphs with figure final-candidate
    review status, Source Data review rows and claim guardrails, and records
    whether the Results prose itself is final.

Current state:

1. `results_paragraphs_aligned={summary["results_paragraphs_aligned"]}`.
2. `figure_links_ready={summary["figure_links_ready"]}`.
3. `source_data_links_ready={summary["source_data_links_ready"]}`.
4. `claim_guardrail_links_ready={summary["claim_guardrail_links_ready"]}`.
5. `risk_rows={summary["risk_rows"]}`.
6. `results_text_final={str(summary["results_text_final"]).lower()}`.
7. `final_figures_ready=false`.
8. `source_data_panel_map_locked=false`.
9. `submission_ready=false`.

Use: review whether each Results paragraph points to the correct figure,
Source Data file and claim boundary before final prose lock.

    Boundary: this is an alignment audit for Results prose and evidence links. It
    does not finalize figures, Source Data, references, availability statements or
    submission.
"""

    write_csv(
        OUT_DIR / "results_figure_source_alignment_matrix.csv",
        [
            "paragraph_id",
            "section_role",
            "topic_sentence",
            "claim_readiness",
            "allowed_strength",
            "forbidden_upgrade",
            "figure_or_table",
            "figure_candidate_link",
            "source_data_review_link",
            "figure_link_ready",
            "source_data_link_ready",
            "claim_guardrail_link_ready",
            "results_alignment_status",
            "finalization_boundary",
        ],
        alignment_rows,
    )
    write_csv(OUT_DIR / "results_claim_risk_guardrails.csv", ["paragraph_id", "risk_type", "risk_text", "mitigation"], risk_rows)
    write_csv(OUT_DIR / "results_figure_source_alignment_qa.csv", ["check", "result", "detail"], qa_rows)
    write_text(OUT_DIR / "RESULTS_FIGURE_SOURCE_ALIGNMENT_README.md", report)
    write_text(OUT_DIR / "results_figure_source_alignment_report.md", report)
    write_text(DESKTOP_REPORT, report)
    summary["desktop_plan_updated"] = update_desktop_plan(summary)
    write_text(OUT_DIR / "results_figure_source_alignment_summary.json", json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
