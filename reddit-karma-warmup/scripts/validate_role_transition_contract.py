#!/usr/bin/env python3
"""Validate distributor routing, independent role packs, and worker autonomy."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
README = ROOT.parent / "README.md"


def require(path: Path, needles: list[str]) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return [f"{path.name}: missing {needle!r}" for needle in needles if needle not in text]


def forbid(path: Path, needles: list[str]) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return [f"{path.name}: forbidden {needle!r}" for needle in needles if needle in text]


checks = {
    ROOT / "SKILL.md": [
        "Five-Step Default Flow",
        "Reddit 启动台",
        "Reddit 分发台",
        "independent account-scoped lane tasks",
        "comments-playbook.md",
        "posts-playbook.md",
        "followup-playbook.md",
        "browse-vote-playbook.md",
        "community-presence-playbook.md",
        "No coordinator task",
        "worker_task_id=<exact destination task ID>",
        "A queued `clientThreadId` is not ready",
        "Ordinary native account posts in `POSTS_WORKER` do not use GPT Inf",
    ],
    ROOT / "references" / "launcher-playbook.md": [
        "Reusable Lane Distributor",
        "registered reuse first",
        "bounded one-time legacy adoption",
        "returns to pinned idle",
        "It is not a coordinator",
        "The distributor never creates timers for workers",
        "Broad `开始/运营` enables comments, posts, and follow-up",
        "first default dispatch is complete only after comments, posts, and follow-up all accept",
        "Create browsing only for an explicit pure-browse/vote request",
        "worker_task_id=<the exact selected destination task ID>",
        "第一轮已分发：Reddit 评论台、Reddit 发帖台、Reddit 跟进台已收到任务。",
    ],
    ROOT / "references" / "thread-supervision-runtime.md": [
        "Account-Keyed Registry",
        "lane-registry/<username>.json",
        "Registered reuse",
        "One-time legacy adoption",
        "Inspect at most the three newest candidates",
        "incoming `mission_id` is new and supersedes prior mission fields",
        "delivery_uncertain",
        "No ongoing task reads between direct user commands",
    ],
    ROOT / "references" / "scheduler-and-heartbeats.md": [
        "The worker is the only scheduler for its lane",
        "There is no launcher/coordinator supervisor Heartbeat",
        "targetThreadId=self_task_id",
    ],
    ROOT / "references" / "comments-playbook.md": [
        "Load only in `Reddit 评论台`",
        "Never prewrite a cluster",
    ],
    ROOT / "references" / "posts-playbook.md": [
        "Load only in `Reddit 发帖台`",
        "Do not use GPT Inf or `loci-prepare-reddit-post`",
    ],
}
if README.exists():
    checks[README] = [
        "立即把首轮 mission 投递给评论台、发帖台和跟进台",
        "后续运营指令优先沿用",
        "lane registry",
        "第一轮已分发：Reddit 评论台、Reddit 发帖台、Reddit 跟进台已收到任务。",
        "首次 Bootstrap 成功时只返回",
    ]

errors: list[str] = []
for path, needles in checks.items():
    if not path.exists():
        errors.append(f"missing file: {path}")
    else:
        errors.extend(require(path, needles))

for obsolete in (
    ROOT / "references" / "coordinator-playbook.md",
    ROOT / "references" / "proactive-playbook.md",
    ROOT / "references" / "twelve-hour-ops-template.md",
):
    if obsolete.exists():
        errors.append(f"obsolete file still present: {obsolete.name}")

forbidden = {
    ROOT / "SKILL.md": ["Use a persistent main coordinator", "Require worker callback"],
    ROOT / "references" / "launcher-playbook.md": ["The coordinator is the only scheduler"],
    ROOT / "references" / "scheduler-and-heartbeats.md": ["supervisor_heartbeat_id"],
}
for path, needles in forbidden.items():
    errors.extend(forbid(path, needles))

if errors:
    print("REUSABLE_LANE_ROUTING_CONTRACT=FAIL")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)

print("REUSABLE_LANE_ROUTING_CONTRACT=PASS")
print("topology=DISTRIBUTOR_PLUS_INDEPENDENT_LANES")
print("reuse=EXACT_ACCOUNT_LANE_TASK_ID")
print("timers=WORKER_OWNED")
print("callbacks=NONE")
print("role_packs=COMMENTS_POSTS_FOLLOWUP_BROWSING_PRESENCE")
