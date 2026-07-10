# Outbound Copy Gate

This reference was split out of SKILL.md to keep the entrypoint small. Load it only when the SKILL.md routing table says it is needed.

## Outbound Copy Gate

Run this gate before every outward text action: proactive comments, follow-up replies, main posts, and mod/Automod acknowledgements. The goal is to avoid fixed-length, generic, or AI-shaped replies.

Before drafting, decide and record:

- `length_tier`: micro / fragment / one-liner / two-beat / compact paragraph / long only-if-needed
- `why_this_length`: why this target deserves that length, based on thread energy and local style
- `tone`: praise-first, useful nit, crisp question, clarification, playful aside, or direct answer
- `interesting_hook`: the specific detail, contrast, question, or observation that makes the text worth posting
- `local_style_basis`: nearby comment/post style sampled from the target surface
- `avoid_pattern`: what common/generic reply shape to avoid, especially default two-sentence replies
- `length_mix_state`: the last `10` outward comment/reply measurements from `history_ledger`, including `char_count`, `word_count`, `sentence_form`, and `length_tier`
- `comment_fun_score`: for comments/replies only, whether the text is actually worth saying instead of just safe

Measurement rules:

- `char_count`: count the trimmed final Unicode text, including internal spaces and punctuation. This is the primary cross-language measure.
- `word_count`: count whitespace-delimited tokens. Treat it as secondary for Japanese or other scripts where whitespace is not a reliable word boundary.
- `sentence_form`: `fragment`, `one_sentence`, `two_sentence`, or `paragraph`.
- Measure the exact final text after publishing; do not estimate from the draft.

Length ladder:

| Tier | Typical size | Use when |
|-|-|-|
| `micro` | 1-6 words | simple reaction is enough and nearby replies are short |
| `fragment` | 5-15 words | one sharp observation or praise detail lands better than a full sentence |
| `one-liner` | 8-25 words | most ordinary comments; one idea only |
| `two-beat` | 20-45 words | useful when adding a small contrast, caveat, or question |
| `compact paragraph` | 45-90 words | only for concrete advice, detailed feedback, or nuanced follow-up |
| `long only-if-needed` | 90+ words | rare; only when the target explicitly asks for detailed feedback |

## Comment Copy Gate

Use this stricter gate for proactive comments and follow-up replies. Comments should bias short. A longer comment must earn its length with a concrete insight, useful detail, or direct requested feedback.

Default length bias for ordinary comment sessions:

- `75-85%` should be `micro`, `fragment`, or `one-liner`.
- `10-20%` can be `two-beat`.
- `3-8%` can be `compact paragraph`.
- `long only-if-needed` should be exceptional, normally `<1%`.

Before publishing a comment/reply, score `comment_fun_score`:

| Factor | Points | Good signal |
|-|-:|-|
| Specific visible detail | 0-25 | reacts to a concrete thing in the post/comment, not a generic vibe |
| Small insight or useful distinction | 0-25 | adds one crisp idea, contrast, question, or nit |
| Local style fit | 0-20 | matches nearby reply length, slang level, and energy |
| Brevity/compression | 0-20 | says only what it needs; no setup sentence if unnecessary |
| Rhythm variation | 0-10 | differs from the last few comments in length/opening/syntax |

Decision:

- `Act`: `>=76`, no blocker, and the draft is no longer than needed.
- `Rewrite shorter`: `65-75`, or any draft that defaults to two polished sentences.
- `Skip`: `<65`, generic, summary-like, too long, or only safe praise.

Short-first rewrite rules:

- If the draft is two sentences, test whether it can become one sentence or one fragment. Prefer the shorter version if the meaning survives.
- If a full sentence sounds too polished, use a fragment when local style supports it.
- If the comment only praises, name the exact detail being praised or skip it.
- If the comment adds advice, keep one advice point only.
- If the comment asks a question, ask one question only.
- Compact paragraphs require `comment_fun_score >=85` and an explicit reason: OP asked for feedback, technical advice is useful, or the parent comment needs nuance.
- Long comments require explicit user request, OP request, or a high-value feedback context; otherwise cut to compact paragraph or shorter.

Rules:

- Read the last `10` measured comment/reply entries before choosing a tier. If the last `3` share the same tier or the rolling set is dominated by one sentence form, explicitly reassess whether the next target naturally supports another shape.
- Do not rotate or randomize tiers mechanically. Change length only when the target's information need and nearby style support it; never add filler or cut a useful point merely to alter the count.
- Keep facts and persona coherent with history while varying length, opening, subreddit, and syntax.
- Do not default to two sentences. Two-beat replies must earn their length.
- If the only draft is generic praise, filler, a summary of the post, or a safe-sounding two-sentence template, skip or rewrite.
- If you cannot state the `interesting_hook` in one line before posting, do not post yet.
- Prefer shorter than the model's first instinct unless the thread asks for depth.
- For long or medium replies, add natural compression and internet phrasing where appropriate; avoid polished essay cadence.
- After verification, append the measured counts and form to `history_ledger` before discovering the next candidate.

## Main Post Copy Shape

- Sample recent surviving native posts in the target subreddit before choosing length and structure.
- Use the shortest body that supplies the context the community expects; do not force comment-length brevity onto a post.
- Compare recent account posts for title pattern, opening, angle, paragraph shape, and length. Avoid repeating all of them together.
- Preserve factual/persona consistency even when the post format changes.
- Run final title/body/flair checks through Double-Check B in `publish-consistency.md`.
