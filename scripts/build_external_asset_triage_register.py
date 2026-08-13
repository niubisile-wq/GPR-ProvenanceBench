#!/usr/bin/env python3
"""Build a triage register for real external blind asset acquisition."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "external_asset_triage_register_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"

READINESS_SUMMARY = REPORTS / "external_validation_readiness_20260810" / "external_validation_readiness_summary.json"
ACQUISITION_SUMMARY = REPORTS / "blind_external_acquisition_package_20260810" / "blind_external_acquisition_package_summary.json"
REQUEST_ITEMS = REPORTS / "blind_external_acquisition_package_20260810" / "external_asset_request_items.csv"
HANDOFF_CHECKLIST = REPORTS / "blind_external_acquisition_package_20260810" / "blind_handoff_checklist.csv"
RIGHTS_CHECKLIST = REPORTS / "blind_external_acquisition_package_20260810" / "external_asset_rights_checklist.csv"
EXTERNAL_WORKSPACE = BENCH_ROOT / "external_blind"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def update_desktop_plan(section: str) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    text = DESKTOP_PLAN.read_text(encoding="utf-8")
    marker = "### 18.75 External asset triage register update"
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


def external_workspace_payload_count() -> int:
    if not EXTERNAL_WORKSPACE.exists():
        return 0
    return sum(1 for path in EXTERNAL_WORKSPACE.rglob("*") if path.is_file() and path.name != "README_20260810.md")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    readiness = read_json(READINESS_SUMMARY)
    acquisition = read_json(ACQUISITION_SUMMARY)
    request_rows = read_csv(REQUEST_ITEMS)
    handoff_rows = read_csv(HANDOFF_CHECKLIST)
    rights_rows = read_csv(RIGHTS_CHECKLIST)
    tracks = readiness.get("tracks", [])
    payload_files = external_workspace_payload_count()

    route_rows: list[dict[str, object]] = []
    for track in tracks:
        track_id = track["track_id"]
        if track_id == "A":
            route_priority = 2
            contact_target = "authorized TIGPR/Mendeley source access route"
            request_mode = "restore_public_source_media"
            triage_decision = "candidate_if_authorized_source_tree_is_recovered"
        elif track_id == "B":
            route_priority = 1
            contact_target = "advisor, collaborator or third-party GPR data holder"
            request_mode = "request_new_unlabeled_blind_asset"
            triage_decision = "primary_route_for_real_blind_external_validation"
        elif track_id == "C":
            route_priority = 3
            contact_target = "4TU-like raw-trace data holder with better project/label balance"
            request_mode = "request_balanced_raw_trace_asset"
            triage_decision = "candidate_stress_test_extension_not_current_main_route"
        else:
            route_priority = 4
            contact_target = "none"
            request_mode = "do_not_use_as_blind_external"
            triage_decision = "exclude_from_blind_external_claim"
        route_rows.append(
            {
                "route_priority": route_priority,
                "track_id": track_id,
                "track_name": track["name"],
                "current_status": track["current_status"],
                "contact_target": contact_target,
                "request_mode": request_mode,
                "triage_decision": triage_decision,
                "next_action": track["next_action"],
                "can_close_blind_gate_now": "no",
            }
        )

    route_rows = sorted(route_rows, key=lambda row: int(row["route_priority"]))

    acceptance_rows = [
        {
            "gate_id": "EXT-ACCEPT-001",
            "requirement": "asset_independence",
            "minimum_evidence": "Written confirmation that the asset was not used for model development, model selection, threshold tuning or figure selection.",
            "pass_condition": "confirmation_received_before_manifest_intake",
            "current_status": "missing",
            "no_go_if_missing": "yes",
        },
        {
            "gate_id": "EXT-ACCEPT-002",
            "requirement": "unlabeled_analyst_manifest",
            "minimum_evidence": "Manifest with sample_id, path, file_sha256, source_group, modality and target_task, but no label or label hint.",
            "pass_condition": "validate_external_blind_intake.py --strict-sha passes",
            "current_status": "missing",
            "no_go_if_missing": "yes",
        },
        {
            "gate_id": "EXT-ACCEPT-003",
            "requirement": "sealed_labels_held_outside_analyst_workflow",
            "minimum_evidence": "Label holder, sealed label-file hash and unlock authorization recorded without label values visible to analyst.",
            "pass_condition": "unlock occurs only after prediction file is frozen and hashed",
            "current_status": "missing",
            "no_go_if_missing": "yes",
        },
        {
            "gate_id": "EXT-ACCEPT-004",
            "requirement": "one_shot_prediction_freeze",
            "minimum_evidence": "Frozen model/preprocessing/seeds/thresholds and one prediction CSV hash before label unlock.",
            "pass_condition": "exactly one main-claim prediction submission exists before labels are opened",
            "current_status": "missing",
            "no_go_if_missing": "yes",
        },
        {
            "gate_id": "EXT-ACCEPT-005",
            "requirement": "rights_for_reporting",
            "minimum_evidence": "Written permission for metric reporting, manuscript use, Source Data/public release boundaries and journal publication.",
            "pass_condition": "rights checklist has explicit compatible answers",
            "current_status": "missing",
            "no_go_if_missing": "yes",
        },
    ]

    contact_rows = [
        {
            "contact_packet_id": "CONTACT-B-001",
            "route": "Track B new third-party blind GPR image set",
            "recipient_type": "advisor/collaborator/data holder",
            "send_material": "external_blind_asset_request_letter.md plus external_asset_request_items.csv and external_asset_rights_checklist.csv",
            "requested_return": "unlabeled files or images, analyst-facing manifest, sealed-label holder identity, rights statement",
            "priority": 1,
            "status": "ready_not_sent",
        },
        {
            "contact_packet_id": "CONTACT-A-001",
            "route": "Track A TIGPR restoration",
            "recipient_type": "authorized dataset access route",
            "send_material": "TIGPR restoration request with local NO-GO audit facts",
            "requested_return": "complete five-class source image tree and licence/redistribution conditions",
            "priority": 2,
            "status": "ready_not_sent",
        },
        {
            "contact_packet_id": "CONTACT-C-001",
            "route": "Track C 4TU-like raw-trace asset",
            "recipient_type": "raw-trace data holder",
            "send_material": "raw-trace feasibility request and grouped-split minimum requirements",
            "requested_return": "project-balanced traces, labels held out, rights statement and group identifiers",
            "priority": 3,
            "status": "ready_not_sent",
        },
    ]

    no_go_rows = [
        {
            "no_go_id": "EXT-NOGO-001",
            "shortcut": "Use Res-SAM again as blind external validation",
            "reason": "Res-SAM is already used in the model-family synthesis and cannot be relabelled blind external.",
            "current_decision": "forbidden",
        },
        {
            "no_go_id": "EXT-NOGO-002",
            "shortcut": "Open labels before prediction freeze",
            "reason": "This invalidates one-shot blind evaluation and converts the run to exploratory analysis.",
            "current_decision": "forbidden",
        },
        {
            "no_go_id": "EXT-NOGO-003",
            "shortcut": "Accept external files without strict SHA manifest validation",
            "reason": "The sample set and file identities would not be frozen before prediction.",
            "current_decision": "forbidden",
        },
        {
            "no_go_id": "EXT-NOGO-004",
            "shortcut": "Treat template dry-run metrics as external validation",
            "reason": "Template dry runs test software flow only and contain placeholder labels/predictions.",
            "current_decision": "forbidden",
        },
        {
            "no_go_id": "EXT-NOGO-005",
            "shortcut": "Redistribute raw third-party GPR files without written rights",
            "reason": "Public release rights and manuscript reporting rights are separate and must be explicit.",
            "current_decision": "forbidden",
        },
    ]

    qa_rows = [
        {
            "check": "readiness_gate_is_no_go",
            "result": "PASS" if readiness.get("gate", {}).get("status") == "NO-GO" else "FAIL",
            "detail": f"gate_status={readiness.get('gate', {}).get('status')}",
        },
        {
            "check": "external_workspace_has_no_payload_files",
            "result": "PASS" if payload_files == 0 else "FAIL",
            "detail": f"payload_files={payload_files}",
        },
        {
            "check": "acquisition_materials_ready_but_no_asset",
            "result": "PASS" if acquisition.get("package_ready_for_data_holder") is True and acquisition.get("creates_real_external_result") is False else "FAIL",
            "detail": f"package_ready={acquisition.get('package_ready_for_data_holder')}; creates_result={acquisition.get('creates_real_external_result')}",
        },
        {
            "check": "all_acceptance_gates_currently_missing",
            "result": "PASS" if all(row["current_status"] == "missing" for row in acceptance_rows) else "FAIL",
            "detail": f"acceptance_rows={len(acceptance_rows)}",
        },
        {
            "check": "request_handoff_rights_inputs_imported",
            "result": "PASS" if len(request_rows) == 5 and len(handoff_rows) == 7 and len(rights_rows) == 5 else "FAIL",
            "detail": f"request={len(request_rows)}; handoff={len(handoff_rows)}; rights={len(rights_rows)}",
        },
        {
            "check": "no_external_validation_claimed",
            "result": "PASS",
            "detail": "This register prepares acquisition triage only; it does not acquire, intake or evaluate a real external asset.",
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(
        OUT_DIR / "external_asset_route_triage.csv",
        route_rows,
        ["route_priority", "track_id", "track_name", "current_status", "contact_target", "request_mode", "triage_decision", "next_action", "can_close_blind_gate_now"],
    )
    write_csv(
        OUT_DIR / "external_asset_acceptance_gates.csv",
        acceptance_rows,
        ["gate_id", "requirement", "minimum_evidence", "pass_condition", "current_status", "no_go_if_missing"],
    )
    write_csv(
        OUT_DIR / "external_asset_contact_packet_queue.csv",
        contact_rows,
        ["contact_packet_id", "route", "recipient_type", "send_material", "requested_return", "priority", "status"],
    )
    write_csv(OUT_DIR / "external_asset_no_go_shortcuts.csv", no_go_rows, ["no_go_id", "shortcut", "reason", "current_decision"])
    write_csv(OUT_DIR / "external_asset_triage_register_qa.csv", qa_rows, ["check", "result", "detail"])

    readme = """# External Asset Triage Register 2026-08-10

This package turns the blind external validation NO-GO state into a concrete acquisition triage register.

It ranks feasible routes, defines acceptance gates, queues contact packets and records forbidden shortcuts.

Boundary: no real external asset has been acquired, no strict-SHA manifest has passed, labels remain unavailable, no one-shot prediction has been frozen and no external validation result exists.
"""
    write_text(OUT_DIR / "EXTERNAL_ASSET_TRIAGE_REGISTER_README.md", readme)

    report = [
        "# External asset triage register report 2026-08-10",
        "",
        "Status: `external_asset_triage_ready_waiting_real_asset`",
        "",
        f"- Route rows: {len(route_rows)}",
        f"- Acceptance gates: {len(acceptance_rows)}",
        f"- Contact packet rows: {len(contact_rows)}",
        f"- No-go shortcut rows: {len(no_go_rows)}",
        f"- External workspace payload files: {payload_files}",
        f"- QA pass: {qa_pass}",
        "",
        "Primary route: Track B, a new advisor-held/collaborator-held/third-party blind GPR asset with labels held outside the analyst workflow.",
        "",
        "Boundary: this is acquisition triage only and does not close blind external validation.",
        "",
    ]
    write_text(OUT_DIR / "external_asset_triage_register_report.md", "\n".join(report))

    summary = {
        "package": "external_asset_triage_register_20260810",
        "route_rows": len(route_rows),
        "primary_route": "Track B new third-party blind GPR image set",
        "acceptance_gates": len(acceptance_rows),
        "acceptance_gates_closed": 0,
        "contact_packet_rows": len(contact_rows),
        "contact_packets_sent": 0,
        "no_go_shortcuts": len(no_go_rows),
        "external_workspace_payload_files": payload_files,
        "real_external_asset_acquired": False,
        "strict_sha_manifest_passed": False,
        "one_shot_prediction_frozen": False,
        "locked_external_evaluation_complete": False,
        "blind_external_gate_closed": False,
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "submission_ready": False,
        "status": "external_asset_triage_ready_waiting_real_asset",
    }

    section = f"""### 18.75 External asset triage register update

Added an external asset triage register. This converts the blind external validation NO-GO state into ranked acquisition routes, acceptance gates, contact-packet queue and forbidden shortcuts.

New directory: `{OUT_DIR}`

New files:
1. `external_asset_route_triage.csv`
2. `external_asset_acceptance_gates.csv`
3. `external_asset_contact_packet_queue.csv`
4. `external_asset_no_go_shortcuts.csv`
5. `external_asset_triage_register_qa.csv`
6. `EXTERNAL_ASSET_TRIAGE_REGISTER_README.md`
7. `external_asset_triage_register_report.md`
8. `external_asset_triage_register_summary.json`

Current result:
1. route_rows = {summary['route_rows']}
2. primary_route = `Track B new third-party blind GPR image set`
3. acceptance_gates = {summary['acceptance_gates']}
4. acceptance_gates_closed = 0
5. contact_packet_rows = {summary['contact_packet_rows']}
6. contact_packets_sent = 0
7. external_workspace_payload_files = {payload_files}
8. real_external_asset_acquired = false
9. strict_sha_manifest_passed = false
10. locked_external_evaluation_complete = false
11. blind_external_gate_closed = false
12. qa_pass = {str(qa_pass).lower()}
13. submission_ready = false
14. status = `external_asset_triage_ready_waiting_real_asset`

Boundary:
1. This step does not acquire a real external asset.
2. This step does not validate a strict-SHA manifest.
3. This step does not freeze a one-shot prediction.
4. This step does not run a real locked external evaluation.
5. This step does not close the blind external gate."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "external_asset_triage_register_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("External asset triage register QA failed")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
