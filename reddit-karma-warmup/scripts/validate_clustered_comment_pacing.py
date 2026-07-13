#!/usr/bin/env python3
"""Validate clustered comment scheduling without uniform clocks or catch-up floods."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

required = {
    "references/default-operations-sop.md": [
        "missing comment pacing: `clustered_windows`",
        "minimum_completed_cluster_size=2",
        "single_comment_cluster=forbidden",
        "80 comments / 10h = 8/hour",
        "pacing_mode=clustered_windows",
    ],
    "references/scheduler-and-heartbeats.md": [
        "Clustered Comment Windows",
        "2-3` batch windows per hour",
        "20-35m",
        "2-4` verified comments",
        "do not yield, schedule the next Heartbeat, or report a completed window after only one",
        "verified_comments_in_current_window >= 2",
        "4-8m",
        "batch_target_remaining",
        "without lowering thresholds or creating a catch-up burst",
        "3 + 2 + 3",
    ],
    "references/twelve-hour-ops-template.md": [
        "Deliberate short comment windows are allowed; catch-up floods are not",
        "One comment is not a completed window",
    ],
    "references/proactive-playbook.md": [
        "`clustered_windows` schedule",
        "at least `2` verified proactive comments",
    ],
}

errors: list[str] = []
for relative, needles in required.items():
    body = (ROOT / relative).read_text(encoding="utf-8")
    for needle in needles:
        if needle not in body:
            errors.append(f"missing:{relative}:{needle}")

if errors:
    raise SystemExit(json.dumps({"status": "FAIL", "errors": errors}, ensure_ascii=False))

print(json.dumps({
    "status": "PASS",
    "pacing": "CLUSTERED_WINDOWS",
    "minimum_completed_cluster_size": 2,
    "single_comment_cluster": "FORBIDDEN_EXCEPT_EXPLICIT_EXACT_ONE_MISSION",
    "uniform_per_comment_clock": "FORBIDDEN",
    "underfill": "CARRY_FORWARD_NO_CATCHUP_FLOOD",
}, ensure_ascii=False, sort_keys=True))
