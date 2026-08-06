# Unit guides

For `direct_target_mode`, keep browsing, comments, and follow-up inside the
compiled `target_posts` list. Do not expand to other communities or create a
new target unless the user supplies a new assignment.

Load the selected section only after the owner decides `RUN`.

Before drafting any public text, apply [public writing defaults](operation-defaults.json#public_writing):
keep it short, conversational, and slightly imperfect. Every ordinary comment
must contain at least one contextual marker, and every post's opening paragraph
must contain at least one; a second marker is welcome when it sounds natural.
Rotate markers by context; do not manufacture typos or repeat a stock catchphrase.
Formal rules, form fields, and technical passages are the explicit exceptions.
Style never overrides truth, community rules, or the actual contribution.

## Browsing

Read current community pages in Chrome, including enough body/context to classify
each item. Build a dated candidate pack with a compact source reference for the
comments/posts unit, or record `RESEARCH_ONLY`. For an action-authorized mission,
browsing is supporting work: do not end the formal round after a candidate pack
when an action unit can search for and attempt its own target. Voting is not a
supported operation: do not inspect vote controls or emit upvote/downvote
mutations from any unit.

For `discover` or `seeded_expandable` scope, prefer communities not already
audited in the current mission. Coverage budget changes the breadth of this
packet, not the Heartbeat. Do not rescan a route parked as `RULE_BLOCKED` or a
post goal parked as `MATERIAL_REQUIRED` unless a revision or fresh material
explicitly re-arms it.

If the pack establishes an exact route and a truthful contribution boundary for
an authorized comment or post, call the queue's atomic `handoff` with the target
unit, `ACTION_ELIGIBLE`, the exact candidate reference, and a compact source
reference when useful. Handoff is optional because the action unit may discover
another target in the same packet. If no truthful boundary exists, keep searching
within the action packet before ending the round; never create a pause/resume
revision merely to alter cadence.

## Comments

Use the comment action path: read the post and nearby context, one visible current
rule or submit signal, and the composer. A short context-fit comment needs no
broad Web Search; add one focused query only for a factual, technical, or
unfamiliar claim. With explicit comment authority, attempt one original comment
in every formal action round. If a candidate fails, continue to new targets in
the same packet, up to 60 target reads, and stop at the first compliant target.
Write one or two short sentences by default, with natural contractions and at
least one contextual filler such as `honestly`, `kinda`, `wait`, or `ngl`; use
only the ones that fit the community, vary the pattern, and optionally add a
second. Do not invent a personal
experience, factual claim, or product promotion. Check
duplicates only on the same target. If all tested candidates fail, record the
specific no-action reason and continue at the next wake; do not park the whole
comments lane.
If the candidate is still specific and truthful but the live rule/composer
gate cannot be completed because Chrome or DOM reads time out, record
`LIVE_GATE_UNVERIFIED` and finish as `YIELDED`. After a completed submit that
stays visually pending, use at most one same-target refresh/read-only verification;
never submit a second time. Do not mark the candidate
`RULE_BLOCKED` unless the blocking rule, approval message, form state, or mod
instruction was actually visible.

## Posts

Complete the post Web Search pack and Chrome finalist gate. Hard compliance
comes first; truthful minimum context comes second; quality only ranks passing
candidates. Do not use a quality score as an additional hard lock once rule,
truth, format, session, duplicate, and submit gates pass. A native discussion can ask a real, answerable question without a
project link. A project/showcase post requires real artifacts/details and clear
relationship disclosure. Missing a project link does not itself block a native
discussion post. With explicit post authority, publish at most one
native post and verify it once. If a completed submit has no immediate UI echo,
use at most one same-target refresh/read-only verification, never a second post.
Draft the shortest complete version: short
paragraphs, contractions, and at least one natural discourse marker in the
opening paragraph are required by default; add more only when they fit;
include only the context the subreddit requires. Never cross-post a template to force a KPI. If
the truthful subject/artifact/relationship is absent, record
`MATERIAL_REQUIRED` only after a bounded mission-wide audit proves every
allowed truthful post format needs absent material, with
`--block-scope MISSION` and evidence. A failed candidate/community instead
uses `candidate-reject` and returns to browsing.
If the final route appears viable but Chrome cannot read the current rules,
format, duplicate, session, or composer state, yield with
`LIVE_GATE_UNVERIFIED`; do not convert an unread gate into `RULE_BLOCKED`.

Persist a compact `live_gate_checkpoint` once the final target route is known:
target URL, internal session proof, relevant rule/format proof, duplicate proof,
composer proof, and capture time. If the same packet resumes after context
compaction and the tab remains on the target, do not rerun the broad Web Search
or navigate away and back just to recreate the checkpoint. Take one fresh,
minimal session/composer snapshot immediately before `MUTATION_INTENT`; rerun
the full gate only after a tab rebind, login change, route change, or stale
checkpoint. Every actual submission still has one deterministic action key and
one attempt.

## Follow-up

When `全面推进` authorizes follow-up, run an account-wide sweep instead of
waiting for a browsing handoff. In the same logged-in Chrome inspect the user's
own posts, own comments, notifications/inbox replies, recent account activity,
and previously recorded own permalinks. Build one de-duplicated queue of
conversations with a new reply, an unanswered direct question, or an open own
thread that still needs a truthful response.

This sweep is independent of the business direction and community-discovery
filter: maintain every eligible account-owned conversation, but never discover
or reply to unrelated third-party threads. For each queued item, read the
parent and nearby context, confirm the current rule/composer, persist one
action key, submit one concise truthful reply, and verify it. If a completed
submit stays visually pending, use one same-target refresh/read-only verification
before deciding it is uncertain. Process all
eligible items found until the packet/hourly cap; carry the remainder to the
next wake. A sweep with no eligible items records `FOLLOW_UP_SWEEP_EMPTY`, not
`NOT_APPLICABLE`. Moderator instructions, pending/removed content, closed
threads, or an unread Chrome gate are recorded per item and do not block the
rest of the queue.

Outside `全面推进`, follow-up remains read-only unless explicit follow-up
authority is present. Do not delete content automatically or repost after an
uncertain submission.

## Presence

Inspect or change profile, membership, flair, or tags only when explicitly
authorized, truthful, and tied to a concrete requested change. Otherwise record
`NOT_APPLICABLE`; it never publishes text or touches vote controls.
