# Unit guides

Load the selected section only after the owner decides `RUN`.

## Browsing

Read current community pages in Chrome, including enough body/context to classify
each item. Build a dated candidate pack with a compact source reference for the
comments/posts unit that can genuinely use it, or record `RESEARCH_ONLY`.
Candidate discovery does not itself complete a comment or post objective. Votes are disabled
unless the mission explicitly grants `browsing: VOTE_AUTHORIZED`; only then may
this unit inspect and operate one visible vote control. No other unit touches
votes.

For `discover` or `seeded_expandable` scope, prefer communities not already
audited in the current mission. Coverage budget changes the breadth of this
packet, not the Heartbeat. Do not rescan a route parked as `RULE_BLOCKED` or a
post goal parked as `MATERIAL_REQUIRED` unless a revision or fresh material
explicitly re-arms it.

If the pack establishes an exact route and a truthful contribution boundary for
an authorized comment or post, call the queue's atomic `handoff` with the
target unit, `ACTION_ELIGIBLE`, the exact candidate reference, and a compact
source reference before the
browsing packet finishes. This arms the target's next verified Heartbeat packet;
it does not bypass that packet's research, live-rule, duplicate, account, or
composer gate. If no truthful boundary exists, leave the target `PENDING` or
park it with the evidence reason—never create a pause/resume revision merely
to alter its cadence.

## Comments

Complete the research/index SOP, then open only candidates with a specific,
truthful contribution. Read the post, relevant parent, nearby replies, live
rule context, and composer. With explicit comment authority, publish at most
one original context-fit comment in the packet; otherwise record research only.
Do not manufacture a quota, a personal experience, a factual claim, or product
promotion. If the exact candidate fails a visible rule or fit gate, call
`candidate-reject`; do not park the whole comments lane. Browsing must refill a
different candidate at the next verified Heartbeat, and the rejected exact
candidate must not be handed back.
If the candidate is still specific and truthful but the live rule/composer
gate cannot be completed because Chrome or DOM reads time out, record
`LIVE_GATE_UNVERIFIED` and finish as `YIELDED`. Do not mark the candidate
`RULE_BLOCKED` unless the blocking rule, approval message, form state, or mod
instruction was actually visible.

## Posts

Complete the post Web Search pack and Chrome finalist gate. Hard compliance
comes first; truthful minimum context comes second; quality only ranks passing
candidates. Do not use a quality score as an additional hard lock once rule,
truth, format, account, duplicate, and submit gates pass. A native discussion can ask a real, answerable question without a
project link. A project/showcase post requires real artifacts/details and clear
relationship disclosure. Missing a project link does not itself block a native
discussion post. With explicit post authority, publish at most one
native post and verify it once. Never cross-post a template to force a KPI. If
the truthful subject/artifact/relationship is absent, record
`MATERIAL_REQUIRED` only after a bounded mission-wide audit proves every
allowed truthful post format needs absent material, with
`--block-scope MISSION` and evidence. A failed candidate/community instead
uses `candidate-reject` and returns to browsing.
If the final route appears viable but Chrome cannot read the current rules,
format, duplicate, account, or composer state, yield with
`LIVE_GATE_UNVERIFIED`; do not convert an unread gate into `RULE_BLOCKED`.

Persist a compact `live_gate_checkpoint` once the final target route is known:
target URL, account proof, relevant rule/format proof, duplicate proof,
composer proof, and capture time. If the same packet resumes after context
compaction and the tab remains on the target, do not rerun the broad Web Search
or navigate away and back just to recreate the checkpoint. Take one fresh,
minimal account/composer snapshot immediately before `MUTATION_INTENT`; rerun
the full gate only after a tab rebind, login change, route change, or stale
checkpoint. Every actual submission still has one deterministic action key and
one attempt.

## Follow-up

Inspect only known own verified permalinks, supplied URLs, notifications, and
recent account activity. Without a verified own permalink record
`NOT_APPLICABLE` and do not poll. An explicit follow-up authority may permit one useful reply;
otherwise it is read-only. Do not discover unrelated threads, vote, or delete
content automatically. Moderator instructions or a pending/removed result are
risks to report, not permission to repost.

## Presence

Inspect or change profile, membership, flair, or tags only when explicitly
authorized, truthful, and tied to a concrete requested change. Otherwise record
`NOT_APPLICABLE`; it never publishes text or touches votes.
