# Posts Coverage and Conditional KPI

Load only in the active `posts` unit. Numeric settings come from
`operation-defaults.json`.

## Conditional publication target

The normal publication KPI is `CONDITIONAL_ONE_VERIFIED_POST`: find and publish
at most one post only when an exact candidate passes every live gate. Coverage
and publication are separate:

- coverage records the configured reference sweep, Web Search pack, live
  reads, and candidate packets;
- publication remains `0/1` until a visible verified permalink exists.

Never invent facts, project ownership, metrics, lived experience, or a rule
exception merely to satisfy the KPI. A deadline or a genuinely empty eligible
pool reports the shortfall honestly.

## Fixed decision order

1. **Hard compliance:** route, current rules, account/submit gate,
   flair/title/body/megathread, duplicate/recent-own-post and promotion checks.
2. **Truthful minimum content floor:** relevant, native-format, non-spam, not
   an FAQ/recent duplicate, and no unsupported personal or external claim.
3. **Secondary ranking:** only among passing candidates, prefer audience fit,
   timing, survivor fit, and lower moderation friction.

`native_discussion` is the default when the user did not supply a truthful
artifact. It does not require a project link or metric. `artifact` mode requires
directly verifiable ownership and factual support. Content scores identify a
concrete rewrite/retarget problem; they never override compliance or reject an
otherwise compliant, truthful native discussion for failing an arbitrary high
quality score.

Each candidate packet records community, mode, premise, exact gate evidence,
content-floor result, secondary rank only if eligible, and the accept/reject
reason. The active unit yields instead of forcing publication when recovery or
the mission deadline intervenes.

