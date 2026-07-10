# Bootstrap Profile And Community Setup

Use only during first-account bootstrap or an explicit one-off setup repair. It is not a recurring operation lane, has no worker, and owns no heartbeat. It covers profile/homepage upkeep, target-based join/subscribe, truthful flair/tag, and membership review.

## Presence State

Track:

- profile: display name, avatar/banner, about, last edit
- membership: subreddit, fit reason, joined state, flair, joined/visited/review timestamps
- cadence: joins and flair/profile edits in the last hour and `24h`

If no prior log exists, reconstruct what is visible and begin conservatively.

## Default Cadence Ceilings

| Action | Ceiling |
|-|-:|
| Join/subscribe | `5/hour`, `10/24h` |
| Flair/tag changes | `3/hour`, `8/24h` |
| Profile/about/avatar/banner edits | `2/day` total |

These are ceilings, not targets. A bootstrap setup slot joins `1-3` strong communities or makes one coherent profile update.

## Membership Gate

Before join/subscribe:

1. Open the subreddit and read home/about/sidebar plus recent `Hot` or `New`.
2. Confirm the pool layer is not `A0`/`No-go`.
3. Score target relevance, activity, culture fit, rules/risk, diversity value, and useful truthful flair.

- `Act >=78`: fit is clear and cadence remains.
- `Watch 60-77`: revisit later.
- `Skip <60`: off-topic, inactive, sensitive, high-risk, or useful only for promotion.

Do not join and immediately publish a main post unless the user explicitly asks and live rules clearly support it.

## Profile And Flair

For internal Loci accounts with no user-specified persona, use a broad truthful interest profile: AR/VR/XR, 3D tools, spatial social, location-based play, indie apps, game development, photography, and creative tech.

Keep the profile legible rather than promotional. Do not claim founder, employer, expertise, location, age, metrics, testing history, or product usage unless true and explicitly provided. Avoid product links, waitlists, Discord, and sales copy.

Use ordinary truthful flair such as `Beginner`, `Hobbyist`, `Indie Dev`, `VR User`, `iOS`, `Photography`, `Student`, or `Learner` only when the community offers it and it is accurate.

## Presence Slot

1. Confirm account/time and restore prior presence state.
2. Compute remaining cadence capacity.
3. Inspect profile and high-fit membership candidates.
4. Run membership gate.
5. Reselect the main task's dedicated bootstrap tab before each edit/join/flair action, verify account/target, and verify final state.
6. Update timestamps and set the next review only when another action is genuinely due.

Complete and verify the bootstrap setup before operation workers start. Summarize changed communities/profile surfaces inside the main task's first report. Keep watched/skipped candidates, scores, reasons, and remaining cadence internal unless they explain why no action occurred.
