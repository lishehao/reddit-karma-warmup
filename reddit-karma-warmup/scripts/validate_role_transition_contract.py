#!/usr/bin/env python3
"""Validate reusable distributor, account-scoped lane routing, and worker autonomy."""

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


def main() -> int:
    checks = {
        ROOT / "SKILL.md": [
            "REDDIT_LAUNCHER",
            "Reddit 启动台",
            "Reddit 分发台",
            "reusable distributor",
            "account-keyed registry",
            "reuse each healthy registered task",
            "bounded one-time legacy adoption",
            "new mission IDs",
            "heartbeat_owner=self",
            "worker_task_id=<exact destination task ID>",
            "launcher_callback=none",
            "No coordinator task, coordinator registry, coordinator supervisor Heartbeat",
            "自然浏览/投票：随以上执行台读取内容时完成",
            "L1_DIRECTION",
            "L2_READY",
            "pinned=true",
            "Ordinary native account posts in `POSTS_WORKER` do not use GPT Inf",
            "must not be routed through `loci-prepare-reddit-post`",
        ],
        ROOT / "references" / "launcher-playbook.md": [
            "Reusable Lane Distributor",
            "registered reuse first",
            "bounded one-time legacy adoption",
            "creates only missing/unusable replacements",
            "returns to pinned idle",
            "It is not a coordinator",
            "The distributor never creates timers for workers",
            "next command generates new mission IDs but normally reuses the registered lane tasks",
            "Broad `开始/运营` enables comments, posts, and follow-up",
            "Create browsing only for an explicit pure-browse/vote request",
            "Keep the distributor pinned and every execution task unpinned",
            "worker_task_id=<the exact selected destination task ID>",
        ],
        ROOT / "references" / "thread-supervision-runtime.md": [
            "Reusable Lane Task Routing",
            "Account-Keyed Registry",
            "lane-registry/<username>.json",
            "Registered reuse",
            "One-time legacy adoption",
            "Inspect at most the three newest candidates",
            "Unarchive that exact registered task when needed",
            "Do not create a duplicate when a healthy registered task accepted delivery",
            "incoming `mission_id` is new and supersedes prior mission fields",
            "delivery_uncertain",
            "worker_task_id=<that same exact destination task ID>",
            "No ongoing task reads between direct user commands",
        ],
        ROOT / "references" / "runtime-and-setup.md": [
            "account+lane task registry",
            "lane-registry/<username>.json",
            "Persistent task list/read/send/create plus archive-state support",
        ],
        ROOT / "references" / "scheduler-and-heartbeats.md": [
            "The worker is the only scheduler for its lane",
            "There is no launcher/coordinator supervisor Heartbeat",
            "targetThreadId=self_task_id",
            "target_binding_proof=verified",
        ],
        ROOT / "references" / "risk-escalation.md": [
            "There is no callback or central risk surface",
            "Never send this to `Reddit 分发台`",
        ],
        ROOT / "references" / "proactive-playbook.md": [
            "This lane owns ordinary native posts end to end",
            "does not call GPT Inf or `loci-prepare-reddit-post`",
            "GPT Inf is not a readiness gate, a blocker, or a report field for ordinary posts",
        ],
    }

    if README.exists():
        checks[README] = [
            "按账号长期沿用的独立执行台",
            "首轮创建并登记评论台、发帖台和跟进台",
            "后续运营指令优先沿用",
            "lane registry",
            "最多检查三个最新同名候选",
            "不能仅凭标题猜测",
            "已分发：<任务标题 + 沿用/收编/新建/替换>",
            "首次 Bootstrap 成功时只返回",
            "电脑需要保持开机且不要休眠",
        ]

    errors: list[str] = []
    for path, needles in checks.items():
        if not path.exists():
            errors.append(f"missing file: {path}")
            continue
        errors.extend(require(path, needles))

    obsolete = [
        ROOT / "references" / "coordinator-playbook.md",
        ROOT / "references" / "startup-health-check.md",
        ROOT / "references" / "operations-audit.md",
    ]
    for path in obsolete:
        if path.exists():
            errors.append(f"obsolete file still present: {path.name}")

    forbidden = {
        ROOT / "SKILL.md": [
            "create fresh requested lane tasks",
            "Every distribution command creates another fresh run",
            "never search or reuse old tasks",
        ],
        ROOT / "references" / "launcher-playbook.md": [
            "For every direct command it creates fresh requested lane tasks",
            "Do not list/search/read/reuse/unarchive/revive historical tasks",
            "next command repeats fresh creation with a new run ID",
        ],
        ROOT / "references" / "thread-supervision-runtime.md": [
            "# Fresh-Only Task Allocation",
            "must not reuse, unarchive, revive",
            "No historical task discovery or fallback",
        ],
        ROOT / "references" / "scheduler-and-heartbeats.md": [
            "The coordinator is the only scheduler",
            "supervisor_heartbeat_id",
            "Coordinator Creation Flow",
        ],
    }
    if README.exists():
        forbidden[README] = [
            "每次我发运营指令，都创建全新的独立执行台",
            "分发台会再次创建全新执行任务并投递",
            "分发台禁止搜索、读取、复用、反归档",
        ]
    for path, needles in forbidden.items():
        errors.extend(forbid(path, needles))

    if errors:
        print("REUSABLE_LANE_ROUTING_CONTRACT=FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    scenarios = {
        "setup_command": "RENAME_LAUNCHER_FIRST",
        "setup_health_passed": "RENAME_AND_PIN_DISTRIBUTOR",
        "first_lane_dispatch": "CREATE_AND_REGISTER",
        "later_same_account_lane": "REUSE_REGISTERED_TASK",
        "legacy_registry_missing": "BOUNDED_EXACT_ADOPTION_THEN_CREATE",
        "ambiguous_legacy_candidates": "DO_NOT_GUESS_CREATE_NEW",
        "registered_archived_task": "UNARCHIVE_AND_REUSE",
        "registered_unusable_task": "REPLACE_AND_UPDATE_REGISTRY",
        "different_reddit_account": "SEPARATE_REGISTRY",
        "later_mission": "NEW_MISSION_ID_SAME_TASK",
        "worker_first_slot": "EXECUTE_NOW",
        "worker_continuation": "SELF_OWNED_HEARTBEAT",
        "launcher_callback": "FORBIDDEN",
        "coordinator_supervisor": "ABSENT",
        "launcher_idle": "PINNED_NO_BACKGROUND_READS",
        "ordinary_post_gpt_inf": "NOT_REQUIRED",
    }
    print("REUSABLE_LANE_ROUTING_CONTRACT=PASS")
    for scenario, result in scenarios.items():
        print(f"{scenario}={result}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
