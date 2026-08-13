#!/usr/bin/env python3
"""Build a single author reply packet for Nat Comms finalization gates."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "natcomms_author_finalization_reply_packet_20260810"

MASTER_CHECKLIST = BENCH_ROOT / "reports" / "natcomms_finalization_master_checklist_20260810" / "finalization_master_checklist.csv"
OWNER_QUEUE = BENCH_ROOT / "reports" / "natcomms_finalization_master_checklist_20260810" / "owner_action_master_queue.csv"
TITLE_PAGE = BENCH_ROOT / "reports" / "natcomms_admin_declarations_prelock_20260810" / "title_page_field_prelock.csv"
AUTHOR_CONTRIB = BENCH_ROOT / "reports" / "natcomms_admin_declarations_prelock_20260810" / "author_contribution_intake_matrix.csv"
REVIEWERS = BENCH_ROOT / "reports" / "natcomms_admin_declarations_prelock_20260810" / "reviewer_suggestion_intake.csv"
POLICY = BENCH_ROOT / "reports" / "natcomms_admin_declarations_prelock_20260810" / "editorial_policy_decision_prelock.csv"
REPORTING_CONFIRM = BENCH_ROOT / "reports" / "reporting_summary_finalization_prelock_20260810" / "reporting_summary_author_confirmation_checklist.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def preserve_existing_fields(
    path: Path,
    rows: list[dict[str, str]],
    key_field: str,
    fields_to_preserve: list[str],
) -> int:
    """Keep manually filled author-facing fields when regenerating templates."""
    if not path.exists():
        return 0
    existing_rows = read_csv(path)
    existing_by_key = {row.get(key_field, ""): row for row in existing_rows if row.get(key_field, "")}
    preserved = 0
    for row in rows:
        existing = existing_by_key.get(row.get(key_field, ""))
        if not existing:
            continue
        for field in fields_to_preserve:
            value = existing.get(field, "")
            if value:
                row[field] = value
                preserved += 1
    return preserved


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    master_rows = read_csv(MASTER_CHECKLIST)
    owner_rows = read_csv(OWNER_QUEUE)
    title_rows = read_csv(TITLE_PAGE)
    contribution_rows = read_csv(AUTHOR_CONTRIB)
    reviewer_rows = read_csv(REVIEWERS)
    policy_rows = read_csv(POLICY)
    reporting_rows = read_csv(REPORTING_CONFIRM)

    reply_rows = [
        {
            "field_id": "AFR-001",
            "decision_area": "corresponding_author_identity",
            "question_cn": "请确认通讯作者姓名、单位、邮箱、ORCID（如使用）和投稿系统账户。",
            "recommended_default": "留空，必须由通讯作者填写。",
            "author_reply": "",
            "required_to_close_gate": "FM-001; FM-008",
            "blocks_if_blank": "title page; cover letter; portal metadata",
        },
        {
            "field_id": "AFR-002",
            "decision_area": "author_order_and_affiliations",
            "question_cn": "请确认全部作者顺序、单位、共同一作/共同通讯说明和单位编号。",
            "recommended_default": "留空，必须由作者组确认。",
            "author_reply": "",
            "required_to_close_gate": "FM-001",
            "blocks_if_blank": "title page; author contributions; final manuscript file",
        },
        {
            "field_id": "AFR-003",
            "decision_area": "author_contributions",
            "question_cn": "请逐位确认 Author Contributions，至少覆盖概念、方法、代码、实验、数据、写作和监督。",
            "recommended_default": "使用 CRediT 风格，但不得编造贡献。",
            "author_reply": "",
            "required_to_close_gate": "FM-001",
            "blocks_if_blank": "author contribution statement; portal metadata",
        },
        {
            "field_id": "AFR-004",
            "decision_area": "competing_interests",
            "question_cn": "请确认所有作者是否存在 financial 或 non-financial competing interests。",
            "recommended_default": "无利益冲突时填写 The authors declare no competing interests.",
            "author_reply": "",
            "required_to_close_gate": "FM-001",
            "blocks_if_blank": "competing interests statement; portal metadata",
        },
        {
            "field_id": "AFR-005",
            "decision_area": "funding_acknowledgements",
            "question_cn": "请确认基金编号、资助机构、非作者贡献和致谢对象。",
            "recommended_default": "留空，必须由作者确认。",
            "author_reply": "",
            "required_to_close_gate": "FM-001",
            "blocks_if_blank": "Acknowledgements; funding metadata",
        },
        {
            "field_id": "AFR-006",
            "decision_area": "ethics_consent_governance",
            "question_cn": "请确认是否涉及 ethics、consent、敏感数据或机构数据治理要求。",
            "recommended_default": "如完全不涉及，明确填写 Not applicable，并说明依据。",
            "author_reply": "",
            "required_to_close_gate": "FM-001; FM-005",
            "blocks_if_blank": "Reporting Summary; editorial policy metadata",
        },
        {
            "field_id": "AFR-007",
            "decision_area": "manuscript_branch",
            "question_cn": "请确认当前是否按 Track B（benchmark/resource + evidence-boundary）投稿；若有真实盲外部数据持有人，请提供姓名/机构/可用时间。",
            "recommended_default": "若现在没有真实盲外部数据，确认 Track B。",
            "author_reply": "",
            "required_to_close_gate": "FM-002",
            "blocks_if_blank": "title; abstract; cover letter; limitation wording",
        },
        {
            "field_id": "AFR-008",
            "decision_area": "figure_backend",
            "question_cn": "请选择唯一正式出图后端：Python 或 R。当前推荐 Python。",
            "recommended_default": "Python",
            "author_reply": "",
            "required_to_close_gate": "FM-003",
            "blocks_if_blank": "formal figure rendering; Source Data mapping; Reporting Summary",
        },
        {
            "field_id": "AFR-009",
            "decision_area": "licence_rights_repository",
            "question_cn": "请确认代码 licence、派生 Source Data licence、第三方数据权限和是否允许公开仓库/Zenodo DOI。",
            "recommended_default": "Code: MIT or BSD-3-Clause; derived data: CC BY 4.0 unless rights review fails.",
            "author_reply": "",
            "required_to_close_gate": "FM-004",
            "blocks_if_blank": "Data Availability; Code Availability; repository DOI; portal upload",
        },
        {
            "field_id": "AFR-010",
            "decision_area": "reviewer_editorial_policy",
            "question_cn": "请提供 suggested reviewers、excluded reviewers，并确认 preprint、previous editor discussion 和 transparent peer review 选择。",
            "recommended_default": "留空，必须由通讯作者确认。",
            "author_reply": "",
            "required_to_close_gate": "FM-001; FM-008",
            "blocks_if_blank": "cover letter; portal metadata",
        },
        {
            "field_id": "AFR-011",
            "decision_area": "reporting_summary_confirmation",
            "question_cn": "请确认 Reporting Summary 中 blinding、randomization、sample size、data exclusion 和 availability 相关答案。",
            "recommended_default": "保持 prelock 答案为非最终，逐项确认后再锁定。",
            "author_reply": "",
            "required_to_close_gate": "FM-005",
            "blocks_if_blank": "Reporting Summary; submission package",
        },
        {
            "field_id": "AFR-012",
            "decision_area": "final_submission_author_approval",
            "question_cn": "请确认所有作者在最终文件生成后同意投稿版本、作者列表和贡献声明。",
            "recommended_default": "最终文件生成前不得预先视为已同意。",
            "author_reply": "",
            "required_to_close_gate": "FM-007; FM-008",
            "blocks_if_blank": "portal upload; actual submission",
        },
    ]
    preserved_manual_fields = 0
    preserved_manual_fields += preserve_existing_fields(
        OUT_DIR / "author_finalization_reply_form_cn.csv",
        reply_rows,
        "field_id",
        ["author_reply"],
    )
    write_csv(
        OUT_DIR / "author_finalization_reply_form_cn.csv",
        reply_rows,
        ["field_id", "decision_area", "question_cn", "recommended_default", "author_reply", "required_to_close_gate", "blocks_if_blank"],
    )

    metadata_rows = []
    for row in title_rows:
        metadata_rows.append(
            {
                "metadata_id": row.get("field_id", ""),
                "source_field": row.get("field", ""),
                "required_value": row.get("required_value", ""),
                "current_status": row.get("current_status", "author_required"),
                "author_reply": "",
                "notes": "Do not infer this field from local files; corresponding author must confirm.",
            }
        )
    preserved_manual_fields += preserve_existing_fields(
        OUT_DIR / "corresponding_author_metadata_form.csv",
        metadata_rows,
        "metadata_id",
        ["author_reply", "notes"],
    )
    write_csv(
        OUT_DIR / "corresponding_author_metadata_form.csv",
        metadata_rows,
        ["metadata_id", "source_field", "required_value", "current_status", "author_reply", "notes"],
    )

    backend_rows = [
        {
            "ticket_id": "FIG-BACKEND-001",
            "decision": "Choose final rendering backend",
            "recommended_choice": "Python",
            "allowed_choices": "Python; R",
            "current_choice": "",
            "evidence_or_reason": "The current source packages are CSV/Markdown-driven and existing automation is Python-first.",
            "after_choice_action": "Run the formal figure rendering workflow and visual QA; do not claim rendered figures before exports exist.",
        },
        {
            "ticket_id": "FIG-BACKEND-002",
            "decision": "Confirm figure set scope",
            "recommended_choice": "Figure 1-Figure 6 unless journal-length reduction is required.",
            "allowed_choices": "Figure 1-Figure 6; reduced display set with SI relocation",
            "current_choice": "",
            "evidence_or_reason": "Current preassembly plans six display items but none is rendered.",
            "after_choice_action": "Lock final figure legends, Source Data mapping and Reporting Summary figure references.",
        },
    ]
    preserved_manual_fields += preserve_existing_fields(
        OUT_DIR / "figure_backend_decision_ticket.csv",
        backend_rows,
        "ticket_id",
        ["current_choice"],
    )
    write_csv(
        OUT_DIR / "figure_backend_decision_ticket.csv",
        backend_rows,
        ["ticket_id", "decision", "recommended_choice", "allowed_choices", "current_choice", "evidence_or_reason", "after_choice_action"],
    )

    branch_rows = [
        {
            "branch_id": "BRANCH-001",
            "question": "Is a real held-label external blind GPR asset available now?",
            "required_reply": "Name holder/institution/timeline or explicitly confirm none is available.",
            "current_default": "Track B remains applicable because external validation is currently NO-GO.",
            "author_reply": "",
            "claim_boundary": "Do not claim blind external validation unless a strict intake asset and one locked evaluation exist.",
        },
        {
            "branch_id": "BRANCH-002",
            "question": "If no external asset is available, confirm Track B manuscript route.",
            "required_reply": "Confirm benchmark/resource plus evidence-boundary framing.",
            "current_default": "Track B",
            "author_reply": "",
            "claim_boundary": "Res-SAM is the main local evidence; Mojahid is directional support; 4TU is stress-test/failure-boundary evidence.",
        },
    ]
    preserved_manual_fields += preserve_existing_fields(
        OUT_DIR / "track_branch_and_external_validation_reply.csv",
        branch_rows,
        "branch_id",
        ["author_reply"],
    )
    write_csv(
        OUT_DIR / "track_branch_and_external_validation_reply.csv",
        branch_rows,
        ["branch_id", "question", "required_reply", "current_default", "author_reply", "claim_boundary"],
    )

    licence_rows = [
        {
            "item_id": "LIC-001",
            "item": "Analysis code",
            "recommended_route": "MIT or BSD-3-Clause",
            "author_reply": "",
            "blocks": "code DOI; Code Availability",
        },
        {
            "item_id": "LIC-002",
            "item": "Derived figure/source tables",
            "recommended_route": "CC BY 4.0 if rights review permits",
            "author_reply": "",
            "blocks": "Source Data deposit; Data Availability",
        },
        {
            "item_id": "LIC-003",
            "item": "Third-party or restricted source data",
            "recommended_route": "Exclude raw restricted files; publish derived non-identifying summaries only if allowed",
            "author_reply": "",
            "blocks": "repository DOI; portal upload",
        },
        {
            "item_id": "LIC-004",
            "item": "Zenodo/GitHub repository release",
            "recommended_route": "Create only after author/institution rights clearance",
            "author_reply": "",
            "blocks": "final Data/Code Availability; Reporting Summary",
        },
    ]
    preserved_manual_fields += preserve_existing_fields(
        OUT_DIR / "licence_rights_reply_sheet.csv",
        licence_rows,
        "item_id",
        ["author_reply"],
    )
    write_csv(
        OUT_DIR / "licence_rights_reply_sheet.csv",
        licence_rows,
        ["item_id", "item", "recommended_route", "author_reply", "blocks"],
    )

    reviewer_policy_rows = []
    for row in reviewer_rows:
        reviewer_policy_rows.append(
            {
                "item_id": row.get("item_id", ""),
                "category": "reviewer",
                "question": row.get("item", ""),
                "current_prelock_value": row.get("current_prelock_value", ""),
                "author_reply": "",
                "notes": row.get("notes", "Author/corresponding author confirmation required."),
            }
        )
    for row in policy_rows:
        reviewer_policy_rows.append(
            {
                "item_id": row.get("decision_id", ""),
                "category": "editorial_policy",
                "question": row.get("decision", ""),
                "current_prelock_value": row.get("current_prelock_value", ""),
                "author_reply": "",
                "notes": row.get("notes", "Corresponding author confirmation required."),
            }
        )
    preserved_manual_fields += preserve_existing_fields(
        OUT_DIR / "reviewer_and_policy_reply_sheet.csv",
        reviewer_policy_rows,
        "item_id",
        ["author_reply", "notes"],
    )
    write_csv(
        OUT_DIR / "reviewer_and_policy_reply_sheet.csv",
        reviewer_policy_rows,
        ["item_id", "category", "question", "current_prelock_value", "author_reply", "notes"],
    )

    reporting_export_rows = []
    for row in reporting_rows:
        reporting_export_rows.append(
            {
                "reporting_item": row.get("reporting_item", ""),
                "author_confirmation_needed": row.get("author_confirmation_needed", ""),
                "current_prelock_answer": row.get("current_prelock_answer", ""),
                "author_reply": "",
                "blocks_if_blank": "Reporting Summary final lock",
            }
        )
    preserved_manual_fields += preserve_existing_fields(
        OUT_DIR / "reporting_summary_author_reply_sheet.csv",
        reporting_export_rows,
        "reporting_item",
        ["author_reply"],
    )
    write_csv(
        OUT_DIR / "reporting_summary_author_reply_sheet.csv",
        reporting_export_rows,
        ["reporting_item", "author_confirmation_needed", "current_prelock_answer", "author_reply", "blocks_if_blank"],
    )

    email = [
        "# 给作者/通讯作者的一次性最终确认邮件草稿",
        "",
        "各位老师/合作者好，",
        "",
        "当前 Nature Communications 方向仍处于 submission-prelock 状态，不能视为已可投稿。为避免后续反复返工，需要一次性确认以下事项：",
        "",
        "1. 作者顺序、单位、通讯作者、ORCID、Author Contributions、Competing Interests、Funding 和 Acknowledgements。",
        "2. 当前是否确认走 Track B：benchmark/resource + evidence-boundary；若有真实盲外部验证数据持有人，请提供数据持有人、机构、时间线和标签托管方式。",
        "3. 正式出图后端请选择 Python 或 R；当前自动化链路推荐 Python。",
        "4. 代码、派生 Source Data、第三方数据和仓库 DOI 的 licence/rights 路线。",
        "5. suggested reviewers、excluded reviewers、preprint/prior posting、previous editor discussion 和 transparent peer review 选择。",
        "6. Reporting Summary 中 blinding、randomization、sample size、data exclusion 和 availability 相关答案。",
        "",
        "请直接填写 `author_finalization_reply_form_cn.csv` 及配套表格中的 author_reply 列。所有空白项在确认前均视为 open gate，不会写入最终投稿文件。",
        "",
        "边界说明：这封邮件和表格只是收集最终确认，不代表作者已经同意投稿，也不代表 figures、DOI、Reporting Summary、references 或 portal upload 已完成。",
        "",
    ]
    (OUT_DIR / "coauthor_finalization_email_cn.md").write_text("\n".join(email), encoding="utf-8")

    qa_rows = [
        {"check": "Reply form fields", "result": "PASS" if len(reply_rows) >= 12 else "FAIL", "detail": f"{len(reply_rows)} reply fields."},
        {"check": "All master gates remain open", "result": "PASS" if all(row.get("closed") != "yes" for row in master_rows) else "FAIL", "detail": f"{len(master_rows)} master gates imported."},
        {"check": "Manual reply preservation", "result": "PASS", "detail": f"{preserved_manual_fields} existing manual fields preserved; no new author replies are inferred."},
        {"check": "Backend decision ticket exists", "result": "PASS" if len(backend_rows) == 2 else "FAIL", "detail": f"{len(backend_rows)} backend tickets."},
        {"check": "Reviewer/policy sheet exists", "result": "PASS" if len(reviewer_policy_rows) >= 7 else "FAIL", "detail": f"{len(reviewer_policy_rows)} reviewer/policy rows."},
        {"check": "Reporting author sheet exists", "result": "PASS" if len(reporting_export_rows) >= 4 else "FAIL", "detail": f"{len(reporting_export_rows)} Reporting Summary confirmation rows."},
    ]
    write_csv(OUT_DIR / "author_reply_packet_qa.csv", qa_rows, ["check", "result", "detail"])

    readme = [
        "# Nat Comms author finalization reply packet",
        "",
        "Purpose: collect the author/corresponding-author replies needed to close the remaining Nat Comms finalization gates.",
        "",
        "Boundary: this package does not invent author metadata, close gates, render figures, create DOI records, finalize Reporting Summary answers, lock references or submit the manuscript.",
        "",
        "Fill only the `author_reply` columns after explicit author confirmation.",
        "",
    ]
    (OUT_DIR / "NATCOMMS_AUTHOR_FINALIZATION_REPLY_PACKET_README.md").write_text("\n".join(readme), encoding="utf-8")

    report = [
        "# Author finalization reply packet report",
        "",
        f"- Reply fields: {len(reply_rows)}",
        f"- Metadata fields: {len(metadata_rows)}",
        f"- Backend decision tickets: {len(backend_rows)}",
        f"- Branch/external-validation rows: {len(branch_rows)}",
        f"- Licence/rights rows: {len(licence_rows)}",
        f"- Reviewer/policy rows: {len(reviewer_policy_rows)}",
        f"- Reporting Summary author rows: {len(reporting_export_rows)}",
        f"- Owner queue rows imported: {len(owner_rows)}",
        f"- QA failures: {sum(1 for row in qa_rows if row['result'] == 'FAIL')}",
        "- Status: natcomms_author_finalization_reply_packet_ready_replies_not_collected",
        "",
    ]
    (OUT_DIR / "author_finalization_reply_packet_report.md").write_text("\n".join(report), encoding="utf-8")

    summary = {
        "run_id": "20260810_natcomms_author_finalization_reply_packet",
        "reply_fields": len(reply_rows),
        "metadata_fields": len(metadata_rows),
        "decision_tickets": len(backend_rows) + len(branch_rows) + len(licence_rows),
        "reviewer_policy_rows": len(reviewer_policy_rows),
        "reporting_author_rows": len(reporting_export_rows),
        "owner_queue_rows_imported": len(owner_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] != "FAIL" for row in qa_rows),
        "preserved_manual_fields": preserved_manual_fields,
        "author_replies_collected": False,
        "submission_ready": False,
        "status": "natcomms_author_finalization_reply_packet_ready_replies_not_collected",
        "boundary": "Author reply packet collects required replies only; it is not author approval and does not close any finalization gate.",
    }
    (OUT_DIR / "author_finalization_reply_packet_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if summary["qa_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
