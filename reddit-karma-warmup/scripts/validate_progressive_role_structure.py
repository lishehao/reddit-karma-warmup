#!/usr/bin/env python3
"""Validate concise entry routing, role-pack boundaries, and direct references."""

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
body = SKILL.read_text(encoding="utf-8")
errors: list[str] = []

if len(body.splitlines()) > 500:
    errors.append(f"skill_entry_too_long:{len(body.splitlines())}")

direct_refs = sorted(set(re.findall(r"`(references/[^`]+)`", body)))
for relative in direct_refs:
    if not (ROOT / relative).exists():
        errors.append(f"missing_direct_reference:{relative}")

required_role_refs = {
    "references/comments-playbook.md": "Load only in `Reddit 评论台`",
    "references/posts-playbook.md": "Load only in `Reddit 发帖台`",
    "references/followup-playbook.md": "Use only for notifications",
    "references/browse-vote-playbook.md": "Load in `Reddit 浏览台`",
    "references/community-presence-playbook.md": "Reddit 主页台",
}
for relative, needle in required_role_refs.items():
    path = ROOT / relative
    if not path.exists():
        errors.append(f"missing_role_pack:{relative}")
    elif needle not in path.read_text(encoding="utf-8"):
        errors.append(f"bad_role_identity:{relative}:{needle}")

for obsolete in (
    "references/proactive-playbook.md",
    "references/twelve-hour-ops-template.md",
    "references/coordinator-playbook.md",
):
    if (ROOT / obsolete).exists():
        errors.append(f"obsolete_role_file:{obsolete}")

required_entry = [
    "`references/operation-defaults.json` is the machine-authoritative source",
    "comments-playbook.md",
    "posts-playbook.md",
    "followup-playbook.md",
    "browse-vote-playbook.md",
    "community-presence-playbook.md",
    "lane-state-checkpoint.md",
    "There is no persistent main coordinator",
]
for needle in required_entry:
    if needle not in body:
        errors.append(f"missing_entry_contract:{needle}")

checkpoint = (ROOT / "references" / "lane-state-checkpoint.md").read_text(encoding="utf-8")
for needle in (
    "lane-state/<username>/<lane>/<self_task_id>.json",
    "lane-history/<username>/<lane>.ndjson",
    "checkpoint_schema_version=1",
    "Every Heartbeat carries `checkpoint_path`",
):
    if needle not in checkpoint:
        errors.append(f"checkpoint_contract:{needle}")

defaults = json.loads((ROOT / "references" / "operation-defaults.json").read_text(encoding="utf-8"))
if defaults.get("schema_version") != 1:
    errors.append("defaults_schema_version")
if defaults["votes"]["default_target"] is not None:
    errors.append("default_vote_target_present")
if not defaults["voice"]["percentage_quota_is_forbidden"]:
    errors.append("voice_percentage_quota_allowed")
if defaults["scheduler"].get("first_mutation_phase_step_minutes") != 10:
    errors.append("scheduler_phase_default")
if defaults["posts"].get("research_cadence_minutes") != [120, 180]:
    errors.append("post_research_cadence_default")

voice_docs = "\n".join(
    (ROOT / relative).read_text(encoding="utf-8")
    for relative in ("references/outbound-copy-gate.md", "references/reddit-us-voice-patterns.md")
)
for stale in ("90-98%", "85-95%", "95-100%"):
    if stale in voice_docs:
        errors.append(f"stale_voice_quota:{stale}")

if errors:
    raise SystemExit(json.dumps({"status": "FAIL", "errors": errors}, ensure_ascii=False))

print(json.dumps({
    "status": "PASS",
    "skill_lines": len(body.splitlines()),
    "direct_references": len(direct_refs),
    "roles": sorted(required_role_refs),
    "defaults": "ONE_STRUCTURED_AUTHORITY",
    "state": "PER_ACCOUNT_LANE_TASK",
}, ensure_ascii=False, sort_keys=True))
