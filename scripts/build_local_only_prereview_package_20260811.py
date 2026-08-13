#!/usr/bin/env python3
"""Build a local-only pre-review package that avoids unavailable manual actions."""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "local_only_prereview_package_20260811"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"
DESKTOP_GUIDE = Path.home() / "Desktop" / "NatComms_20260811_local_only_prereview_package.md"


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


def copy_if_exists(source: Path, target_name: str) -> str:
    target = OUT_DIR / "package_files" / target_name
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.exists():
        shutil.copy2(source, target)
        return str(target.relative_to(BENCH_ROOT))
    return ""


def update_desktop_plan(summary: dict[str, object]) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    marker = "### 20.01 Local-only pre-review package update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- Added `reports/local_only_prereview_package_20260811/` and Desktop guide `NatComms_20260811_local_only_prereview_package.md` as a workaround for unavailable external/manual actions.
- Current `local_prereview_ready={str(summary["local_prereview_ready"]).lower()}`, `included_items={summary["included_items"]}`, `excluded_formal_submission_items={summary["excluded_formal_submission_items"]}`.
- Current `formal_submission_ready=false`, `portal_upload_allowed=false`, `external_manual_actions_required_for_formal_submission=true`.
- Boundary: this is a local pre-review package only. It does not claim formal submission readiness, replace external evidence, run writeback/recheck, upload portal files or submit.
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

    assembly_items = read_csv(
        BENCH_ROOT
        / "reports"
        / "natcomms_submission_assembly_preflight_20260810"
        / "natcomms_submission_item_preflight.csv"
    )
    assembly_summary = read_json(
        BENCH_ROOT
        / "reports"
        / "natcomms_submission_assembly_preflight_20260810"
        / "natcomms_submission_assembly_preflight_summary.json"
    )
    blocker_summary = read_json(
        BENCH_ROOT
        / "reports"
        / "external_manual_evidence_blocker_certificate_20260810"
        / "external_manual_evidence_blocker_certificate_summary.json"
    )

    included = []
    excluded = []
    for item in assembly_items:
        if item["assembly_status"] == "preassemblable":
            included.append(
                {
                    "submission_item": item["submission_item"],
                    "source_artifact": item["current_artifact"],
                    "current_status": item["current_status"],
                    "local_use": "include_for_internal_prereview",
                    "formal_submission_boundary": item["blocking_condition"],
                }
            )
        else:
            excluded.append(
                {
                    "submission_item": item["submission_item"],
                    "source_artifact": item["current_artifact"],
                    "current_status": item["current_status"],
                    "reason_excluded": item["blocking_condition"],
                    "minimum_final_evidence": item["minimum_final_evidence"],
                }
            )

    copied_rows = [
        {
            "package_file": copy_if_exists(
                BENCH_ROOT
                / "reports"
                / "natcomms_initial_submission_text_preassembly_20260810"
                / "natcomms_initial_submission_text_preassembly.md",
                "natcomms_initial_submission_text_preassembly.md",
            ),
            "source_role": "preassembled manuscript text",
        },
        {
            "package_file": copy_if_exists(
                BENCH_ROOT / "reports" / "submission_package_skeleton_20260810" / "title_abstract_significance.md",
                "title_abstract_significance.md",
            ),
            "source_role": "title abstract significance skeleton",
        },
        {
            "package_file": copy_if_exists(
                BENCH_ROOT / "reports" / "submission_package_skeleton_20260810" / "cover_letter_skeleton.md",
                "cover_letter_skeleton.md",
            ),
            "source_role": "cover letter skeleton",
        },
    ]
    copied_rows = [row for row in copied_rows if row["package_file"]]

    next_actions = [
        {
            "priority": 1,
            "action": "Use the local package for internal scientific review and prose editing.",
            "allowed_now": "yes",
            "does_not_require_external_manual_action": "yes",
        },
        {
            "priority": 2,
            "action": "Revise text, title, abstract and cover letter within local package boundaries.",
            "allowed_now": "yes",
            "does_not_require_external_manual_action": "yes",
        },
        {
            "priority": 3,
            "action": "Submit to journal portal.",
            "allowed_now": "no",
            "does_not_require_external_manual_action": "no",
        },
    ]

    qa_rows = [
        {
            "check": "preassemblable items are included",
            "result": "PASS" if len(included) == int(assembly_summary.get("preassemblable_items", 0)) else "FAIL",
            "detail": f"included={len(included)}; expected={assembly_summary.get('preassemblable_items')}",
        },
        {
            "check": "blocked formal submission items are excluded",
            "result": "PASS" if len(excluded) == int(assembly_summary.get("blocked_items", 0)) else "FAIL",
            "detail": f"excluded={len(excluded)}; expected={assembly_summary.get('blocked_items')}",
        },
        {
            "check": "external manual blocker is preserved",
            "result": "PASS" if blocker_summary.get("goal_complete") is False else "FAIL",
            "detail": f"goal_complete={blocker_summary.get('goal_complete')}",
        },
        {
            "check": "package files copied",
            "result": "PASS" if len(copied_rows) == 3 else "FAIL",
            "detail": f"copied_files={len(copied_rows)}",
        },
    ]

    summary = {
        "package": "local_only_prereview_package_20260811",
        "local_prereview_ready": True,
        "included_items": len(included),
        "excluded_formal_submission_items": len(excluded),
        "copied_package_files": len(copied_rows),
        "formal_submission_ready": False,
        "portal_upload_allowed": False,
        "external_manual_actions_required_for_formal_submission": True,
        "submission_ready": False,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "desktop_guide": str(DESKTOP_GUIDE),
        "desktop_guide_exists": True,
        "status": "local_only_prereview_package_ready_formal_submission_blocked",
    }

    guide = f"""# Local-only Pre-review Package

Purpose: provide a usable path when external/manual actions cannot be done.

This package is ready for internal pre-review, text editing and scientific
argument review. It is not a formal journal submission package.

Included now:

1. Preassembled manuscript text.
2. Title, abstract and significance skeleton.
3. Cover letter skeleton.

Excluded from formal submission:

"""
    for row in excluded:
        guide += f"- {row['submission_item']}: {row['reason_excluded']}\n"
    guide += """
Allowed next actions:

1. Review and revise the copied local package files.
2. Improve prose, framing, claims and cover letter.
3. Keep formal submission, portal upload, writeback and guarded recheck blocked.

Boundary: this package does not replace external evidence, author decisions,
figure approvals, DOI/licence/rights clearance or final portal checks.
"""

    write_csv(
        OUT_DIR / "local_only_prereview_included_items.csv",
        ["submission_item", "source_artifact", "current_status", "local_use", "formal_submission_boundary"],
        included,
    )
    write_csv(
        OUT_DIR / "local_only_prereview_excluded_formal_items.csv",
        ["submission_item", "source_artifact", "current_status", "reason_excluded", "minimum_final_evidence"],
        excluded,
    )
    write_csv(OUT_DIR / "local_only_prereview_copied_files.csv", ["package_file", "source_role"], copied_rows)
    write_csv(OUT_DIR / "local_only_prereview_next_actions.csv", ["priority", "action", "allowed_now", "does_not_require_external_manual_action"], next_actions)
    write_csv(OUT_DIR / "local_only_prereview_package_qa.csv", ["check", "result", "detail"], qa_rows)
    write_text(OUT_DIR / "LOCAL_ONLY_PREREVIEW_PACKAGE_README.md", guide)
    write_text(OUT_DIR / "local_only_prereview_package_report.md", guide)
    write_text(DESKTOP_GUIDE, guide)
    summary["desktop_plan_updated"] = update_desktop_plan(summary)
    write_text(OUT_DIR / "local_only_prereview_package_summary.json", json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
