# New Account Bootstrap

Use when a `K0 New` account is in `fresh_bootstrap`: blank, under `48h` old, has very low/unknown karma, has unknown verification, or has no clean visible history. Bootstrap is a substate, not a separate account tier or a no-action waiting room.

Run the full flow only while `bootstrap_state` is `not_started`, `in_progress`, or `needs_repair`. After the main task stores the first-hour baseline and sets `bootstrap_state=initialized`, later user commands use MISSION flow even if the account remains `K0 fresh_bootstrap` for pacing/risk purposes.

## Default Sequence

1. **Inspect first.** Confirm the account, visible age/karma/history, email-verification or eligibility signals where Reddit exposes them, notifications, and any currently active warning/removal state. Keep historical/cleared events in the ledger without turning them into startup blockers.
2. **Establish a truthful presence baseline.** `Reddit 分发台` may allocate `Reddit 主页台`; that task loads `community-presence-playbook.md`, makes one immediate best-effort display/about/avatar/banner checkpoint, and owns any requested retry without holding outward tasks.
3. **Join a few high-fit communities.** `Reddit 主页台` runs the membership gate and prefers `1-3` in the first slot. Profile/Join/Flair incompleteness never blocks outward lanes once account identity is known.
4. **Read before and alongside publishing.** Comment, post, and follow-up tasks independently assess natural incidental votes on external content they already open. These votes have no quota and never cause extra browsing. Create a separate intensity-sized browse slot only when the user explicitly requests pure browsing/voting.
5. **Run the first-hour launch.** If the user did not specify intensity/count, use the fresh-account low default: comment target/cap `3/4`, first-day proactive-comment cap `12`, and main-post cap `1`. Immediately execute comments, post preflight, and follow-up. Comments remain micro/fragment/one-liner first and span at least three lower-restriction communities. Add pure browsing only when explicitly requested.
6. **Pause between submissions.** After every verified comment, use a local `60-120 sec` pause before the next publish. Discovery, reading, drafting, and both checks happen in addition to this pause.
7. **Verify locally.** Record and verify the first permalink in the comment task while its mission continues. Any removal retires only its exact subreddit; continue in unaffected communities. Timed rate limits auto-resume; allowlisted account repair states withhold only impossible mutations while this task's Heartbeat and permitted work continue. A pending delayed check or historical event is not a reason to wait.
8. **Continue after the first hour.** Continue the user's selected intensity; explicit high-volume mode follows `proactive-playbook.md`. A currently active blocker uses its minimum recovery condition, then resumes the same latest command. Historical or cleared failures never select a recovery level. Avoid repeating one subreddit, topic cluster, opening, or opinion pattern.
9. **Main-post lane.** Broad operation includes one immediate candidate/preflight micro-slot. Default to the truthful `beginner-common-mistake` tendency in `proactive-playbook.md`, using a narrow community-specific pitfall that experienced members can answer. Permit up to two no-link, specific, native posts on the first day only when each passes the full live post preflight. `K0` does not create a six-hour wait before the first eligible post. Only the second requires the first to remain visible, a different subreddit and angle cluster, and at least `6h` separation.

The user's explicit sequence overrides these defaults. Only a current allowlisted user-repair state can temporarily withhold the exact impossible mutation.

## Default Persona

For internal Loci accounts without another supplied persona:

- interests: AR/VR/XR, 3D, spatial social, place-based play, indie apps, game development, photography/creative tech
- voice: curious, practical, brief, praise-first
- never invent founder/employee/expert status, location, age, metrics, product use, or testing history
- keep bootstrap free of product pitches, Loci, waitlist, Discord, landing page, and app links

## First-Day Defaults

- profile/avatar/banner/about edits: max `2`
- joins: prefer `1-3`, max `5`
- incidental voting: comments/posts/follow-up score only already-read external content, with no quota or extra discovery
- explicit browsing: when requested, one intensity-sized slot at launch; standard starts at `20` qualified reads, vote target `2`, cap `4`
- proactive comments: unspecified operation defaults to target/cap `3/4` in the first hour and no more than `12` in the first `24h`; `60/day` requires explicit high-volume mode, at least `6h`, and enough passing candidates
- startup checkpoint: the comment task verifies its first permalink immediately; delayed visibility may be checked on its next wake without pausing work
- main posts: unspecified operation defaults to `0-1/day`; explicit higher intensity may use `0-2/day`; never more than one per subreddit per `24h`
- first main post: no skill-level `6h` wait; publish only after full live eligibility/preflight passes
- first-hour comments: low target/cap `3/4`, standard `5/6`, high `8/10`, with `60-120 sec` local pause after every verified submission
- second post checkpoint: first post remains visible after `30-60 min`, no account/community warning, different community and angle, `>=6h` later

These are operating defaults, not Reddit platform rules, guarantees, or grounds to reject an explicit override. Timed limits auto-retry; allowlisted user-repair states withhold only the mutations they prevent, while Heartbeats and permitted work continue. For one removal or invisibility event, retire that target/community, inspect the exact notice, and continue elsewhere.

`bootstrap_state=initialized` records workflow completion only. It does not change Karma tier, account age, subreddit eligibility, recovery rules, or post limits.

## Bootstrap Exit And Tier Change

Change `K0 fresh_bootstrap -> K0 active_new` only when all are true:

- account has at least `48h` of age or observed clean activity
- email/eligibility is not visibly blocking the account
- at least `10` comments remain visible across at least `3` communities
- no captcha, sitewide rate limit, account warning, lock/suspension, or login mismatch is currently active at the checkpoint

A visible main post is useful evidence but is not required to exit bootstrap. Karma alone does not override failed visibility or verification signals.

Demotion/recovery:

- one community removal: apply `R1 Isolated` from `proactive-playbook.md`; retire that subreddit and continue elsewhere
- removals across multiple communities: apply `R2 Multiple Community Retirements`; retire those subreddits without changing the account tier or operating envelope
- current timed rate limit: automatic wait/re-probe while permitted work continues
- allowlisted current account repair state: record `R3 User Repair`, keep Heartbeats active, withhold only impossible mutations, and resume the latest command after repair

## Help-Seeking Post

Use a real workflow question with one clear ask. The default first form is a community-specific beginner/common-mistake question that invites experienced members to recall what went wrong and why. Never claim the account personally made the mistake unless true. The second same-day post, when allowed, must use a different native form such as a concrete observation, comparison, or artifact discussion rather than a rewritten copy of the first question.

- beginner trap
- workflow friction
- tool-choice tradeoff
- AR/3D/location/social design pain

Do not use `I built an app`, `Would you use this?`, tester recruitment, surveys, product screenshots, or link drops. If submit says moderator approval is required, skip. If an own submitted post becomes pending, delete/withdraw immediately without asking, verify once, retire that subreddit, and continue elsewhere; a temporary cleanup-route failure enters automatic retry and never pauses another lane.

## Bootstrap State

Store `profile_done`, `presence_done`, `waiting`, `comments_started`, `help_post_done`, or `lane_recovering` internally. The user-facing round report uses the exact three lines from `SKILL.md`; expose bootstrap state only inside `本轮完成` when it explains why no outward action occurred.
