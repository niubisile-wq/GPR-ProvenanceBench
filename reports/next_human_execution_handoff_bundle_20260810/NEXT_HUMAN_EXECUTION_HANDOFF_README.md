# NatComms 下一步人工执行 handoff 2026-08-10

当前状态：还不能投稿。这个压缩包只用于人工执行下一步，不代表已经发送、已经收到证据或已经关 gate。

## 打开顺序

1. 先看 `01_start_here/NatComms_今日人工动作最小包_20260810.md`。
2. 发送或请求真实材料后，把返回文件放进 `manual_evidence_inbox_20260810` 对应文件夹。
3. 跑 inbox audit，再看 writeback queue。
4. 只有 post-dispatch validator 通过后，才跑后续 branch validators。

## 当前状态

- manual_actions_executed: `False`
- candidate_evidence_files: `0`
- writeback_allowed_rows: `0`
- evidence_rows_passed: `0`
- gate_closure_allowed: `False`
- submission_ready: `False`

## 禁止

- 不要把这个 handoff zip 当成已发送证据。
- 不要从 recommended choice 直接写 tracker。
- 不要把 inbox 文件存在当成 gate closure。
- 不要在 submission_ready=false 时上传 portal。
