#!/usr/bin/env python3
"""Validate measured Reddit reading, click, and comment timing floors."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


required = {
    "SKILL.md": [
        "`interaction-pacing.md`",
        "measured `30 sec` readable dwell",
        "`45 sec` readable-to-submit",
        "`5-12 sec` post-entry pause",
    ],
    "references/interaction-pacing.md": [
        "distinct candidate post/comment remains open after readable content appears",
        "`30 sec`",
        "post/parent readable to comment or reply submission",
        "`45 sec`",
        "draft entered to final comment/reply/Post click",
        "`5 sec`",
        "separate non-atomic UI clicks",
        "`1 sec`",
        "prefer a local terminal sleep",
        "Never create a Heartbeat for a 30-second read dwell",
        "comment_readable_to_submit_seconds",
        "candidate_dwell_seconds",
    ],
    "references/default-operations-sop.md": [
        "interaction_pacing=measured_human_scale",
        "candidate_dwell_min_seconds=30",
        "comment_readable_to_submit_min_seconds=45",
        "pre_submit_pause_seconds=5-12",
        "inter_click_pause_seconds=1-4",
    ],
    "references/launcher-playbook.md": [
        "`interaction_pacing=measured_human_scale`",
        "candidate_dwell_min_seconds=30",
        "comment_readable_to_submit_min_seconds=45",
    ],
    "references/proactive-playbook.md": [
        "`candidate_dwell_seconds >=30`",
        "`comment_readable_to_submit_seconds >=45`",
        "`pre_submit_pause_seconds=5-12`",
    ],
    "references/followup-playbook.md": [
        "`candidate_dwell_seconds >=30`",
        "`comment_readable_to_submit_seconds >=45`",
        "keep `1-3 min` between follow-up replies",
    ],
    "references/browse-vote-playbook.md": [
        "measured `30 sec` minimum",
        "`candidate_dwell_seconds >=30`",
    ],
    "references/scheduler-and-heartbeats.md": [
        "prefer local terminal `sleep <seconds>`",
        "never create one for a 30-second candidate dwell",
    ],
}

errors = []
for relative, needles in required.items():
    body = (ROOT / relative).read_text(encoding="utf-8")
    for needle in needles:
        if needle not in body:
            errors.append(f"missing:{relative}:{needle}")

forbidden = {
    "references/proactive-playbook.md": ["wait `18-70 sec`"],
    "references/followup-playbook.md": ["wait `18-70 sec`"],
}
for relative, needles in forbidden.items():
    body = (ROOT / relative).read_text(encoding="utf-8")
    for needle in needles:
        if needle in body:
            errors.append(f"forbidden:{relative}:{needle}")

if errors:
    raise SystemExit(json.dumps({"status": "FAIL", "errors": errors}, ensure_ascii=False))

print(json.dumps({
    "status": "PASS",
    "candidate_dwell_min_seconds": 30,
    "comment_readable_to_submit_min_seconds": 45,
    "pre_submit_pause_seconds": "5-12",
    "inter_click_pause_seconds": "1-4",
    "short_timer": "LOCAL_SLEEP_AT_MOST_5_MIN",
    "long_timer": "SELF_TARGETED_HEARTBEAT_OVER_5_MIN",
}, ensure_ascii=False, sort_keys=True))
