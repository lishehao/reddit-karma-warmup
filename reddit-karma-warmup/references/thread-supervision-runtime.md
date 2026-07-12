# Persistent Task Supervision Runtime

Canonical owner of persistent task identity, registry, create/reuse/send/read operations, and task presentation/lifecycle. It does not define lane execution, timer math, or coordinator policy.

Load only in the user-facing `Reddit 主控台` coordinator for `BOOTSTRAP`, `MISSION`, `STATUS`, or `AUDIT`. This is the bundled supervision subset for Reddit operations; no external `thread-supervisor` Skill is required.

## Required Capability Bundle

The host must expose equivalent operations for:

- list/search existing Codex tasks
- create a persistent user-visible task
- read a task's recent result
- send or amend a task instruction
- send a decision-requiring risk/blocker, non-blocking subreddit-retirement notice, or terminal mission-completion return from a worker back to the exact coordinator task
- rename a task when title control exists
- pin/unpin a task when presentation control exists
- archive a completed temporary or retired task after ownership is released
- view each relevant task-owned automation and its persisted binding/schedule/run evidence when the host exposes it

The user's `开始` or concrete operation command explicitly authorizes creation of the requested lane tasks. Do not create them during install/preflight and do not create unrelated tasks.

Persistent tasks are intentional: each lane needs durable history, an exact task ID, a coordinator-managed recurring Heartbeat targeted to that ID, independent recovery, and a reliable risk-return path. A temporary subagent may assist a worker with bounded read-only analysis when available, but it cannot own Chrome mutations, a lane, scheduling, or a user-risk decision.

## Registry

Maintain one owner per lane:

```text
lane | title | single_objective | worker_thread_id | status | mission_id | last_proof | operation_timer_id
comments | Reddit 评论台 | qualified new comments only
posts | Reddit 发帖台 | eligible native main posts only
follow-up | Reddit 跟进台 | actionable account follow-up only
browsing | Reddit 浏览台 | qualified reading and gated vote decisions only
presence | Reddit 主页台 | truthful profile, membership, and flair state only
```

Task search/title metadata is discovery only. It may survive after the underlying rollout has been removed and therefore never proves that a worker can accept another mission. Prefer the exact owner ID already stored in the coordinator registry.

Classify every candidate before reuse:

| State | Evidence | Action |
|-|-|-|
| `LIVE_REGISTERED` | exact registry ID, correct lane, unarchived, and the current mission dispatch succeeds | retain the owner and update its mission state |
| `RETIRED` | archived, explicitly released, or already removed from the registry | keep archived; never auto-unarchive for reuse |
| `STALE_OWNER_TOMBSTONE` | task metadata/summary exists but read or send returns `failed to resolve rollout path`, `file does not exist`, or equivalent missing-rollout evidence | retire atomically and create at most one replacement |
| `TRANSIENT_UNREACHABLE` | host unavailable, transport/tool timeout, or another temporary control failure without missing-rollout evidence | preserve the owner and retry once after recovery; do not archive or duplicate it |

`Readable summary` is not a health state. The first real mission delivery is the definitive write-capability check and already serves useful work; do not send a separate probe. A successful delivery promotes the candidate to `LIVE_REGISTERED`. A missing-rollout error is deterministic and must not be retried against the old ID.

For `STALE_OWNER_TOMBSTONE`, run one coordinator-owned replacement transaction:

1. Record the old task ID, lane, prior archive state, and exact failure.
2. Inspect coordinator-managed automations for the old ID and record every timer still targeting it; absence of automation evidence remains explicit. Do not remove a still-active continuation yet.
3. Create exactly one replacement, capture the returned new task ID, set the canonical lane title, and keep it unpinned/unarchived.
4. Send the actual current mission to the new ID, require same-turn `start_proof`, then create and verify the new worker's recurring Heartbeat.
5. Only after the new owner and timer are verified, disable/remove timers targeting the old ID, remove the old ID from the active registry, unpin it, and keep/set it archived. Do not temporarily unarchive it again.
6. Persist `old_worker_thread_id`, `replacement_worker_thread_id`, replacement reason, old-timer retirement proof, and new automation binding in coordinator state.

When the replacement succeeds, this is an internal self-repair, not a user approval gate or Reddit account risk. Escalate only if the replacement task cannot be created, cannot accept the mission, or cannot receive a correctly bound continuation. Never create a second replacement in the same reconciliation pass.

Every task handoff begins with this compact objective card; do not bury it below setup details:

```text
唯一目标：<one lane outcome>
本轮交付：<count/time/deadline>
明确不做：<other lane outcomes>
长期计时：主控台创建 recurring operation_timer_id；首轮立即执行
```

The card defines one outcome, not one action. A worker may search, score, draft, check rules, pace, verify, and report only as supporting steps toward that outcome.

## Dispatch

When `presence_required=true`, run this dispatch sequence for `Reddit 主页台` first, but wait only for one bounded checkpoint. Then dispatch comments, posts, follow-up, and browsing even when presence needs later retry; only unresolved account/login identity holds outward mutations.

1. Resolve enabled lanes before creating anything. Broad `开始/运营` enables comments, posts, follow-up, and browsing. A first bootstrap additionally enables presence only when the baseline is incomplete; a named lane enables only that lane.
2. List/reconcile the registry once.
3. Select the exact registered candidate for each lane. Keep archived/retired candidates out of the active set; create the one missing task when no eligible unarchived candidate exists. Capture every created task ID and rename it immediately when title control exists.
4. Pin the verified `Reddit 主控台`; explicitly unpin every candidate worker. Verify distinct candidate IDs for broad operation, with each ID mapped to exactly one lane title. A title, plan, or heartbeat card without a persistent task ID is not a worker.
5. Send each candidate exactly one actual `default-operations-sop.md` mission handoff: `role=WORKER`, lane, `single_objective`, `out_of_scope`, `worker_thread_id`, coordinator thread ID, account, mission, intensity, style, targets, stop time, first due=`now`, and required references. Success promotes it to `LIVE_REGISTERED`. Missing-rollout evidence triggers the one replacement transaction and exactly one mission delivery to the replacement; a transient failure preserves the candidate without creating a duplicate. After this step, verify one distinct live ID per enabled lane. If a lane still lacks one, mark only that lane `lane_recovering`; the recurring supervisor retries owner resolution while healthy lanes continue.
6. Require the worker to execute its first Chrome slot immediately and return an action, browser-backed no-action, or recovery checkpoint; task creation or acknowledgement is not proof.
7. Read each enabled worker in the same coordinator turn. A plan-only worker receives one explicit amendment: execute the assigned lane now, verify it, then report proof.
8. If the amended worker still has no browser checkpoint because its task/runtime is temporarily unreachable, mark only that lane `lane_recovering`, retain its owner, and let the supervisor retry delivery. Never execute the lane in the coordinator and never merge it into another worker.

## Supervision

- Pull routine worker state through the coordinator's recurring mission supervisor Heartbeat. The first BOOTSTRAP hour adds checks near `+15m`, `+35m`, and `+60m`; later operation keeps lower-cost slot/scheduler reconciliation until the mission deadline. Do not require routine callbacks; require risk/blocker returns, non-blocking `SUBREDDIT_RETIRED` notices, and one terminal `MISSION_COMPLETE` return per assigned lane mission.
- Read only the latest result needed to classify `running`, `first_round_running`, `lane_recovering`, `user_repair`, or `completed`.
- Send amendments only for the same lane's current mission. Queue unrelated future changes in coordinator state until the worker is idle.
- Every worker owns its dedicated Chrome tab and history. After that lane's first action/no-action/recovery checkpoint, the coordinator creates one repeat-on Heartbeat explicitly targeting its worker ID and records it in the registry; workers never mutate automations.
- The coordinator owns one repeat-on, read-only `Reddit 主控台-任务监督` Heartbeat for every multi-slot mission. It cannot execute Reddit actions or continue lane work.
- The coordinator verifies exact `target_thread_id`, repeat-on state, next run, recurrence, and stop guard for every created timer. Repair a misbound lane Heartbeat in place when possible; if replacement is required, create and verify the corrected timer before removing the superseded item.
- Timer creation is per-lane, never a central all-lanes barrier. Create each distinct Heartbeat immediately after its own checkpoint; a combined execution Heartbeat remains forbidden.
- Different lane tasks sharing one Chrome profile/account remain independent; do not pause one merely because another is active.
- The recurring supervisor performs lightweight continuation monitoring. When the user explicitly requests a deeper execution/quality audit, load `operations-audit.md` and compare worker, automation, action, cadence, length, and quality evidence against the mission contract.
- When a worker escalates an allowlisted user-repair state, the coordinator becomes the only user-facing decision surface. The affected worker withholds only the exact impossible or uncertain action while its recurring Heartbeat remains active for re-probe; workers never contact the user or ask for confirmation in their own tasks.
- When a worker returns `MISSION_COMPLETE`, the coordinator marks only that lane terminal and disables its Heartbeat. It reports overall completion only after every lane enabled for the same `mission_id` is terminal and all mission Heartbeats are inactive.
- When a worker returns `SUBREDDIT_RETIRED`, record the subreddit in the shared retired set, notify the user once, and leave all workers/timers running. Never convert this event into a risk decision without separate account-level evidence.
- A recovered `STALE_OWNER_TOMBSTONE` remains internal. The mission report may state that one lane owner was replaced, but does not ask the user to approve continuation. A failed replacement stays `lane_recovering`; the supervisor retries later without affecting other owners.

## User Surface

The user continues speaking only in `Reddit 主控台`. Report lane titles and concrete blockers when useful, but keep task IDs, tool names, registry internals, and worker prompts hidden unless explicitly requested.

## Presentation And Lifecycle

- Pin: `Reddit 主控台` only.
- Keep unpinned/unarchived: `Reddit 评论台`, `Reddit 发帖台`, `Reddit 跟进台`, `Reddit 浏览台`, and `Reddit 主页台`, including while idle between missions.
- Archive after completion: installer probes, timezone diagnostics, smoke tests, and other temporary tasks that own no active heartbeat/tab.
- Retired worker: stop/remove its heartbeat, release its tab, remove it from the registry, unpin it, then archive it.
- Never archive a task merely to hide a blocker or while an automation still targets it.
- Missing pin/archive presentation controls do not block Reddit operations; record the unavailable UI action internally.

## Exclusions

- no invisible subagents in place of persistent tasks
- no routine or per-Heartbeat callback requirement; the recurring coordinator supervisor pulls worker proof and maintains slot counts
- no Goal Mode
- no combined worker or combined execution heartbeat
- no coordinator fallback that publishes, replies, performs exploratory/natural browsing, or votes; exact read-only permalink/profile verification during acceptance or audit is allowed
- no model rules from an external supervisor Skill; use `model-runtime.md`
