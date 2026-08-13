#!/usr/bin/env python3
"""Audit that manuscript-facing R4 text uses the current 4TU boundary."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "r4_manuscript_boundary_sync_audit_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"

CURRENT_MARKERS = [
    "4TU multi-layer counterfactual stress tests",
    "feasibility-boundary",
    "main confirmation",
    "blind external validation",
]

OBSOLETE_MARKERS = [
    "4TU counterfactual stress tests showed strong fixed-split sensitivity, but this signal weakened under project-level repeated splits",
    "Stress-test evidence only; not final causal proof or main 4TU confirmation",
    "fixed-split sensitivity that weakens under project-level repeated splits",
    "not as a main confirmation matrix",
]

ACTIVE_FILES = [
    "reports/results_section_skeleton_20260810/results_section_skeleton.md",
    "reports/results_section_skeleton_20260810/results_paragraph_claim_evidence_map.csv",
    "reports/submission_package_skeleton_20260810/title_abstract_significance.md",
    "reports/submission_package_skeleton_20260810/submission_claim_evidence_map.csv",
    "reports/manuscript_claim_readiness_audit_20260810/manuscript_claim_readiness_audit.csv",
    "reports/manuscript_claim_readiness_audit_20260810/allowed_manuscript_claims.md",
    "reports/conservative_manuscript_draft_20260810/conservative_manuscript_draft_v0_1.md",
    "reports/conservative_methods_draft_20260810/methods_draft_v0_1.md",
    "reports/author_review_manuscript_package_20260810/author_review_manuscript_v0_1.md",
    "reports/natcomms_initial_submission_text_preassembly_20260810/natcomms_initial_submission_text_preassembly.md",
    "reports/natcomms_initial_submission_text_preassembly_20260810/natcomms_display_item_preassembly.csv",
    "reports/natcomms_supplementary_info_preassembly_20260810/supplementary_information_preassembly.md",
    "reports/natcomms_supplementary_info_preassembly_20260810/supplementary_source_data_boundary_map.csv",
    "reports/figure4_sources_20260810/figure4_source_summary.md",
    "reports/figure4_sources_20260810/figure4_evidence_layer_boundary.csv",
]


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
    text = DESKTOP_PLAN.read_text(encoding="utf-8")
    marker = "### 18.71 R4 manuscript boundary synchronization audit 更新"
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
    audit_rows: list[dict[str, object]] = []
    obsolete_hits: list[str] = []
    missing_files: list[str] = []

    for rel_path in ACTIVE_FILES:
        path = BENCH_ROOT / rel_path
        if not path.exists():
            missing_files.append(rel_path)
            audit_rows.append(
                {
                    "relative_path": rel_path,
                    "exists": False,
                    "current_marker_hits": 0,
                    "obsolete_marker_hits": 0,
                    "status": "missing",
                    "detail": "File missing from active manuscript package.",
                }
            )
            continue
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        current_hits = [marker for marker in CURRENT_MARKERS if marker in text]
        old_hits = [marker for marker in OBSOLETE_MARKERS if marker in text]
        obsolete_hits.extend(f"{rel_path}: {marker}" for marker in old_hits)
        if old_hits:
            status = "fail_obsolete_r4_boundary"
        elif current_hits or "Figure 4" in text or "4TU" in text:
            status = "pass"
        else:
            status = "pass_not_r4_specific"
        audit_rows.append(
            {
                "relative_path": rel_path,
                "exists": True,
                "current_marker_hits": len(current_hits),
                "obsolete_marker_hits": len(old_hits),
                "status": status,
                "detail": "; ".join(old_hits) if old_hits else "No obsolete R4 marker detected.",
            }
        )

    qa_rows = [
        {
            "check": "All active files exist",
            "result": "PASS" if not missing_files else "FAIL",
            "detail": f"missing={len(missing_files)}",
        },
        {
            "check": "No obsolete R4 boundary markers",
            "result": "PASS" if not obsolete_hits else "FAIL",
            "detail": f"obsolete_hits={len(obsolete_hits)}",
        },
        {
            "check": "Current R4 markers present in manuscript-facing layer",
            "result": "PASS" if any(int(row["current_marker_hits"]) > 0 for row in audit_rows) else "FAIL",
            "detail": "At least one active package contains the current R4 wording.",
        },
        {
            "check": "No submission readiness asserted",
            "result": "PASS",
            "detail": "R4 text synchronization does not close figure rendering, blind external validation, DOI/rights or Reporting Summary gates.",
        },
    ]

    write_csv(
        OUT_DIR / "r4_manuscript_boundary_sync_audit.csv",
        audit_rows,
        ["relative_path", "exists", "current_marker_hits", "obsolete_marker_hits", "status", "detail"],
    )
    write_csv(OUT_DIR / "r4_boundary_sync_qa.csv", qa_rows, ["check", "result", "detail"])

    report = [
        "# R4 Manuscript Boundary Synchronization Audit",
        "",
        "Status: `r4_manuscript_boundary_sync_ready_submission_not_ready`",
        "",
        "Purpose: verify that manuscript-facing R4 text uses the current Figure 4 boundary after the 4TU model-family extension audit.",
        "",
        f"- Active files checked: {len(ACTIVE_FILES)}",
        f"- Missing files: {len(missing_files)}",
        f"- Obsolete marker hits: {len(obsolete_hits)}",
        f"- QA pass: {all(row['result'] != 'FAIL' for row in qa_rows)}",
        "",
        "Boundary: this audit synchronizes wording only. It does not render figures, close blind external validation, create DOI records, finalize Reporting Summary or make the manuscript submission-ready.",
        "",
    ]
    write_text(OUT_DIR / "r4_manuscript_boundary_sync_report.md", "\n".join(report))

    summary = {
        "package": "r4_manuscript_boundary_sync_audit_20260810",
        "active_files_checked": len(ACTIVE_FILES),
        "missing_files": len(missing_files),
        "obsolete_marker_hits": len(obsolete_hits),
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] != "FAIL" for row in qa_rows),
        "current_r4_boundary": "4TU multi-layer counterfactual stress tests defined a feasibility-boundary layer rather than a main confirmation result.",
        "submission_ready": False,
        "status": "r4_manuscript_boundary_sync_ready_submission_not_ready",
    }

    section = f"""### 18.71 R4 manuscript boundary synchronization audit 更新

已新增 R4 manuscript boundary synchronization audit。这个包检查 Results、submission skeleton、claim readiness audit、conservative manuscript、Methods、author-review manuscript 和 NatComms preassembly 等活跃稿件层是否仍保留旧的 Figure 4 / 4TU 表述。

新增目录：
`{OUT_DIR}`

新增材料：
1. `r4_manuscript_boundary_sync_audit.csv`
2. `r4_boundary_sync_qa.csv`
3. `r4_manuscript_boundary_sync_report.md`
4. `r4_manuscript_boundary_sync_summary.json`

当前结果：
1. active_files_checked = {len(ACTIVE_FILES)}
2. missing_files = {len(missing_files)}
3. obsolete_marker_hits = {len(obsolete_hits)}
4. qa_pass = {str(summary['qa_pass']).lower()}
5. submission_ready = false
6. 当前状态：`r4_manuscript_boundary_sync_ready_submission_not_ready`

当前 R4 canonical wording：
`4TU multi-layer counterfactual stress tests defined a feasibility-boundary layer rather than a main confirmation result.`

边界：
1. 这一步只同步稿件文字和边界。
2. 这一步不渲染 Figure 4。
3. 这一步不把 4TU 升级为主确认层。
4. 这一步不关闭 blind external validation。
5. 这一步不生成 DOI、final Reporting Summary 或 final submission files。
"""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "r4_manuscript_boundary_sync_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not summary["qa_pass"]:
        raise SystemExit("R4 manuscript boundary synchronization audit failed")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
