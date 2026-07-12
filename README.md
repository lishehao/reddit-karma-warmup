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
3. Automation/Heartbeat 能创建、更新、读取和删除 repeat-on 的长期任务，并能显式绑定目标 Thread。
4. Codex 能创建、读取并向独立用户任务发送后续指令；预检只确认能力，不提前创建运营任务。
5. 能读取真实当地时间、时区、UTC offset 与 UTC 时间。

Chrome Browser control 是 Reddit 写操作的硬依赖。Computer Use、内置 Browser、Playwright、终端浏览器和普通 Web Search 不能替代。macOS 屏幕录制、系统音频录制和辅助功能权限不是本 Skill 的依赖。

Heartbeat 创建、repeat-on 读取和删除成功即可证明基础能力可用。若运行时不显示 `next_run_at`、DTSTART 或下一次运行标签，内部记录 `created_unreadable` 并继续；这不是用户可修复的问题，也不能阻断第一轮。首次依赖无人值守的多小时运行时，由 Skill 的主控台监督 Heartbeat 验证第一次真实 recurring wake。

### 4. 向用户交接

预检健康时只回复：

```text
状态健康。当前账号：u/name。

你希望接下来怎么运营？可以指定时长、低/标准/高强度，以及混合探索、建设者、游戏/3D、空间地点、轻社交/创意或自定义风格；也可以直接指定评论、发帖、跟进或自然浏览。自然浏览还可以指定阅读量、投票目标和轮次间隔。如果暂时没想法，回复“开始”即授权我创建或复用 Reddit 评论台、Reddit 发帖台、Reddit 跟进台和 Reddit 浏览台四个独立工作任务，并按标准强度、混合探索风格运行 3 小时。
```

不要展示依赖表、日志、Task ID、Automation ID、模型回退或时区计算。

若 Chrome control 或 Reddit 登录缺失，只返回一项用户能完成的修复动作。用户回复“继续”后，仅重查缺失项，不重新安装健康的 Skill。

### 5. 用户开始运营后

用户回复“开始”或给出具体运营指令，即明确授权为所启用的工作线创建或复用用户可见的独立 Codex 任务。调用已安装的 `$reddit-karma-warmup` 并由 Skill 接管全部运营细节。Skill 已在 `references/thread-supervision-runtime.md` 内置与本流程兼容的任务创建、复用、读取、发消息和首轮验收协议，不需要另装 `thread-supervisor` Skill。所有指令和汇报都留在 `Reddit 主控台`；主控台负责派发、集中调度、读取、验证和汇报，不能自己执行 Reddit 动作。默认广泛运营必须创建或复用 `Reddit 评论台`、`Reddit 发帖台`、`Reddit 跟进台`、`Reddit 浏览台` 四个独立任务；单独点名一种动作时只启用对应任务。禁止使用不可见 subagent、一个合并 worker 或合并执行 Heartbeat 替代这些任务。

首轮 proof 后，主控台为每个启用的执行台创建一个显式绑定该 Thread、repeat-on、带 mission 截止保护的长期 Heartbeat，并为自己创建一个 repeat-on 的只读任务监督 Heartbeat。执行台只在被唤醒后执行 bounded slot、记录 proof，不创建、不续排、不修改 Heartbeat。用户修改任务、任务结束或调度异常时，只有主控台更新、修复或删除 Heartbeat。

`运营 [时长] [强度] [风格]` 自动拆成四条工作线。默认风格是混合探索，也可选建设者、游戏/3D、空间地点、轻社交/创意或自定义，并可附加“更犀利”“更轻松”等语气修饰。自然浏览包含符合门槛的 Upvote/Downvote；标准强度每轮默认阅读 `20-30` 条并以 `2` 次合格投票为目标。每轮完成后，默认重新选择 `20-40` 分钟的等待时间再开始下一轮；用户可以改成例如“标准强度运营 3 小时，游戏/3D 风格”“自然浏览 30 条，目标投票 5 次，每 10-20 分钟一轮”或“只浏览不投票”。不要再次运行安装流程。

必须在同一个用户 turn 创建或复用全部启用的独立工作任务，并让每个任务通过 Chrome 完成和验证一个请求相关微轮次，或形成真实浏览后的具体无动作/阻塞证据。读 Skill、做计划、派发任务、创建 Heartbeat 或回复“已启动”都不算开始；任一工作线没有 proof，就不能声称整项任务已启动。worker 只返回计划时，主控台只能向该 worker 追加一次“立即执行”指令并重新读取；仍无 proof 就报告该 lane 启动失败，禁止主控台代做。

多小时持续运行不能用 `COUNT=1` 或 repeat-off 后依赖 worker 自续。主控台必须验证每个长期 Heartbeat 的 `targetThreadId`、repeat-on、下一次运行、本地/UTC、recurrence 和截止保护，并通过自己的监督 Heartbeat维护 `planned/started/completed/blocked/missed` slot 统计。只有至少一次 recurring wake 产生新的 worker turn 和 slot proof 后，才能声称持续调度已实际运行；链路断裂按 `SCHEDULER_CONTINUATION_FAILURE` 上报，不得归因于 Reddit 账号风险。

## Requirements

- Codex 本地 Skill 支持
- ChatGPT Chrome Extension 提供的 Chrome Browser control
- 用户已在同一 Chrome profile 登录 Reddit
- 多轮运行需要 repeat-on Automation/Heartbeat，并支持显式 `targetThreadId`
- Codex 独立任务的创建、读取和后续发送能力
- 能访问 GitHub HTTPS archive

不需要单独安装 `thread-supervisor`；兼容的监督子集已经包含在 Reddit Skill 内。

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
