# Reddit Karma Warmup

用于通过用户已登录的 Chrome 会话执行授权的 Reddit 社区运营。公开仓库只有一个安装入口和一个 Skill 本体；运营规则以 Skill 内 references 为准。

## 直接安装

把下面一句发送给普通 Codex 任务：

```text
请通过 HTTPS 打开并完整遵循 https://raw.githubusercontent.com/lishehao/reddit-karma-warmup/main/README.md，按 README 安装或升级 reddit-karma-warmup，并继续完成其中的预检与启动交接；不要进入目标模式。
```

## Codex 安装协议

如果你是执行上述 Prompt 的 Codex：当前 README 就是唯一安装协议。只读取一次并直接执行，不要寻找其他 installer 文档，不要进入 Goal Mode。

### 1. 下载与校验

固定来源：

- Repository: `https://github.com/lishehao/reddit-karma-warmup`
- Archive: `https://codeload.github.com/lishehao/reddit-karma-warmup/zip/refs/heads/main`
- Skill directory: `reddit-karma-warmup/`
- Install target: `${CODEX_HOME:-$HOME/.codex}/skills/reddit-karma-warmup`

通过 HTTPS 下载并安全解压 archive。确认目标 Skill 目录唯一，并检查：

- `SKILL.md` 含有效 `name` 与 `description` frontmatter。
- `manifest.json` 的 name、version、schema 和 repository 可读。
- `agents/openai.yaml`、所有 references 及 SKILL.md 引用的文件存在且可读。

Git、GitHub CLI、Python、Node.js、包管理器和 API Key 都不是依赖。存在 Skill validator 时可以使用；不存在时完成上述等价结构检查。

### 2. 安装与升级

按 `manifest.json` 数字段比较版本：

- 未安装：安装完整 Skill 目录。
- 已安装但没有 manifest：视为 legacy，先完整备份再升级。
- GitHub 版本更高：备份旧目录后，用同文件系统临时目录原子替换整个受管目录。
- 版本和内容都相同：NOOP。
- 同版本但内容不同：停止为冲突，不静默覆盖。
- GitHub 版本更低：默认不降级。
- 替换后校验失败：恢复旧目录。

不要逐文件混合新旧版本。备份放入 `${CODEX_HOME:-$HOME/.codex}/skill-backups/`。

### 3. 运行预检

安装完成后先不修改 Reddit，只检查：

1. Chrome Browser control 可实际连接；掉线时最多重连两次。
2. 通过 Chrome 只读打开 Reddit，确认用户已登录并记录准确账号。不要输入、索取或保存密码。
3. Automation/Heartbeat 能创建、更新和删除一次性任务。
4. 能读取真实当地时间、时区、UTC offset 与 UTC 时间。

Chrome Browser control 是 Reddit 写操作的硬依赖。Computer Use、内置 Browser、Playwright、终端浏览器和普通 Web Search 不能替代。macOS 屏幕录制、系统音频录制和辅助功能权限不是本 Skill 的依赖。

Heartbeat 创建与删除成功即可证明能力可用。若运行时不显示 `next_run_at`、DTSTART 或下一次运行标签，内部记录 `created_unreadable` 并继续；这不是用户可修复的问题，也不能阻断第一轮。只有创建、更新或删除本身失败，才不能依赖多轮自动续跑。

### 4. 向用户交接

预检健康时只回复：

```text
状态健康。当前账号：u/name。

你希望接下来怎么运营？可以指定时长、评论或发帖数量、目标社区，也可以只浏览并偶尔投票；如果暂时没想法，直接回复“开始”，我会按默认方案先试运行 3 小时。
```

不要展示依赖表、日志、Task ID、Automation ID、模型回退或时区计算。

若 Chrome control 或 Reddit 登录缺失，只返回一项用户能完成的修复动作。用户回复“继续”后，仅重查缺失项，不重新安装健康的 Skill。

### 5. 用户开始运营后

用户回复“开始”或给出具体运营指令后，调用已安装的 `$reddit-karma-warmup` 并由 Skill 接管全部运营细节。不要再次运行安装流程。

必须在同一个用户 turn 让每条明确启用的工作线通过 Chrome 完成并验证一个请求相关微轮次，或形成真实浏览后的具体无动作/阻塞证据。读 Skill、做计划、派发任务、创建 Heartbeat 或回复“已启动”都不算开始；任一工作线没有 proof，就不能声称整项任务已启动。只有取得 `start_proof_by_lane` 后，Heartbeat 才能承接下一轮。此后每次执行型 Heartbeat 唤醒也必须先完成当前 slot 并记录 `slot_proof`，再安排后继 Heartbeat；禁止连续排期却不执行。

## Requirements

- Codex 本地 Skill 支持
- ChatGPT Chrome Extension 提供的 Chrome Browser control
- 用户已在同一 Chrome profile 登录 Reddit
- 多轮运行需要一次性 Automation/Heartbeat
- 能访问 GitHub HTTPS archive

## Repository Layout

```text
README.md
LICENSE
reddit-karma-warmup/
  SKILL.md
  manifest.json
  agents/
  references/
```

## Boundaries

仅操作用户明确授权的账号和浏览器会话。遵守 Reddit 全站规则、实时 subreddit 规则和 Skill 内的执行边界；遇到登录失效、captcha、rate limit、账号 warning 或明确规则禁止时停止对应写操作。

## License

MIT
