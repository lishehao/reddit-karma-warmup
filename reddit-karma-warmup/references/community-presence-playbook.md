# Bootstrap Profile And Community Setup

Use only in `Reddit 主页台` during first-account bootstrap or an explicit setup/repair mission. This lane covers profile/homepage upkeep, target-based Join/subscribe, truthful Flair/tag, and membership review. It normally terminates after one verified slot; when the user explicitly requested later presence work, this task creates and owns its own recurring Heartbeat.

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
3. Score the exact community:

| Factor | Points | Simple question |
|-|-:|-|
| Relevance | 0-25 | Does it fit the account's truthful interests? |
| Current activity | 0-20 | Are recent native posts and discussions alive? |
| Culture fit | 0-20 | Can the account participate normally rather than only promote? |
| Rules and risk | 0-20 | Are ordinary membership and participation clearly allowed? |
| Diversity/flair value | 0-15 | Does it add a useful distinct interest or truthful flair? |

- `Act >=78`: fit is clear and cadence remains.
- `Watch 60-77`: revisit later.
- `Skip <60`: off-topic, inactive, sensitive, high-risk, or useful only for promotion.

Do not join and immediately publish a main post unless the user explicitly asks and live rules clearly support it.

## Profile And Flair

Resolve `account-direction.md` before profile or membership changes. For internal Loci accounts with no user-specified direction, use its broad truthful default rather than inventing a narrow persona.

Keep the profile legible rather than promotional. Do not claim founder, employer, expertise, location, age, metrics, testing history, or product usage unless true and explicitly provided. Avoid product links, waitlists, Discord, and sales copy.

Use ordinary truthful flair such as `Beginner`, `Hobbyist`, `Indie Dev`, `VR User`, `iOS`, `Photography`, `Student`, or `Learner` only when the community offers it and it is accurate.

## Presence Slot

1. Confirm account/time and restore prior presence state.
2. Compute remaining cadence capacity.
3. Inspect profile and high-fit membership candidates.
4. Run membership gate.
5. Reselect `Reddit 主页台`'s dedicated tab before each edit/join/flair action, verify account/target, and verify final state.
6. Update timestamps and set the next review only when another action is genuinely due.

Record verified changed state or exact inspected surfaces plus the valid no-action gate. For the usual one-slot bootstrap mission, report completion in this task and create no recurring timer. Keep watched/skipped candidates, scores, reasons, and remaining cadence local unless they explain no action.
