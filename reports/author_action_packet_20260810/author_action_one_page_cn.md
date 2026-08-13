# 8月10日 CNS 计划：作者行动一页纸

当前本地证据链已经整理到可审计状态，但投稿级闭环还没有完成。下一步必须先解决作者/外部输入，不能继续用内部脚本替代真实决策。

## 必须先回复的 4 件事

1. Choose figure backend：Python or R。
2. Send external blind asset request package：Name the data holder/advisor/collaborator or confirm no contact yet。
3. Choose tentative code/data licence direction：MIT/BSD/Apache for code; CC BY/CC0/restricted for derived data, pending institutional approval。
4. Choose repository route：GitHub+Zenodo, Zenodo only, OSF, institutional repository, or other。

## 当前不能写成已完成的内容

1. 不能写已完成真实外部盲测。
2. 不能写已有 repository DOI 或 code DOI。
3. 不能写 Reporting Summary 已最终锁定。
4. 不能写 Figure 1-6 已正式渲染并完成视觉 QA。

## 决策后立即能做什么

- Rendered main figures: future build_rendered_figures_<backend>.py
- Blind external validation result: validate_external_blind_intake.py --strict-sha; evaluate_external_blind_submission.py --main-claim
- Public code release DOI: release archive creation and DOI registration
- Public source-data DOI: repository deposit using repository_metadata_package_20260810
- Final Reporting Summary: future build_reporting_summary_final.py
