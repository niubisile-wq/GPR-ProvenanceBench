#!/usr/bin/env python3
"""Build author-facing action packet for unresolved submission gates."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
IN_DIR = BENCH_ROOT / "reports" / "author_decision_intake_package_20260810"
OUT_DIR = BENCH_ROOT / "reports" / "author_action_packet_20260810"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_author_decision_form(decisions: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in decisions:
        rows.append(
            {
                "decision_id": row["decision_id"],
                "decision_cn": {
                    "D001": "正式论文图件用 Python 还是 R 渲染",
                    "D002": "真实外部盲测数据走哪条路线",
                    "D003": "代码采用什么许可",
                    "D004": "衍生数据/Source Data 采用什么许可",
                    "D005": "代码和数据放在哪个可生成 DOI 的仓库",
                    "D006": "外部验证未完成时论文按什么定位推进",
                    "D007": "最终参考文献编号何时转换",
                }.get(row["decision_id"], row["decision"]),
                "recommended_choice": row["recommended_default"],
                "author_fill_in": "",
                "deadline_reason": row["blocks"],
                "status": row["status"],
            }
        )
    return rows


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    decisions = read_csv(IN_DIR / "author_decision_register.csv")
    actions = read_csv(IN_DIR / "next_author_actions.csv")
    dependencies = read_csv(IN_DIR / "decision_dependency_map.csv")

    decision_form = build_author_decision_form(decisions)
    write_csv(
        OUT_DIR / "author_decision_form_cn.csv",
        decision_form,
        ["decision_id", "decision_cn", "recommended_choice", "author_fill_in", "deadline_reason", "status"],
    )

    next_72h_rows = [
        {
            "time_window": "0-24 h",
            "owner": "author",
            "action": "回复 D001：Python 或 R。若无强偏好，按当前环境选择 Python。",
            "output_unlocked": "Figure 1-6 formal rendering and visual QA can start.",
        },
        {
            "time_window": "0-24 h",
            "owner": "author/advisor",
            "action": "确定是否存在可独立持有标签的真实外部 GPR 数据联系人。",
            "output_unlocked": "Blind external acquisition package can be sent to a named holder.",
        },
        {
            "time_window": "24-48 h",
            "owner": "author/institution",
            "action": "初步确认代码许可和衍生数据许可是否可公开。",
            "output_unlocked": "Repository metadata draft can become deposit-ready.",
        },
        {
            "time_window": "48-72 h",
            "owner": "author",
            "action": "选择投稿叙事：等待真实外部验证，或按 benchmark/resource framing 先推进。",
            "output_unlocked": "Title, abstract, cover letter and claim strength can be locked.",
        },
    ]
    write_csv(
        OUT_DIR / "next_72h_author_actions.csv",
        next_72h_rows,
        ["time_window", "owner", "action", "output_unlocked"],
    )

    external_email = """# External blind GPR asset request email draft

Subject: Request for advisor-held blind GPR validation asset

Dear [Name],

We are preparing a manuscript on ground-penetrating-radar recognition and provenance-aware generalization. The current internal evidence indicates that model performance can change substantially under environment/provenance shifts. To avoid overclaiming, we need one independent blind validation asset held outside the model-development workflow.

Requested asset:

1. GPR images/traces or derived examples from one or more sites/projects not used in our current model development.
2. Stable sample identifiers and file checksums.
3. Labels held by you or a delegated label holder until our predictions are frozen.
4. Permission status for using aggregate metrics in a manuscript.
5. Clear indication of whether raw data may be redistributed, or whether only derived metrics/source-data tables may be shared.

Proposed blind protocol:

1. We receive files and a manifest without labels.
2. We freeze preprocessing, model version, seeds and prediction files before seeing labels.
3. You release labels only after the prediction submission is timestamped.
4. We run one locked evaluation for main claims; any reruns are reported as exploratory only.

If this is feasible, please confirm the available modality, approximate sample count, label type and rights constraints.

Best regards,
[Author]
"""
    (OUT_DIR / "external_blind_request_email_draft.md").write_text(external_email, encoding="utf-8")

    coauthor_checklist = """# Coauthor decision checklist

Please answer these items before the next manuscript-production step.

1. Figure backend: Python or R?
2. External blind asset: name of data holder/contact, or confirm no real external asset is available yet.
3. Code licence: MIT, BSD-3-Clause, Apache-2.0, institutional licence or restricted?
4. Derived data licence: CC BY 4.0, CC0, restricted derived metrics only or no public derived data?
5. Repository route: GitHub+Zenodo, Zenodo only, OSF, institutional repository or other DOI-capable route?
6. Manuscript framing if external validation remains open: hold submission, or proceed as a benchmark/resource and fragility-evidence paper?
7. Reference numbering: keep temporary [P#] markers until final prose lock?

Current default recommendation:

1. Use Python for figure rendering because the current environment and evidence pipeline are Python-based.
2. Pursue a third-party/advisor-held blind asset if any real contact exists.
3. Use benchmark/resource framing unless a real blind external validation asset is acquired and evaluated.
4. Do not claim repository DOI, code DOI, final Reporting Summary or external validation until these gates are actually closed.
"""
    (OUT_DIR / "coauthor_decision_checklist.md").write_text(coauthor_checklist, encoding="utf-8")

    one_page = [
        "# 8月10日 CNS 计划：作者行动一页纸",
        "",
        "当前本地证据链已经整理到可审计状态，但投稿级闭环还没有完成。下一步必须先解决作者/外部输入，不能继续用内部脚本替代真实决策。",
        "",
        "## 必须先回复的 4 件事",
        "",
    ]
    for row in actions:
        one_page.append(f"{row['priority']}. {row['action']}：{row['exact_author_response_needed']}。")
    one_page.extend(
        [
            "",
            "## 当前不能写成已完成的内容",
            "",
            "1. 不能写已完成真实外部盲测。",
            "2. 不能写已有 repository DOI 或 code DOI。",
            "3. 不能写 Reporting Summary 已最终锁定。",
            "4. 不能写 Figure 1-6 已正式渲染并完成视觉 QA。",
            "",
            "## 决策后立即能做什么",
            "",
        ]
    )
    for row in dependencies:
        one_page.append(f"- {row['blocked_output']}: {row['next_script_after_decision']}")
    one_page.append("")
    (OUT_DIR / "author_action_one_page_cn.md").write_text("\n".join(one_page), encoding="utf-8")

    summary = {
        "run_id": "20260810_author_action_packet",
        "decision_form_rows": len(decision_form),
        "next_72h_actions": len(next_72h_rows),
        "email_drafts": 1,
        "coauthor_checklists": 1,
        "one_page_briefs": 1,
        "status": "author_action_packet_ready",
        "boundary": "Action packet supports author/external decisions only; it does not close figure, repository, external-validation or Reporting Summary gates.",
    }
    (OUT_DIR / "author_action_packet_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    report = [
        "# Author action packet report 2026-08-10",
        "",
        f"- Decision form rows: {summary['decision_form_rows']}",
        f"- Next-72h actions: {summary['next_72h_actions']}",
        f"- Email drafts: {summary['email_drafts']}",
        f"- Coauthor checklists: {summary['coauthor_checklists']}",
        f"- One-page briefs: {summary['one_page_briefs']}",
        "",
        "Boundary: this is an author/external action package, not new experimental evidence.",
        "",
    ]
    (OUT_DIR / "author_action_packet_report.md").write_text("\n".join(report), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
