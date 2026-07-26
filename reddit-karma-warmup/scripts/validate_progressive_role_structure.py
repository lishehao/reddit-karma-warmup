#!/usr/bin/env python3
"""Validate concise staged routing, lane boundaries, and direct references."""

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
body = SKILL.read_text(encoding="utf-8")
errors: list[str] = []

if len(body.splitlines()) > 500:
    errors.append(f"skill_entry_too_long:{len(body.splitlines())}")

agent_yaml = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
if "Use $reddit-karma-warmup" not in agent_yaml:
    errors.append("agent_default_prompt_missing_skill")
if len(agent_yaml.splitlines()) > 8:
    errors.append("agent_metadata_too_long")
if "Temporarily name this task Reddit 启动台" in agent_yaml:
    errors.append("agent_metadata_contains_stale_bootstrap_protocol")

direct_refs = sorted(set(re.findall(r"references/[A-Za-z0-9_.-]+", body)))
for relative in direct_refs:
    if not (ROOT / relative).exists():
        errors.append(f"missing_direct_reference:{relative}")

required_role_refs = {
    "references/comments-playbook.md": "Load only in `Reddit 评论台`",
    "references/posts-playbook.md": "Load only in `Reddit 发帖台`",
    "references/followup-playbook.md": "Use only in `Reddit 跟进台` for notifications",
    "references/browse-vote-playbook.md": "Load only in `Reddit 浏览台`",
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
    "Fixed identities",
    "Route and load progressively",
    "operation-defaults.json` is the only numeric-default authority",
    "comments-playbook.md",
    "posts-playbook.md",
    "followup-playbook.md",
    "browse-vote-playbook.md",
    "community-presence-playbook.md",
    "lane-state-checkpoint.md",
    "lane-action-ownership.md",
    "chrome-atomic-command-runtime.md",
    "reddit-surface-routing.md",
    "Only `Reddit 浏览台` may inspect or operate",
    "Do not preload all of these",
    "hard compliance → truthful minimum content floor",
    "An archived task is never healthy/reusable",
    "One lane slot",
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
if defaults["votes"].get("allowed_lanes") != ["browsing"]:
    errors.append("vote_allowed_lanes")
if defaults["votes"].get("non_browsing_policy") != "DISABLED_BY_LANE":
    errors.append("non_browsing_vote_policy")
if defaults["votes"].get("non_browsing_cap") != 0:
    errors.append("non_browsing_vote_cap")
if not defaults["voice"]["percentage_quota_is_forbidden"]:
    errors.append("voice_percentage_quota_allowed")
if defaults["scheduler"].get("first_mutation_phase_step_minutes") != 10:
    errors.append("scheduler_phase_default")
if defaults["scheduler"].get("heartbeat_trigger_tolerance_seconds") != 300:
    errors.append("heartbeat_trigger_tolerance_default")
expected_thread_reuse = {
    "require_present_unarchived": True,
    "archived_task_policy": "REPLACE_NEVER_AUTO_UNARCHIVE",
    "readable_archived_is_liveness": False,
    "registry_update_after_acceptance_only": True,
    "transient_liveness_policy": "ROUTING_UNVERIFIED_NO_REPLACEMENT",
    "unknown_archive_capability_policy": "ROUTING_UNVERIFIED_NO_REPLACEMENT",
    "explicit_missing_task_policy": "REPLACE",
    "permanent_delivery_rejection_policy": "REPLACE",
    "delivery_uncertain_policy": "DELIVERY_UNCERTAIN_NO_REPLACEMENT",
}
if defaults.get("thread_reuse") != expected_thread_reuse:
    errors.append("thread_reuse_contract")
if defaults["posts"].get("research_cadence_minutes") != [120, 180]:
    errors.append("post_research_cadence_default")

voice_docs = "\n".join(
    (ROOT / relative).read_text(encoding="utf-8")
    for relative in ("references/outbound-copy-gate.md", "references/reddit-us-voice-patterns.md")
)
for stale in ("90-98%", "85-95%", "95-100%"):
    if stale in voice_docs:
        errors.append(f"stale_voice_quota:{stale}")

if "Every worker loads" in body:
    errors.append("eager_common_pack")
if "together with `proactive-common.md`" in (ROOT / "references" / "comments-playbook.md").read_text(encoding="utf-8"):
    errors.append("comments_eager_pack")
if "together with `proactive-common.md`" in (ROOT / "references" / "posts-playbook.md").read_text(encoding="utf-8"):
    errors.append("posts_eager_pack")
outbound = (ROOT / "references" / "outbound-copy-gate.md").read_text(encoding="utf-8")
if "Publish only at `post_copy_score >=80`" in outbound:
    errors.append("post_copy_score_hard_gate")
for needle in (
    "`post_copy_score` is a revision cue, not an eligibility gate",
    "does not reach an arbitrary writing-score threshold",
    "blocks an otherwise compliant,\ntruthful native discussion",
):
    if needle not in outbound:
        errors.append(f"post_copy_policy:{needle}")

if errors:
    raise SystemExit(json.dumps({"status": "FAIL", "errors": errors}, ensure_ascii=False))

print(json.dumps({
    "status": "PASS",
    "skill_lines": len(body.splitlines()),
    "direct_references": len(direct_refs),
    "roles": sorted(required_role_refs),
    "loading": "STAGED_NOT_EAGER",
    "defaults": "ONE_STRUCTURED_AUTHORITY",
    "state": "PER_ACCOUNT_LANE_TASK",
}, ensure_ascii=False, sort_keys=True))
