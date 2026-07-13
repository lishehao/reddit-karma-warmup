# Reddit Karma Warmup

通过用户已登录的 Chrome 会话执行授权的 Reddit 社区运营。架构是“临时启动台 -> 可重复使用的无状态分发台 + 相互独立的执行台”，没有长期主控台。

## 直接安装

把下面一句发送给普通 Codex 任务：

```text
请先将当前任务重命名为“Reddit 启动台”，再通过 HTTPS 打开并完整遵循 https://raw.githubusercontent.com/lishehao/reddit-karma-warmup/main/README.md，安装或升级 reddit-karma-warmup，完成只读预检。预检健康后立即把同一任务重命名为“Reddit 分发台”并置顶：每次我发运营指令，都创建全新的独立执行台并单向投递，然后回到 pinned idle；执行台不返回分发台。不要进入目标模式。
```

## Codex 安装协议

当前 README 是唯一安装协议。只读取一次并直接执行，不寻找其他 installer，不进入 Goal Mode。

### 0. 启动与分发

收到 setup/安装命令后，第一个可用展示动作是把当前任务临时命名为 `Reddit 启动台`，早于下载、预检或解释。启动台只负责安装和只读预检。全部必要预检通过后，立即把同一任务重命名为 `Reddit 分发台`，并使用当前任务的精确 ID 将其置顶。分发台负责：

- 解析用户当前这一次运营指令；
- 为每条新指令生成新 run，并创建全新的对应执行台；
- 完成投递后进入 idle。

启动台和分发台都不操作 Reddit、不创建或管理运营 Heartbeat、不读取执行台后续状态、不接收 callback、不汇总风险或结果，也不晋升为 `Reddit 主控台`。

用户以后可以随时从置顶区回到同一个 `Reddit 分发台` 再发一条运营指令。分发台会再次创建全新执行任务并投递；执行任务始终不会返回分发台。用户也可以直接在某个执行台继续它当前的 run。执行台保持不置顶。

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

首次健康后，先按当前 Reddit 用户名读取 `${CODEX_HOME:-$HOME/.codex}/reddit-karma-warmup/account-directions/<username>.json`。这是 Skill 目录之外的用户配置，升级不得覆盖，也不得把一个账号的配置自动套给另一个账号。

- 已有匹配配置：直接复用，不重复询问。
- 首次账号：保持 `Reddit 启动台`，展示建议方向并确认一次。
- 用户明确提供方向：视为已确认，规范成 3–5 个相邻、真实兴趣后保存。
- 用户回复 `确认`：保存默认方向，再询问本轮怎么运营。
- 用户回复 `确认并开始`：保存默认方向并立即启动标准强度、混合探索、3 小时运营。
- 首次安装时只回复 `开始` 不等于确认方向；先完成这一次确认。以后同一账号回复 `开始` 不再重复确认。

首次账号使用：

```text
状态健康。当前账号：u/name。

建议账号方向：移动产品、3D/AR、游戏与 UGC、摄影与地点体验、创作工具。它是宽口径兴趣范围，不是虚构身份；每轮只需选择其中一个重点。

请回复“确认”，或直接告诉我需要增加/删除的方向；回复“确认并开始”会保存后立即按默认 3 小时运营。
```

确认后把同一任务改名为 `Reddit 分发台` 并置顶。以后用户可以直接再次下达同类指令：

```text
状态健康。当前账号：u/name。

账号方向已确认：<3-5 个兴趣支柱>。

当前任务已切换为 Reddit 分发台。

分发台已置顶；后续新一轮运营都从这里分配。

你可以指定评论、发帖、跟进、纯浏览/投票、时长、强度和风格；暂时没想法就回复“开始”。
```

每次用户回复“开始”时，默认标准强度、混合探索、3 小时，并为该次新 run 创建全新的：

- `Reddit 评论台`
- `Reddit 发帖台`
- `Reddit 跟进台`
- `Reddit 浏览台`，仅在用户明确要求纯浏览/投票时
- `Reddit 主页台`，仅在首次主页基础未完成或用户明确要求时

分发台为每个新任务发送完整 lane mission，设置明确动作目标/上限/最低有效阅读量、`first_due=now`、`heartbeat_owner=self`、`launcher_callback=none`，验证消息投递成功后返回任务路由卡并进入 idle。评论、发帖和跟进只对各自主流程已经读到的外部内容做独立附带投票判断；没有投票额度，也不会为投票额外刷内容。下一条用户命令会生成另一个新 run，不继承前一轮状态。

默认发帖采用保守的 `beginner-common-mistake` 角度：在有真实技能门槛和经验分享文化的社区，提出一个多数成员经历过、但具有该社区具体对象和后果的新手常见坑。发帖前必须搜索近期重复内容和 FAQ；不能伪造新手身份、使用经历或错误，也不能把同一模板只替换社区名后批量发送。不适合该角度的社区改用具体工作流摩擦、工具取舍或原生观察题。

社区路由 Reference `loci-subreddit-pool-v1.md` 同步自飞书《Loci Reddit Subreddit 档案总表》，包含 144 个社区的主要用户、常见痛点、版规边界、可发内容、账号适配和近期信号。Loci 全组织永久禁入项单独保存在 `organization-community-denylist.md`，必须在打开候选社区前先排除；它约束自有、员工、代理和其他协调账号。社区总表按 subreddit 行或关键词候选集渐进读取，不应整表无条件加载；其中规则是历史证据，发帖前仍以 Reddit 当天规则和提交页为准。

最新复核结论保存在 `community-action-routing-overrides.md`。它不再用一个等级同时代表全部动作，而是分别判断普通评论、主帖和产品提及；例如技术评论可用不代表 Loci 主帖可发。路由顺序是永久禁入表、动作级覆盖表、历史社区总表、当天版规与账号状态。

`community-live-audit-30-2026-07-13.md` 保存本轮 30 个社区的 Chrome 只读 live 证据和关键门槛；对应动作已同步进覆盖表。该证据表只用于解释和当天复核，不能把可见提交页或存活帖子当作发布许可。

凡最新复核明确“降级”的社区一律进入 `research-only`：后续不发表评论、不发主帖、不回复、不投票，也不做产品提及。只有未降级但按动作受限的社区，才保留技术评论可用、主帖关闭等拆分权限。

扩展研究 `community-expansion-pending-review-2026-07-13.md` 也随 Skill 打包，包含 18 个 suspension 后需要重新 preflight 的候选和 29 个新增名称级候选。它只用于候选发现：没有当天 live 版规、账号资格、New/Hot 和提交页证据时，不能据此评论、发帖、投票或 Join。

公开动作审计 `community-action-expansion-public-audit-2026-07-13.md` 进一步记录 30 个候选，其中 14 个有当前或近期公开规则证据、3 个只有较弱信号、13 个仍是名称级。它只能决定 suspension 结束后的 live preflight 顺序，不会直接扩大可执行社区池。

```text
已启动：<本次创建的任务>。

后续请直接到对应任务操作：
- 评论、候选帖子互动：Reddit 评论台
- 主帖、版规和发帖候选：Reddit 发帖台
- Notifications、回复和后续互动：Reddit 跟进台
- 自然浏览/投票：随以上执行台读取内容时完成；纯浏览任务才单独创建 Reddit 浏览台
- 新开一轮或重新分配任务：回到 Reddit 分发台
```

路由卡只列本次实际创建的执行台，但始终保留自然浏览说明和分发台入口。若明确创建了浏览台，则对应行直接写 `纯浏览/投票：Reddit 浏览台`。

分发台禁止搜索、读取、复用、反归档、唤醒、改名或向历史执行任务重新发 mission。即使旧任务同名、仍可读或仍在运行，也必须忽略。每个新 run 只认本次 `create_thread` 返回的新 Task ID；fresh task 创建失败时只报告本次失败，不得退回旧任务。

### 5. 执行台自治

每个执行台：

- 立即执行自己的首轮，不等 Heartbeat；
- 先确定动作数量目标，并用最低有效阅读量作为检索深度参考；动作目标未满足时继续读取真实最新帖子和评论并扩展合格社区，不因第一批候选不足而提前结束；
- 评论和主帖以成功发布数量作为主要完成条件；阅读量只是检索深度参考。达到阅读参考值但动作数量不足时继续扩展候选，未完成数量跨 Heartbeat 原样续跑，不得重置或把候选不足报告为已完成；
- 每个候选独立评分，达到门槛才动作；增加阅读量不能降低评论、发帖或投票阈值；
- 评论、发帖和跟进对已经读到的外部内容做一次独立投票判断；投票前若任一方向已明确选中则记录 `existing_vote` 并不点击，状态不清则 `no_vote`，成功点击后不重复验证；
- 使用独立 Chrome tab/Tab Group；
- 自己创建、验证、更新和结束指向自身任务的 recurring Heartbeat；
- 自己处理网络恢复、规则复核、重试、候选替换和用户修复；
- 在自己的任务里汇报，用户后续直接和该任务沟通；
- 不读取、不 callback、不暂停、不修改其他执行台。

评论台和跟进台在每条评论前执行短检查：快速确认相关版规，读完整帖子/父评论及附近回复，记录一个具体细节、一个重复观点和当前社区的本地语气样本，再从 micro、one-liner、two-beat 三个内部版本中选择最短且有信息量的版本。评论应经常使用当前社区自然出现的缩写、碎句和 Reddit 口吻，但不得机械堆黑话或复制别人的表达。

`reddit-us-voice-patterns.md` 提供美国 Reddit 常见的赞同、反对、修正、建议、追问、轻吐槽和技术判断句型，并区分稳定表达、语境表达和陈旧 Reddit 梗。该表只作回退；当前帖子附近真实回复始终优先。

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

## 反馈与贡献

这是公开仓库，但公开不代表任何人都能直接修改 `main`。未获得仓库写权限的用户可以：

- 提交 [Issue](https://github.com/lishehao/reddit-karma-warmup/issues) 报告问题或提出建议；
- 在已有 Issue 或 Pull Request 下评论；
- fork 仓库、修改后提交 Pull Request，等待维护者审阅和合并。

只有仓库所有者或被授予写权限的协作者可以直接推送。完整要求见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## License

MIT
