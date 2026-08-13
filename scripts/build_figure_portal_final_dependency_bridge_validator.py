#!/usr/bin/env python3
"""Bridge final figure/source-data readiness to portal-upload and submission gates."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "figure_portal_final_dependency_bridge_validator_20260810"
POST_GATE_DIR = BENCH_ROOT / "reports" / "post_gate_manual_evidence_dependency_bridge_validator_20260810"
FIGURE_LOCK_DIR = BENCH_ROOT / "reports" / "figure_source_data_lock_20260810"
FINAL_CANDIDATE_DIR = BENCH_ROOT / "reports" / "python_figure_final_candidate_preflight_20260810"
EXPORT_QA_DIR = BENCH_ROOT / "reports" / "python_figure_final_export_qa_template_20260810"
FIGURE_PORTAL_DIR = BENCH_ROOT / "reports" / "python_figure_portal_upload_blocker_20260810"
PANEL_MAP_DIR = BENCH_ROOT / "reports" / "python_figure_source_data_panel_map_preflight_20260810"
PORTAL_FILE_DIR = BENCH_ROOT / "reports" / "portal_submission_file_preflight_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def as_bool(value: object) -> bool:
    return value is True or str(value).strip().lower() in {"true", "yes", "1"}


def update_desktop_plan(summary: dict[str, object]) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    marker = "### 19.45 Figure/portal final dependency bridge validator update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- 新增 `reports/figure_portal_final_dependency_bridge_validator_20260810/`，把 19.44 post-gate manual bridge、figure source-data lock、final candidate preflight、final export QA、figure portal blocker、source-data panel-map preflight 和 portal file preflight 绑定到同一最终上传前置链。
- 当前 `post_gate_manual_bridge_allowed={str(summary["post_gate_manual_bridge_allowed"]).lower()}`，`figure_final_assets_ready={str(summary["figure_final_assets_ready"]).lower()}`，`source_data_panel_map_ready={str(summary["source_data_panel_map_ready"]).lower()}`。
- 当前 `figure_portal_upload_allowed=false`，`portal_upload_ready=false`，`submission_ready=false`。
- 当前 `rendered_figures_final={summary["rendered_figures_final"]}`，`final_export_qa_allowed_rows={summary["final_export_qa_allowed_rows"]}`，`figure_portal_upload_allowed_rows={summary["figure_portal_upload_allowed_rows"]}`。
- 边界：该 bridge 只读，不渲染最终图、不锁定 panel map、不上传 portal 文件、不生成最终提交状态。
"""
    if marker in text:
        start = text.index(marker)
        next_start = text.find("\n### ", start + len(marker))
        if next_start == -1:
            text = text[:start].rstrip()
        else:
            text = text[:start].rstrip() + "\n\n" + text[next_start:].lstrip("\n")
    text = text.rstrip() + block
    DESKTOP_PLAN.write_text(text + "\n", encoding="utf-8")
    return True


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    post_gate = read_json(POST_GATE_DIR / "post_gate_manual_evidence_dependency_bridge_validator_summary.json")
    figure_lock = read_json(FIGURE_LOCK_DIR / "figure_source_data_lock_summary.json")
    final_candidate = read_json(FINAL_CANDIDATE_DIR / "python_figure_final_candidate_preflight_summary.json")
    export_qa = read_json(EXPORT_QA_DIR / "python_figure_final_export_qa_template_summary.json")
    figure_portal = read_json(FIGURE_PORTAL_DIR / "python_figure_portal_upload_blocker_summary.json")
    panel_map = read_json(PANEL_MAP_DIR / "python_figure_source_data_panel_map_preflight_summary.json")
    portal_file = read_json(PORTAL_FILE_DIR / "portal_submission_file_preflight_summary.json")

    candidate_rows = read_csv(FINAL_CANDIDATE_DIR / "python_figure_final_candidate_queue.csv")
    export_rows = read_csv(EXPORT_QA_DIR / "python_figure_final_export_qa_checklist.csv")
    portal_rows = read_csv(FIGURE_PORTAL_DIR / "python_figure_portal_upload_blocker_overlay.csv")
    panel_rows = read_csv(PANEL_MAP_DIR / "python_figure_source_data_panel_map_preflight.csv")

    post_gate_manual_bridge_allowed = as_bool(post_gate.get("post_gate_manual_bridge_allowed"))
    source_data_lock_ready = (
        as_bool(figure_lock.get("qa_pass"))
        and figure_lock.get("figures_locked", 0) == figure_lock.get("source_manifest_rows", -1)
        and figure_lock.get("figures_locked", 0) == figure_lock.get("caption_rows", -2)
    )
    final_candidate_ready = (
        as_bool(final_candidate.get("qa_pass"))
        and as_bool(final_candidate.get("final_candidate_generation_allowed"))
        and int(final_candidate.get("approved_rows", 0)) == int(final_candidate.get("candidate_rows", -1))
        and as_bool(final_candidate.get("final_figures_ready"))
    )
    final_export_ready = (
        as_bool(export_qa.get("qa_pass"))
        and int(export_qa.get("final_export_qa_allowed_rows", 0)) == int(export_qa.get("export_qa_rows", -1))
        and as_bool(export_qa.get("source_data_panel_map_locked"))
        and as_bool(export_qa.get("captions_locked_final"))
        and as_bool(export_qa.get("final_figures_ready"))
    )
    source_data_panel_map_ready = (
        as_bool(panel_map.get("qa_pass"))
        and int(panel_map.get("missing_source_rows", 1)) == 0
        and int(panel_map.get("panel_map_lock_allowed_rows", 0)) > 0
        and as_bool(panel_map.get("source_data_panel_map_locked"))
    )
    figure_portal_upload_allowed = (
        post_gate_manual_bridge_allowed
        and final_candidate_ready
        and final_export_ready
        and source_data_panel_map_ready
        and int(figure_portal.get("figure_portal_upload_allowed_rows", 0)) > 0
        and as_bool(figure_portal.get("portal_upload_ready"))
    )
    portal_file_upload_allowed = (
        figure_portal_upload_allowed
        and as_bool(portal_file.get("upload_allowed_now"))
        and as_bool(portal_file.get("portal_upload_ready"))
    )
    figure_final_assets_ready = final_candidate_ready and final_export_ready
    portal_upload_ready = figure_portal_upload_allowed and portal_file_upload_allowed
    submission_ready = (
        portal_upload_ready
        and as_bool(portal_file.get("submission_ready"))
        and as_bool(figure_portal.get("submission_ready"))
    )

    dependency_rows = [
        {
            "dependency": "post_gate_manual_bridge_allowed",
            "source": "19.44 post-gate manual evidence bridge",
            "current": post_gate_manual_bridge_allowed,
            "required": "true",
            "passes_now": "yes" if post_gate_manual_bridge_allowed else "no",
        },
        {
            "dependency": "source_data_lock_ready",
            "source": "figure source-data lock",
            "current": source_data_lock_ready,
            "required": "true",
            "passes_now": "yes" if source_data_lock_ready else "no",
        },
        {
            "dependency": "final_candidate_ready",
            "source": "Python figure final candidate preflight",
            "current": final_candidate_ready,
            "required": "all candidates approved and final figures ready",
            "passes_now": "yes" if final_candidate_ready else "no",
        },
        {
            "dependency": "final_export_ready",
            "source": "Python figure final export QA template",
            "current": final_export_ready,
            "required": "all export QA rows allowed, captions and panel map locked",
            "passes_now": "yes" if final_export_ready else "no",
        },
        {
            "dependency": "source_data_panel_map_ready",
            "source": "Python figure source-data panel-map preflight",
            "current": source_data_panel_map_ready,
            "required": "locked panel map with no missing sources",
            "passes_now": "yes" if source_data_panel_map_ready else "no",
        },
        {
            "dependency": "figure_portal_upload_allowed",
            "source": "Python figure portal upload blocker",
            "current": figure_portal_upload_allowed,
            "required": "true",
            "passes_now": "yes" if figure_portal_upload_allowed else "no",
        },
        {
            "dependency": "portal_file_upload_allowed",
            "source": "portal submission file preflight",
            "current": portal_file_upload_allowed,
            "required": "true",
            "passes_now": "yes" if portal_file_upload_allowed else "no",
        },
        {
            "dependency": "submission_ready",
            "source": "19.45 bridge boundary",
            "current": submission_ready,
            "required": "false in current blocked state",
            "passes_now": "yes" if not submission_ready else "no",
        },
    ]

    asset_rows = []
    for row in candidate_rows:
        asset_rows.append(
            {
                "asset_id": row.get("candidate_id", row.get("figure_id", "")),
                "asset": row.get("figure", row.get("asset", "")),
                "source": "python_figure_final_candidate_queue",
                "upstream_allowed": row.get("candidate_generation_allowed", row.get("allowed_now", "")),
                "bridge_allowed": "yes" if figure_final_assets_ready else "no",
                "reason": "Blocked until manual bridge, approvals and final candidate gates pass.",
            }
        )
    for row in export_rows:
        asset_rows.append(
            {
                "asset_id": row.get("figure_id", row.get("export_id", "")),
                "asset": row.get("figure", row.get("export_item", "")),
                "source": "python_figure_final_export_qa_checklist",
                "upstream_allowed": row.get("export_qa_allowed_now", row.get("allowed_now", "")),
                "bridge_allowed": "yes" if final_export_ready else "no",
                "reason": "Blocked until final export QA and locks are complete.",
            }
        )
    for row in portal_rows:
        asset_rows.append(
            {
                "asset_id": row.get("portal_item_id", row.get("item_id", "")),
                "asset": row.get("portal_item", row.get("item", "")),
                "source": "python_figure_portal_upload_blocker_overlay",
                "upstream_allowed": row.get("upload_allowed_now", row.get("allowed_now", "")),
                "bridge_allowed": "yes" if figure_portal_upload_allowed else "no",
                "reason": "Blocked until final figure export and source-data panel map are locked.",
            }
        )
    for row in panel_rows:
        asset_rows.append(
            {
                "asset_id": row.get("figure_id", row.get("panel_id", "")),
                "asset": row.get("figure", row.get("panel", "")),
                "source": "python_figure_source_data_panel_map_preflight",
                "upstream_allowed": row.get("panel_map_lock_allowed_now", row.get("allowed_now", "")),
                "bridge_allowed": "yes" if source_data_panel_map_ready else "no",
                "reason": "Blocked until panel-map lock is allowed and recorded.",
            }
        )

    blocker_rows = [
        {
            "blocker": "post-gate manual bridge blocks figure finalization",
            "evidence": f"post_gate_manual_bridge_allowed={post_gate.get('post_gate_manual_bridge_allowed')}",
            "blocks": "final figure candidate generation",
        },
        {
            "blocker": "final candidates are not approved",
            "evidence": (
                f"approved_rows={final_candidate.get('approved_rows')}; "
                f"blank_rows={final_candidate.get('blank_rows')}; "
                f"final_candidate_generation_allowed={final_candidate.get('final_candidate_generation_allowed')}"
            ),
            "blocks": "final figure assets",
        },
        {
            "blocker": "final export QA is not allowed",
            "evidence": (
                f"final_export_qa_allowed_rows={export_qa.get('final_export_qa_allowed_rows')}; "
                f"source_data_panel_map_locked={export_qa.get('source_data_panel_map_locked')}; "
                f"captions_locked_final={export_qa.get('captions_locked_final')}"
            ),
            "blocks": "portal-upload figure package",
        },
        {
            "blocker": "source-data panel map is not locked",
            "evidence": (
                f"panel_map_lock_allowed_rows={panel_map.get('panel_map_lock_allowed_rows')}; "
                f"source_data_panel_map_locked={panel_map.get('source_data_panel_map_locked')}"
            ),
            "blocks": "source data and figure portal upload",
        },
        {
            "blocker": "portal file preflight blocks upload",
            "evidence": (
                f"upload_allowed_now={portal_file.get('upload_allowed_now')}; "
                f"portal_upload_ready={portal_file.get('portal_upload_ready')}"
            ),
            "blocks": "portal upload and submission-ready state",
        },
    ]

    qa_rows = [
        {
            "check": "all upstream summaries loaded",
            "result": "PASS",
            "detail": "post-gate, figure lock, final candidate, export QA, figure portal, panel map and portal file summaries loaded.",
        },
        {
            "check": "post-gate manual bridge remains blocking",
            "result": "PASS" if not post_gate_manual_bridge_allowed else "FAIL",
            "detail": f"post_gate_manual_bridge_allowed={post_gate_manual_bridge_allowed}",
        },
        {
            "check": "final figures remain not ready",
            "result": "PASS" if not figure_final_assets_ready else "FAIL",
            "detail": f"figure_final_assets_ready={figure_final_assets_ready}",
        },
        {
            "check": "portal upload remains blocked",
            "result": "PASS" if not portal_upload_ready else "FAIL",
            "detail": f"portal_upload_ready={portal_upload_ready}",
        },
        {
            "check": "submission remains false",
            "result": "PASS" if not submission_ready else "FAIL",
            "detail": f"submission_ready={submission_ready}",
        },
    ]

    summary = {
        "package": "figure_portal_final_dependency_bridge_validator_20260810",
        "post_gate_manual_bridge_allowed": post_gate_manual_bridge_allowed,
        "source_data_lock_ready": source_data_lock_ready,
        "final_candidate_ready": final_candidate_ready,
        "final_export_ready": final_export_ready,
        "source_data_panel_map_ready": source_data_panel_map_ready,
        "figure_final_assets_ready": figure_final_assets_ready,
        "figure_portal_upload_allowed": figure_portal_upload_allowed,
        "portal_file_upload_allowed": portal_file_upload_allowed,
        "portal_upload_ready": portal_upload_ready,
        "submission_ready": submission_ready,
        "rendered_figures_final": final_candidate.get("rendered_figures_final", 0),
        "approved_rows": final_candidate.get("approved_rows", 0),
        "final_export_qa_allowed_rows": export_qa.get("final_export_qa_allowed_rows", 0),
        "panel_map_lock_allowed_rows": panel_map.get("panel_map_lock_allowed_rows", 0),
        "figure_portal_upload_allowed_rows": figure_portal.get("figure_portal_upload_allowed_rows", 0),
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": "figure_portal_final_dependency_bridge_validator_ready_blocked",
    }
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(
        OUT_DIR / "figure_portal_final_dependency_bridge_matrix.csv",
        ["dependency", "source", "current", "required", "passes_now"],
        dependency_rows,
    )
    write_csv(
        OUT_DIR / "figure_portal_final_asset_bridge.csv",
        ["asset_id", "asset", "source", "upstream_allowed", "bridge_allowed", "reason"],
        asset_rows,
    )
    write_csv(
        OUT_DIR / "figure_portal_final_dependency_bridge_blockers.csv",
        ["blocker", "evidence", "blocks"],
        blocker_rows,
    )
    write_csv(
        OUT_DIR / "figure_portal_final_dependency_bridge_qa.csv",
        ["check", "result", "detail"],
        qa_rows,
    )

    readme = """# Figure/portal Final Dependency Bridge Validator

This validator bridges final figure, source-data panel-map and portal-upload
readiness to the post-gate manual evidence bridge.

Boundary: read-only. It does not render final figures, lock panel maps, upload
portal files or mark the manuscript submission-ready.
"""
    write_text(OUT_DIR / "FIGURE_PORTAL_FINAL_DEPENDENCY_BRIDGE_VALIDATOR_README.md", readme)

    report = f"""# Figure/portal Final Dependency Bridge Validator Report

Status: `{summary["status"]}`

Current result:

1. Post-gate manual bridge allowed: {str(summary["post_gate_manual_bridge_allowed"]).lower()}
2. Figure final assets ready: {str(summary["figure_final_assets_ready"]).lower()}
3. Source-data panel map ready: {str(summary["source_data_panel_map_ready"]).lower()}
4. Figure portal upload allowed: {str(summary["figure_portal_upload_allowed"]).lower()}
5. Portal file upload allowed: {str(summary["portal_file_upload_allowed"]).lower()}
6. Portal upload ready: {str(summary["portal_upload_ready"]).lower()}
7. Submission ready: {str(summary["submission_ready"]).lower()}

Boundary: this package records final figure/portal dependencies only. It cannot
replace author approval, final export QA, panel-map locking, portal upload or
submission verification.
"""
    write_text(OUT_DIR / "figure_portal_final_dependency_bridge_validator_report.md", report)
    write_text(
        OUT_DIR / "figure_portal_final_dependency_bridge_validator_summary.json",
        json.dumps(summary, indent=2, ensure_ascii=False),
    )


if __name__ == "__main__":
    main()
