#!/usr/bin/env python3
"""Validate clustered comment windows and independent per-item copy gates."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
defaults = json.loads((ROOT / "references" / "operation-defaults.json").read_text(encoding="utf-8"))
comments = defaults["comments"]
errors: list[str] = []

if comments["cluster_size_min"] != 2:
    errors.append("cluster_size_min")
if (comments["cluster_size_normal_min"], comments["cluster_size_normal_max"]) != (2, 4):
    errors.append("cluster_size_normal_range")

required = {
    "references/default-operations-sop.md": [
        "Every proactive target of `2+` is decomposed into windows of at least two",
        "5 -> 2+3",
        "per_comment_gate_id",
        "prewriting or sharing a copy decision is forbidden",
        "cluster_incomplete",
    ],
    "references/scheduler-and-heartbeats.md": [
        "Clustered Comment Windows",
        "comments.cluster_windows_per_hour",
        "comments.cluster_window_gap_minutes",
        "comments.cluster_size_*",
        "do not yield, schedule the next Heartbeat, or report a completed window after only one",
        "verified_comments_in_current_window >= comments.cluster_size_min",
        "CHECK_A -> DRAFT -> CHECK_B -> ACT -> measured log",
        "without lowering thresholds or creating a catch-up burst",
        "canonical comment fields",
    ],
    "references/comments-playbook.md": [
        "clustered windows with at least two verified comments",
        "Never prewrite a cluster",
        "A user request for exactly one total comment",
    ],
}
for relative, needles in required.items():
    body = (ROOT / relative).read_text(encoding="utf-8")
    for needle in needles:
        if needle not in body:
            errors.append(f"missing:{relative}:{needle}")

for obsolete in ("references/twelve-hour-ops-template.md", "references/proactive-playbook.md"):
    if (ROOT / obsolete).exists():
        errors.append(f"obsolete_file:{obsolete}")

if errors:
    raise SystemExit(json.dumps({"status": "FAIL", "errors": errors}, ensure_ascii=False))

print(json.dumps({
    "status": "PASS",
    "minimum_completed_cluster_size": 2,
    "normal_cluster_size": "2-4",
    "single_comment_cluster": "EXPLICIT_EXACT_ONE_ONLY",
    "copy_gate": "PER_ITEM",
}, ensure_ascii=False, sort_keys=True))
