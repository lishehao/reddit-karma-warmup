# Reddit Karma Warmup

通过用户已登录的 Chrome 会话执行授权的 Reddit 社区运营。架构是“可重复使用的无状态启动台 + 相互独立的执行台”，没有长期主控台。

## 直接安装

把下面一句发送给普通 Codex 任务：

```text
请先将当前任务重命名为“Reddit 启动台”，再通过 HTTPS 打开并完整遵循 https://raw.githubusercontent.com/lishehao/reddit-karma-warmup/main/README.md，安装或升级 reddit-karma-warmup，完成只读预检。此后把当前任务作为可重复使用的无状态启动台：每次我发运营指令，都创建全新的独立执行台并单向投递，然后回到 idle；执行台不返回启动台。不要进入目标模式。
```

## Codex 安装协议

当前 README 是唯一安装协议。只读取一次并直接执行，不寻找其他 installer，不进入 Goal Mode。

### 0. 启动台

收到 setup/安装命令后，第一个可用展示动作是把当前任务命名为 `Reddit 启动台`，早于下载、预检或解释。启动台只负责：

- 安装或升级 Skill；
- 只读检查 Chrome、Reddit 登录、独立任务、Heartbeat 和真实时间；
- 解析用户当前这一次运营指令；
- 为每条新指令生成新 run，并创建全新的对应执行台；
- 完成投递后进入 idle。

启动台不操作 Reddit、不创建或管理运营 Heartbeat、不读取执行台后续状态、不接收 callback、不汇总风险或结果，也不晋升为 `Reddit 主控台`。

用户以后可以随时回到同一个 `Reddit 启动台` 再发一条运营指令。启动台会再次创建全新执行任务并投递；执行线程始终不会返回启动台。用户也可以直接在某个执行台继续它当前的 run。

### 1. 下载与校验

固定来源：

- Repository: `https://github.com/lishehao/reddit-karma-warmup`
- Archive: `https://codeload.github.com/lishehao/reddit-karma-warmup/zip/refs/heads/main`
- Skill directory: `reddit-karma-warmup/`
- Install target: `${CODEX_HOME:-$HOME/.codex}/skills/reddit-karma-warmup`

通过 HTTPS 下载并安全解压。确认唯一 Skill 根目录，校验 `SKILL.md` frontmatter、`manifest.json`、`agents/openai.yaml`、references、scripts 和所有引用路径。

Git、GitHub CLI、Python、Node.js、包管理器和 API Key 都不是运行依赖。存在 validator 时可使用；不存在时完成等价结构检查。

### 2. 安装与升级

按 `manifest.json` 数字段比较版本：

- 未安装：安装完整目录。
- legacy：先完整备份再升级。
- GitHub 版本更高：备份后原子替换整个受管目录。
- 同版本同内容：NOOP。
- 同版本不同内容：停止为冲突。
- GitHub 版本更低：不自动降级。
- 替换后校验失败：恢复旧目录。

不要逐文件混合版本。备份放入 `${CODEX_HOME:-$HOME/.codex}/skill-backups/`。

### 3. 只读预检

安装完成后先不修改 Reddit，只检查：

1. Chrome Browser control 可连接并能在掉线后重连。
2. 通过 Chrome 确认 Reddit 已登录和准确账号；不处理密码。
3. Codex 能创建、读取并向独立用户任务发送初始指令。
4. Automation/Heartbeat 支持 repeat-on 和显式 `targetThreadId`。
5. 能读取真实当地时间、时区、UTC offset 和 UTC。

Chrome Browser control 是 Reddit 写操作依赖。Computer Use、内置 Browser、Playwright 和普通 Web Search 不能替代。屏幕录制、系统音频录制和辅助功能权限不是本 Skill 依赖。

隐藏 `next_run_at` 只记录 `created_unreadable`，不阻断第一轮。若 Chrome 或登录需要用户修复，只返回一个具体动作；用户回复“继续”后仅重查缺失项。

### 4. 可重复的一键分配

首次健康后在 `Reddit 启动台` 询问；以后用户可以直接再次下达同类指令：

```text
状态健康。当前账号：u/name。

你希望怎么运营？可以指定评论、发帖、跟进、自然浏览、时长、强度和风格。暂时没想法就回复“开始”，我会创建独立的 Reddit 评论台、发帖台、跟进台和浏览台；它们之后各自运行，你直接去对应任务继续沟通。
```

每次用户回复“开始”时，默认标准强度、混合探索、3 小时，并为该次新 run 创建全新的：

- `Reddit 评论台`
- `Reddit 发帖台`
- `Reddit 跟进台`
- `Reddit 浏览台`
- `Reddit 主页台`，仅在首次主页基础未完成或用户明确要求时

启动台为每个新任务发送完整 lane mission，设置明确动作目标/上限/最低有效阅读量、唯一 `vote_owner`、`first_due=now`、`heartbeat_owner=self`、`launcher_callback=none`，验证消息投递成功后进入 idle。它不等待执行结果。下一条用户命令会生成另一个新 run，不继承前一轮状态。

启动台禁止搜索、读取、复用、反归档、唤醒、改名或向历史执行任务重新发 mission。即使旧任务同名、仍可读或仍在运行，也必须忽略。每个新 run 只认本次 `create_thread` 返回的新 Task ID；fresh task 创建失败时只报告本次失败，不得退回旧任务。

### 5. 执行台自治

每个执行台：

- 立即执行自己的首轮，不等 Heartbeat；
- 同时完成动作数量目标与最低有效阅读量；未满足时继续读取真实最新帖子和评论并扩展合格社区，不因第一批候选不足而提前结束；
- 每个候选独立评分，达到门槛才动作；增加阅读量不能降低评论、发帖或投票阈值；
- 使用独立 Chrome tab/Tab Group；
- 自己创建、验证、更新和结束指向自身任务的 recurring Heartbeat；
- 自己处理网络恢复、规则复核、重试、候选替换和用户修复；
- 在自己的任务里汇报，用户后续直接和该任务沟通；
- 不读取、不 callback、不暂停、不修改其他执行台。

同一 Chrome profile 或同一 Reddit 账号不是冲突。某个执行台失败只影响它自己，其他任务继续运行。

## Requirements

- Codex 本地 Skill 支持
- ChatGPT Chrome Extension 提供的 Chrome Browser control
- 用户已在同一 Chrome profile 登录 Reddit
- 多轮任务需要 repeat-on Heartbeat 和显式 `targetThreadId`
- 首次分配需要独立任务创建及向本次新任务发送指令的能力
- GitHub HTTPS archive 可访问

## Repository Layout

```text
README.md
LICENSE
reddit-karma-warmup/
  SKILL.md
  manifest.json
  agents/
  references/
  scripts/
```

## Boundaries

仅操作用户明确授权的账号和浏览器会话。实时 subreddit 规则约束具体动作。登录/CAPTCHA/账号锁只暂停受影响执行台；定时 rate limit 自动复查；明确社区禁止则换社区；网络和页面故障由当前执行台及其 Heartbeat继续恢复。

## License

MIT
