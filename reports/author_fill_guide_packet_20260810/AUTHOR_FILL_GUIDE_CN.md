# 作者/负责人填写指南

这份指南只说明怎么填写已经生成的作者回复表，不替作者作出决定。

## 必填原则

1. 只填写 `author_reply`、`current_choice`、发送日志和返回日志中的人工字段。
2. 不修改 recommendation、evidence、gate、source file 或 checksum 字段。
3. backend 必须明确写 `Python` 或 `R`，不能写“都可以”。
4. figure scope 必须明确写 `Figure 1-Figure 6` 或 `reduced display set with SI relocation`。
5. Track A external validation 只有在真实 held-label blind asset 完成 strict intake 和 locked evaluation 后才能写。
6. final author approval 不能在 final manuscript/SI/figures/source data 生成前提前确认。

## 填完后的验证顺序

1. `py scripts\build_natcomms_author_response_log_validator.py`
2. `py scripts\build_natcomms_author_reply_ingestion_validator.py`
3. `py scripts\build_figure_backend_decision_validator.py`
4. `py scripts\build_natcomms_gate_closure_evidence_binder.py`
5. `py scripts\build_natcomms_finalization_command_dashboard_v3.py`
6. `py scripts\check_manuscript_text_encoding.py`
7. `& scripts\run_m0_m2_checks.ps1`

当前边界：这份指南不是作者批准，不是回复收集完成，不是 backend 选择，不是 final files，也不是投稿。
