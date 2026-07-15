# Reddit Karma Warmup

通过用户已登录的 Chrome 会话执行授权的 Reddit 社区运营。架构是“临时启动台 -> 可重复使用的分发台 + 按账号长期沿用的独立执行台”，没有长期主控台。

## 最常用流程

1. **安装预检：**当前任务临时成为 `Reddit 启动台`，安装 Skill 并完成只读环境检查。
2. **一次提问：**健康后同一任务改名并置顶为 `Reddit 分发台`，只询问运营方向和时长；用户已经给出时直接进入下一步。
3. **立即分发：**分发台优先沿用当前 Reddit 账号已登记的评论台、发帖台和跟进台，只创建缺失或不可用的执行台，并在同一轮送达完整 mission。
4. **独立执行：**每个执行台立即开始浏览器工作，并保留一个专属、持久化的 Reddit 主标签；只管理自己的标签、任务状态和 Heartbeat，不 callback、不读取或暂停其他执行台。
5. **完成复用：**目标完成后执行台删除自己的 Heartbeat，但保留任务本身；以后从置顶的分发台下达新指令时继续复用。

通用 `thread-supervisor` Skill 不是安装依赖。Reddit Skill 已内置与其当前身份/创建契约对齐的最小子集：使用精确 `task ID + hostId`、区分可立即使用的 `threadId` 和仍在排队的 `clientThreadId`，并且除非用户明确要求，否则不覆盖新任务的模型或思考等级。

## 直接安装

把下面一句发送给普通 Codex 任务：

```text
请先将当前任务重命名为“Reddit 启动台”，再通过 HTTPS 打开并完整遵循 https://raw.githubusercontent.com/lishehao/reddit-karma-warmup/main/README.md，安装或升级 reddit-karma-warmup，完成只读预检。预检成功后把同一任务重命名为“Reddit 分发台”并置顶；如果我还没有给出方向和时长，只返回 README 规定的“运营方向 + 运营时长”提问，不显示版本、校验器、账号、预检清单、NOOP、改名置顶或无操作报告，也不要创建测试 Heartbeat。健康提问后我回复“继续”时，立即把默认 3 小时首轮 mission 投递给评论台、发帖台和跟进台；只有精确投递被接受后才回报已分发，并提醒后续所有 Reddit 运营任务仍可在这个分发台下达。后续运营指令优先沿用同一 Reddit 账号已经登记的原执行台，只在缺失或不可用时新建替代台。投递后回到 pinned idle；执行台不返回分发台。不要进入目标模式。
```

## Codex 安装协议

当前 README 是唯一安装协议。只读取一次并直接执行，不寻找其他 installer，不进入 Goal Mode。

### 0. 启动与分发

收到 setup/安装命令后，第一个可用展示动作是把当前任务临时命名为 `Reddit 启动台`，早于下载、预检或解释。启动台只负责安装和只读预检。全部必要预检通过后，立即把同一任务重命名为 `Reddit 分发台`，并使用当前任务的精确 ID 将其置顶。分发台负责：

- 解析用户当前这一次运营指令；
- 为每条新指令生成新 mission，优先沿用该 Reddit 账号已登记的对应执行台；
- 只为尚未登记、无法确认或永久不可用的 lane 新建替代执行台；
- 完成投递后进入 idle。

启动台和分发台都不操作 Reddit、不创建或管理运营 Heartbeat、不接收 callback、不汇总风险或结果，也不晋升为 `Reddit 主控台`。分发台只在用户直接下达分发命令时读取登记执行台的身份和可用性；两次命令之间不读取执行台状态。

用户以后可以随时从置顶区回到同一个 `Reddit 分发台` 再发一条运营指令。分发台会优先把新 mission 投递给原有的评论台、发帖台和跟进台；只有对应执行台缺失或不可用时才新建并更新登记。执行任务始终不会返回分发台。用户也可以直接在某个执行台继续当前 mission。执行台保持不置顶。

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
3. Codex 能列出、读取、创建、反归档并向独立用户任务发送指令；能保留工具返回的 `hostId`，并区分 ready `threadId` 与 queued `clientThreadId`。
4. Automation/Heartbeat 工具 schema 支持 repeat-on、显式 `targetThreadId`，并能按返回的 automation ID 读回目标任务 ID。Bootstrap 不创建测试 Heartbeat；第一个真实执行台负责首次创建和读回验证。
5. 能读取真实当地时间、时区、UTC offset 和 UTC。

Chrome Browser control 是 Reddit 写操作依赖。Computer Use、内置 Browser、Playwright 和普通 Web Search 不能替代。屏幕录制、系统音频录制和辅助功能权限不是本 Skill 依赖。

隐藏 `next_run_at` 只记录 `created_unreadable`，不阻断第一轮；目标任务 ID 隐藏或不匹配则不能算绑定成功。若 Chrome 或登录需要用户修复，记录 `BOOTSTRAP_REPAIR_REQUIRED` 并只返回一个具体动作；此状态下用户回复“继续”仅重查缺失项，不启动运营。

### 4. 可重复的一键分配

首次健康后，先按当前 Reddit 用户名静默读取 `${CODEX_HOME:-$HOME/.codex}/reddit-karma-warmup/account-directions/<username>.json`。这是 Skill 目录之外的用户配置，升级不得覆盖，也不得把一个账号的配置自动套给另一个账号。

- 已有匹配配置：作为默认方向静默复用，仍在成功 Bootstrap 提问里询问本轮方向和时长。
- 首次账号：准备默认方向，不单独要求确认；用户对成功 Bootstrap 提问的回答同时完成方向确认和本轮启动。
- 用户明确提供方向和时长：规范并保存方向，立即启动。
- 只给方向：默认 `3 小时`；只给时长：使用已有方向或默认方向。
- 健康提问后的回复 `继续`、`开始`、`默认` 或 `没想法`：使用已有方向或默认方向，直接运行 `3 小时`；故障提示后的 `继续` 只复检故障。

首次 Bootstrap 成功时只返回：

```text
你希望这个 Reddit 账号往什么方向运营，先运营多久？

- 方向：指账号接下来主要参与的主题范围，例如移动产品、3D/AR、游戏与 UGC、摄影与地点体验。可以给 1–3 个相邻方向；没有想法就使用默认方向。
- 时长：指本轮自动运营持续多久。期间电脑需要保持开机且不要休眠，Chrome 保持登录，网络尽量稳定；关机、休眠、关闭 Chrome 或断网会影响后续轮次。

请直接回复，例如：`3D/AR、地点体验，先运营 3 小时。`
没有特别要求也可以回复：`继续`（按已有或默认方向运营 3 小时）。
```

成功时不要在这段提问前后追加版本、安装/NOOP、validator、账号、预检、schema、改名/置顶、未执行动作、来源链接或 probe 信息。只有真实失败时才返回一个最小修复动作。

健康 Bootstrap 提问后，用户回复“继续”即默认标准强度、混合探索、3 小时，并立即把首轮 mission 投递给评论台、发帖台和跟进台。只有三条精确任务消息都被对应执行台接受后，才能说“第一轮已分发”；部分失败时必须写“本轮部分分发”并点名未确认 lane。后续新 mission 优先沿用同一 Reddit 账号原有的执行台：

- `Reddit 评论台`
- `Reddit 发帖台`
- `Reddit 跟进台`
- `Reddit 浏览台`，仅在用户明确要求纯浏览/投票时
- `Reddit 主页台`，仅在首次主页基础未完成或用户明确要求时

K0 新号（combined Karma 少于 50）仍会收到发帖台，但该台只做选址和只读预检，主帖目标/上限固定为 `0/0`。只有账号进入 K1：至少 50 combined Karma、账号满 7 天、至少 10 条可见评论分布在 3 个合格社区、当前状态干净，并且候选 subreddit 的门槛审计与当天 Chrome 复核都通过后，才开始解锁首帖。K1 解锁后仍最多每 24 小时 1 篇。50 Karma 是本 Skill 的最低内部门槛，不是 Reddit 全站发帖许可，也不会覆盖目标社区更高、local/community Karma 或隐藏的要求。

分发台按当前 Reddit 账号读取 Skill 外部的 lane registry，通过精确 Task ID 沿用已有执行台，并为每个新 mission 设置 `worker_task_id=<精确目标任务 ID>`、明确动作目标/上限/最低有效阅读量、`first_due=now`、`heartbeat_owner=self`、`launcher_callback=none`。同一账号同时启用多个执行台时，按评论、跟进、发帖、浏览、主页的顺序，把首次写入依次错开约 `0/10/20/30...` 分钟；所有执行台仍会立刻读帖和准备，后续保持相对相位并允许 `2-4` 分钟浮动，错过窗口就顺延而不补发突刺。这里没有共享锁或跨线程账本。每个真实候选在内容可读后至少停留 `30` 秒才可计为有效阅读、投票、评论或切换下一条；评论/回复从内容可读到提交至少 `45` 秒，输入后再等 `5-12` 秒，页面内独立点击间隔 `1-4` 秒。评论簇中相邻两条发布再额外保留变化的 `3-5` 分钟间隔。五分钟以内的等待使用本地短 `sleep`，更长等待才用 Heartbeat。评论、发帖、跟进和显式浏览每轮都维护硬投票目标：低/标准强度默认 Upvote+Downvote 合计至少 `2`，高强度至少 `4`；两个方向分开统计但默认不强制各一次。评分门槛不会为了补数降低，目标不足只能继续在本 lane 的合格范围内扫描或如实报告差额。新 mission 替换该 lane 的旧任务字段，但不会复活上一轮已经删除的 Heartbeat。

评论或发帖 mission 下发前，分发台会结合已确认账号方向和本轮重点，从本地 subreddit Reference 中评估最多 100 个匹配社区，优先选择流量达标、动作路由开放且版规摩擦较低的候选。评论台和发帖台各收到最多 20 个已过基础门槛的候选；不足时按真实数量下发，不会用 research-only 或高风险社区凑数。若目标是必须完成 1 篇主帖，发帖台可先用 20–30 分钟做选址，并用 Chrome 深查排名前 8–15 个社区的当天版规、账号门槛、近期存活内容和提交页；100 条 Reference 扫描用于广度，不等于在 30 分钟内机械打开 100 个 Reddit 页面。

默认发帖采用讨论优先的 `beginner-common-mistake` 角度：在有真实技能门槛和经验分享文化的社区，提出一个小白也能理解、多数成员经历过、答案不唯一且能引出故事的新手常见坑。发帖前至少抽样 10 条近期本地讨论帖，并通过 `discussion_potential_score >=80`：识别度、答案多样性、故事空间、低回复成本、当前社区证据和非 FAQ。问题可以简单，但不能伪装新手、伪造使用经历或故意写错；也不能把同一模板只替换社区名后批量发送。不适合该角度的社区改用具体工作流摩擦、工具取舍或原生观察题。

社区路由 Reference `loci-subreddit-pool-v1.md` 同步自飞书《Loci Reddit Subreddit 档案总表》，包含 144 个社区的主要用户、常见痛点、版规边界、可发内容、账号适配和近期信号。Loci 全组织永久禁入项单独保存在 `organization-community-denylist.md`，必须在打开候选社区前先排除；它约束自有、员工、代理和其他协调账号。社区总表按 subreddit 行或关键词候选集渐进读取，不应整表无条件加载；其中规则是历史证据，发帖前仍以 Reddit 当天规则和提交页为准。

启动时会把已确认的账号方向映射到 `subreddit-profile-index.csv` 的主题、受众、需求、内容形态和风险标签，先生成最多 12 个候选。只有已缓存且不少于 5,000 weekly visitors 的社区可进入 operating shortlist；流量未知或过期的匹配只进入待复核队列。画像匹配和流量达标都不是发布许可，执行台仍需读取动作级覆盖和当天版规。

2026-07-14 的扩展把标签索引从 174 个增加到 254 个社区：80 个新增社区覆盖年轻人/轻社交、泛游戏、电影电视、动漫、音乐、摄影、艺术设计、旅行地点、效率工具、AI 陪伴、移动产品和空间 3D；38 个既有社区补齐了实时周流量。原始只读搜索快照保存在 `reddit-community-search-snapshot-2026-07-14.json`，筛选结果保存在 `subreddit-catalog-expansion-2026-07-14.csv`。新增行全部保持 `research_only`，不能因为达到 5K 流量门槛而直接评论、发帖或提及产品。

最新复核结论保存在 `community-action-routing-overrides.md`。它不再用一个等级同时代表全部动作，而是分别判断普通评论、主帖和产品提及；例如技术评论可用不代表 Loci 主帖可发。路由顺序是永久禁入表、动作级覆盖表、历史社区总表、当天版规与账号状态。

`community-live-audit-30-2026-07-13.md` 保存本轮 30 个社区的 Chrome 只读 live 证据和关键门槛；对应动作已同步进覆盖表。该证据表只用于解释和当天复核，不能把可见提交页或存活帖子当作发布许可。

`posting-account-gates-audit-2026-07-14.csv` 单独记录每个社区公开可见的账号年龄、combined/post/comment/community Karma、verified email、参与历史、Flair、megathread 和 mod approval 门槛。当前 254 行中，普通社区仅 22 个完成了本轮门槛判断，229 个仍为 unknown，另有 1 个 blocked 和 2 个组织级 deny；因此这项审计尚未完成。K0 不发主帖；对 K1 主帖，unknown 直接关闭候选。`no_public_gate_found` 也不代表没有隐藏 Automod 门槛，仍须当天 Chrome 复核。

凡最新复核明确“降级”的社区一律进入 `research-only`：后续不发表评论、不发主帖、不回复、不投票，也不做产品提及。只有未降级但按动作受限的社区，才保留技术评论可用、主帖关闭等拆分权限。

扩展研究 `community-expansion-pending-review-2026-07-13.md` 也随 Skill 打包，包含 18 个 suspension 后需要重新 preflight 的候选和 29 个新增名称级候选。它只用于候选发现：没有当天 live 版规、账号资格、New/Hot 和提交页证据时，不能据此评论、发帖、投票或 Join。

公开动作审计 `community-action-expansion-public-audit-2026-07-13.md` 进一步记录 30 个候选，其中 14 个有当前或近期公开规则证据、3 个只有较弱信号、13 个仍是名称级。它只能决定 suspension 结束后的 live preflight 顺序，不会直接扩大可执行社区池。

```text
第一轮已分发：Reddit 评论台、Reddit 发帖台、Reddit 跟进台已收到任务。

后续所有 Reddit 运营任务都可以继续在这个 Reddit 分发台下达；告诉我方向、时长或具体动作即可，我会优先沿用已有执行台。

进行中的评论、发帖或跟进，请直接到对应执行台查看或调整。
```

后续完整分发把第一行改成 `本轮已分发：<实际接受任务的执行台>已收到任务。`；部分分发写 `本轮部分分发：<已接受执行台>已收到任务；<未确认 lane>未确认投递。`。不要把“已解析任务”或“已准备消息”写成“已分发”。

lane registry 位于 `${CODEX_HOME:-$HOME/.codex}/reddit-karma-warmup/lane-registry/<username>.json`，按 Reddit 账号隔离并在升级时保留。后续分发优先读取登记的精确 ready Task ID 和可选 `hostId`；`clientThreadId` 只代表任务仍在创建队列，不能登记成可用执行台。若旧版没有登记，可仅在第一次做一次有限查找，最多检查三个最新同名候选，并且只有一个候选的 lane 与当前 Reddit 账号都明确匹配时才收编。不能仅凭标题猜测，也不能仅按最新时间猜测。登记任务永久不可用或投递失败后才新建替代台并覆盖该 lane 的登记。

### 5. 执行台自治

每个执行台：

- 立即执行自己的首轮，不等 Heartbeat；
- 先确定动作数量目标，并用最低有效阅读量作为检索深度参考；动作目标未满足时继续读取真实最新帖子和评论并扩展合格社区，不因第一批候选不足而提前结束；
- 评论和主帖以成功发布数量作为主要完成条件；阅读量只是检索深度参考。达到阅读参考值但动作数量不足时继续扩展候选，未完成数量跨 Heartbeat 原样续跑，不得重置或把候选不足报告为已完成；
- 每个候选独立评分，达到门槛才动作；增加阅读量不能降低评论、发帖或投票阈值；
- 评论、发帖、跟进和显式浏览每轮都把 Upvote/Downvote 分开记账，并以两者合计目标作为默认硬完成条件；用户明确指定方向数量时分别成为硬目标。投票前若任一方向已明确选中则记录 `existing_vote` 并不点击，状态不清则 `no_vote`，成功点击后不重复验证；
- 始终拥有一个专属 Reddit 主标签：用两次浏览器调用完成创建，第一次只创建标签并返回/持久记录 tab ID，第二次才通过 `tab.goto(...)` 导航并等待最多 60 秒；禁止把创建和首次导航放在同一次调用里。超时只代表导航确认不确定，必须重连同一 Chrome、重领同一 tab ID 并检查实际 URL/页面；不得删除它、另建标签或抢用户/其他任务的标签。后续心跳只重领这个标签；非终态以 `handoff` 保留，任务终态关闭/释放。Tab Group 仅用于视觉整理，不能替代主标签；`openTabs()` 只看到 URL/标题不算页面控制成功；
- 只从当前任务上下文读取自己的精确 Task ID；定时前核对 mission 的 `worker_task_id`，创建/更新时显式绑定自身，创建后按 automation ID 读回目标并再次核对；每次唤醒还会复核一次；
- 自己处理网络恢复、规则复核、重试、候选替换和用户修复；
- 在自己的任务里汇报，用户后续直接和该任务沟通；
- 不读取、不 callback、不暂停、不修改其他执行台。

评论台和跟进台在每条评论前执行短检查：快速确认相关版规，读完整帖子/父评论及附近回复，记录一个具体细节、一个重复观点和当前社区的本地语气样本，再从 micro、one-liner、two-beat 三个内部版本中选择最短且有信息量的版本。主动评论簇内每一条都必须重新执行这套门控并生成新的 `per_comment_gate_id`，禁止一次写完整簇或复用第一条的长度/黑话决定。普通簇内评论默认不超过 25 个英文词；每簇最多一条可因真实信息需求放宽到 26–45 词。评论应高频使用当前社区自然出现的缩写、碎句和 Reddit 口吻，但每条通常只放一个、最多两个，不得机械堆黑话或复制别人的表达。

主动评论强制按簇执行：除非用户明确只要求总共 1 条评论，否则每个完成的评论窗口至少发布并验证 2 条。发完 1 条不能结束该轮、不能把窗口记为完成，也不能直接安排下一次 Heartbeat；应继续寻找第 2 条。只有用户停止、截止时间到达或当前硬阻塞才能留下 `cluster_incomplete`，其余数量原样续跑。

当前 Heartbeat 承载的整份用户任务目标一旦完成，执行台必须先删除自己的 Heartbeat、清空下一次运行时间，再回报任务完成；不能因为授权时长仍有剩余而保留空转 Heartbeat。单个评论簇、每小时配额或阅读下限只是中间进度，不会误触发终止。

`reddit-us-voice-patterns.md` 提供美国 Reddit 常见的赞同、反对、修正、建议、追问、轻吐槽和技术判断句型，并区分稳定表达、语境表达和陈旧 Reddit 梗。该表只作回退；当前帖子附近真实回复始终优先。

同一 Chrome profile 或同一 Reddit 账号不是冲突。某个执行台失败只影响它自己，其他任务继续运行。

## Requirements

- Codex 本地 Skill 支持
- ChatGPT Chrome Extension 提供的 Chrome Browser control
- 用户已在同一 Chrome profile 登录 Reddit
- 多轮任务需要 repeat-on Heartbeat、显式 `targetThreadId` 和按 automation ID 读回目标任务的能力
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

仅操作用户明确授权的账号和浏览器会话。实时 subreddit 规则约束具体动作。登录/CAPTCHA/账号锁只暂停受影响执行台；明确 HTTP `429`/`Too Many Requests` 会立刻结束该执行台的当前轮次，保留任务与 Heartbeat，并在下一正常轮次或更晚的服务端指定时间自动复查，不会取消长期运营或集中补发；明确社区禁止则换社区；网络和页面故障由当前执行台及其 Heartbeat 继续恢复。

## 反馈与贡献

这是公开仓库，但公开不代表任何人都能直接修改 `main`。未获得仓库写权限的用户可以：

- 提交 [Issue](https://github.com/lishehao/reddit-karma-warmup/issues) 报告问题或提出建议；
- 在已有 Issue 或 Pull Request 下评论；
- fork 仓库、修改后提交 Pull Request，等待维护者审阅和合并。

只有仓库所有者或被授予写权限的协作者可以直接推送。完整要求见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## License

MIT
