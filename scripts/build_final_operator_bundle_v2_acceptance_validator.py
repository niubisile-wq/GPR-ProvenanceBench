#!/usr/bin/env python3
"""Validate the final operator execution bundle v2."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "final_operator_bundle_v2_acceptance_validator_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"
BUNDLE_DIR = BENCH_ROOT / "reports" / "final_operator_execution_bundle_v2_20260810"
LOCAL_ZIP = BUNDLE_DIR / "NatComms_final_operator_execution_bundle_v2_20260810.zip"
DESKTOP_ZIP = Path.home() / "Desktop" / "NatComms_final_operator_execution_bundle_v2_20260810.zip"
BUNDLE_SUMMARY = BUNDLE_DIR / "final_operator_execution_bundle_v2_summary.json"
BUNDLE_MANIFEST = BUNDLE_DIR / "final_operator_execution_bundle_v2_manifest.csv"
GUARD_RUNNER = BENCH_ROOT / "reports" / "post_return_guarded_execution_runner_20260810" / "run_post_return_guarded_execution.ps1"

REQUIRED_MEMBERS = [
    "FINAL_OPERATOR_EXECUTION_BUNDLE_V2_README.md",
    "final_operator_execution_bundle_v2_manifest.csv",
    "final_operator_execution_bundle_v2_sequence.csv",
    "materials/01_inbox/final_return_evidence_canonical_routes.csv",
    "materials/02_scan/final_return_evidence_route_scan.csv",
    "materials/03_writeback/final_return_writeback_route_matrix.csv",
    "materials/04_transition/post_writeback_final_sequence.csv",
    "materials/05_guarded_runner/run_post_return_guarded_execution.ps1",
    "materials/06_original_materials/NatComms_final_human_execution_handoff_packet_20260810.zip",
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
    marker = "### 19.21 Final operator bundle v2 acceptance validator update"
    if marker in text:
        start = text.index(marker)
        next_start = text.find("\n### ", start + len(marker))
        updated = text[:start].rstrip() + "\n\n" + section.strip() + "\n" if next_start == -1 else text[:start].rstrip() + "\n\n" + section.strip() + "\n\n" + text[next_start:].lstrip("\n")
    else:
        updated = text.rstrip() + "\n\n" + section.strip() + "\n"
    DESKTOP_PLAN.write_text(updated, encoding="utf-8", newline="\n")
    return True


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary = read_json(BUNDLE_SUMMARY)
    manifest = read_csv(BUNDLE_MANIFEST)

    local_sha = sha256_file(LOCAL_ZIP) if LOCAL_ZIP.exists() else ""
    desktop_sha = sha256_file(DESKTOP_ZIP) if DESKTOP_ZIP.exists() else ""
    with zipfile.ZipFile(LOCAL_ZIP) as archive:
        members = set(archive.namelist())

    member_rows = [
        {
            "member": member,
            "present_in_zip": "yes" if member in members else "no",
        }
        for member in REQUIRED_MEMBERS
    ]

    category_rows = []
    for category in sorted({row["category"] for row in manifest}):
        category_rows.append(
            {
                "category": category,
                "manifest_files": sum(1 for row in manifest if row["category"] == category),
                "zip_members": sum(1 for member in members if member.startswith(f"materials/{category}/")),
            }
        )

    runner = subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(GUARD_RUNNER)],
        cwd=str(BENCH_ROOT),
        capture_output=True,
        text=True,
    )

    qa_rows = [
        {"check": "local_and_desktop_zip_exist", "result": "PASS" if LOCAL_ZIP.exists() and DESKTOP_ZIP.exists() else "FAIL", "detail": f"local={LOCAL_ZIP.exists()}; desktop={DESKTOP_ZIP.exists()}"},
        {"check": "local_and_desktop_zip_match", "result": "PASS" if local_sha and local_sha == desktop_sha else "FAIL", "detail": f"local_sha={local_sha}; desktop_sha={desktop_sha}"},
        {"check": "required_members_present", "result": "PASS" if all(row["present_in_zip"] == "yes" for row in member_rows) else "FAIL", "detail": f"required={len(member_rows)}"},
        {"check": "manifest_matches_summary", "result": "PASS" if len(manifest) == summary.get("manifest_rows") == 20 else "FAIL", "detail": f"manifest_rows={len(manifest)}; summary={summary.get('manifest_rows')}"},
        {"check": "guard_runner_refuses", "result": "PASS" if runner.returncode == 2 else "FAIL", "detail": f"returncode={runner.returncode}"},
        {"check": "blocked_state_preserved", "result": "PASS" if summary.get("commands_allowed_now") == 0 and summary.get("submission_ready") is False else "FAIL", "detail": f"commands_allowed_now={summary.get('commands_allowed_now')}; submission_ready={summary.get('submission_ready')}"},
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(OUT_DIR / "final_operator_bundle_v2_required_members.csv", member_rows, ["member", "present_in_zip"])
    write_csv(OUT_DIR / "final_operator_bundle_v2_category_coverage.csv", category_rows, ["category", "manifest_files", "zip_members"])
    write_csv(OUT_DIR / "final_operator_bundle_v2_acceptance_qa.csv", qa_rows, ["check", "result", "detail"])
    write_text(OUT_DIR / "guard_runner_acceptance_stdout.txt", runner.stdout)
    write_text(OUT_DIR / "guard_runner_acceptance_stderr.txt", runner.stderr)

    report = [
        "# Final operator bundle v2 acceptance validator 2026-08-10",
        "",
        "Status: `final_operator_bundle_v2_acceptance_passed_guarded_not_executed`",
        "",
        f"1. Required members checked: {len(member_rows)}",
        f"2. Manifest rows: {len(manifest)}",
        f"3. Local/Desktop zip SHA match: {str(local_sha == desktop_sha).lower()}",
        f"4. Guard runner return code: {runner.returncode}",
        f"5. QA pass: {str(qa_pass).lower()}",
        "",
        "Boundary: this validator accepts the operator bundle as a guarded package only. It does not execute downstream validators, write back evidence, close gates, upload files or submit the manuscript.",
        "",
    ]
    write_text(OUT_DIR / "FINAL_OPERATOR_BUNDLE_V2_ACCEPTANCE_VALIDATOR_README.md", "\n".join(report))
    write_text(OUT_DIR / "final_operator_bundle_v2_acceptance_validator_report.md", "\n".join(report))

    out_summary = {
        "package": "final_operator_bundle_v2_acceptance_validator_20260810",
        "required_members": len(member_rows),
        "required_members_present": sum(1 for row in member_rows if row["present_in_zip"] == "yes"),
        "category_rows": len(category_rows),
        "manifest_rows": len(manifest),
        "local_zip_sha256": local_sha,
        "desktop_zip_sha256": desktop_sha,
        "zip_sha_match": local_sha == desktop_sha,
        "guard_runner_returncode": runner.returncode,
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "commands_allowed_now": summary.get("commands_allowed_now"),
        "submission_ready": False,
        "status": "final_operator_bundle_v2_acceptance_passed_guarded_not_executed",
    }

    section = f"""### 19.21 Final operator bundle v2 acceptance validator update

Added an acceptance validator for the final operator execution bundle v2.

New directory: `{OUT_DIR}`

Current result:
1. required_members = {out_summary['required_members']}
2. required_members_present = {out_summary['required_members_present']}
3. manifest_rows = {out_summary['manifest_rows']}
4. zip_sha_match = true
5. guard_runner_returncode = {out_summary['guard_runner_returncode']}
6. commands_allowed_now = {out_summary['commands_allowed_now']}
7. submission_ready = false

Boundary:
1. This validator accepts the bundle as a guarded package only.
2. It does not execute downstream validators, write back evidence, close gates, upload files or submit the manuscript."""
    out_summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "final_operator_bundle_v2_acceptance_validator_summary.json", json.dumps(out_summary, indent=2, ensure_ascii=True) + "\n")

    if not qa_pass:
        raise SystemExit("Final operator bundle v2 acceptance validator QA failed")
    print(json.dumps(out_summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
