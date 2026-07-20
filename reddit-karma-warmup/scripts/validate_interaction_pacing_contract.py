#!/usr/bin/env python3
"""Validate canonical measured Reddit timing and short-wait ownership."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
defaults = json.loads((ROOT / "references" / "operation-defaults.json").read_text(encoding="utf-8"))
timing = defaults["interaction_pacing"]
comments = defaults["comments"]
followup = defaults["followup"]

expected = {
    "candidate_dwell_min_seconds": 30,
    "candidate_dwell_normal_seconds": [30, 75],
    "candidate_dwell_long_seconds": [60, 180],
    "comment_readable_to_submit_min_seconds": 45,
    "comment_readable_to_submit_normal_seconds": [45, 120],
    "pre_submit_pause_seconds": [5, 12],
    "inter_click_pause_seconds": [1, 4],
    "local_sleep_max_seconds": 300,
}
errors = []
for key, value in expected.items():
    if timing.get(key) != value:
        errors.append(f"default:{key}:{timing.get(key)}")
if (comments["proactive_submit_gap_seconds_min"], comments["proactive_submit_gap_seconds_max"]) != (180, 300):
    errors.append("proactive_submit_gap")
if (followup["reply_submit_gap_seconds_min"], followup["reply_submit_gap_seconds_max"]) != (60, 180):
    errors.append("followup_submit_gap")

required = {
    "references/interaction-pacing.md": [
        "interaction_pacing.candidate_dwell_*",
        "interaction_pacing.comment_readable_to_submit_*",
        "interaction_pacing.pre_submit_pause_seconds",
        "separate non-atomic UI clicks",
        "use a local terminal sleep",
        "Never create a Heartbeat for an in-item read or submit-pause floor",
        "candidate_dwell_seconds",
        "comment_readable_to_submit_seconds",
        "Never bundle that wait with click, fill, type, vote, or submit",
        "Every click, fill/type, and result observation is a separate `node_repl` cell",
    ],
    "references/chrome-atomic-command-runtime.md": [
        "Do not call `playwright.waitForTimeout` in the submit cell",
        "Run exactly one final click as the only browser-boundary command",
    ],
    "references/comments-playbook.md": [
        "comments.proactive_submit_gap_seconds_*",
        "canonical pacing clocks",
    ],
    "references/followup-playbook.md": [
        "every matching configured field in `interaction_pacing`",
        "followup.reply_submit_gap_seconds_*",
    ],
    "references/browse-vote-playbook.md": [
        "measured dwell in `interaction-pacing.md`",
    ],
    "references/scheduler-and-heartbeats.md": [
        "configured local-sleep maximum",
        "use the lane Heartbeat between windows",
    ],
}
for relative, needles in required.items():
    body = (ROOT / relative).read_text(encoding="utf-8")
    for needle in needles:
        if needle not in body:
            errors.append(f"missing:{relative}:{needle}")

if errors:
    raise SystemExit(json.dumps({"status": "FAIL", "errors": errors}, ensure_ascii=False))

print(json.dumps({
    "status": "PASS",
    "candidate_dwell_min_seconds": 30,
    "comment_readable_to_submit_min_seconds": 45,
    "pre_submit_pause_seconds": "5-12",
    "inter_click_pause_seconds": "1-4",
    "local_sleep_max_seconds": 300,
}, ensure_ascii=False, sort_keys=True))
