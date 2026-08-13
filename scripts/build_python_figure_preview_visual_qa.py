#!/usr/bin/env python3
"""Build visual QA and finalization queue for Python preview figures."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from PIL import Image


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "python_figure_preview_visual_qa_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8\u670810\u65e5cns.md"

PREVIEW_MANIFEST = REPORTS / "python_figure_preview_package_20260810" / "python_figure_preview_manifest.csv"
PREVIEW_SUMMARY = REPORTS / "python_figure_preview_package_20260810" / "python_figure_preview_summary.json"
CAPTIONS = REPORTS / "figure_source_data_lock_20260810" / "figure_caption_boundary_drafts.csv"
PREFLIGHT_QA = REPORTS / "figure_rendering_preflight_20260810" / "figure_visual_qa_import.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def update_desktop_plan(section: str) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    marker = "### 18.98 Python figure preview visual QA update"
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


def image_info(path: Path) -> tuple[int, int]:
    with Image.open(path) as image:
        return image.size


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    manifest = read_csv(PREVIEW_MANIFEST)
    summary = read_json(PREVIEW_SUMMARY)
    captions = {row["figure_id"]: row for row in read_csv(CAPTIONS)}
    preflight_qa = read_csv(PREFLIGHT_QA)

    visual_rows: list[dict[str, object]] = []
    caption_rows: list[dict[str, object]] = []
    final_queue_rows: list[dict[str, object]] = []

    for row in manifest:
        figure_id = row["figure_id"]
        png = BENCH_ROOT / row["png"]
        svg = BENCH_ROOT / row["svg"]
        pdf = BENCH_ROOT / row["pdf"]
        width, height = image_info(png)
        caption = captions[figure_id]
        min_width = 1400
        min_height = 800
        triplet_exists = png.exists() and svg.exists() and pdf.exists()
        dimensions_ok = width >= min_width and height >= min_height
        boundary_ok = row["boundary"] == caption["required_boundary_sentence"]
        preview_only_ok = row["preview_status"] == "rendered_preview_not_final"

        visual_rows.append(
            {
                "figure_id": figure_id,
                "png": row["png"],
                "png_width_px": width,
                "png_height_px": height,
                "svg_exists": svg.exists(),
                "pdf_exists": pdf.exists(),
                "triplet_exists": triplet_exists,
                "dimensions_ok_for_author_review": dimensions_ok,
                "visual_status": "author_review_preview_ready" if triplet_exists and dimensions_ok else "needs_preview_revision",
            }
        )
        caption_rows.append(
            {
                "figure_id": figure_id,
                "caption_lock_status": caption["caption_lock_status"],
                "required_boundary_sentence": caption["required_boundary_sentence"],
                "manifest_boundary": row["boundary"],
                "boundary_match": boundary_ok,
                "forbidden_upgrade": caption["forbidden_upgrade"],
                "preview_only_status": preview_only_ok,
            }
        )
        final_queue_rows.append(
            {
                "figure_id": figure_id,
                "current_artifact": "author_review_preview",
                "required_author_review": "yes",
                "required_finalization_action": "Check final panel layout, caption wording, source-data crosswalk, journal size, line weights, fonts and final export settings.",
                "allowed_next_state_after_review": "final_candidate_not_submission_ready",
                "blocked_now": "yes",
                "blocking_reason": "No author visual approval, final export QA, source-data panel mapping lock or final caption approval is recorded.",
            }
        )

    qa_rows = [
        {
            "check": "all_preview_figures_present",
            "result": "PASS" if len(manifest) == 6 and summary.get("figures_rendered") == 6 else "FAIL",
            "detail": f"manifest_rows={len(manifest)}; figures_rendered={summary.get('figures_rendered')}",
        },
        {
            "check": "all_triplets_exist",
            "result": "PASS" if all(row["triplet_exists"] for row in visual_rows) else "FAIL",
            "detail": "PNG/SVG/PDF triplets checked",
        },
        {
            "check": "author_review_dimensions_ok",
            "result": "PASS" if all(row["dimensions_ok_for_author_review"] for row in visual_rows) else "FAIL",
            "detail": "; ".join(f"{row['figure_id']}={row['png_width_px']}x{row['png_height_px']}" for row in visual_rows),
        },
        {
            "check": "caption_boundaries_match_manifest",
            "result": "PASS" if all(row["boundary_match"] for row in caption_rows) else "FAIL",
            "detail": "caption required boundary compared with preview manifest boundary",
        },
        {
            "check": "preflight_qa_imported",
            "result": "PASS" if len(preflight_qa) == 6 else "FAIL",
            "detail": f"preflight_qa_rows={len(preflight_qa)}",
        },
        {
            "check": "final_gate_not_closed",
            "result": "PASS" if summary.get("rendered_figures_final") == 0 and summary.get("final_figures_ready") is False else "FAIL",
            "detail": f"rendered_figures_final={summary.get('rendered_figures_final')}; final_figures_ready={summary.get('final_figures_ready')}",
        },
        {
            "check": "external_validation_not_claimed",
            "result": "PASS" if summary.get("blind_external_validation_claimed") is False else "FAIL",
            "detail": f"blind_external_validation_claimed={summary.get('blind_external_validation_claimed')}",
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(
        OUT_DIR / "python_figure_preview_visual_qa.csv",
        visual_rows,
        ["figure_id", "png", "png_width_px", "png_height_px", "svg_exists", "pdf_exists", "triplet_exists", "dimensions_ok_for_author_review", "visual_status"],
    )
    write_csv(
        OUT_DIR / "python_figure_caption_boundary_qa.csv",
        caption_rows,
        ["figure_id", "caption_lock_status", "required_boundary_sentence", "manifest_boundary", "boundary_match", "forbidden_upgrade", "preview_only_status"],
    )
    write_csv(
        OUT_DIR / "python_figure_finalization_queue.csv",
        final_queue_rows,
        ["figure_id", "current_artifact", "required_author_review", "required_finalization_action", "allowed_next_state_after_review", "blocked_now", "blocking_reason"],
    )
    write_csv(OUT_DIR / "python_figure_preview_visual_qa_summary.csv", qa_rows, ["check", "result", "detail"])

    report = [
        "# Python figure preview visual QA report 2026-08-10",
        "",
        "Status: `python_figure_preview_visual_qa_ready_final_blocked`",
        "",
        f"1. Preview figures audited: {len(visual_rows)}",
        f"2. Caption-boundary rows audited: {len(caption_rows)}",
        f"3. Finalization queue rows: {len(final_queue_rows)}",
        f"4. QA pass: {str(qa_pass).lower()}",
        "",
        "Conclusion: all preview figures have export triplets and are suitable for author review, but none are final submission figures.",
        "",
        "Boundary: this package does not approve final figures, lock final captions, create final TIFFs, close the figure gate or claim completed blind external validation.",
        "",
    ]
    write_text(OUT_DIR / "PYTHON_FIGURE_PREVIEW_VISUAL_QA_README.md", "\n".join(report))
    write_text(OUT_DIR / "python_figure_preview_visual_qa_report.md", "\n".join(report))

    output_summary = {
        "package": "python_figure_preview_visual_qa_20260810",
        "preview_figures_audited": len(visual_rows),
        "caption_boundary_rows": len(caption_rows),
        "finalization_queue_rows": len(final_queue_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "author_review_preview_ready_rows": sum(1 for row in visual_rows if row["visual_status"] == "author_review_preview_ready"),
        "finalization_blocked_rows": sum(1 for row in final_queue_rows if row["blocked_now"] == "yes"),
        "rendered_figures_final": 0,
        "final_figures_ready": False,
        "blind_external_validation_claimed": False,
        "submission_ready": False,
        "status": "python_figure_preview_visual_qa_ready_final_blocked",
    }

    section = f"""### 18.98 Python figure preview visual QA update

Added a visual QA and finalization queue for the six Python preview figures.

New directory: `{OUT_DIR}`

New files:
1. `python_figure_preview_visual_qa.csv`
2. `python_figure_caption_boundary_qa.csv`
3. `python_figure_finalization_queue.csv`
4. `python_figure_preview_visual_qa_summary.csv`
5. `PYTHON_FIGURE_PREVIEW_VISUAL_QA_README.md`
6. `python_figure_preview_visual_qa_report.md`
7. `python_figure_preview_visual_qa_summary.json`

Current result:
1. preview_figures_audited = {output_summary['preview_figures_audited']}
2. author_review_preview_ready_rows = {output_summary['author_review_preview_ready_rows']}
3. finalization_queue_rows = {output_summary['finalization_queue_rows']}
4. qa_pass = {str(qa_pass).lower()}
5. rendered_figures_final = 0
6. final_figures_ready = false
7. submission_ready = false

Boundary:
1. This QA package authorizes author review only.
2. It does not approve final figures or final captions.
3. It does not close the figure gate or claim completed blind external validation."""
    output_summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "python_figure_preview_visual_qa_summary.json", json.dumps(output_summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("Python figure preview visual QA failed")
    print(json.dumps(output_summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
