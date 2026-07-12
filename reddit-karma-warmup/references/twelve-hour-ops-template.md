# Twelve Hour Ops Template

Use for about `8-12h`, overnight, or other long low-frequency runs. This is a planning overlay; lane behavior still comes from each playbook.

## Core Rule

- Execute the H0/current slot immediately.
- Each worker owns one lane and at most one future trigger.
- The coordinator creates one recurring Heartbeat per enabled worker with nonterminal future work plus one recurring read-only supervisor for the full window. Each worker wake runs one due slot or records `not_due`; workers never renew timers. A terminal bootstrap presence slot receives no recurring timer.
- Do not run every lane at every wake-up and do not catch up after a late trigger.
- Follow-up keeps its own `20-40 min` default sweep rhythm; the table below is only a coarse session map.

## K0 Fresh Bootstrap Track

| Window | Default work |
|-|-|
| H0-H1 | Account/time check; `Reddit 主页台` completes bootstrap presence when required; then immediate comment, post-preflight, follow-up, and natural-browse micro-slots at the selected intensity. The coordinator checks the first permalink in parallel. |
| H1-H3 | Continue all four operation lanes at the selected intensity after first-hour reconciliation. |
| H3-H6 | Keep diverse comment/browse slots, follow-up sweeps, and native post candidate checks; publish only passing candidates. |
| H6-H10 | Continue the selected intensity without catch-up bursts; explicit high-volume mode may progress toward its authorized daily ceiling. |
| H11 | Closeout visibility, replies, remaining target, and tier checkpoint. |

## Activated K0 / K1 / K2 Track

| Window | Default work |
|-|-|
| H0 | Execute one immediate micro-slot for comments, posts, follow-up, and natural browsing. |
| H1-H3 | Continue all four lanes at the selected intensity. |
| H4-H6 | Follow-up/visibility, diverse comment/browse slots, and native post candidate checks. |
| H7-H9 | Continue within the chosen envelope; no forced daily target unless explicitly requested. |
| H10-H11 | Final follow-up, visibility, comment/browse/post reconciliation, and closeout. |

## Dispatch

Broad operation enables comments, posts, follow-up, and natural browsing. Profile/community setup is bootstrap-only. Each worker receives the shared stop time, intensity, account tier, pool, first due slot, and its independent Chrome tab rule.

Actual trigger intervals come from `scheduler-and-heartbeats.md`, not fixed hourly recurrence. Use the three-line report from `orchestration-core.md`; keep selected track, lane owners, slot math, stop time, and scheduler readback internal unless they create a risk or scheduling failure.
