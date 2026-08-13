#!/usr/bin/env python3
"""Build the final operator execution bundle v2 with all current guard layers."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import zipfile
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "final_operator_execution_bundle_v2_20260810"
MATERIALS_DIR = OUT_DIR / "materials"
DESKTOP = Path.home() / "Desktop"
DESKTOP_PLAN = DESKTOP / "8月10日cns.md"
LOCAL_ZIP = OUT_DIR / "NatComms_final_operator_execution_bundle_v2_20260810.zip"
DESKTOP_ZIP = DESKTOP / "NatComms_final_operator_execution_bundle_v2_20260810.zip"

SUMMARY_INPUTS = {
    "handoff_packet": BENCH_ROOT / "reports" / "final_human_execution_handoff_packet_20260810" / "final_human_execution_handoff_packet_summary.json",
    "inbox_scaffold": BENCH_ROOT / "reports" / "final_return_evidence_inbox_scaffold_20260810" / "final_return_evidence_inbox_scaffold_summary.json",
    "intake_scanner": BENCH_ROOT / "reports" / "final_return_evidence_intake_scanner_20260810" / "final_return_evidence_intake_scanner_summary.json",
    "writeback_preflight": BENCH_ROOT / "reports" / "final_return_evidence_writeback_preflight_20260810" / "final_return_evidence_writeback_preflight_summary.json",
    "transition_validator": BENCH_ROOT / "reports" / "post_writeback_gate_transition_validator_20260810" / "post_writeback_gate_transition_validator_summary.json",
    "guarded_runner": BENCH_ROOT / "reports" / "post_return_guarded_execution_runner_20260810" / "post_return_guarded_execution_runner_summary.json",
}

SOURCE_FILES = [
    ("00_read_first", "final_human_execution_return_routing.csv", BENCH_ROOT / "reports" / "final_human_execution_handoff_packet_20260810" / "final_human_execution_return_routing.csv"),
    ("00_read_first", "final_human_execution_operator_checklist.csv", BENCH_ROOT / "reports" / "final_human_execution_handoff_packet_20260810" / "final_human_execution_operator_checklist.csv"),
    ("00_read_first", "final_human_execution_validation_commands.csv", BENCH_ROOT / "reports" / "final_human_execution_handoff_packet_20260810" / "final_human_execution_validation_commands.csv"),
    ("01_inbox", "final_return_evidence_canonical_routes.csv", BENCH_ROOT / "reports" / "final_return_evidence_inbox_scaffold_20260810" / "final_return_evidence_canonical_routes.csv"),
    ("01_inbox", "final_return_evidence_folder_manifest.csv", BENCH_ROOT / "reports" / "final_return_evidence_inbox_scaffold_20260810" / "final_return_evidence_folder_manifest.csv"),
    ("01_inbox", "FINAL_RETURN_EVIDENCE_INBOX_SCAFFOLD_README.md", BENCH_ROOT / "reports" / "final_return_evidence_inbox_scaffold_20260810" / "FINAL_RETURN_EVIDENCE_INBOX_SCAFFOLD_README.md"),
    ("02_scan", "final_return_evidence_route_scan.csv", BENCH_ROOT / "reports" / "final_return_evidence_intake_scanner_20260810" / "final_return_evidence_route_scan.csv"),
    ("02_scan", "final_return_evidence_next_validation_commands.csv", BENCH_ROOT / "reports" / "final_return_evidence_intake_scanner_20260810" / "final_return_evidence_next_validation_commands.csv"),
    ("02_scan", "FINAL_RETURN_EVIDENCE_INTAKE_SCANNER_README.md", BENCH_ROOT / "reports" / "final_return_evidence_intake_scanner_20260810" / "FINAL_RETURN_EVIDENCE_INTAKE_SCANNER_README.md"),
    ("03_writeback", "final_return_writeback_route_matrix.csv", BENCH_ROOT / "reports" / "final_return_evidence_writeback_preflight_20260810" / "final_return_writeback_route_matrix.csv"),
    ("03_writeback", "final_return_writeback_protected_targets.csv", BENCH_ROOT / "reports" / "final_return_evidence_writeback_preflight_20260810" / "final_return_writeback_protected_targets.csv"),
    ("03_writeback", "FINAL_RETURN_EVIDENCE_WRITEBACK_PREFLIGHT_README.md", BENCH_ROOT / "reports" / "final_return_evidence_writeback_preflight_20260810" / "FINAL_RETURN_EVIDENCE_WRITEBACK_PREFLIGHT_README.md"),
    ("04_transition", "post_writeback_route_transition_matrix.csv", BENCH_ROOT / "reports" / "post_writeback_gate_transition_validator_20260810" / "post_writeback_route_transition_matrix.csv"),
    ("04_transition", "post_writeback_final_sequence.csv", BENCH_ROOT / "reports" / "post_writeback_gate_transition_validator_20260810" / "post_writeback_final_sequence.csv"),
    ("04_transition", "POST_WRITEBACK_GATE_TRANSITION_VALIDATOR_README.md", BENCH_ROOT / "reports" / "post_writeback_gate_transition_validator_20260810" / "POST_WRITEBACK_GATE_TRANSITION_VALIDATOR_README.md"),
    ("05_guarded_runner", "post_return_guarded_command_plan.csv", BENCH_ROOT / "reports" / "post_return_guarded_execution_runner_20260810" / "post_return_guarded_command_plan.csv"),
    ("05_guarded_runner", "post_return_global_guard_state.csv", BENCH_ROOT / "reports" / "post_return_guarded_execution_runner_20260810" / "post_return_global_guard_state.csv"),
    ("05_guarded_runner", "run_post_return_guarded_execution.ps1", BENCH_ROOT / "reports" / "post_return_guarded_execution_runner_20260810" / "run_post_return_guarded_execution.ps1"),
    ("05_guarded_runner", "POST_RETURN_GUARDED_EXECUTION_RUNNER_README.md", BENCH_ROOT / "reports" / "post_return_guarded_execution_runner_20260810" / "POST_RETURN_GUARDED_EXECUTION_RUNNER_README.md"),
    ("06_original_materials", "NatComms_final_human_execution_handoff_packet_20260810.zip", BENCH_ROOT / "reports" / "final_human_execution_handoff_packet_20260810" / "NatComms_final_human_execution_handoff_packet_20260810.zip"),
]


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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def update_desktop_plan(section: str) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    marker = "### 19.20 Final operator execution bundle v2 update"
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
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    MATERIALS_DIR.mkdir(parents=True, exist_ok=True)

    summaries = {name: read_json(path) for name, path in SUMMARY_INPUTS.items()}
    manifest_rows: list[dict[str, object]] = []
    missing_files: list[str] = []

    for category, name, source in SOURCE_FILES:
        if not source.exists():
            missing_files.append(str(source))
            continue
        target_dir = MATERIALS_DIR / category
        target_dir.mkdir(parents=True, exist_ok=True)
        dest = target_dir / name
        shutil.copy2(source, dest)
        manifest_rows.append(
            {
                "category": category,
                "file_name": name,
                "source_path": str(source),
                "bundle_path": str(dest.relative_to(OUT_DIR)),
                "bytes": dest.stat().st_size,
                "sha256": sha256_file(dest),
            }
        )

    readme = [
        "# NatComms final operator execution bundle v2",
        "",
        "Use this bundle after real human-returned evidence is available.",
        "",
        "Current state: all post-return commands are guarded and refused because no returned evidence, protected writeback, gate transition, or submission readiness condition is met.",
        "",
        "Execution order:",
        "1. Put real returned files into the canonical folders under `final_return_evidence_inbox_20260810`.",
        "2. Regenerate the final return evidence intake scanner.",
        "3. Run the writeback preflight and manually inspect allowed protected fields.",
        "4. Only after protected writeback is documented, regenerate the gate transition validator.",
        "5. Use the guarded runner; it must refuse execution until guard conditions pass.",
        "",
        "Do not upload portal files or submit the manuscript from this bundle.",
        "",
    ]
    write_text(OUT_DIR / "FINAL_OPERATOR_EXECUTION_BUNDLE_V2_README.md", "\n".join(readme))

    operator_sequence_rows = [
        {"sequence": 1, "stage": "return_evidence_drop", "artifact": "materials/01_inbox/final_return_evidence_canonical_routes.csv", "allowed_now": "manual_only"},
        {"sequence": 2, "stage": "scan_return_evidence", "artifact": "materials/02_scan/final_return_evidence_route_scan.csv", "allowed_now": "diagnostic_only"},
        {"sequence": 3, "stage": "protected_writeback_preflight", "artifact": "materials/03_writeback/final_return_writeback_route_matrix.csv", "allowed_now": "no"},
        {"sequence": 4, "stage": "gate_transition_validation", "artifact": "materials/04_transition/post_writeback_final_sequence.csv", "allowed_now": "no"},
        {"sequence": 5, "stage": "guarded_command_runner", "artifact": "materials/05_guarded_runner/run_post_return_guarded_execution.ps1", "allowed_now": "refuses_execution"},
        {"sequence": 6, "stage": "original_handoff_materials", "artifact": "materials/06_original_materials/NatComms_final_human_execution_handoff_packet_20260810.zip", "allowed_now": "reference_only"},
    ]
    write_csv(OUT_DIR / "final_operator_execution_bundle_v2_manifest.csv", manifest_rows, ["category", "file_name", "source_path", "bundle_path", "bytes", "sha256"])
    write_csv(OUT_DIR / "final_operator_execution_bundle_v2_sequence.csv", operator_sequence_rows, ["sequence", "stage", "artifact", "allowed_now"])

    if LOCAL_ZIP.exists():
        LOCAL_ZIP.unlink()
    with zipfile.ZipFile(LOCAL_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(OUT_DIR.rglob("*")):
            if path == LOCAL_ZIP or path.is_dir():
                continue
            archive.write(path, path.relative_to(OUT_DIR).as_posix())
    shutil.copy2(LOCAL_ZIP, DESKTOP_ZIP)
    with zipfile.ZipFile(LOCAL_ZIP) as archive:
        zip_members = len(archive.namelist())

    qa_rows = [
        {
            "check": "all_source_files_present",
            "result": "PASS" if not missing_files else "FAIL",
            "detail": f"missing_files={len(missing_files)}",
        },
        {
            "check": "all_guard_layers_imported",
            "result": "PASS" if len(manifest_rows) == len(SOURCE_FILES) else "FAIL",
            "detail": f"manifest_rows={len(manifest_rows)}; expected={len(SOURCE_FILES)}",
        },
        {
            "check": "desktop_zip_created",
            "result": "PASS" if LOCAL_ZIP.exists() and DESKTOP_ZIP.exists() and zip_members >= len(manifest_rows) else "FAIL",
            "detail": f"local_zip={LOCAL_ZIP.exists()}; desktop_zip={DESKTOP_ZIP.exists()}; zip_members={zip_members}",
        },
        {
            "check": "blocked_state_preserved",
            "result": "PASS"
            if summaries["guarded_runner"].get("commands_allowed_now") == 0
            and summaries["transition_validator"].get("submission_ready") is False
            else "FAIL",
            "detail": f"commands_allowed_now={summaries['guarded_runner'].get('commands_allowed_now')}; submission_ready={summaries['transition_validator'].get('submission_ready')}",
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)
    write_csv(OUT_DIR / "final_operator_execution_bundle_v2_qa.csv", qa_rows, ["check", "result", "detail"])

    report = [
        "# Final operator execution bundle v2 2026-08-10",
        "",
        "Status: `final_operator_execution_bundle_v2_ready_guarded_not_executed`",
        "",
        f"1. Source files bundled: {len(manifest_rows)}",
        f"2. Zip members: {zip_members}",
        f"3. Desktop zip: `{DESKTOP_ZIP}`",
        f"4. Commands allowed now: {summaries['guarded_runner'].get('commands_allowed_now')}",
        f"5. Submission ready: {summaries['transition_validator'].get('submission_ready')}",
        f"6. QA pass: {str(qa_pass).lower()}",
        "",
        "Boundary: this bundle packages current operator materials only. It does not execute commands, write back evidence, close gates, upload files or submit the manuscript.",
        "",
    ]
    write_text(OUT_DIR / "final_operator_execution_bundle_v2_report.md", "\n".join(report))

    summary = {
        "package": "final_operator_execution_bundle_v2_20260810",
        "manifest_rows": len(manifest_rows),
        "missing_files": len(missing_files),
        "operator_sequence_rows": len(operator_sequence_rows),
        "zip_members": zip_members,
        "local_zip": str(LOCAL_ZIP),
        "local_zip_exists": LOCAL_ZIP.exists(),
        "desktop_zip": str(DESKTOP_ZIP),
        "desktop_zip_exists": DESKTOP_ZIP.exists(),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "commands_allowed_now": summaries["guarded_runner"].get("commands_allowed_now"),
        "candidate_return_files": summaries["intake_scanner"].get("candidate_return_files"),
        "writeback_allowed_rows": summaries["writeback_preflight"].get("writeback_allowed_rows"),
        "transition_allowed_rows": summaries["transition_validator"].get("transition_allowed_rows"),
        "submission_ready": False,
        "status": "final_operator_execution_bundle_v2_ready_guarded_not_executed",
    }

    section = f"""### 19.20 Final operator execution bundle v2 update

Added a final operator execution bundle v2 that packages the current handoff materials plus the canonical inbox, scanner, writeback preflight, gate-transition validator and guarded runner.

New directory: `{OUT_DIR}`

Desktop zip:
`{DESKTOP_ZIP}`

New files:
1. `final_operator_execution_bundle_v2_manifest.csv`
2. `final_operator_execution_bundle_v2_sequence.csv`
3. `final_operator_execution_bundle_v2_qa.csv`
4. `FINAL_OPERATOR_EXECUTION_BUNDLE_V2_README.md`
5. `final_operator_execution_bundle_v2_report.md`
6. `final_operator_execution_bundle_v2_summary.json`
7. `NatComms_final_operator_execution_bundle_v2_20260810.zip`

Current result:
1. manifest_rows = {summary['manifest_rows']}
2. operator_sequence_rows = {summary['operator_sequence_rows']}
3. zip_members = {summary['zip_members']}
4. desktop_zip_exists = true
5. commands_allowed_now = {summary['commands_allowed_now']}
6. candidate_return_files = {summary['candidate_return_files']}
7. writeback_allowed_rows = {summary['writeback_allowed_rows']}
8. transition_allowed_rows = {summary['transition_allowed_rows']}
9. submission_ready = false

Boundary:
1. This bundle packages current operator materials only.
2. It does not execute commands, write back evidence, close gates, upload files or submit the manuscript.
3. The guarded runner remains the only post-return execution entry point."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "final_operator_execution_bundle_v2_summary.json", json.dumps(summary, indent=2, ensure_ascii=True) + "\n")

    if not qa_pass:
        raise SystemExit("Final operator execution bundle v2 QA failed")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
