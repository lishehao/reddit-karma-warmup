# Reddit Community Operations Installer Protocol

Machine execution protocol. Follow it directly after the user-facing bootstrap Prompt fetches this file. Do not ask the user to read or copy this protocol.

Protocol version: `2026.07.10.26`

## Execute

```text
请在普通任务模式完成下面的安装与启动流程，不要进入目标模式。不要查找随附 ZIP，不要调用 `git clone`、`git pull` 或 GitHub CLI。你已经读取到 canonical protocol，不要再次递归读取安装协议。

固定分发源：
- repository: `https://github.com/lishehao/reddit-karma-warmup`
- installer protocol: `https://raw.githubusercontent.com/lishehao/reddit-karma-warmup/main/INSTALLER-PROTOCOL.md`
- archive: `https://codeload.github.com/lishehao/reddit-karma-warmup/zip/refs/heads/main`
- skill path inside repository: `reddit-karma-warmup/`

通过 HTTPS 下载 archive 到临时目录，安全解压，确认仓库快照中只有一个目标 `reddit-karma-warmup/` Skill 目录，读取其中的 `manifest.json` 并运行 Skill 校验。下载失败时只报告 GitHub HTTPS 不可用，不要退回 Git；公开仓库不需要 Token。

Python 不是依赖，缺少 Python 不能写入 required_missing，也不能单独阻塞安装或运营。有可用的 Skill 校验器时直接运行；没有 Python/校验器时执行等价检查：确认 GitHub archive 可完整解压、目标 Skill 根目录唯一、SKILL.md 含有效的 name/description frontmatter、manifest.json 的 name/version/schema/repository 可读、agents/openai.yaml 和所有 references 可读、引用的关键文件存在。等价检查通过即可继续。

目标安装路径是 ${CODEX_HOME:-$HOME/.codex}/skills/reddit-karma-warmup。按照 manifest.json 的 name 和 version 执行：
1. 未安装：正常安装。
2. 已安装同名 Skill，但没有 manifest.json：视为 legacy 旧版，先备份再升级。
3. GitHub 版本高于已安装版本：先把整个旧目录压缩备份到 ${CODEX_HOME:-$HOME/.codex}/skill-backups/，再用同文件系统临时目录进行原子替换。
4. 版本相同且内容相同：NOOP，不重复覆盖。
5. 版本相同但内容不同：BLOCKED_CONFLICT，保留旧安装并报告；不要猜测哪份正确。
6. GitHub 版本低于已安装版本：BLOCKED_DOWNGRADE；除非用户明确要求降级，否则不要覆盖。

升级必须替换整个受管 Skill 目录，不逐文件合并。切换后重新运行 Skill 校验；若校验失败，立即恢复旧目录并返回 ROLLED_BACK。不要自动把旧目录中的未知文件混入新版；旧内容已保存在本机备份中。

安装完成后暂时不要调用 $reddit-karma-warmup，也不要进行 Reddit 写操作。当前安装任务先独立完成依赖预检：

必需依赖：
1. 能通过 HTTPS 读取上述公开 GitHub installer 和 archive；不要求 Git 或 GitHub 账号。
2. 已安装的 SKILL.md、agents/openai.yaml 和 references 目录可读取且校验通过。
3. 必须存在并能够实际调用 Chrome Browser control。尝试发现 Chrome 会话和读取标签页；连接失效时最多重连两次。
4. 必须通过 Chrome Browser control 只读打开 Reddit，确认已登录账号并记录准确用户名。不要输入或处理密码。
5. 必须存在 automation/heartbeat 的创建、更新、查看和删除能力。
6. 必须能读取真实当地时间、时区和 UTC offset。
7. 不使用 Goal Mode。首次启动、首小时观察和多小时运营都依赖当前 slot 立即执行加一次性 Heartbeat 续跑。

Chrome Browser control 是硬依赖。Computer Use、内置 Browser、Playwright、终端浏览器和普通 Web Search 都不能替代它。如果环境只能使用这些工具，dependency_status 必须是 BLOCKED，不要降级执行 Reddit 操作。

macOS 的“屏幕录制”“系统音频录制”和“辅助功能”权限不是 Chrome Browser control 的依赖，不要检查它们，也不要因为它们未授权而阻塞。Chrome Browser control 依赖的是 Chrome 正在运行、ChatGPT Chrome Extension 已安装并启用、Native Messaging 通信正常，以及 Reddit 已登录。只有改用 Computer Use、操作桌面应用或录制桌面/音频时才可能需要系统权限；本 Skill 不把这些能力作为替代方案。

对 scheduler 做一次不访问 Reddit、不会产生外部动作的 create/readback 探针：选择未来 7–10 分钟的测试时刻，记录目标当地时间和 UTC；创建单次 heartbeat，并读取自动化工具实际暴露的字段，然后删除测试 heartbeat。创建与删除成功即可证明 heartbeat capability 可用。若持久化 next_run_at 或显示时间可读，再据此判断 scheduler_clock_mode=UTC_FIELDS 或 LOCAL_FIELDS；若运行时不暴露这些字段，记录 heartbeat_timing=CREATED_UNREADABLE、scheduler_clock_mode=UNKNOWN，并继续安装与第一轮 Reddit 操作。缺少 next_run_at/DTSTART/下一次运行标签不是用户可修复的问题，不能据此暂停或要求用户回复“继续”。只有创建、更新或删除本身失败时，heartbeat_support=UNAVAILABLE 并阻塞多小时自动续跑。实际时间正确性由开始运营后的 smoke test 和第一次真实唤醒验证。

可选依赖：
- Codex task/thread 的创建、读取、发送调整和重命名能力。只有创建+读取+发送三项都可用时才启用分布式任务；缺一项就使用 SEQUENTIAL_FALLBACK。重命名缺失只影响标题，不阻塞。
- 主任务优先使用 gpt-5.6-sol + Extra High（xhigh），执行任务统一使用 gpt-5.6-luna + High（high）；任一组合不可用时使用当前环境实际暴露的最强可用回退，不单独阻塞。
- Python/Skill 校验器；缺失时使用上述等价结构检查，不阻塞 Reddit 运行。

把下面的详细依赖状态保存在内部 handoff，不要在健康状态下逐项展示：
install_action: INSTALLED | UPGRADED | NOOP | BLOCKED_CONFLICT | BLOCKED_DOWNGRADE | ROLLED_BACK
github_source: AVAILABLE | UNAVAILABLE | UNVERIFIED
skill_version: old_version | incoming_version | active_version
upgrade_backup: backup_path | NONE
dependency_status: READY | BLOCKED
required_ready: [已通过项]
required_missing: [缺失、失效或未验证项]
optional_missing: [可降级项]
repair_actions: [用户可以直接执行的修复动作]
chrome_control: AVAILABLE | RECONNECTED | UNAVAILABLE
reddit_session: LOGGED_IN:u/name | LOGGED_OUT | UNVERIFIED
heartbeat_support: READBACK_VERIFIED | CREATED_UNREADABLE | UNAVAILABLE
scheduler_clock_mode: UTC_FIELDS | LOCAL_FIELDS | UNKNOWN
scheduler_probe: target_local | target_utc | persisted_next_run_at_OR_NOT_EXPOSED | deleted
thread_support: FULL_CREATE_READ_SEND | SEQUENTIAL_FALLBACK
model_runtime: coordinator requested gpt-5.6-sol/xhigh | workers requested gpt-5.6-luna/high | actual | fallback
local_time_check: local time | timezone | UTC offset
bootstrap_state: not_started | in_progress | initialized | needs_repair

如果 required_missing 为空且 dependency_status=READY，只向用户返回：
“状态健康。当前账号：u/name。

你希望接下来怎么运营？可以指定时长、评论或发帖数量、目标社区，也可以只浏览并偶尔投票；如果暂时没想法，直接回复‘开始’，我会按默认方案先试运行 3 小时。”
不要展示其余健康字段。Task/thread、模型或其他可降级能力的回退保持内部处理；只有它实际阻止用户目标时才说明影响。

“状态健康”只表示运行依赖通过，不代表 Reddit 账号或目标 subreddit 没有审核风险；账号和社区风险在第一轮实时检查。

如果 required_missing 非空或 dependency_status=BLOCKED，只返回简短的“需要你处理”，把底层错误翻译成用户可直接完成的一项修复动作，并说明当前暂停范围。不要展示已通过项、原始日志、内部字段或无关依赖，也不要询问是否开始。结尾写“完成后回复‘继续’”。

优先使用以下新手返回，不要让用户自行推断：

- `chrome_control=UNAVAILABLE`：`需要你处理：请打开 Chrome，安装或启用 ChatGPT Chrome Extension，并保持 Chrome 运行。影响：Skill 已安装，但 Reddit 操作尚未开始。完成后回复“继续”。`
- `reddit_session=LOGGED_OUT|UNVERIFIED`：`需要你处理：请在当前 Chrome 手动打开 reddit.com，创建或登录账号，并完成 Reddit 页面显示的验证。不要把密码发给 Codex。影响：Skill 已安装，但 Reddit 操作尚未开始。完成后回复“继续”。`
- 两项都缺失时先处理 Chrome；用户回复“继续”后重新检查，再只提示 Reddit 登录。

如果我回答“是”“开始”“可以”或同义确认，立即使用 $reddit-karma-warmup 开始第一轮，不要重复依赖预检，也不要再次确认。用户另行指定的时长覆盖默认 3 小时。

确认时读取真实本地开始时间并计算：
- `operation_stop_at = started_at + 用户指定时长`，未指定则 `3 小时`。
- `startup_watch_deadline = min(operation_stop_at, started_at + 60 分钟)`。

同时保存两个时间的本地日期、时区、UTC offset 和 UTC instant。它们都是硬截止时间，不因任务延迟、代理位置或错过 Heartbeat 自动顺延。

用户确认后不要创建 Goal。主任务立即执行或派发第一轮，并维护一个临时只读 one-shot Heartbeat；在 `startup_watch_deadline` 做最终验收与交接：评论首小时目标 10 条，内容浏览完成 8–12 条有效阅读并应用投票门槛，首条发布内容通过立即和延迟可见性检查，每个执行任务成功创建不超过 `operation_stop_at` 的下一次 Heartbeat；运行时暴露时间字段时必须回读校验，未暴露时记为 `created_unreadable` 并在真实唤醒时校验。主任务删除临时检查并进入 `IDLE`。

确认后，本消息授权：把当前主任务命名为“Loci Reddit运营”，作为长期唯一入口；本次运行类型为 BOOTSTRAP。任务创建+读取+发送能力完整时，创建并立即启动 4 个执行任务，分别命名为“主动评论”“消息跟进”“主页维护”“内容浏览”；主动发帖默认关闭。主任务负责首小时观察、技术修复和最终交接；执行任务不向主任务做 routine Callback。任务能力不完整时，在当前任务按跟进 -> 主页维护 -> 内容浏览 -> 主动评论顺序执行。

派发后立即只向用户返回：“已启动：主动评论首小时目标 10 条，消息跟进、主页维护和内容浏览同步运行；第一小时结束后汇报。”然后继续执行，不等待用户回复。

主任务内部遵循 `INTAKE -> PREFLIGHT -> DISPATCH -> STARTUP_ACCEPTANCE -> AUTO_REPAIR -> HEARTBEAT_WATCH -> HANDOFF -> IDLE`。它自动处理 Chrome 重连、独立 Tab 恢复、任务重试、scheduler 时间修正、Heartbeat 回读和模型/任务能力回退，不进入 Goal Mode，不让用户选择 worker、读取 Thread ID 或理解技术日志。仅登录失效、验证码/限流/锁定、Chrome Browser control 持续不可用或其他必须由用户完成的修复才中断并请求用户操作。

主任务把 dependency report 作为 handoff 传给每个执行任务，包括账号、当地时间、scheduler_clock_mode、thread/model fallback，并保存每个执行任务的 ID、工作线、目标和完成条件。主任务优先请求 gpt-5.6-sol + Extra High，执行任务统一请求 gpt-5.6-luna + High；环境不能覆盖时继承实际最强可用组合。

第一轮必须先执行，并到达已验证动作、已验证无动作结果或具体阻塞，再安排后续 heartbeat。每个执行任务只能修改 target_thread_id 等于自己且属于自己 lane 的 automation；其他 lane 只读。

首次安装并开始运营时，主动评论任务立即执行完整首小时批次：所有健康档位（包括纯新 `K0`）都以首小时 `10` 条合格评论为目标。每条评论成功发布并验证后，用本地短暂停留等待 `60–120 秒`再发布下一条；寻找帖子、阅读、写作、Double-Check A/B 和结果验证仍然必须完成。只有出现明确账号/可见性阻塞，或者没有足够合格候选时，首小时才少于 `10` 条。

每条评论发布并验证后，记录最终文本的字符数、词数、句段形态和长度档位。生成下一条前读取最近 `10` 条评论长度记录，并结合当前帖子信息量和附近原生回复风格决定长短；不要固定成两句话，也不要为了制造差异而机械轮换、填充废话或截断有效内容。

内容浏览任务每个 slot 真实读完 `8–12` 条内容，覆盖 `2–4` 个合格社区；标题扫过、重复内容、广告和误触不计数。每个 slot 最多进行 `1` 次 Upvote 或 Downvote：Upvote 仅用于足够有趣、有质量且符合真实兴趣画像的内容；Downvote 仅用于明确 spam、误导、骚扰、违规或不贡献内容，普通观点不合不点踩。比例是机会窗口，不是强制配额；没有达到门槛的内容就完成 `0` 次投票。

每条工作线最多保留一个下一次 one-shot heartbeat。按可用的 scheduler_clock_mode 写 RRULE；若时间字段可读，创建后必须回读实际 next_run_at 并换算成 UTC 和当地时间，发现错误时更新原 automation，不创建重复任务。若时间字段不可读，创建成功后记为 `created_unreadable`，保留目标当地时间和 UTC 在 heartbeat prompt 中，继续当前工作并在真实唤醒时校验；不得因此删除成功的 heartbeat 或暂停 Reddit 操作。

任何执行任务都不得创建或保留发生在 `operation_stop_at` 或之后的 Heartbeat。主任务的首小时观察只通过 one-shot Heartbeat 唤醒：先在 `5–10 分钟`读取一次初始进度，按 `15–30 分钟`窗口检查首条可见性，之后按需安排下一次检查，并在 `startup_watch_deadline` 做强制终检。等待期间必须结束当前 turn，禁止目标模式、连续自动续跑、轮询时钟或重复汇报“还没到时间”。只有终检时所有启用工作线都通过首轮验收才记为启动通过；否则准确汇报缺口。终检后必须删除主任务 Heartbeat 并进入 IDLE，不能继续主动跟进或静默延长截止时间。

每个执行任务创建或认领一个自己的 Reddit Tab；Chrome 支持时再使用独立 Tab Group。各任务共享同一个 Chrome profile 和 Reddit 登录，但彼此完全独立：只操作自己的 Tab，不读取、不等待、不比较其他任务的目标、动作、时间或账号使用情况。执行前只需重新选中自己的 Tab，并核对当前账号和 URL。

每个发布型执行任务的第一条向外内容必须立即记录准确 permalink、作者、目标 subreddit/父帖、发布时间和刷新结果。主动评论任务记录第一条后继续完成首小时目标，不等待主任务复查。主任务在自己的只读验收 Tab 中独立打开 permalink，并在帖子场景检查 subreddit `/new` 与作者 Posts，在评论/回复场景检查父帖评论链与作者 Comments。相同登录态下两处均可见记为 `surface_visible`，不能直接称为匿名公开可见。内容浏览不做 permalink 延迟验收；它以 `8–12` 条有效阅读日志及投票后刷新状态作为首轮验收。

“Loci Reddit运营”维护一个临时只读启动健康 heartbeat，在最新一条首发内容发布后的 `15–30 分钟`再次检查 permalink 和第二 Reddit 页面。仍然可见才记为 `survivor_visible`。只有已有独立的未登录/Guest Chrome context 时才额外记为 `public_visible`；不要为此退出当前 Reddit 账号。

主任务不能把“已派发”“同账号立即看到”或早期验收通过当作首小时启动成功。首发内容必须通过立即检查、第二 Reddit 页面检查和 `15–30 分钟`延迟复查；需要继续的工作线还必须成功创建下一次 heartbeat，时间字段可读时再要求回读正确。`created_unreadable` 不阻塞首轮验收，第一次真实唤醒负责补做时间校验。主任务由自己的 one-shot heartbeat 唤醒到第一小时边界，终检后记录 `bootstrap_state=initialized`，删除临时 heartbeat 并停止主动跟进。后续由各执行任务自己的 heartbeat 独立运行。

此后用户继续在“Loci Reddit运营”主任务下达任何主动运营指令时，运行类型改为 MISSION：读取当前账号状态和 worker registry，复用已有 `主动评论`、`主动发帖`、`消息跟进`、`主页维护`、`内容浏览` 任务，只发送新的数量、社区、链接、时长和截止时间。不要重新安装、不要重复装修健康主页、不要再次运行 BOOTSTRAP。一次性任务验证完成即可交接；持续任务最多由主任务只读观察第一小时，之后进入 IDLE。

MISSION 语义：用户说“再/额外/追加 N 条”时增加该工作线的剩余目标；说“改成/总共 N 条”时替换剩余目标；说“暂停/停止/继续 X”时只修改指定工作线，其他工作线继续。用户没有重新指定的社区、语言、时长或其他字段沿用当前 mission，不要自行清空。
```

## 主流程

```text
HTTPS 下载 GitHub archive -> 临时解压 -> 读取 manifest -> 校验目标 Skill
-> 比较同名 Skill 版本 -> 备份旧版 -> 整目录原子替换 -> 再校验/失败回滚
-> 安装 Markdown 检查 Chrome、Reddit 登录、Heartbeat、时区和可选能力
-> 创建并删除无 Reddit scheduler 探针 -> 可回读时得到 scheduler_clock_mode；不可回读时记 CREATED_UNREADABLE 并继续
-> 缺少硬依赖：返回 required_missing + repair_actions，停止
-> READY：携带账号只询问一次 -> 用户确认
-> 计算 operation_stop_at 与 startup_watch_deadline -> 不创建 Goal，准备首小时 one-shot Heartbeat
-> 主任务改名“Loci Reddit运营” -> 创建评论、跟进、主页维护、内容浏览 4 个任务（或顺序降级）
-> 向用户返回一行“已启动”；技术状态全部留在内部
-> 每个执行任务建立自己的 Reddit Tab / 可选 Tab Group；彼此互不感知
-> 主动评论首小时目标 10 条 -> 每条验证后本地等待 60–120 秒
-> 内容浏览每 slot 有效阅读 8–12 条 -> 达到门槛时最多投 1 票，未达到则 0 票
-> 评论/发帖/回复执行 Double-Check A -> 写作 -> Double-Check B；内容浏览执行阅读与投票门槛
-> 发布后立即验证 permalink -> 主任务检查第二 Reddit 页面
-> 每个执行任务只维护自己的 lane automation
-> 写一个下一次 heartbeat -> 时间字段可读则回读 next_run_at；不可读则在真实唤醒时校验
-> 首小时内主任务持续只读回访、复查可见性和自动修复
-> 第一小时边界强制终检 -> 删除临时健康 heartbeat
-> 记录 bootstrap_state=initialized -> 返回四字段首小时结果 -> 主任务进入 IDLE
-> 执行任务独立恢复执行，直到停止时间；Loci Reddit运营仅响应用户查询或新目标
-> 后续新指令进入 MISSION -> 复用对应执行任务 -> 不重复 BOOTSTRAP
```

## 必需与可选依赖

| 能力 | 级别 | 缺失时行为 |
|-|-|-|
| GitHub installer/archive HTTPS 下载 | 必需 | 安装或升级暂停；不回退到 Git |
| manifest 读取、版本比较、临时校验及原子替换 | 必需 | 保留旧安装并报告 |
| Chrome Browser control | 必需 | 阻塞；禁止其他浏览器工具替代 |
| Chrome 内 Reddit 登录 | 必需 | 要求用户自行登录 |
| macOS 屏幕录制/系统音频/辅助功能 | 不需要 | 不检查，不影响 Chrome Extension 控制 |
| Heartbeat 创建、更新、删除 | 必需 | 创建/更新/删除失败时阻塞多小时自动续跑；仅时间回读缺失不阻塞 |
| 当地时间、时区、UTC | 必需 | 阻塞无人值守调度 |
| Task/Thread 创建+读取+发送 | 可选组合 | 任一缺失则顺序执行；不创建不可回读的孤立任务 |
| Task/Thread 重命名 | 可选 | 保留原名称，不阻塞 |
| Sol+xhigh / Luna+high 覆盖 | 可选 | 使用环境实际暴露的最强可用回退 |
| Python/Skill 校验器 | 可选 | 改用 archive、frontmatter、manifest 和引用完整性检查 |

## 运行边界

- 用户指定的时长、数量、语言、社区和 lane 优先。
- 默认启用跟进、主页维护、内容浏览和主动评论；主帖可选。
- Chrome 掉线先重连；提交附近掉线先检查是否已经发布。
- captcha、rate limit、锁定、错号、凭据请求或账号 warning 会停止写操作。
- 主帖每次实时检查版规、账号资格、flair、megathread、频率和审核状态。
- `A0` 与 `No-go` 社区只读；不编造身份、经历、产品使用或指标。
- 用户数量是规划目标，不能用低质量内容机械补足。

## 升级策略

- 版本来源：GitHub `main/reddit-karma-warmup/manifest.json`，格式为 `YYYY.MM.DD.N`。
- 按数字段比较版本；任何分发文件发生变化时递增最后一段版本号。
- 默认只升级，不自动降级。
- 同名旧版采用“备份整个旧目录 -> 替换整个目录 -> 校验 -> 必要时回滚”。
- 不进行文件级合并，避免旧 references 或已删除文件残留。
- 同版本内容冲突时停止并报告，不静默覆盖。
- 升级成功后再执行 Chrome、Reddit 登录和 Heartbeat 依赖预检。
