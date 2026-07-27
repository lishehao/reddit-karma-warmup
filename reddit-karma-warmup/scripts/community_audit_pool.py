#!/usr/bin/env python3
"""Maintain one local, read-only Reddit community audit cache.

This script intentionally has no Reddit mutation endpoints. It is invoked only
by the single Reddit operating task during bootstrap or later research; active
units consume its output as read-only evidence.
"""

from __future__ import annotations

import argparse
import csv
import fcntl
import hashlib
import json
import os
import sqlite3
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator


SCHEMA_VERSION = 1
DEFAULT_OPERATING_QPM = 60
DEFAULT_RULES_TTL_SECONDS = 86_400
DEFAULT_HOT_POINTER_TTL_SECONDS = 21_600
DEFAULT_HOT_POINTER_LIMIT = 3


def now_epoch() -> int:
    return int(time.time())


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def default_root() -> Path:
    codex_home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    return codex_home / "reddit-karma-warmup" / "community-audit-pool"


def canonical_subreddit(value: str) -> str:
    name = value.strip().lower()
    if name.startswith("r/"):
        name = name[2:]
    if not name or any(char not in "abcdefghijklmnopqrstuvwxyz0123456789_" for char in name):
        raise ValueError(f"invalid subreddit: {value!r}")
    return name


def database_path(root: Path) -> Path:
    return root / "community-audit.sqlite3"


def connect(root: Path) -> sqlite3.Connection:
    root.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path(root))
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA foreign_keys=ON")
    return connection


def initialize(root: Path) -> None:
    connection = connect(root)
    try:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS snapshots (
                subreddit TEXT NOT NULL,
                provider TEXT NOT NULL,
                status TEXT NOT NULL,
                evidence_level TEXT NOT NULL,
                fetched_at TEXT NOT NULL,
                fetched_epoch INTEGER NOT NULL,
                expires_epoch INTEGER NOT NULL,
                rules_hash TEXT,
                public_rule_url TEXT NOT NULL,
                about_json TEXT NOT NULL,
                rules_json TEXT NOT NULL,
                sidebar_json TEXT NOT NULL,
                sticky_json TEXT NOT NULL,
                hot_pointers_json TEXT NOT NULL,
                error_json TEXT NOT NULL,
                PRIMARY KEY (subreddit, provider)
            );
            CREATE TABLE IF NOT EXISTS rate_state (
                provider TEXT PRIMARY KEY,
                window_started_epoch INTEGER NOT NULL,
                requests_used INTEGER NOT NULL,
                blocked_until_epoch INTEGER NOT NULL,
                updated_at TEXT NOT NULL
            );
            """
        )
        connection.execute(
            "INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)",
            ("schema_version", str(SCHEMA_VERSION)),
        )
        connection.commit()
    finally:
        connection.close()


@contextmanager
def refresh_lock(root: Path) -> Iterator[None]:
    lock_path = root / "community-audit.lock"
    with lock_path.open("a+") as handle:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RuntimeError("REFRESH_IN_PROGRESS") from error
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))


def load_rate_state(connection: sqlite3.Connection, provider: str) -> sqlite3.Row | None:
    return connection.execute(
        "SELECT * FROM rate_state WHERE provider = ?", (provider,)
    ).fetchone()


def reserve_request(connection: sqlite3.Connection, provider: str, qpm: int) -> None:
    if qpm <= 0:
        raise ValueError("operating QPM must be positive")
    current = now_epoch()
    state = load_rate_state(connection, provider)
    if state is None or current - state["window_started_epoch"] >= 60:
        window_started = current
        requests_used = 0
        blocked_until = 0
    else:
        window_started = state["window_started_epoch"]
        requests_used = state["requests_used"]
        blocked_until = state["blocked_until_epoch"]
    if blocked_until > current:
        raise RuntimeError(f"RATE_PAUSED_UNTIL={blocked_until}")
    if requests_used >= qpm:
        raise RuntimeError(f"RATE_WINDOW_EXHAUSTED_UNTIL={window_started + 60}")
    connection.execute(
        """
        INSERT INTO rate_state(provider, window_started_epoch, requests_used, blocked_until_epoch, updated_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(provider) DO UPDATE SET
          window_started_epoch=excluded.window_started_epoch,
          requests_used=excluded.requests_used,
          blocked_until_epoch=excluded.blocked_until_epoch,
          updated_at=excluded.updated_at
        """,
        (provider, window_started, requests_used + 1, blocked_until, now_iso()),
    )
    connection.commit()


def pause_provider(connection: sqlite3.Connection, provider: str, retry_after_seconds: int) -> None:
    state = load_rate_state(connection, provider)
    current = now_epoch()
    connection.execute(
        """
        INSERT INTO rate_state(provider, window_started_epoch, requests_used, blocked_until_epoch, updated_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(provider) DO UPDATE SET
          blocked_until_epoch=excluded.blocked_until_epoch,
          updated_at=excluded.updated_at
        """,
        (
            provider,
            state["window_started_epoch"] if state else current,
            state["requests_used"] if state else 0,
            current + max(1, retry_after_seconds),
            now_iso(),
        ),
    )
    connection.commit()


def request_json(
    connection: sqlite3.Connection,
    provider: str,
    url: str,
    token: str,
    user_agent: str,
    qpm: int,
) -> Any:
    reserve_request(connection, provider, qpm)
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "User-Agent": user_agent,
            "Accept": "application/json",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        if error.code == 429:
            retry_after = error.headers.get("Retry-After", "60")
            try:
                retry_seconds = int(float(retry_after))
            except ValueError:
                retry_seconds = 60
            pause_provider(connection, provider, retry_seconds)
            raise RuntimeError(f"RATE_PAUSED_UNTIL={now_epoch() + retry_seconds}") from error
        raise


def compact_hot_pointers(payload: Any, limit: int) -> list[dict[str, Any]]:
    children = payload.get("data", {}).get("children", []) if isinstance(payload, dict) else []
    pointers = []
    for child in children[:limit]:
        data = child.get("data", {}) if isinstance(child, dict) else {}
        post_id = data.get("id")
        permalink = data.get("permalink")
        if not post_id or not permalink:
            continue
        pointers.append(
            {
                "id": post_id,
                "permalink": permalink,
                "created_utc": data.get("created_utc"),
                "score": data.get("score"),
                "num_comments": data.get("num_comments"),
            }
        )
    return pointers


def rule_hash(rules_payload: Any) -> str:
    normalized = json.dumps(rules_payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def upsert_snapshot(
    connection: sqlite3.Connection,
    subreddit: str,
    provider: str,
    about: Any,
    rules: Any,
    sidebar: Any,
    sticky: list[Any],
    hot_pointers: list[dict[str, Any]],
    ttl_seconds: int,
) -> None:
    current = now_epoch()
    evidence_level = "public_rules" if provider == "official_reddit" else "public_rules_enriched"
    connection.execute(
        """
        INSERT INTO snapshots(
          subreddit, provider, status, evidence_level, fetched_at, fetched_epoch,
          expires_epoch, rules_hash, public_rule_url, about_json, rules_json,
          sidebar_json, sticky_json, hot_pointers_json, error_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(subreddit, provider) DO UPDATE SET
          status=excluded.status,
          evidence_level=excluded.evidence_level,
          fetched_at=excluded.fetched_at,
          fetched_epoch=excluded.fetched_epoch,
          expires_epoch=excluded.expires_epoch,
          rules_hash=excluded.rules_hash,
          public_rule_url=excluded.public_rule_url,
          about_json=excluded.about_json,
          rules_json=excluded.rules_json,
          sidebar_json=excluded.sidebar_json,
          sticky_json=excluded.sticky_json,
          hot_pointers_json=excluded.hot_pointers_json,
          error_json=excluded.error_json
        """,
        (
            subreddit,
            provider,
            "COMPLETED",
            evidence_level,
            now_iso(),
            current,
            current + ttl_seconds,
            rule_hash(rules),
            f"https://www.reddit.com/r/{subreddit}/about/rules/",
            json.dumps(about, ensure_ascii=False, sort_keys=True),
            json.dumps(rules, ensure_ascii=False, sort_keys=True),
            json.dumps(sidebar, ensure_ascii=False, sort_keys=True),
            json.dumps(sticky, ensure_ascii=False, sort_keys=True),
            json.dumps(hot_pointers, ensure_ascii=False, sort_keys=True),
            "{}",
        ),
    )
    connection.commit()


def refresh_official(
    root: Path,
    subreddits: list[str],
    token_env: str,
    user_agent_env: str,
    qpm: int,
    include_hot: bool,
    hot_limit: int,
    rules_ttl_seconds: int,
) -> dict[str, Any]:
    token = os.environ.get(token_env, "").strip()
    user_agent = os.environ.get(user_agent_env, "").strip()
    if not token or not user_agent:
        raise RuntimeError(f"MISSING_OFFICIAL_API_CREDENTIALS token_env={token_env} user_agent_env={user_agent_env}")
    initialize(root)
    completed, failed = [], []
    with refresh_lock(root):
        connection = connect(root)
        try:
            for subreddit in subreddits:
                base = f"https://oauth.reddit.com/r/{urllib.parse.quote(subreddit)}/"
                try:
                    about = request_json(connection, "official_reddit", base + "about", token, user_agent, qpm)
                    rules = request_json(connection, "official_reddit", base + "about/rules", token, user_agent, qpm)
                    sidebar = request_json(connection, "official_reddit", base + "sidebar", token, user_agent, qpm)
                    sticky = []
                    for position in (1, 2):
                        try:
                            sticky.append(
                                request_json(
                                    connection,
                                    "official_reddit",
                                    base + f"sticky?num={position}",
                                    token,
                                    user_agent,
                                    qpm,
                                )
                            )
                        except urllib.error.HTTPError as error:
                            if error.code != 404:
                                raise
                    hot_pointers: list[dict[str, Any]] = []
                    if include_hot:
                        hot = request_json(
                            connection,
                            "official_reddit",
                            base + f"hot?limit={hot_limit}",
                            token,
                            user_agent,
                            qpm,
                        )
                        hot_pointers = compact_hot_pointers(hot, hot_limit)
                    upsert_snapshot(
                        connection,
                        subreddit,
                        "official_reddit",
                        about,
                        rules,
                        sidebar,
                        sticky,
                        hot_pointers,
                        rules_ttl_seconds,
                    )
                    completed.append(subreddit)
                except Exception as error:  # Keep other public rows independent.
                    failed.append({"subreddit": subreddit, "error": str(error)})
                    if str(error).startswith("RATE_"):
                        break
        finally:
            connection.close()
    return {"status": "REFRESH_COMPLETED", "completed": completed, "failed": failed}


def decode_json(value: str) -> Any:
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return {}


def rule_titles(rules_json: str) -> str:
    payload = decode_json(rules_json)
    rules = payload.get("rules", []) if isinstance(payload, dict) else []
    titles = []
    for rule in rules:
        if isinstance(rule, dict):
            title = rule.get("short_name") or rule.get("description")
            if title:
                titles.append(" ".join(str(title).split()))
    return " | ".join(titles)


def export_reference(root: Path, output: Path) -> dict[str, Any]:
    initialize(root)
    connection = connect(root)
    try:
        rows = connection.execute(
            "SELECT * FROM snapshots WHERE provider = ? ORDER BY subreddit", ("official_reddit",)
        ).fetchall()
    finally:
        connection.close()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = [
            "subreddit",
            "status",
            "evidence_level",
            "fetched_at",
            "freshness",
            "rules_hash",
            "subreddit_type",
            "submission_type",
            "over18",
            "rule_titles",
            "public_rule_url",
            "hot_pointer_count",
            "unresolved",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        current = now_epoch()
        for row in rows:
            about = decode_json(row["about_json"])
            about_data = about.get("data", {}) if isinstance(about, dict) else {}
            hot_pointers = decode_json(row["hot_pointers_json"])
            writer.writerow(
                {
                    "subreddit": f"r/{row['subreddit']}",
                    "status": row["status"],
                    "evidence_level": row["evidence_level"],
                    "fetched_at": row["fetched_at"],
                    "freshness": "fresh" if row["expires_epoch"] >= current else "stale",
                    "rules_hash": row["rules_hash"],
                    "subreddit_type": about_data.get("subreddit_type", ""),
                    "submission_type": about_data.get("submission_type", ""),
                    "over18": about_data.get("over18", ""),
                    "rule_titles": rule_titles(row["rules_json"]),
                    "public_rule_url": row["public_rule_url"],
                    "hot_pointer_count": len(hot_pointers) if isinstance(hot_pointers, list) else 0,
                    "unresolved": "Chrome account and submit gate required",
                }
            )
    return {"status": "EXPORTED", "rows": len(rows), "output": str(output)}


def status(root: Path) -> dict[str, Any]:
    initialize(root)
    connection = connect(root)
    try:
        rows = connection.execute("SELECT expires_epoch FROM snapshots").fetchall()
        state = load_rate_state(connection, "official_reddit")
    finally:
        connection.close()
    current = now_epoch()
    return {
        "status": "READY",
        "root": str(root),
        "schema_version": SCHEMA_VERSION,
        "snapshot_count": len(rows),
        "fresh_snapshot_count": sum(row["expires_epoch"] >= current for row in rows),
        "stale_snapshot_count": sum(row["expires_epoch"] < current for row in rows),
        "official_rate_paused_until_epoch": state["blocked_until_epoch"] if state else 0,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=default_root())
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("init")
    subparsers.add_parser("status")
    refresh = subparsers.add_parser("refresh")
    refresh.add_argument("--subreddit", action="append", required=True)
    refresh.add_argument("--provider", choices=("official_reddit",), default="official_reddit")
    refresh.add_argument("--token-env", default="REDDIT_AUDIT_API_TOKEN")
    refresh.add_argument("--user-agent-env", default="REDDIT_AUDIT_USER_AGENT")
    refresh.add_argument("--operating-qpm", type=int, default=DEFAULT_OPERATING_QPM)
    refresh.add_argument("--rules-ttl-seconds", type=int, default=DEFAULT_RULES_TTL_SECONDS)
    refresh.add_argument("--include-hot-pointers", action="store_true")
    refresh.add_argument("--hot-pointer-limit", type=int, default=DEFAULT_HOT_POINTER_LIMIT)
    export = subparsers.add_parser("export")
    export.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.expanduser().resolve()
    try:
        if args.command == "init":
            initialize(root)
            emit({"status": "INITIALIZED", "root": str(root), "schema_version": SCHEMA_VERSION})
        elif args.command == "status":
            emit(status(root))
        elif args.command == "refresh":
            subreddits = [canonical_subreddit(value) for value in args.subreddit]
            if len(set(subreddits)) != len(subreddits):
                raise ValueError("duplicate subreddit refresh input")
            if args.hot_pointer_limit < 1 or args.hot_pointer_limit > DEFAULT_HOT_POINTER_LIMIT:
                raise ValueError("hot pointer limit must be 1..3")
            if args.operating_qpm > DEFAULT_OPERATING_QPM:
                raise ValueError(f"operating QPM may not exceed {DEFAULT_OPERATING_QPM}")
            emit(
                refresh_official(
                    root,
                    subreddits,
                    args.token_env,
                    args.user_agent_env,
                    args.operating_qpm,
                    args.include_hot_pointers,
                    args.hot_pointer_limit,
                    args.rules_ttl_seconds,
                )
            )
        elif args.command == "export":
            emit(export_reference(root, args.output.expanduser().resolve()))
        return 0
    except Exception as error:
        emit({"status": "ERROR", "error": str(error)})
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
