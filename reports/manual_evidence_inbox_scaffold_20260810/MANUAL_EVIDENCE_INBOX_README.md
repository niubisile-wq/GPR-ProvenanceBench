# NatComms 人工证据回收 Inbox 说明 2026-08-10

当前状态：还不能投稿。这个 inbox 只用于临时接收真实人工返回材料，不代表证据已经写入 tracker。

Inbox root: `<REPO_ROOT>\manual_evidence_inbox_20260810`

## 使用顺序

1. 把真实返回文件放进对应 `MD-xxx` 文件夹。
2. 按 worksheet 目标文件填写路径、时间、选择或回复。
3. 先运行 post-dispatch intake validator。
4. 只有 validator 通过后，才运行对应 branch validator。

## 禁止

- INBOX-STOP-001: Inbox file presence is not gate evidence until the validator passes.
- INBOX-STOP-002: Do not put external blind labels into analyst-visible inbox folders.
- INBOX-STOP-003: Do not overwrite tracker files from raw returned attachments.
- INBOX-STOP-004: Do not mark email_sent or returned rows from planned/simulated messages.
- INBOX-STOP-005: Do not store third-party raw files in public release staging from this inbox.
