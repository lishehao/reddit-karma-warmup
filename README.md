# Reddit Karma Warmup

Protocol version: `2026.07.27.2`

Run authorized Reddit operations through one persistent, user-visible `Reddit
运营台`. It owns a durable five-unit queue—browsing, comments, posts, follow-up,
and presence—rather than creating five Chrome-contending tasks.

## Send this one prompt

```text
请完整读取并执行 https://raw.githubusercontent.com/lishehao/reddit-karma-warmup/main/README.md：通过 HTTPS 安装或升级 reddit-karma-warmup，先完成只读预检；成功后把当前任务命名并置顶为“Reddit 运营台”，不要创建评论/发帖/跟进/浏览/主页的独立 Chrome 任务。为当前任务请求 gpt-5.6-luna/high（仅在宿主支持时；记录实际模型证据，不因不可读或不可切换而创建替代任务）。我会在同一任务中给出账号、方向、时长、五个单元和逐单元授权；默认所有外部动作只研究、投票关闭。不要进入目标模式。
```

## Runtime contract

### 1. Install and preflight

1. Download only from this repository's HTTPS archive and install the complete
   `reddit-karma-warmup/` directory atomically under
   `${CODEX_HOME:-$HOME/.codex}/skills/`.
2. Compare `manifest.json` versions. Back up before replacement; same version
   with different content is a conflict; do not downgrade or merge files.
3. Rename the current healthy task `Reddit 运营台` and pin it. Rename failure is
   presentation-only; do not create a successor merely to obtain a title.
4. Request `gpt-5.6-luna/high` only if the host exposes a model request. Store
   `requested`, `actual`, and `evidence_state`; absent/unknown model metadata
   keeps the same task.
5. Do read-only Chrome, account, task/automation, local time, and public audit
   cache preflight. Do not create a test Heartbeat, a test Reddit task, or any
   Reddit mutation during bootstrap.

Chrome preflight must distinguish browser control, tab metadata, page content,
route, and account state. `openTabs`/claim/title success plus content timeout is
`CHROME_CONTENT_CHANNEL_TIMEOUT`, not a disconnect, missing tab, or account
risk. Use separate calls for tab creation, navigation, and page read; a
navigation timeout requires a metadata readback before any recovery. Never use
`Promise.race` to fake cancellation.

### 2. Start one mission

Interpret one direct user instruction into a structured input, then compile it
before Chrome with `scripts/compile_single_owner_mission.py`. The default is:

```text
账号 u/<name>; 方向 <topic/context>; 时长 <N hours>;
单元=浏览、评论、发帖、跟进、主页; 授权=只研究; 投票=关闭
```

The compiler writes a canonical immutable envelope with account, duration,
selected/paused units, per-unit authority, vote policy, source-prompt hash,
model-request state, and revision hash. It does not open Chrome or infer user
authorization.

Bootstrap `scripts/single_owner_queue.py` with the exact envelope. The one task
owns one Chrome binding and one primary Reddit tab. After a neutral canary, it
runs only one unit at a time in this order:

```text
browsing -> comments -> posts -> follow-up -> presence
```

At most two agent-owned, public read tabs may be used after a healthy canary.
They are an optimization inside the same owner only. All focus/input/click,
submit, verification, tab claim/close, recovery, and finalization calls remain
globally serial. Never claim or alter a user tab.

### 3. Unit authority

| Unit | Default | Explicit action authority | Votes |
| --- | --- | --- | --- |
| browsing | `READ_ONLY` | `VOTE_AUTHORIZED` | only this unit, with `BROWSING_ONLY` policy |
| comments | `RESEARCH_ONLY` | `COMMENT_AUTHORIZED` | disabled |
| posts | `RESEARCH_ONLY` | `POST_AUTHORIZED` | disabled |
| follow-up | `RESEARCH_ONLY` | `FOLLOWUP_AUTHORIZED` | disabled |
| presence | `RESEARCH_ONLY` | `PRESENCE_AUTHORIZED` | disabled |

Every non-default authority needs a direct user authorization receipt in the
new envelope. It never overrides current live community rules, account gates,
truthful evidence, submit state, pacing, or mutation uncertainty. Comments and
posts require built-in Web Search as `research_brief -> query_plan ->
evidence_synthesis -> Chrome live gate` before candidate narrowing. Chrome is
the final authority for Reddit-specific live facts.

Before every outward action, persist a deterministic `MUTATION_INTENT` /
`action_key`. If acknowledgement or verification is uncertain, freeze that exact
key forever. Do not retry it, reopen it, or ask another unit to verify it.

### 4. Hot-plug the five units safely

All five units can be added, paused, removed, resumed, or have their scoped
authority/vote policy revised without creating a new Chrome owner. This is a
revision, not an in-place mutation of the current mission:

```text
current envelope hash -> compile full revision n+1 -> apply queue revision
```

The queue accepts a revision only when there is no running unit, no open read
batch, no browser boundary in flight, and the mission has not retired. It keeps
append-only history:

- `ADD`: enqueue a fresh generation;
- `PAUSE`: preserve a queued/yielded unit and its evidence in history;
- `REMOVE`: preserve history, mark removed for this revision;
- `RESUME`: enqueue a fresh generation, never rewrite old evidence.
- authority/vote-policy change: record exact `from`/`to` values; an increase
  still requires a fresh direct authorization receipt.

If a unit is active, return `HOTPLUG_DEFERRED_UNSAFE_BOUNDARY`; finish or yield
the current unit first. A yielded unit resumes before later queued units unless
a safe revision pauses/removes it.

### 5. Heartbeat, recovery, and retirement

One mission-level recurring Heartbeat belongs only to `Reddit 运营台`. It wakes
the same task, preserves the same queue, and continues a yielded unit before
starting later work. A real trigger deviation within ±5 minutes is acceptable;
continue normally. Do not use a `COUNT=1` self-rescheduling timer.

At mission end, prove all units terminal/paused/removed, settle all browser
boundaries, release only agent-owned tabs, delete that one Heartbeat, and retire
the queue. Keep the visible `Reddit 运营台` available for a new mission.

### 6. Public community-audit cache

The bundled audit-pool script is a local, GET-only, locked public-rule cache.
It is not a Codex task, does not own Chrome, and never publishes. It can reduce
repeated public rule reads, but never replaces live Chrome checks for current
rules, account eligibility, composer state, content context, or publication.

### 7. Legacy compatibility

`execution_topology=legacy_multi_lane_compat` exists only for an explicit,
bounded migration of an already-running legacy mission. It is never the default
for a new account direction or a broad “start Reddit operation” request.

## Release rule

Skill changes default to direct GitHub `main` publication: version bump,
validators, ZIP integrity, public codeload readback, and atomic local install.
If a live runtime fence proves an active old mission, publish the new package but
defer only the local managed-directory replacement until that runtime releases.
