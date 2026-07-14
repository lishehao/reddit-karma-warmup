#!/usr/bin/env python3
"""Validate the per-comment rule, context, voice, and brevity gate."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    required = {
        ROOT / "references" / "publish-consistency.md": [
            "quick rule glance",
            "context_detail",
            "duplicate_to_avoid",
            "local_voice_sample",
            "at least `3` nearby/top replies",
        ],
        ROOT / "references" / "outbound-copy-gate.md": [
            "Reddit-native voice",
            "micro/fragment",
            "three internal alternatives",
            "native compression, not cosplay",
            "native_marker_plan",
            "native_marker_used",
            "output_surface",
            "voice_band",
            "slang_or_abbrev_used",
            "proactive comment, ordinary",
            "creative/gaming/casual comment",
            "Chinese user-facing operation report",
            "Never reuse the same social marker more than `2` times",
            "`80-90%` should be `micro`, `fragment`, or `one-liner`",
            "target `90-98%` of published comments",
            "routine contraction alone does not satisfy",
            "no more than `1` such exception in the rolling last `20` comments",
            "plain_local_voice",
            "PER_ITEM_COPY_GATE_REQUIRED=true",
            "cluster_copy_batching=forbidden",
            "per_comment_gate_id=<mission_id>:<cluster_id>:<item_index>",
            "default to `<=25` English words",
            "at most one `26-45` word two-beat exception",
            "Routine proactive clusters do not use compact paragraphs",
        ],
        ROOT / "references" / "proactive-playbook.md": [
            "Missing rule/context/voice evidence is `Watch`",
            "micro/one-liner/two-beat alternatives",
            "Choose the shortest passing alternative",
            "ordinary sessions target `80-90%`",
            "`90-98%` with one locally supported strong native marker",
            "`85-95%` with an actual social slang/Reddit abbreviation",
            "classify `output_surface`",
            "slang_or_abbrev_used",
            "return to step 1 and rerun the entire context, length, shortening, local-marker, and submit gate",
            "never draft the cluster in bulk",
        ],
        ROOT / "references" / "default-operations-sop.md": [
            "per_item_copy_gate=required",
            "cluster_copy_batching=forbidden",
            "routine_comment_word_cap=25",
        ],
        ROOT / "references" / "launcher-playbook.md": [
            "Every comments handoff also carries `per_item_copy_gate=required`",
            "`cluster_copy_batching=forbidden`",
            "`routine_comment_word_cap=25`",
        ],
        ROOT / "references" / "followup-playbook.md": [
            "ordinary follow-up, technical, sensitive/support, or mod acknowledgement",
            "slang_or_abbrev_used",
        ],
    }
    errors = []
    for path, needles in required.items():
        body = path.read_text(encoding="utf-8")
        for needle in needles:
            if needle not in body:
                errors.append(f"missing:{path.name}:{needle}")

    if errors:
        print("COMMENT_REVIEW_CONTRACT=FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("COMMENT_REVIEW_CONTRACT=PASS")
    print("rule_check=QUICK_CURRENT")
    print("context=POST_PARENT_NEARBY_REPLIES")
    print("voice=LOCAL_REDDIT_NATIVE")
    print("drafts=MICRO_ONE_LINER_TWO_BEAT")
    print("selection=SHORTEST_PASSING")
    print("short_bias=80_TO_90_PERCENT")
    print("native_marker_target=90_TO_98_PERCENT")
    print("social_slang_target=85_TO_95_PERCENT")
    print("frequency=OUTPUT_SURFACE_SPECIFIC")
    print("distribution=ACROSS_OUTPUTS_NOT_STACKED")
    print("cluster_copy=PER_ITEM_GATE_NO_BATCH_DRAFT")
    print("routine_cluster_length=DEFAULT_MAX_25_WORDS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
