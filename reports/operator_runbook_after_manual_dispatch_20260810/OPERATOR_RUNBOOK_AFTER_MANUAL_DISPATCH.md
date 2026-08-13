# NatComms 人工证据填写与安全重跑说明 2026-08-10

当前状态：还不能投稿。这个说明只告诉操作者如何在真实人工证据出现后填写和重跑。

## 先看这三个文件

1. Master dispatch zip: `<LOCAL_DESKTOP>\\NatComms_manual_dispatch_master_packet_20260810.zip`
2. Evidence worksheet: `<REPO_ROOT>\reports\manual_evidence_intake_worksheet_20260810\manual_evidence_intake_worksheet.csv`
3. Safe rerun matrix: `<REPO_ROOT>\reports\post_evidence_safe_rerun_guard_20260810\post_evidence_branch_rerun_matrix.csv`

## 操作顺序

1. 先真实发送或真实获取材料；没有证据时，不要填写 `sent`、backend、rights、Reporting Summary 或 reference 授权。
2. 有真实证据后，只按 worksheet 的 `target_file`、`fields_to_fill` 和 `allowed_values_or_format` 填写。
3. 填完先运行：

```powershell
py scripts\build_post_dispatch_evidence_intake_validator.py
```

4. 再查看：

```text
reports\post_evidence_safe_rerun_guard_20260810\post_evidence_branch_rerun_matrix.csv
```

5. 只有 `blocked_now=no` 的分支命令可以继续跑。
6. 最后再运行完整检查：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_m0_m2_checks.ps1
```

## 当前数字

1. worksheet rows: 7
2. evidence rows passed: 0
3. branch commands safe now: 0
4. submission_ready: false

## 禁止操作

1. 不要用 recommended choice 代替作者选择。
2. 不要把 template dry run 写成 blind external validation。
3. 不要在没有 DOI/licence/rights 证据时写 public availability。
4. 不要在 final prose 和 figure/table calls 稳定前替换 `[P#]`。
5. 不要在 dashboard 仍为 `submission_ready=false` 时投稿。
