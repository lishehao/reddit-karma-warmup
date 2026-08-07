#!/usr/bin/env python3
"""Maintain a bounded per-account library of verified Reddit public writing."""

import argparse
import datetime as dt
import fcntl
import json
import os
import re
import tempfile
from pathlib import Path
from difflib import SequenceMatcher


CODEX_HOME = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
DEFAULT_ROOT = CODEX_HOME / "reddit-karma-warmup" / "recent-public-content"
MAX_ENTRIES = 24
MAX_AGE_DAYS = 30
MARKER_POOL = {"honestly", "tbh", "kinda", "wait", "ngl", "lowkey", "like", "i mean", "yeah", "right"}
WORD_RE = re.compile(r"[\w’'-]+", re.UNICODE)


def now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def parse_time(value: str) -> dt.datetime:
    text = value.strip().replace("Z", "+00:00")
    parsed = dt.datetime.fromisoformat(text)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=dt.timezone.utc)


def account_key(account: str) -> str:
    value = account.strip().lower()
    value = re.sub(r"^u/", "", value)
    value = re.sub(r"[^a-z0-9._-]+", "-", value).strip(".-")
    if not value:
        raise ValueError("account is empty")
    return value[:80]


def path_for(root: Path, account: str) -> Path:
    return root / f"{account_key(account)}.jsonl"


def normalize_text(text: str) -> str:
    return " ".join(text.lower().split())


def words(text: str) -> list[str]:
    return [token.lower() for token in WORD_RE.findall(text)]


def opening(text: str) -> str:
    return " ".join(words(text)[:6])


def load_entries(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    entries: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict) and item.get("text"):
            entries.append(item)
    return entries


def recent_entries(entries: list[dict], reference: dt.datetime | None = None) -> list[dict]:
    reference = reference or now_utc()
    cutoff = reference - dt.timedelta(days=MAX_AGE_DAYS)
    kept: list[dict] = []
    for item in entries:
        try:
            stamp = parse_time(str(item["published_at"]))
        except (KeyError, TypeError, ValueError):
            continue
        if stamp >= cutoff:
            kept.append(item)
    kept.sort(key=lambda item: str(item.get("published_at", "")), reverse=True)
    return kept[:MAX_ENTRIES]


def jaccard(left: str, right: str) -> float:
    a, b = set(words(left)), set(words(right))
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def similar_score(left: str, right: str) -> float:
    return max(jaccard(left, right), SequenceMatcher(None, normalize_text(left), normalize_text(right)).ratio())


def check_candidate(entries: list[dict], text: str, unit: str, marker: str, primary_move: str) -> dict:
    candidate = normalize_text(text)
    candidate_opening = opening(text)
    matches: list[dict] = []
    for item in entries:
        same_unit = item.get("unit") == unit
        existing = str(item.get("text", ""))
        score = similar_score(text, existing)
        if normalize_text(existing) == candidate:
            matches.append({"reason": "EXACT_DUPLICATE", "score": 1.0, "published_at": item.get("published_at")})
        elif same_unit and score >= 0.62:
            matches.append({"reason": "HIGH_TEXT_SIMILARITY", "score": round(score, 3), "published_at": item.get("published_at")})
        elif same_unit and candidate_opening and candidate_opening == item.get("opening") and primary_move and primary_move == item.get("primary_move"):
            matches.append({"reason": "SAME_OPENING_AND_MOVE", "score": round(score, 3), "published_at": item.get("published_at")})
        elif same_unit and marker and marker.lower() == str(item.get("marker", "")).lower():
            matches.append({"reason": "RECENT_MARKER_REUSE", "score": round(score, 3), "published_at": item.get("published_at")})
    return {
        "decision": "REWRITE" if matches else "ALLOW",
        "recent_count": len(entries),
        "matches": matches[:5],
        "candidate": {"opening": candidate_opening, "word_count": len(words(text)), "unit": unit, "primary_move": primary_move or None},
    }


def append_entry(root: Path, args: argparse.Namespace) -> dict:
    root.mkdir(parents=True, exist_ok=True)
    path = path_for(root, args.account)
    lock_path = path.with_suffix(".lock")
    stamp = args.published_at or now_utc().isoformat().replace("+00:00", "Z")
    text = args.text.strip()
    entry = {
        "published_at": stamp,
        "account": args.account,
        "unit": args.unit,
        "community": args.community or None,
        "target_url": args.target_url or None,
        "text": text,
        "word_count": len(words(text)),
        "opening": opening(text),
        "marker": (args.marker or "").strip().lower() or None,
        "primary_move": (args.primary_move or "").strip().upper() or None,
    }
    with lock_path.open("a+", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        entries = recent_entries(load_entries(path))
        entries.insert(0, entry)
        entries = recent_entries(entries, parse_time(stamp))
        payload = "".join(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n" for item in entries)
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=root, delete=False) as tmp:
            tmp.write(payload)
            temp_name = tmp.name
        os.replace(temp_name, path)
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
    return {"status": "RECORDED", "path": str(path), "recent_count": len(entries), "entry": entry}


def self_test() -> dict:
    import tempfile

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        append_entry(root, argparse.Namespace(account="u/Test", unit="comments", community="r/example", target_url=None, text="The archive loop is neat.", marker="", primary_move="REACTION", published_at="2026-08-07T00:00:00Z"))
        path = path_for(root, "u/Test")
        entries = load_entries(path)
        exact = check_candidate(entries, "The archive loop is neat.", "comments", "", "REACTION")
        different = check_candidate(entries, "Does the archive change next-week retention?", "comments", "", "QUESTION")
        assert exact["decision"] == "REWRITE" and different["decision"] == "ALLOW"
    return {"status": "PASS", "max_entries": MAX_ENTRIES, "max_age_days": MAX_AGE_DAYS}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--self-test", action="store_true")
    sub = parser.add_subparsers(dest="command")
    check = sub.add_parser("check")
    check.add_argument("--account", required=True)
    check.add_argument("--unit", choices=("comments", "posts", "follow-up"), required=True)
    check.add_argument("--text", required=True)
    check.add_argument("--marker", default="")
    check.add_argument("--primary-move", default="")
    append = sub.add_parser("append")
    append.add_argument("--account", required=True)
    append.add_argument("--unit", choices=("comments", "posts", "follow-up"), required=True)
    append.add_argument("--text", required=True)
    append.add_argument("--community", default="")
    append.add_argument("--target-url", default="")
    append.add_argument("--marker", default="")
    append.add_argument("--primary-move", default="")
    append.add_argument("--published-at", default="")
    recent = sub.add_parser("recent")
    recent.add_argument("--account", required=True)
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), ensure_ascii=False, separators=(",", ":")))
        return
    if not args.command:
        parser.error("a command or --self-test is required")
    path = path_for(args.root, args.account)
    if args.command == "check":
        print(json.dumps(check_candidate(recent_entries(load_entries(path)), args.text, args.unit, args.marker, args.primary_move), ensure_ascii=False, separators=(",", ":")))
    elif args.command == "recent":
        print(json.dumps({"status": "OK", "path": str(path), "entries": recent_entries(load_entries(path))}, ensure_ascii=False, separators=(",", ":")))
    else:
        print(json.dumps(append_entry(args.root, args), ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
