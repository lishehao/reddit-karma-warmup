# One-prompt Reddit Mission

Use one direct user instruction to start or revise the single-owner runtime.
Do not create five lane tasks.

## Start shape

```text
开始 Reddit 运营：账号 u/<name>；方向 <topic/audience/context>；时长 <N 小时>；
单元=浏览、评论、发帖、跟进、主页；授权=只研究；投票=关闭。
```

`全部` expands to the five fixed unit IDs. Default authority is read/research
only. An explicit outward action is scoped by unit, for example a comment
authorization does not authorize posts, follow-up, profile work, or votes.

The compiled envelope contains:

```text
mission_id, mission_revision, parent_envelope_sha256,
account, direction, operation_start_at, operation_stop_at,
selected_units, paused_units, unit_authority, vote_policy,
unit_changes, model_request, authorization_receipt,
source_prompt_sha256, mission_envelope_sha256
```

The runtime, not the compiler, interprets a natural-language instruction into
the structured input. The compiler opens no Chrome, creates no task, and never
widens permission. It rejects nested overrides, cross-unit vote authority,
unknown unit IDs, malformed revision chains, and action authority without an
authorization receipt.

## Hot-plug shape

Use a new direct instruction after a safe boundary:

```text
调整当前 Reddit 运营：暂停发帖；恢复评论；加入主页维护；其余保持；
不改变既有授权。
```

The runtime reads the current envelope hash, compiles a full successor plan,
then asks the queue to apply it. It does not change the active work item in
place. If the active unit or read batch has not settled, record
`HOTPLUG_DEFERRED_UNSAFE_BOUNDARY` and continue the existing unit; retry only
on the next safe boundary.

Do not use “hot-plug” to smuggle an action authorization. Increasing any unit
from research-only to an outward authority requires a new, direct user
authorization receipt and fresh Chrome/rule gates when that unit runs.
That authority-only change is itself a valid hashed revision even if no unit is
added, paused, removed, or resumed; the revision records exact `from`/`to`
authority and vote-policy deltas.

## Model request

For this user-authorized architecture, request `gpt-5.6-luna/high` when the
host exposes model selection. Record `REQUESTED`, `ACTUAL_CONFIRMED`, or
`UNVERIFIED` separately. The same `Reddit 运营台` remains the owner if model
metadata is unavailable or switching is unsupported; never create a duplicate
task just to chase a model label.
