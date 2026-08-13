#!/usr/bin/env python3
"""Build an author-review packet for Python preview figures."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import zipfile
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "python_figure_author_review_packet_20260810"
FIG_OUT = OUT_DIR / "figures_for_author_review"
DESKTOP = Path.home() / "Desktop"
DESKTOP_PLAN = DESKTOP / "8\u670810\u65e5cns.md"

PREVIEW_MANIFEST = REPORTS / "python_figure_preview_package_20260810" / "python_figure_preview_manifest.csv"
VISUAL_QA_SUMMARY = REPORTS / "python_figure_preview_visual_qa_20260810" / "python_figure_preview_visual_qa_summary.json"
VISUAL_QA = REPORTS / "python_figure_preview_visual_qa_20260810" / "python_figure_preview_visual_qa.csv"
CAPTION_QA = REPORTS / "python_figure_preview_visual_qa_20260810" / "python_figure_caption_boundary_qa.csv"
FINALIZATION_QUEUE = REPORTS / "python_figure_preview_visual_qa_20260810" / "python_figure_finalization_queue.csv"


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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def update_desktop_plan(section: str) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    marker = "### 18.99 Python figure author review packet update"
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
    FIG_OUT.mkdir(parents=True, exist_ok=True)

    manifest = read_csv(PREVIEW_MANIFEST)
    visual_summary = read_json(VISUAL_QA_SUMMARY)
    visual_rows = read_csv(VISUAL_QA)
    caption_rows = read_csv(CAPTION_QA)
    finalization_rows = read_csv(FINALIZATION_QUEUE)
    caption_by_figure = {row["figure_id"]: row for row in caption_rows}
    visual_by_figure = {row["figure_id"]: row for row in visual_rows}

    copied_rows: list[dict[str, object]] = []
    for row in manifest:
        for fmt in ["png", "pdf"]:
            src = BENCH_ROOT / row[fmt]
            dest_name = f"{row['figure_id'].lower().replace(' ', '_')}_author_review.{fmt}"
            dest = FIG_OUT / dest_name
            shutil.copy2(src, dest)
            copied_rows.append(
                {
                    "figure_id": row["figure_id"],
                    "format": fmt,
                    "source": row[fmt],
                    "packet_file": str(dest.relative_to(BENCH_ROOT)).replace("\\", "/"),
                    "bytes": dest.stat().st_size,
                    "sha256": sha256(dest),
                }
            )

    review_rows = []
    for row in manifest:
        figure_id = row["figure_id"]
        review_rows.append(
            {
                "figure_id": figure_id,
                "author_review_required": "yes",
                "preview_file_png": f"figures_for_author_review/{figure_id.lower().replace(' ', '_')}_author_review.png",
                "preview_file_pdf": f"figures_for_author_review/{figure_id.lower().replace(' ', '_')}_author_review.pdf",
                "core_conclusion": row["core_conclusion"],
                "required_boundary": row["boundary"],
                "current_visual_status": visual_by_figure[figure_id]["visual_status"],
                "author_approval_status": "blank",
                "allowed_values": "approve_preview_for_final_candidate; request_revision; reject_claim_framing",
                "author_comment": "",
            }
        )

    stop_rows = [
        {"rule_id": "FIG-AUTHOR-STOP-001", "rule": "Do not mark a figure final from this packet alone."},
        {"rule_id": "FIG-AUTHOR-STOP-002", "rule": "Do not remove boundary language from any caption during author review."},
        {"rule_id": "FIG-AUTHOR-STOP-003", "rule": "Do not treat Figure 6 as completed blind external validation."},
        {"rule_id": "FIG-AUTHOR-STOP-004", "rule": "Do not portal-upload preview figures."},
        {"rule_id": "FIG-AUTHOR-STOP-005", "rule": "Do not close the figure gate until all six author approvals and final export QA are recorded."},
    ]

    instructions = """# Python figure author review packet 2026-08-10

This packet contains PNG and PDF preview files for Figure 1-Figure 6.

Author task:
1. Open each PNG or PDF preview.
2. Fill `python_figure_author_review_form.csv`.
3. Use only the allowed values in `author_approval_status`.
4. Add specific comments for any requested revision.

Boundary:
1. These are author-review previews, not final submission figures.
2. Figure 6 is an open-gate placeholder only.
3. Do not upload these files to a submission portal.
4. Do not remove the required boundary sentence for any figure.
"""
    write_text(OUT_DIR / "PYTHON_FIGURE_AUTHOR_REVIEW_INSTRUCTIONS.md", instructions)

    write_csv(
        OUT_DIR / "python_figure_author_review_packet_manifest.csv",
        copied_rows,
        ["figure_id", "format", "source", "packet_file", "bytes", "sha256"],
    )
    write_csv(
        OUT_DIR / "python_figure_author_review_form.csv",
        review_rows,
        ["figure_id", "author_review_required", "preview_file_png", "preview_file_pdf", "core_conclusion", "required_boundary", "current_visual_status", "author_approval_status", "allowed_values", "author_comment"],
    )
    write_csv(OUT_DIR / "python_figure_author_review_stop_rules.csv", stop_rows, ["rule_id", "rule"])

    zip_path = OUT_DIR / "NatComms_python_figure_author_review_packet_20260810.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(FIG_OUT.iterdir()):
            archive.write(path, path.relative_to(OUT_DIR))
        for name in [
            "PYTHON_FIGURE_AUTHOR_REVIEW_INSTRUCTIONS.md",
            "python_figure_author_review_packet_manifest.csv",
            "python_figure_author_review_form.csv",
            "python_figure_author_review_stop_rules.csv",
        ]:
            archive.write(OUT_DIR / name, name)

    desktop_zip = DESKTOP / "NatComms_python_figure_author_review_packet_20260810.zip"
    shutil.copy2(zip_path, desktop_zip)

    zip_members = zipfile.ZipFile(zip_path).namelist()
    qa_rows = [
        {
            "check": "visual_qa_ready_imported",
            "result": "PASS" if visual_summary.get("author_review_preview_ready_rows") == 6 else "FAIL",
            "detail": f"author_review_preview_ready_rows={visual_summary.get('author_review_preview_ready_rows')}",
        },
        {
            "check": "png_pdf_copied_for_each_figure",
            "result": "PASS" if len(copied_rows) == 12 else "FAIL",
            "detail": f"copied_rows={len(copied_rows)}",
        },
        {
            "check": "author_review_form_blank",
            "result": "PASS" if all(row["author_approval_status"] == "blank" for row in review_rows) else "FAIL",
            "detail": "approval fields intentionally blank",
        },
        {
            "check": "finalization_remains_blocked",
            "result": "PASS" if len(finalization_rows) == 6 and all(row["blocked_now"] == "yes" for row in finalization_rows) else "FAIL",
            "detail": f"finalization_rows={len(finalization_rows)}",
        },
        {
            "check": "desktop_zip_created",
            "result": "PASS" if desktop_zip.exists() and len(zip_members) == 16 else "FAIL",
            "detail": f"desktop_zip_exists={desktop_zip.exists()}; zip_members={len(zip_members)}",
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)
    write_csv(OUT_DIR / "python_figure_author_review_packet_qa.csv", qa_rows, ["check", "result", "detail"])

    report = [
        "# Python figure author review packet report 2026-08-10",
        "",
        "Status: `python_figure_author_review_packet_ready_not_approved`",
        "",
        f"1. Figures included: {len(manifest)}",
        f"2. PNG/PDF files copied: {len(copied_rows)}",
        f"3. Author review form rows: {len(review_rows)}",
        f"4. Stop rules: {len(stop_rows)}",
        f"5. Zip members: {len(zip_members)}",
        f"6. QA pass: {str(qa_pass).lower()}",
        "",
        "Conclusion: the figure preview packet is ready for author review, but no author approvals are recorded and final figures remain blocked.",
        "",
    ]
    write_text(OUT_DIR / "python_figure_author_review_packet_report.md", "\n".join(report))

    output_summary = {
        "package": "python_figure_author_review_packet_20260810",
        "figures_included": len(manifest),
        "copied_preview_files": len(copied_rows),
        "author_review_rows": len(review_rows),
        "author_approvals_recorded": 0,
        "stop_rules": len(stop_rows),
        "zip_members": len(zip_members),
        "desktop_zip_exists": desktop_zip.exists(),
        "desktop_zip_name": desktop_zip.name,
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "finalization_blocked_rows": sum(1 for row in finalization_rows if row["blocked_now"] == "yes"),
        "rendered_figures_final": 0,
        "final_figures_ready": False,
        "submission_ready": False,
        "status": "python_figure_author_review_packet_ready_not_approved",
    }

    section = f"""### 18.99 Python figure author review packet update

Packaged the six Python preview figures for author review with PNG/PDF files, a blank approval form and stop rules.

New directory: `{OUT_DIR}`

New files:
1. `figures_for_author_review/*.png`
2. `figures_for_author_review/*.pdf`
3. `python_figure_author_review_packet_manifest.csv`
4. `python_figure_author_review_form.csv`
5. `python_figure_author_review_stop_rules.csv`
6. `PYTHON_FIGURE_AUTHOR_REVIEW_INSTRUCTIONS.md`
7. `python_figure_author_review_packet_qa.csv`
8. `python_figure_author_review_packet_report.md`
9. `python_figure_author_review_packet_summary.json`
10. `NatComms_python_figure_author_review_packet_20260810.zip`

Desktop zip: `{desktop_zip}`

Current result:
1. figures_included = {output_summary['figures_included']}
2. copied_preview_files = {output_summary['copied_preview_files']}
3. author_review_rows = {output_summary['author_review_rows']}
4. author_approvals_recorded = 0
5. qa_pass = {str(qa_pass).lower()}
6. final_figures_ready = false
7. submission_ready = false

Boundary:
1. This packet is for author review only.
2. It does not approve final figures or final captions.
3. It does not close the figure gate or authorize portal upload."""
    output_summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "python_figure_author_review_packet_summary.json", json.dumps(output_summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("Python figure author review packet QA failed")
    print(json.dumps(output_summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
