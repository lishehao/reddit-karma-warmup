#!/usr/bin/env python3
"""Maintain a compact, GET-only public Reddit community index.

This helper is deliberately not a task, daemon, browser client, or write API.
It is optional discovery evidence for one Reddit operating task.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MAX_SUBREDDITS = 8
MAX_HOT_POINTERS = 3
MAX_QPM = 30
RULES_TTL_SECONDS = 86_400
HOT_TTL_SECONDS = 21_600
EXCLUDED_COMMUNITIES = {"saas"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def epoch_now() -> int:
    return int(time.time())


def default_root() -> Path:
    codex_home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    return codex_home / "reddit-karma-warmup" / "community-index"


def canonical_subreddit(value: str) -> str:
    name = value.strip().lower()
    if name.startswith("r/"):
        name = name[2:]
    if not name or any(char not in "abcdefghijklmnopqrstuvwxyz0123456789_" for char in name):
        raise ValueError("invalid subreddit")
    if name in EXCLUDED_COMMUNITIES:
        raise ValueError("excluded community: r/" + name)
    return name


def index_path(root: Path) -> Path:
    return root / "index.json"


def lock_path(root: Path) -> Path:
    return root / "index.lock"


def load_index(root: Path) -> dict[str, Any]:
    path = index_path(root)
    if not path.exists():
        return {"schema": "reddit_public_community_index/v1", "rate": {}, "communities": {}}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError("INDEX_UNREADABLE") from exc
    if value.get("schema") != "reddit_public_community_index/v1" or not isinstance(value.get("communities"), dict):
        raise RuntimeError("INDEX_SCHEMA_INVALID")
    value.setdefault("rate", {})
    return value


def atomic_write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        json.dump(value, handle, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        handle.flush()
        os.fsync(handle.fileno())
        temp_path = Path(handle.name)
    os.replace(temp_path, path)


def emit(value: dict[str, Any], code: int = 0) -> int:
    print(json.dumps(value, ensure_ascii=False, sort_keys=True))
    return code


def configure_headers() -> tuple[str, str]:
    token = os.environ.get("REDDIT_AUDIT_API_TOKEN", "").strip()
    user_agent = os.environ.get("REDDIT_AUDIT_USER_AGENT", "").strip()
    if not token or not user_agent:
        raise RuntimeError("UNCONFIGURED_OFFICIAL_REDDIT_API")
    return token, user_agent


def reserve_request(index: dict[str, Any]) -> None:
    current = epoch_now()
    rate = index.setdefault("rate", {})
    started = int(rate.get("window_started_epoch", current))
    used = int(rate.get("requests_used", 0))
    paused = int(rate.get("paused_until_epoch", 0))
    if paused > current:
        raise RuntimeError(f"RATE_PAUSED_UNTIL={paused}")
    if current - started >= 60:
        started, used = current, 0
    if used >= MAX_QPM:
        raise RuntimeError(f"RATE_WINDOW_EXHAUSTED_UNTIL={started + 60}")
    index["rate"] = {
        "window_started_epoch": started,
        "requests_used": used + 1,
        "paused_until_epoch": paused,
        "updated_at": utc_now(),
    }


def get_json(index: dict[str, Any], url: str, token: str, user_agent: str) -> Any:
    reserve_request(index)
    request = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {token}", "User-Agent": user_agent, "Accept": "application/json"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 429:
            retry_after = exc.headers.get("Retry-After", "60")
            try:
                seconds = max(1, int(float(retry_after)))
            except ValueError:
                seconds = 60
            index["rate"]["paused_until_epoch"] = epoch_now() + seconds
            raise RuntimeError(f"RATE_PAUSED_UNTIL={index['rate']['paused_until_epoch']}") from exc
        raise RuntimeError(f"HTTP_{exc.code}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError("API_NETWORK_ERROR") from exc


def compact_rules(payload: Any) -> list[dict[str, str]]:
    rules = payload.get("rules", []) if isinstance(payload, dict) else []
    compact: list[dict[str, str]] = []
    for rule in rules:
        if isinstance(rule, dict):
            name = " ".join(str(rule.get("short_name", "")).split())
            description = " ".join(str(rule.get("description", "")).split())
            if name or description:
                compact.append({"name": name[:180], "description": description[:1000]})
    return compact


def compact_hot(payload: Any) -> list[dict[str, Any]]:
    children = payload.get("data", {}).get("children", []) if isinstance(payload, dict) else []
    compact: list[dict[str, Any]] = []
    for child in children[:MAX_HOT_POINTERS]:
        data = child.get("data", {}) if isinstance(child, dict) else {}
        post_id = data.get("id")
        permalink = data.get("permalink")
        if post_id and permalink:
            compact.append({
                "id": post_id,
                "permalink": permalink,
                "title": " ".join(str(data.get("title", "")).split())[:300],
                "created_utc": data.get("created_utc"),
                "score": data.get("score"),
                "comment_count": data.get("num_comments"),
            })
    return compact


def refresh_one(index: dict[str, Any], subreddit: str, token: str, user_agent: str) -> dict[str, Any]:
    base = f"https://oauth.reddit.com/r/{urllib.parse.quote(subreddit)}/"
    about = get_json(index, base + "about", token, user_agent)
    rules = get_json(index, base + "about/rules", token, user_agent)
    hot = get_json(index, base + f"hot?limit={MAX_HOT_POINTERS}", token, user_agent)
    data = about.get("data", {}) if isinstance(about, dict) else {}
    current = epoch_now()
    normalized_rules = compact_rules(rules)
    return {
        "evidence": "public_index_only",
        "fetched_at": utc_now(),
        "rules_expires_epoch": current + RULES_TTL_SECONDS,
        "hot_expires_epoch": current + HOT_TTL_SECONDS,
        "rules_hash": hashlib.sha256(json.dumps(normalized_rules, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest(),
        "community": {
            "title": " ".join(str(data.get("title", "")).split())[:300],
            "public_description": " ".join(str(data.get("public_description", "")).split())[:1000],
            "subscribers": data.get("subscribers"),
            "submission_type": data.get("submission_type"),
            "over18": data.get("over18"),
        },
        "rules": normalized_rules,
        "hot_pointers": compact_hot(hot),
        "live_chrome_required": True,
    }


def command_status(root: Path) -> int:
    index = load_index(root)
    current = epoch_now()
    records = list(index["communities"].values())
    fresh = sum(int(row.get("rules_expires_epoch", 0)) >= current for row in records)
    return emit({"status": "READY", "root": str(root), "community_count": len(records), "fresh_rule_count": fresh, "api_configured": bool(os.environ.get("REDDIT_AUDIT_API_TOKEN") and os.environ.get("REDDIT_AUDIT_USER_AGENT")), "rate": index.get("rate", {})})


def command_show(root: Path, subreddit: str) -> int:
    index = load_index(root)
    record = index["communities"].get(subreddit)
    if record is None:
        return emit({"status": "NOT_FOUND", "subreddit": f"r/{subreddit}"}, 1)
    current = epoch_now()
    return emit({"status": "FOUND", "subreddit": f"r/{subreddit}", "fresh_rules": int(record.get("rules_expires_epoch", 0)) >= current, "record": record})


def command_refresh(root: Path, subreddits: list[str]) -> int:
    if not subreddits or len(subreddits) > MAX_SUBREDDITS or len(set(subreddits)) != len(subreddits):
        return emit({"status": "INVALID_SUBREDDIT_SCOPE", "max_subreddits": MAX_SUBREDDITS}, 2)
    try:
        token, user_agent = configure_headers()
    except RuntimeError as exc:
        return emit({"status": str(exc), "action": "USE_WEB_SEARCH_AND_CHROME"}, 0)
    root.mkdir(parents=True, exist_ok=True)
    with lock_path(root).open("a+") as lock:
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return emit({"status": "REFRESH_IN_PROGRESS", "action": "READ_EXISTING_INDEX_OR_CONTINUE_WITH_WEB_SEARCH_AND_CHROME"}, 0)
        index = load_index(root)
        completed, failed = [], []
        for subreddit in subreddits:
            try:
                index["communities"][subreddit] = refresh_one(index, subreddit, token, user_agent)
                completed.append(subreddit)
            except RuntimeError as exc:
                failed.append({"subreddit": subreddit, "error": str(exc)})
                if str(exc).startswith("RATE_"):
                    break
        atomic_write(index_path(root), index)
        return emit({"status": "REFRESH_COMPLETED", "completed": completed, "failed": failed, "live_chrome_required": True})


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=default_root())
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("status")
    refresh = commands.add_parser("refresh")
    refresh.add_argument("--subreddit", action="append", required=True)
    show = commands.add_parser("show")
    show.add_argument("--subreddit", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.expanduser().resolve()
    try:
        if args.command == "status":
            return command_status(root)
        if args.command == "show":
            return command_show(root, canonical_subreddit(args.subreddit))
        return command_refresh(root, [canonical_subreddit(value) for value in args.subreddit])
    except (OSError, ValueError, RuntimeError) as exc:
        return emit({"status": "ERROR", "error": str(exc)}, 2)


if __name__ == "__main__":
    sys.exit(main())
