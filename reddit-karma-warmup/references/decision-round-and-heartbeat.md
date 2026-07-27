# Decision Rounds and Mission Heartbeat

This is the sole authority for when the single `Reddit 运营台` evaluates and
runs its five units. It prevents a fixed five-unit sweep from turning into
unnecessary Chrome work or forced outward actions.

## Terms

- **Decision round**: one Heartbeat wake's no-Chrome evaluation of every due
  unit. It is not a promise to execute every unit.
- **Work packet**: the one bounded Chrome packet selected by that round.
- **Macro-cycle**: every enabled unit has received a decision since its last
  due time. It can span several Heartbeats.

## Per-wake state machine

```text
deadline? -> cleanup
yielded unit? -> resume it first
otherwise -> list due active units
  -> record RUN | WATCH | SKIP | DEFER for every due unit
  -> run at most one selected packet
  -> persist next_due for every unit
```

`RUN` means the unit receives exactly one bounded packet. `WATCH` performs no
outward action and schedules a normal read check. `SKIP` records that no work
is useful now. `DEFER` records a concrete prerequisite such as no authority,
cooldown, missing truthful evidence, or a live-rule blocker. A decision is not
an action, and a count target never converts a `WATCH`, `SKIP`, or `DEFER` into
`RUN`.

The default packet cap is one Chrome unit and one outward action per wake. An
outward action remains conditional on its unit authority, local Reddit rules,
account/submit state, truthful evidence, pacing, and post-action verification.

## Default cadence

Read `operation-defaults.json.decision_round` rather than calculating ad hoc
intervals. Defaults are decision/recheck intervals, not action quotas:

| Unit | Normal decision interval | Packet purpose |
| --- | ---: | --- |
| browsing | 40 min | 10–18 qualified reads; an explicit vote only if authorized |
| comments | 60 min | 4–8 contextual candidates; 0–1 eligible comment |
| posts | 180 min | 8–12 live rule/community reads; 0–1 compliant native post |
| follow-up | 90 min idle / 20 min active chain | check known chains; 0–1 eligible reply |
| presence | 24 h | one audit; 0–1 truthful profile/community change |

For a short mission, all enabled units are due for the first decision round so
the owner can explicitly choose `RUN`, `WATCH`, `SKIP`, or `DEFER`. Later
rounds use each unit's persisted `next_due`; they do not repeat a full sweep.

Pause means the entire unit, including its research. To keep research while
preventing publication, hot-plug that unit's authority back to
`RESEARCH_ONLY` instead of pausing it.

## One recurring Heartbeat

Create one mission-level recurring Heartbeat every 20 minutes. Use an `UNTIL`
that extends 25 minutes past `operation_stop_at` so the first wake at/after the
deadline can cleanly release agent-owned tabs and delete the Heartbeat. Never
create per-unit timers or a `COUNT=1` replacement timer.

At a wake, compare actual trigger time with expected time:

- within ±5 minutes: ordinary; continue;
- later than ±5 minutes: recompute due units from actual time and do not
  backfill missed packets or actions;
- at/after the mission deadline: no new Reddit work, only cleanup.

Open the durable wake record with both `expected_at_utc` and `actual_at_utc`.
The queue derives `trigger_delta_seconds` and persists either
`WITHIN_TOLERANCE` or `RECOMPUTED_FROM_ACTUAL`; the owner must not estimate the
delta or claim that a missed wake was replayed.

An active unit, open read batch, or open Chrome boundary does not start another
packet. The Heartbeat records the state and waits for the same owner to settle
or yield. A yielded unit has priority over all later due units on the next wake.

## Required durable evidence

For each due unit, append: wake ID, due reason, `RUN/WATCH/SKIP/DEFER`, reason,
next due time, authority state, and any selected packet ID. For a run packet,
append qualified-read totals, candidate/action outcome, exact mutation key if
applicable, and verified completion/yield state. Preserve this history through
hot-plug revisions; never reset it to make a unit appear due sooner.
