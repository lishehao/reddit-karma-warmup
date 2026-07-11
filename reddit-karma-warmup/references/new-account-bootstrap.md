# New Account Bootstrap

Use when a `K0 New` account is in `fresh_bootstrap`: blank, under `48h` old, has very low/unknown karma, has unknown verification, or has no clean visible history. Bootstrap is a substate, not a separate account tier or a no-action waiting room.

Run the full flow only while `bootstrap_state` is `not_started`, `in_progress`, or `needs_repair`. After the main task stores the first-hour baseline and sets `bootstrap_state=initialized`, later user commands use MISSION flow even if the account remains `K0 fresh_bootstrap` for pacing/risk purposes.

## Default Sequence

1. **Inspect first.** Confirm the account, visible age/karma/history, email-verification or eligibility signals where Reddit exposes them, notifications, and any warning/removal state.
2. **Establish a truthful profile.** Load `community-presence-playbook.md`; add a low-risk display/about/avatar/banner only where needed.
3. **Join a few high-fit communities.** Run the membership gate; prefer `1-3` in the first slot.
4. **Browse before and alongside publishing.** Run one intensity-sized qualified-read slot across eligible communities. Standard starts with `20-30` reads and targets `2` combined verified votes without lowering `browse-vote-playbook.md` gates.
5. **Run the first-hour launch.** Immediately execute comments, post preflight, follow-up, and natural browsing using the selected intensity. Comments remain micro/fragment/one-liner first and span lower-restriction communities.
6. **Pause between submissions.** After every verified comment, use a local `60-120 sec` pause before the next publish. Discovery, reading, drafting, and both checks happen in addition to this pause.
7. **Verify in parallel.** Record the first permalink immediately so the coordinator can run `startup-health-check.md` while the comment worker continues. Stop further comments only when that check produces a concrete failure, warning, captcha, rate limit, or removal state; a pending delayed check alone is not a reason to wait.
8. **Continue after the first hour.** A clean first-hour result continues the selected intensity; explicit high-volume mode follows `proactive-playbook.md`. A failed check activates the matching recovery level. Avoid repeating one subreddit, topic cluster, opening, or opinion pattern.
9. **Main-post lane.** Broad operation includes one immediate candidate/preflight micro-slot. Permit up to two no-link, specific, native posts on the first day only when each passes the full live post preflight. `K0` does not create a six-hour wait before the first eligible post. Only the second requires the first to remain visible, a different subreddit and angle cluster, and at least `6h` separation.

The user's explicit sequence may override these defaults unless a hard stop is visible.

## Default Persona

For internal Loci accounts without another supplied persona:

- interests: AR/VR/XR, 3D, spatial social, place-based play, indie apps, game development, photography/creative tech
- voice: curious, practical, brief, praise-first
- never invent founder/employee/expert status, location, age, metrics, product use, or testing history
- keep bootstrap free of product pitches, Loci, waitlist, Discord, landing page, and app links

## First-Day Defaults

- profile/avatar/banner/about edits: max `2`
- joins: prefer `1-3`, max `5`
- browsing: one intensity-sized slot at launch; standard uses `20-30` qualified reads, vote target `2`, cap `4`; explicit user values override, and a shortfall is valid only after the configured budget is exhausted
- proactive comments: use the selected intensity; `60/day` requires explicit high-volume mode, at least `6h`, and enough passing candidates
- startup checkpoint: coordinator verifies the first permalink immediately and again after `15-30 min`, while the comment worker continues within the selected intensity unless a concrete failure appears
- main posts: `0-2/day`; never more than one per subreddit per `24h`
- first main post: no skill-level `6h` wait; publish only after full live eligibility/preflight passes
- first-hour comments: low `2-4`, standard `4-6`, high `6-10`, with `60-120 sec` local pause after every verified submission
- second post checkpoint: first post remains visible after `30-60 min`, no account/community warning, different community and angle, `>=6h` later

These are operating defaults, not Reddit platform rules or guarantees. The hourly range is not a quota and does not override the daily range. Stop account-wide outward actions on captcha, rate limit, account warning, or login mismatch. For one removal or invisibility event, stop that target/community, inspect the exact notice, and continue elsewhere only when no account-wide blocker exists.

`bootstrap_state=initialized` records workflow completion only. It does not change Karma tier, account age, subreddit eligibility, recovery rules, or post limits.

## Bootstrap Exit And Tier Change

Change `K0 fresh_bootstrap -> K0 active_new` only when all are true:

- account has at least `48h` of age or observed clean activity
- email/eligibility is not visibly blocking the account
- at least `10` comments remain visible across at least `3` communities
- no captcha, rate limit, account warning, or repeated visibility failure occurred in the checkpoint window

A visible main post is useful evidence but is not required to exit bootstrap. Karma alone does not override failed visibility or verification signals.

Demotion/recovery:

- one community removal: apply `R1 Isolated` from `proactive-playbook.md`
- two failures across different communities in `24h`: apply `R2 Repeated`; for `K0 recovery`, use `2-5/hour`, `4-10/day`, and no post for the first `24h`
- captcha, rate limit, account warning, lock, or wrong-account state: apply `R3 Account Stop`

## Help-Seeking Post

Use a real workflow question with one clear ask. The second same-day post, when allowed, must use a different native form such as a concrete observation, comparison, or artifact discussion rather than a rewritten copy of the first question.

- beginner trap
- workflow friction
- tool-choice tradeoff
- AR/3D/location/social design pain

Do not use `I built an app`, `Would you use this?`, tester recruitment, surveys, product screenshots, or link drops. If submit says moderator approval is required, skip; if the submitted post becomes pending, withdraw it.

## Bootstrap State

Store `profile_done`, `presence_done`, `waiting`, `comments_started`, `help_post_done`, or `blocked` internally. The user-facing round report uses the exact three lines from `SKILL.md`; expose bootstrap state only inside `本轮完成` when it explains why no outward action occurred.
