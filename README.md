# Reddit Karma Warmup

A Codex skill for authorized Reddit community operations through the user's existing logged-in Chrome session. It supports account bootstrap, contextual comments and posts, notification follow-up, profile/community presence, qualified browsing, occasional genuine voting, and verified one-shot heartbeat continuation.

## Install

Git is not required.

1. Open [INSTALL-AND-USE.md](https://raw.githubusercontent.com/lishehao/reddit-karma-warmup/main/INSTALL-AND-USE.md).
2. Copy its single Prompt into a normal Codex task.
3. Codex fetches the full machine protocol and installs from GitHub automatically.
4. Complete any requested Chrome or Reddit login step, then reply `Continue`.
5. When the environment is healthy, reply `Start` or provide a duration/action target.

The installer downloads the public GitHub archive over HTTPS, validates `manifest.json`, and installs or atomically upgrades `~/.codex/skills/reddit-karma-warmup`.

## Requirements

- Codex with local Skill support
- Chrome Browser control through the ChatGPT Chrome Extension
- A Reddit account already logged in by the user
- One-shot automation/heartbeat support for multi-round operation
- Network access to `github.com`, `raw.githubusercontent.com`, and `codeload.github.com`

Git, GitHub CLI, Python, Node.js, API keys, and macOS screen/audio recording permissions are not runtime requirements.

## Repository Layout

```text
INSTALL-AND-USE.md
INSTALLER-PROTOCOL.md
reddit-karma-warmup/
  SKILL.md
  manifest.json
  agents/
  references/
```

## Boundaries

Use only accounts and browser sessions you are authorized to operate. The skill requires live community checks, truthful identity and experience, genuine vote decisions, and explicit stops on login, captcha, rate-limit, account-warning, or rule-prohibition signals. It is not affiliated with Reddit or OpenAI.

## License

MIT
