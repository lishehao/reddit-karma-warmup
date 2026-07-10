# Twelve Hour Ops Template

Use for about `8-12h`, overnight, or other long low-frequency runs. This is a planning overlay; lane behavior still comes from each playbook.

## Core Rule

- Execute the H0/current slot immediately.
- Each worker owns one lane and at most one future trigger.
- Each wake-up runs one small due slot, reconciles, then schedules the next one-shot continuation.
- Do not run every lane at every wake-up and do not catch up after a late trigger.
- Follow-up keeps its own `20-40 min` default sweep rhythm; the table below is only a coarse session map.

## K0 Fresh Bootstrap Track

| Window | Default work |
|-|-|
| H0-H1 | Account/time check, minimal profile setup, `1-3` strong joins, one `8-12` qualified-read browse slot with at most one gated vote, then target `10` short passing comments across at least `3` communities with a `60-120 sec` pause after each verified submission. The coordinator checks the first permalink in parallel. |
| H1-H3 | Continue the daily target after first-hour reconciliation and optionally preflight the first post. |
| H3-H6 | If clean, continue in comment slots toward roughly `25-35` cumulative comments across diverse communities. |
| H6-H8 | Continue toward `40-45`; optional second post only if the first is visible, the target/angle differs, and `>=6h` elapsed. |
| H8-H10 | Continue toward the `60/day` target only while candidates pass and visibility stays clean. |
| H11 | Closeout visibility and tier checkpoint; do not force missed comments or create a catch-up burst. |

## Activated K0 / K1 / K2 Track

| Window | Default work |
|-|-|
| H0 | Account/time check plus one immediate follow-up, presence action, `8-12` qualified-read browse slot, or `1-2` comments. |
| H1-H3 | Comment slots toward the `60/day` target; one post preflight window only if posts are enabled. |
| H4-H6 | Follow-up/visibility, presence review, and diverse comment slots. |
| H7-H9 | Continue comments toward the daily target; optional second post only for a strong distinct candidate. |
| H10-H11 | Final follow-up/comment slot and closeout; no forced catch-up. |

## Dispatch

Broad operation enables follow-up, presence, comments, and browsing. Add posts only when requested or a strong candidate warrants preflight. Each worker receives the shared stop time, account tier, pool, first due slot, and its independent Chrome tab rule.

Actual trigger intervals come from `scheduler-and-heartbeats.md`, not fixed hourly recurrence. Use the four-field report from `orchestration-core.md`; keep selected track, lane owners, slot math, stop time, and scheduler readback internal unless they create a risk or scheduling failure.
