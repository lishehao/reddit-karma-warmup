# Community Action Routing Overrides

Snapshot: 2026-07-13 secondary review of 78 candidate communities. Load only the exact subreddit row needed. This file overrides the coarse tier in the historical pool, but never overrides `account-community-denylist.md` or stricter current live rules.

The reviewed account surface showed about two years of account age, `119` post karma, and `510` comment karma. Those values are evidence from that snapshot, not permanent account identity. Recheck the visible account every run. Unknown local/community Karma, previous-activity requirements, moderator approval, or current suspension remain separate gates; do not label the account `new` merely because one of those is unknown.

States:

- `default`: ordinary non-product action may enter normal candidate scoring
- `conditional`: act only when the row condition is visibly satisfied
- `closed`: do not perform that action for Loci outward
- `research-only`: no outward action; extract language/pain only when the subreddit is not on the permanent denylist

| Subreddit | Ordinary comment | Main post | Product/Loci mention | Required boundary |
|-|-|-|-|-|
| `r/apps` | conditional | conditional | closed | Ordinary app-experience comments only. A main post must be a no-brand experience retrospective; no dedicated advertising account, giveaway without approval, or low-information promotion. |
| `r/betatesters` | conditional | conditional | conditional | Only a real beta with a concrete testing task after current permission is confirmed. A blank rules page or historical survivor is not permission. |
| `r/StartupSoloFounder` | conditional | closed | closed | Natural founder discussion only; current formal publishing permission remains unconfirmed. |
| `r/gamedesign` | conditional | closed | closed | Comment only on actual game-design mechanics. No general development, Loci outward, or product framing; showcase content belongs in the designated weekly surface. |
| `r/LEGOfortnite` | conditional | closed | closed | Exact game-native comments only; otherwise research-only. |
| `r/gmod` | conditional | closed | closed | Exact GMod-native comments only; no external product narrative. |
| `r/StableDiffusion` | conditional | closed | closed | Technical/non-promotional comments only when directly relevant; no Loci or unrelated AI positioning. |
| `r/collegeadvice` | conditional | closed | closed | Genuine non-product advice only; no product, recruiting, or soft promotion. |
| `r/AppIdeas` | default | conditional | closed | Main post only for no-link idea/concept validation. No completed project, App Store, mailing list, waitlist, or advertising. |
| `r/SideProject` | default | conditional | conditional | Real project, self-contained text, one specific question, no copied cross-post, waitlist-only pitch, pure link, or AI-first packaging. Product context must be transparent and non-CTA. |
| `r/roastmystartup` | default | conditional | conditional | Real project plus a specific critique request; no Product Hunt/Vercel-only link or AI slop. |
| `r/WebXR` | default | conditional | conditional | Real WebXR prototype or technical question only; self-promotion may be contextual but never spammy. |
| `r/Unity3D` | default | conditional | conditional | Unity-specific. Correct flair; no store/download-only post and no phone-recorded screen. Product mention must serve the technical point. |
| `r/IndieDev` | default | conditional | conditional | Development comments are fine. Main posts only when current Wednesday/Capsule and other live format rules match. |
| `r/FlutterDev` | conditional | closed | closed | Non-product technical comments only; main posts remain outside the default Loci route. |
| `r/reactjs` | conditional | closed | closed | Non-product React comments only; honor code/weekly/portfolio boundaries. |
| `r/nextjs` | conditional | closed | closed | Non-product Next.js comments only; no general product feedback or shilling. |
| `r/iOSProgramming` | conditional | closed | closed | Non-product Apple-development comments only; app posts remain subject to Saturday/activity rules and are closed by default. |
| `r/webdev` | conditional | closed | closed | Non-product technical comments only; no product marketing or generic feedback post. |
| `r/web_design` | conditional | closed | closed | Non-product design comments only; no portfolio/product route unless a future explicit rule check opens it. |
| `r/playtesters` | conditional | closed | closed | Natural testing-method comments only. A Loci test request needs a real playable build and a separate current-rule decision. |
| `r/Notion` | conditional | closed | closed | Only fully non-product, non-AI-promotion comments. No Loci, app link, CTA, template sale, or showcase outside allowed surfaces. |
| `r/ObsidianMD` | conditional | closed | closed | Only fully non-product, non-AI-promotion comments. No Loci, vibe-coded project, app link, or CTA. |
| `r/Entrepreneur` | research-only | closed | closed | Default no Loci outward. |
| `r/iosapps` | research-only | closed | closed | Default no Loci outward; local Karma and distribution-specific restrictions remain high friction. |
| `r/CollegeRant` | research-only | closed | closed | Default no Loci outward. |
| `r/SaaS` | research-only | closed | closed | Default no Loci outward. |
| `r/startups` | research-only | closed | closed | Default no Loci outward. |
| `r/GradSchool` | research-only | closed | closed | Default no Loci outward. |
| `r/worldbuilding` | research-only | closed | closed | Default no Loci outward; AI and world-context boundaries are high risk. |
| `r/vibecoding` | research-only | closed | closed | Default no Loci outward. |

## Permanent Deny Boundary

Only `r/gamedev` and `r/CozyGamers` are permanent account-level denylist entries at this snapshot. Do not infer a permanent ban merely because another community shares strict topicality, contribution-first culture, anti-spam/self-promo rules, AI restrictions, local reputation, weekly placement, or moderator approval.

## Decision Rule

1. Denylist match: no visit or action.
2. Current sitewide/account blocker: withhold the impossible mutation and follow lane recovery.
3. Exact action override: gate comment, main post, and product mention separately.
4. Historical pool: use only for audience/pain/background and rows not covered here.
5. Current rules/account controls: tighten when stricter; never loosen from survivor content alone.

When a row says `conditional`, missing evidence means skip/retarget, not permission. A valid technical comment remains technical: do not smuggle product positioning into an otherwise allowed reply.
