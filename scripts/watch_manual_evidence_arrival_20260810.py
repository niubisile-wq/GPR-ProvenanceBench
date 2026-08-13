#!/usr/bin/env python3
"""Watch mapped manual evidence locations and forms for newly arrived evidence."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "manual_evidence_arrival_watcher_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"

IGNORED_NAMES = {".gitkeep"}
IGNORED_PREFIXES = ("README",)
FORM_EMPTY_VALUES = {"", "not_checked", "no", "not_run"}


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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def list_candidate_files(location: str) -> list[Path]:
    root = Path(location)
    if not root.is_absolute():
        root = BENCH_ROOT / root
    if root.is_file():
        return [root]
    if not root.exists():
        return []
    files = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.name in IGNORED_NAMES:
            continue
        if any(path.name.startswith(prefix) for prefix in IGNORED_PREFIXES):
            continue
        files.append(path)
    return sorted(files)


def form_fill_count(form_file: str) -> tuple[int, int]:
    path = BENCH_ROOT / form_file
    if not path.exists():
        return 0, 13
    rows = read_csv(path)
    if not rows:
        return 0, 13
    row = rows[0]
    considered = [
        "performed_by",
        "performed_at_local_time",
        "evidence_file_or_folder",
        "evidence_sha256",
        "source_channel",
        "counterparty_or_owner",
        "decision_or_return_summary",
        "sensitive_content_checked",
        "validator_ran",
        "validator_result",
    ]
    filled = sum(1 for field in considered if row.get(field, "").strip().lower() not in FORM_EMPTY_VALUES)
    return filled, len(considered)


def update_desktop_plan(summary: dict[str, object]) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    marker = "### 19.88 Manual evidence arrival watcher update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- Added `reports/manual_evidence_arrival_watcher_20260810/` to scan the five manual evidence locations and MOF forms for real evidence arrival.
- Current `watched_locations={summary["watched_locations"]}`, `candidate_files_detected={summary["candidate_files_detected"]}`, `forms_with_any_fill={summary["forms_with_any_fill"]}`.
- Current `ready_for_validation_rows={summary["ready_for_validation_rows"]}`, `allowed_commands_now=0`, `portal_upload_allowed=false`, `submission_ready=false`.
- Boundary: this watcher is read-only. It does not move files, fill forms, compute acceptance for evidence, run validators, execute writeback, run recheck, upload portal files or submit.
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

    form_index = read_csv(BENCH_ROOT / "reports" / "manual_only_execution_forms_20260810" / "manual_only_execution_forms_index.csv")
    validation_summary = read_json(
        BENCH_ROOT
        / "reports"
        / "manual_only_execution_forms_validation_20260810"
        / "manual_only_execution_forms_validation_summary.json"
    )
    acceptance_summary = read_json(
        BENCH_ROOT
        / "reports"
        / "manual_execution_brief_acceptance_20260810"
        / "manual_execution_brief_acceptance_summary.json"
    )

    location_rows = []
    candidate_rows = []
    form_rows = []
    readiness_rows = []

    for form in form_index:
        candidates = list_candidate_files(form["evidence_source"])
        location_rows.append(
            {
                "form_id": form["form_id"],
                "primary_fmr": form["primary_fmr"],
                "phase": form["phase"],
                "evidence_location": form["evidence_source"],
                "candidate_files": len(candidates),
                "location_status": "has_candidate_files" if candidates else "empty_or_support_only",
            }
        )
        for path in candidates:
            candidate_rows.append(
                {
                    "form_id": form["form_id"],
                    "primary_fmr": form["primary_fmr"],
                    "path": str(path.relative_to(BENCH_ROOT)) if path.is_relative_to(BENCH_ROOT) else str(path),
                    "bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
            )
        filled, total = form_fill_count(form["form_file"])
        form_rows.append(
            {
                "form_id": form["form_id"],
                "primary_fmr": form["primary_fmr"],
                "form_file": form["form_file"],
                "filled_cells": filled,
                "tracked_cells": total,
                "form_has_any_fill": "yes" if filled > 0 else "no",
            }
        )
        ready_for_validation = len(candidates) > 0 and filled == total
        readiness_rows.append(
            {
                "form_id": form["form_id"],
                "primary_fmr": form["primary_fmr"],
                "candidate_files": len(candidates),
                "filled_cells": filled,
                "tracked_cells": total,
                "ready_for_19_84_validation": "yes" if ready_for_validation else "no",
                "next_action": (
                    "Run py scripts/validate_manual_only_execution_forms_20260810.py"
                    if ready_for_validation
                    else "Place real evidence and complete the matching MOF form."
                ),
                "downstream_validator_allowed_now": "no",
                "writeback_allowed_now": "no",
            }
        )

    candidate_files_detected = len(candidate_rows)
    forms_with_any_fill = sum(1 for row in form_rows if row["form_has_any_fill"] == "yes")
    ready_for_validation_rows = sum(1 for row in readiness_rows if row["ready_for_19_84_validation"] == "yes")

    qa_rows = [
        {
            "check": "watcher covers five manual evidence locations",
            "result": "PASS" if len(location_rows) == 5 else "FAIL",
            "detail": f"watched_locations={len(location_rows)}",
        },
        {
            "check": "current state has no candidate files",
            "result": "PASS" if candidate_files_detected == 0 else "FAIL",
            "detail": f"candidate_files_detected={candidate_files_detected}",
        },
        {
            "check": "current forms are still blank",
            "result": "PASS" if forms_with_any_fill == 0 else "FAIL",
            "detail": f"forms_with_any_fill={forms_with_any_fill}",
        },
        {
            "check": "handoff acceptance remains ready but unexecuted",
            "result": "PASS" if acceptance_summary.get("handoff_acceptance_ready") and not acceptance_summary.get("manual_actions_executed") else "FAIL",
            "detail": (
                f"handoff_acceptance_ready={acceptance_summary.get('handoff_acceptance_ready')}; "
                f"manual_actions_executed={acceptance_summary.get('manual_actions_executed')}"
            ),
        },
        {
            "check": "form validation remains blocked",
            "result": "PASS" if validation_summary.get("validated_form_rows") == 0 else "FAIL",
            "detail": f"validated_form_rows={validation_summary.get('validated_form_rows')}",
        },
    ]

    summary = {
        "package": "manual_evidence_arrival_watcher_20260810",
        "watched_locations": len(location_rows),
        "candidate_files_detected": candidate_files_detected,
        "forms_with_any_fill": forms_with_any_fill,
        "ready_for_validation_rows": ready_for_validation_rows,
        "validated_form_rows": int(validation_summary.get("validated_form_rows", 0) or 0),
        "handoff_acceptance_ready": bool(acceptance_summary.get("handoff_acceptance_ready")),
        "manual_actions_executed": False,
        "allowed_commands_now": 0,
        "portal_upload_allowed": False,
        "submission_ready": False,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": "manual_evidence_arrival_watcher_ready_waiting_candidate_files",
    }
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(
        OUT_DIR / "manual_evidence_watched_locations.csv",
        ["form_id", "primary_fmr", "phase", "evidence_location", "candidate_files", "location_status"],
        location_rows,
    )
    write_csv(OUT_DIR / "manual_evidence_detected_candidates.csv", ["form_id", "primary_fmr", "path", "bytes", "sha256"], candidate_rows)
    write_csv(
        OUT_DIR / "manual_evidence_form_fill_status.csv",
        ["form_id", "primary_fmr", "form_file", "filled_cells", "tracked_cells", "form_has_any_fill"],
        form_rows,
    )
    write_csv(
        OUT_DIR / "manual_evidence_arrival_next_routes.csv",
        [
            "form_id",
            "primary_fmr",
            "candidate_files",
            "filled_cells",
            "tracked_cells",
            "ready_for_19_84_validation",
            "next_action",
            "downstream_validator_allowed_now",
            "writeback_allowed_now",
        ],
        readiness_rows,
    )
    write_csv(OUT_DIR / "manual_evidence_arrival_watcher_qa.csv", ["check", "result", "detail"], qa_rows)

    report = f"""# Manual Evidence Arrival Watcher

Status: `{summary["status"]}`

Current result:

1. Watched locations: {summary["watched_locations"]}
2. Candidate files detected: {summary["candidate_files_detected"]}
3. Forms with any fill: {summary["forms_with_any_fill"]}
4. Ready for 19.84 validation rows: {summary["ready_for_validation_rows"]}
5. Validated form rows: {summary["validated_form_rows"]}
6. Handoff acceptance ready: {str(summary["handoff_acceptance_ready"]).lower()}
7. Manual actions executed: false
8. Allowed commands now: 0
9. Portal upload allowed: false
10. Submission ready: false

Boundary: this watcher is read-only. It does not move files, fill forms,
compute acceptance for evidence, run validators, execute writeback, run recheck,
upload portal files or submit.
"""
    write_text(OUT_DIR / "MANUAL_EVIDENCE_ARRIVAL_WATCHER_README.md", report)
    write_text(OUT_DIR / "manual_evidence_arrival_watcher_report.md", report)
    write_text(OUT_DIR / "manual_evidence_arrival_watcher_summary.json", json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
