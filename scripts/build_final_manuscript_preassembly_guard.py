#!/usr/bin/env python3
"""Guard against treating draft manuscript assets as final submission files."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "final_manuscript_preassembly_guard_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"

DASHBOARD = REPORTS / "submission_readiness_dashboard_20260810" / "submission_readiness_dashboard_summary.json"
PORTAL_PREFLIGHT = REPORTS / "portal_submission_file_preflight_20260810" / "portal_submission_file_inventory.csv"
REFERENCE_QUEUE = REPORTS / "reference_completion_handoff_20260810" / "citation_marker_final_replacement_queue.csv"

SCAN_FILES = [
    REPORTS / "manuscript_assembly_skeleton_20260810" / "manuscript_assembly_skeleton.md",
    REPORTS / "submission_package_skeleton_20260810" / "title_abstract_significance.md",
    REPORTS / "submission_package_skeleton_20260810" / "cover_letter_skeleton.md",
    REPORTS / "results_section_skeleton_20260810" / "results_section_skeleton.md",
    REPORTS / "methods_section_skeleton_20260810" / "methods_section_skeleton.md",
    REPORTS / "narrative_cited_drafts_20260810" / "narrative_section_drafts_v1_cited.md",
    REPORTS / "figure_table_anchor_lock_20260810" / "narrative_section_drafts_v1_anchored.md",
    REPORTS / "companion_artifacts_skeleton_20260810" / "data_availability_skeleton.md",
    REPORTS / "companion_artifacts_skeleton_20260810" / "code_availability_skeleton.md",
    REPORTS / "companion_artifacts_skeleton_20260810" / "reporting_summary_checklist.md",
    REPORTS / "manuscript_table_drafts_20260810" / "manuscript_table_drafts.md",
]

PATTERNS = [
    ("candidate_reference_marker", re.compile(r"\[P\d+(?:,P\d+)*\]")),
    ("planned_or_pending_figure_marker", re.compile(r"\b(planned|pending|not rendered|source_ready_not_rendered|rendered_figures=0)\b", re.IGNORECASE)),
    ("skeleton_or_draft_marker", re.compile(r"\b(skeleton|draft|candidate|not final|not submission-ready)\b", re.IGNORECASE)),
    ("open_gate_marker", re.compile(r"\b(NO-GO|open gate|blocked|missing|not cleared|not locked|not_ready|incomplete)\b", re.IGNORECASE)),
    ("repository_placeholder_marker", re.compile(r"\b(DOI|accession|repository identifier|public repository URL|release tag)\b", re.IGNORECASE)),
]


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def rel(path: Path) -> str:
    return str(path.relative_to(BENCH_ROOT)).replace("\\", "/")


def update_desktop_plan(section: str) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    marker = "### 18.87 Final manuscript preassembly guard update"
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

    dashboard = read_json(DASHBOARD)
    portal_rows = read_csv(PORTAL_PREFLIGHT)
    reference_rows = read_csv(REFERENCE_QUEUE)

    file_rows: list[dict[str, object]] = []
    marker_rows: list[dict[str, object]] = []

    for path in SCAN_FILES:
        text = path.read_text(encoding="utf-8-sig") if path.exists() else ""
        file_marker_count = 0
        pattern_hits: list[str] = []
        for pattern_name, pattern in PATTERNS:
            matches = list(pattern.finditer(text))
            if matches:
                pattern_hits.append(pattern_name)
            file_marker_count += len(matches)
            for match in matches[:25]:
                line_no = text[: match.start()].count("\n") + 1
                snippet = " ".join(text[match.start() : min(match.end() + 80, len(text))].split())
                marker_rows.append(
                    {
                        "file": rel(path),
                        "marker_type": pattern_name,
                        "line": line_no,
                        "matched_text": match.group(0),
                        "context_snippet": snippet,
                        "finalization_rule": "Allowed in draft; must be resolved or explicitly bounded before final/uploadable status.",
                    }
                )

        file_rows.append(
            {
                "file": rel(path),
                "exists": path.exists(),
                "marker_count": file_marker_count,
                "pattern_types": "; ".join(pattern_hits),
                "final_status_allowed": "no",
                "reason": "Draft/skeleton markers remain or submission dashboard is not ready.",
            }
        )

    blocked_reference_rows = sum(1 for row in reference_rows if row.get("replacement_allowed_now") != "true")
    upload_allowed_rows = sum(1 for row in portal_rows if row.get("upload_allowed_now") == "yes")

    stop_rules = [
        {
            "rule_id": "FINAL-GUARD-001",
            "rule": "Do not mark manuscript text final while candidate reference markers remain.",
            "current_evidence": f"blocked_reference_rows={blocked_reference_rows}",
        },
        {
            "rule_id": "FINAL-GUARD-002",
            "rule": "Do not mark figure calls final while rendered figures and visual QA are absent.",
            "current_evidence": "portal item display_figures upload_allowed_now=no",
        },
        {
            "rule_id": "FINAL-GUARD-003",
            "rule": "Do not mark availability statements final before DOI/accession/licence evidence exists.",
            "current_evidence": "Data/code availability portal rows remain upload_allowed_now=no",
        },
        {
            "rule_id": "FINAL-GUARD-004",
            "rule": "Do not remove open-gate limitations before real blind external validation is complete.",
            "current_evidence": "dashboard submission_ready=false; external validation gate open",
        },
        {
            "rule_id": "FINAL-GUARD-005",
            "rule": "Do not treat M0-M2 pass as proof of final manuscript assembly.",
            "current_evidence": f"portal_upload_allowed_rows={upload_allowed_rows}; submission_ready={dashboard.get('submission_ready')}",
        },
    ]

    qa_rows = [
        {
            "check": "scan_files_exist",
            "result": "PASS" if all(row["exists"] for row in file_rows) else "FAIL",
            "detail": f"scan_files={len(file_rows)}",
        },
        {
            "check": "draft_markers_detected",
            "result": "PASS" if marker_rows else "FAIL",
            "detail": f"marker_rows={len(marker_rows)}",
        },
        {
            "check": "not_final_state_preserved",
            "result": "PASS" if dashboard.get("submission_ready") is False and upload_allowed_rows == 0 else "FAIL",
            "detail": f"submission_ready={dashboard.get('submission_ready')}; upload_allowed_rows={upload_allowed_rows}",
        },
        {
            "check": "reference_lock_preserved",
            "result": "PASS" if blocked_reference_rows > 0 else "FAIL",
            "detail": f"blocked_reference_rows={blocked_reference_rows}",
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(
        OUT_DIR / "final_manuscript_file_guard.csv",
        file_rows,
        ["file", "exists", "marker_count", "pattern_types", "final_status_allowed", "reason"],
    )
    write_csv(
        OUT_DIR / "final_manuscript_marker_scan.csv",
        marker_rows,
        ["file", "marker_type", "line", "matched_text", "context_snippet", "finalization_rule"],
    )
    write_csv(OUT_DIR / "final_manuscript_no_finalization_rules.csv", stop_rules, ["rule_id", "rule", "current_evidence"])
    write_csv(OUT_DIR / "final_manuscript_preassembly_guard_qa.csv", qa_rows, ["check", "result", "detail"])

    report = [
        "# Final manuscript preassembly guard report 2026-08-10",
        "",
        "Status: `final_manuscript_preassembly_guard_ready_not_final`",
        "",
        f"1. Files scanned: {len(file_rows)}",
        f"2. Marker rows: {len(marker_rows)}",
        f"3. Stop rules: {len(stop_rules)}",
        f"4. Blocked reference rows: {blocked_reference_rows}",
        f"5. QA pass: {str(qa_pass).lower()}",
        "",
        "Conclusion: draft/skeleton markers are intentionally preserved and final manuscript assembly remains blocked.",
        "",
    ]
    write_text(OUT_DIR / "FINAL_MANUSCRIPT_PREASSEMBLY_GUARD_README.md", "\n".join(report))
    write_text(OUT_DIR / "final_manuscript_preassembly_guard_report.md", "\n".join(report))

    summary = {
        "package": "final_manuscript_preassembly_guard_20260810",
        "files_scanned": len(file_rows),
        "marker_rows": len(marker_rows),
        "stop_rules": len(stop_rules),
        "blocked_reference_rows": blocked_reference_rows,
        "upload_allowed_rows": upload_allowed_rows,
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "final_manuscript_allowed": False,
        "portal_upload_ready": False,
        "submission_ready": False,
        "status": "final_manuscript_preassembly_guard_ready_not_final",
    }

    section = f"""### 18.87 Final manuscript preassembly guard update

Added a final manuscript preassembly guard that scans current manuscript-facing drafts for markers that must not enter final/uploadable files.

New directory: `{OUT_DIR}`

New files:
1. `final_manuscript_file_guard.csv`
2. `final_manuscript_marker_scan.csv`
3. `final_manuscript_no_finalization_rules.csv`
4. `final_manuscript_preassembly_guard_qa.csv`
5. `FINAL_MANUSCRIPT_PREASSEMBLY_GUARD_README.md`
6. `final_manuscript_preassembly_guard_report.md`
7. `final_manuscript_preassembly_guard_summary.json`

Current result:
1. files_scanned = {summary['files_scanned']}
2. marker_rows = {summary['marker_rows']}
3. stop_rules = {summary['stop_rules']}
4. blocked_reference_rows = {summary['blocked_reference_rows']}
5. qa_pass = {str(qa_pass).lower()}
6. final_manuscript_allowed = false
7. submission_ready = false

Boundary:
1. This step does not revise manuscript prose.
2. This step does not replace reference markers.
3. This step does not assemble final submission files or authorize upload."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "final_manuscript_preassembly_guard_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("Final manuscript preassembly guard QA failed")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
