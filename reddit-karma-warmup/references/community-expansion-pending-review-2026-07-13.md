# Loci Reddit 社区扩展研究与版规摩擦审计

审计日期：2026-07-13（Asia/Shanghai）  
报告状态：离线扩展版；本轮新增 live Chrome 核验为 0  
账号边界：原账号仍处于 7 天 sitewide suspension；本机 Chrome 已切换到新 Reddit 账号，因此本轮停止一切 Chrome Reddit 导航  
永久排除：`r/gamedev`、`r/CozyGamers`。本报告不打开、不搜索、不读取、不测试这两个社区。

## 结论先行

这轮不能把“新增社区候选”写成“已确认可参与”。因为最新指令要求停止新账号下的 Chrome 访问，本轮只能把本地档案、上一轮已保存的 Chrome 证据和普通公开 Web Search 的名称级信号合并整理；新增社区全部标成“待人工复审”，不产生评论、主帖或投票许可。

真正值得保留的运营 shortlist 仍来自上一轮已经有规则证据、且没有被最新 action override 关闭的 18 个社区。但它们也只是 suspension 结束后的候选顺序，不是当前可执行权限；恢复前必须重新检查当前账号、社区规则、New/Hot 和提交页。

最重要的判断是：降级社区与 `r/gamedev` 的共性是“高 self-promo 供给 + 贡献优先 + 版主/自动审核容易把产品化内容识别为 spam”，而不是它们都等于永久封禁。`r/gamedev` 是组织级 permanent deny；其余社区最多是 research-only、comment conditional、main-post closed 或人工复审，不能混为同一等级。

## 方法与证据边界

### 已有本地证据

- 社区池快照共 144 个社区，来自 Skill references 的 revision 763（2026-07-12 21:52 CST）。
- 上一轮已用同一 Chrome 读取 78 个 B/B+ 候选的规则页；这是 suspension 前已有的 live evidence，不是本轮新增。
- 上一轮 New/Top 完整提取成功 42/78；36 个社区的当日 feed 未完全确认，其中 18 个受到 `net::ERR_BLOCKED_BY_CLIENT`，另 18 个未在阻塞前完成。网络失败不被当成严格版规。
- 上一轮可见账号证据为约 2 年账号、119 post karma、510 comment karma；另有 7 天 suspension 提示。新账号没有被读取，也没有测试其状态。
- 最新 `community-action-routing-overrides.md` 覆盖历史粗分层：当前路由优先级为组织 denylist > 账号阻塞 > 精确动作覆盖 > 历史池 > survivor pattern。

### 本轮新增动作

- 没有打开、搜索、刷新或读取任何新账号下的 Reddit 页面。
- 没有调用 Computer Use、Playwright 或其他浏览器。
- 通过本地 144 行档案交叉检查了公开 Web Search 得到的候选名称；发现 29 个不在现有档案中的名称级候选，其中 8 个有公开搜索结果或公开帖子信号，21 个仅达到名称级发现。
- Web Search 只用于候选发现和方向判断，不用于确认当前版规、账号门槛、local/community karma、mod approval 或发帖权限。

### 判定标准

- “低摩擦”必须同时满足：普通评论入口清楚、主题不敏感、无明显 local/community karma 或 previous-activity gate、无固定 megathread/approval 才能参与；主帖仍需单独 preflight。
- “中摩擦”表示评论可能自然，但主帖有 flair、时间窗、格式、主题纯度或自推边界。
- “高摩擦”包括 local/community karma、账号年龄、previous activity、Request to Post、mod approval、强制 megathread、固定低频窗口、严格 topic purity、AI/调查/招聘禁令或主观反推广执行。
- 公开帖子 survivor 只能说明有内容存活，不能代替规则、composer 或当前账号资格。
- 真实评论必须是对当前讨论的正常回应；不伪造身份、经历、学生身份、地点经历或测试经历，不把评论写成隐性产品导流。

## 方向覆盖统计

| 方向 | 现有 144 档案中已有覆盖 | 本轮新增名称级候选 | 当前结论 |
|-|-:|-:|-
| 年轻人、校园、室友、轻社交 | 有（college、CollegeRant、GamerPals、roommates 等） | 2 | 研究价值高，但未成年人、心理健康、隐私和 AI 伪装风险高；不作为默认产品入口 |
| 游戏、UGC、avatar、虚拟世界 | 有（IndieGaming、Roblox、VRChat、ZEPETO 等） | 2 | 竞品/开发者社区贡献优先，很多已 research-only 或 A0 |
| 创作、摄影、设计、动画、视频 | 有（godot、threejs、UI/设计等） | 9 | 最值得扩展；普通评论可能自然，但自推、AI、作品展示规则必须 live 复核 |
| 地点、城市、户外、旅行 | 有（geocaching、hiking、walking、whereisthis 等） | 3 | 与“把内容放进世界”相邻；地点隐私、私宅、个人识别和安全风险需要单独门槛 |
| App、独立产品、消费者科技 | 有（apps、AppIdeas、SideProject 等） | 9 | 相关性高但自推污染最重；评论与主帖必须分开 |
| 泛娱乐、音乐、电影、动漫、桌游 | 档案覆盖较少 | 4 | 活跃不等于适合 Loci；只能从真实兴趣评论切入，禁止品牌/产品借势 |
| 合计 | 144 个既有档案 | 29 个新增名称级候选 | 新增 live Chrome 核验 0 |

## Suspension 前证据支持的参与优先 shortlist

以下 18 个是“现有档案 + 上一轮证据 + 最新 action override 没有直接关闭”筛出的恢复后候选。它们不是当前可写名单；账号解除 suspension 后仍需当天 live preflight。`conditional` 表示缺证据就跳过，不是默认许可。

| 社区 | 适合的自然参与 | 评论路由 | 主帖路由 | 摩擦判断 |
|-|-|-|-|-|
| `r/alphaandbetausers` | 对真实可测试 build 的具体测试任务、复现步骤、UX 反馈 | 条件参与 | 条件主帖 | 中；需要真实 build 和清楚测试上下文 |
| `r/betatests` | 测试目标、平台差异、bug 复现 | 条件参与 | 条件主帖 | 中低；测试链接和任务必须真实 |
| `r/AppBetaTesters` | 互测经验、具体测试反馈 | 条件参与 | 条件主帖 | 中低；不能变成招募广告 |
| `r/AndroidClosedTesting` | Google closed testing 流程、测试反馈 | 条件参与 | 条件主帖 | 中；官方测试链路和账号资格要复核 |
| `r/TestMyApp` | 具体互测任务和结果 | 条件参与 | 条件主帖 | 中；不得 solicitation |
| `r/godot` | Godot 节点、脚本、渲染和开发取舍 | 条件参与 | 条件主帖 | 低到中；必须 Godot-specific |
| `r/threejs` | WebGL/WebGPU/Three.js 技术问题和 demo 反馈 | 条件参与 | 条件主帖 | 低到中；技术上下文优先 |
| `r/UnrealEngine` | UE 工具链、性能、原型问题 | 条件参与 | 条件主帖 | 中；不能把产品增长当技术帖 |
| `r/swift` | Swift/SwiftUI/Apple 开发问题 | 条件参与 | 条件主帖 | 低到中；只回答技术问题 |
| `r/visionosdev` | visionOS 设计、空间交互和开发取舍 | 条件参与 | 条件主帖 | 中；平台语境强 |
| `r/vrdev` | VR 开发挑战、空间交互和性能 | 条件参与 | 条件主帖 | 中；开发者语境强 |
| `r/ShowYourApp` | 有真实内容的展示和具体反馈问题 | 条件参与 | 条件主帖 | 中；展示不能退化为 CTA |
| `r/AppIdeas` | 无链接的想法反例、需求场景和概念杀伪 | default comment | conditional main post | 中高；产品/Loci mention closed，不能发完成项目 |
| `r/SideProject` | 项目过程、一个明确问题、真实技术取舍 | default comment | conditional main post | 中；拒绝 waitlist-only、纯链接和 AI 包装 |
| `r/roastmystartup` | 真实项目的具体 critique 请求 | default comment | conditional main post | 中高；禁止 Product Hunt/Vercel-only link 和 AI slop |
| `r/WebXR` | WebXR 原型、空间交互和技术问题 | default comment | conditional main post | 中；必须真实 WebXR，不能泛推广 |
| `r/Unity3D` | Unity 技术、flair 对应的问题和开发过程 | default comment | conditional main post | 中；不能只丢商店/下载链接 |
| `r/IndieDev` | 开发过程、工具、复盘和技术讨论 | default comment | conditional main post | 中；主帖需符合当前窗口/格式 |

这份 shortlist 只有 18 个，不把“15–30”当成数量指标硬凑。原因是最新路由已经把一批看似相关的社区关闭；把它们重新填回 shortlist 会直接违反当前规则底座。

## 需要继续降级的历史候选，以及与 gamedev 的共性

### 已明确降级为 research-only 或 outward closed

最新 override 明确把以下 16 个社区的普通评论路由置为 research-only：

`r/apps`、`r/betatesters`、`r/StartupSoloFounder`、`r/gamedesign`、`r/LEGOfortnite`、`r/gmod`、`r/StableDiffusion`、`r/collegeadvice`、`r/Entrepreneur`、`r/iosapps`、`r/CollegeRant`、`r/SaaS`、`r/startups`、`r/GradSchool`、`r/worldbuilding`、`r/vibecoding`。

另有 9 个社区评论为 conditional、主帖为 closed：`r/FlutterDev`、`r/reactjs`、`r/nextjs`、`r/iOSProgramming`、`r/webdev`、`r/web_design`、`r/playtesters`、`r/Notion`、`r/ObsidianMD`。这类社区不应作为日常养号或产品验证池；最多在未来恢复后，以完全非产品化、准确技术语境的评论人工判断。

上一轮 live 证据还支持把 `r/college`、`r/iosapps`、`r/CollegeRant`、`r/Entrepreneur`、`r/SaaS`、`r/startups`、`r/GradSchool`、`r/worldbuilding` 视作高摩擦或默认不访问。它们的问题不是单一一条规则，而是多重 gate 叠加：local karma、minimum karma、先有本社区活动、固定 weekly/megathread、modmail approval、AI/survey 禁止和强 topic purity。

### 和 gamedev 的共性

共性在治理结构，不在社区主题：

1. 都有大量开发者或项目方进入，self-promo 供给高，版主必须依赖 topic purity、低 effort 和 spam 判断降噪。
2. 都倾向 contribution-first：先回答问题、参与讨论、提供上下文，再允许项目展示；“我做了一个 app/游戏，来看看”通常不够。
3. 都可能把链接、下载、招募、调查、AI 生成内容或重复跨帖视为外部增长，而不是社区贡献。
4. survivor pattern 不能替代账号资格：某个项目帖存活，不代表新账号拥有 local karma、previous activity、flair 或 approval 权限。
5. 规则摩擦往往是动作级的：普通评论可能尚可，主帖可能只在 weekly thread、特定日期、特定 flair 或 approval 后开放。

关键差异：`r/gamedev` 还有确认的社区 ban、ban-evasion suspension 和历史 spam removal，因此是 Loci 组织级 permanent deny；其他高摩擦社区不是永久禁区，只有在 action override 明确 closed/research-only 时停止 outward，不能因为“像 gamedev”就自行新增 permanent deny。

## 本轮新增候选：只做人工复审，不自动升级

以下 29 个名称不在现有 144 行档案中。它们只代表方向覆盖，不代表已经读过规则或确认有评论入口。全部状态为 `pending_manual_review`；在未来同一账号、无 suspension、当天 live 复核前，不评论、不发帖、不投票、不 Join。

### 年轻人、轻社交、校园相邻

| 候选 | 公开搜索/方向信号 | 主要风险 | 暂定动作路由 |
|-|-|-|-|
| `r/GenZ` | 有大学、室友、交友和社会生活讨论 | 未成年人混杂、关系/心理健康、身份伪装风险；可能更像观察而非产品社区 | 人工复审；评论优先，主帖默认关闭 |
| `r/AskGenZ` | 名称级方向候选 | 年龄边界、调查/solicitation 风险、真实身份要求未确认 | 人工复审；无 live 证据不参与 |

### 创作、摄影、设计、动画、视频

| 候选 | 公开搜索/方向信号 | 主要风险 | 暂定动作路由 |
|-|-|-|-|
| `r/photography` | 公开结果显示工具、技术、艺术和主题讨论，并有 themed photo-sharing surfaces | 作品展示、自推、图片版权和地点隐私；规则/发帖窗口未在本轮复核 | 人工复审；若规则允许，先评论再考虑作品语境主帖 |
| `r/photographs` | 与摄影分享相邻的公开搜索结果 | 作品贴、版权、低 effort 和自推边界未知 | 人工复审；主帖关闭 |
| `r/graphic_design` | 公开讨论显示设计、视频、动画和 AI 对职业的交叉争议 | 作品展示、职业建议、AI 争议、自推污染 | 人工复审；技术/审美评论优先 |
| `r/animation` | 动画/作品流程方向候选 | 作品贴、版权、AI 内容和 critique 规则未确认 | 人工复审；主帖关闭 |
| `r/VideoEditing` | 视频制作与编辑方向候选 | 作品展示、软件推荐、素材版权和自推 | 人工复审；评论优先 |
| `r/AfterEffects` | 公开结果显示 motion design、视频和 AI 工具讨论 | showreel、商业服务、AI 生成内容、作品链接 | 人工复审；主帖关闭 |
| `r/Filmmakers` | 影视创作和制作流程方向候选 | 招募、商业服务、版权、项目宣传 | 人工复审；评论优先 |
| `r/ArtistLounge` | 艺术家交流方向候选 | AI、作品盗用、commission、自推和情绪支持边界 | 人工复审；不从脆弱语境导流 |
| `r/learnart` | 学习绘画和 critique 方向候选 | 年龄混杂、作品反馈和低 effort 边界 | 人工复审；真实学习问题评论优先 |

### 地点、旅行、真实世界玩法

| 候选 | 公开搜索/方向信号 | 主要风险 | 暂定动作路由 |
|-|-|-|-|
| `r/urbanexploration` | 城市空间探索方向候选 | 私闯、危险地点、地址暴露、人物/地标隐私 | 研究优先；主帖默认关闭，需人工安全复核 |
| `r/solotravel` | 旅行经验和路线讨论方向候选 | 真实地点暴露、诈骗、安全、旅行建议责任 | 人工复审；不分享可定位个人信息 |
| `r/travel` | 泛旅行讨论方向候选 | 低 effort 旅游帖、商业链接、个人行程和地点安全 | 人工复审；评论优先 |

现有池中的 `r/geocaching`、`r/hiking`、`r/walking` 不计入新增；它们是值得补 live 复核的方向候选，但本轮没有新账号核验，因此不能从历史档案自动升级。

### App、消费者科技、独立产品

| 候选 | 公开搜索/方向信号 | 主要风险 | 暂定动作路由 |
|-|-|-|-|
| `r/AndroidApps` | Android app 发现方向候选 | app promotion、下载链接、低质量推荐、affiliate | 人工复审；评论优先，主帖关闭 |
| `r/Android` | Android 用户体验和功能讨论方向候选 | support 规则、品牌争论、设备购买、自推 | 人工复审；只谈真实用户问题 |
| `r/ios` | 公开讨论包含平台独占 app 和小型 indie app 体验 | 大平台/品牌社区、重复比较、应用推广 | 人工复审；不把 Loci 当产品推荐 |
| `r/InternetIsBeautiful` | 发现有趣网站/互联网项目方向候选 | 纯链接、推广、重复提交、低 effort | 人工复审；必须有真实讨论价值 |
| `r/OpenSource` | 开源项目与协作方向候选 | 项目宣传、维护者招募、许可证、技术深度 | 人工复审；技术贡献优先 |
| `r/Tech` | 泛消费者科技讨论方向候选 | 新闻/链接、品牌和产品营销、主题漂移 | 研究优先；主帖关闭 |
| `r/consumertechnology` | 消费者科技方向候选 | 购买建议、品牌争论、营销和 affiliate | 人工复审；评论优先 |
| `r/IndieApp` | 独立 app 发现方向候选 | self-promo 密度高，可能是展示/广告池 | 研究优先；不得把名称级发现当发布许可 |
| `r/AppStoreOptimization` | ASO/独立开发者增长讨论方向候选 | 增长营销、服务销售、案例自推 | 研究优先；只在非品牌技术讨论中人工判断 |

### 泛娱乐、游戏化和共同创造

| 候选 | 公开搜索/方向信号 | 主要风险 | 暂定动作路由 |
|-|-|-|-|
| `r/BoardGames` | 共同规则、线下社交和玩法讨论方向候选 | 交易、众筹、设计自推、儿童/家庭语境 | 人工复审；真实玩法评论优先 |
| `r/Anime` | 泛娱乐、角色和虚拟身份方向候选 | 版权、低 effort、NSFW、粉丝争议和品牌借势 | 研究优先；不把 Loci 机制硬套进 fandom |
| `r/movies` | 叙事、地点和共同观看讨论方向候选 | 版权链接、泛争论、低 effort、品牌推广 | 研究优先；评论优先 |
| `r/music` | 音乐发现和共同文化讨论方向候选 | 自推、版权、推广、争议内容 | 研究优先；不发项目宣传 |
| `r/popheads` | 流行文化和社群讨论方向候选 | 粉圈冲突、版权、艺人/品牌营销、低 effort | 研究优先 |
| `r/television` | 影视讨论方向候选 | 版权、剧集争论、低 effort 和品牌借势 | 研究优先 |

## 条件参与、只读研究、不访问

### 条件参与

- 现有 18 个 shortlist 社区：只在 suspension 结束后、当天 live preflight 通过、账号没有 local karma/previous activity/approval 阻塞时，先做自然评论。
- 新增创作、摄影、户外和消费者科技候选：只有未来 live 看到普通评论入口清楚、没有产品/调查/AI/招募禁令、没有敏感安全边界时，才进入“人工复审后的评论候选”。
- `r/AppIdeas`、`r/SideProject`、`r/roastmystartup`、`r/WebXR`、`r/Unity3D`、`r/IndieDev`：评论与主帖严格分路由，主帖都需要内容和格式 preflight。

### 只读研究

- 最新 override 明确为 research-only 的 16 个社区：全部只提取用户语言、规则和痛点，不评论、不回复、不投票、不 Join、不发 Loci。
- 竞品/替代行为和敏感社区，包括 avatar、虚拟世界、心理健康、关系危机、真实地点识别等，默认只读，除非未来用户明确授权并有新的动作级复核。
- 本轮新增 29 个候选在 live 复核前全部只读/待人工复审；“公开搜索中有帖子”不改变这个状态。

### 默认不访问

- `r/gamedev`、`r/CozyGamers`：永久 deny，任何账号、任何 Loci 关联活动均不访问。
- 当前账号仍在 suspension：所有 Reddit 写操作和账号状态测试都不执行。
- 对有 local/community karma、minimum karma、previous activity、Request to Post、modmail approval、固定 megathread/周窗口、强制 flair 或严重自推/AI 禁令但未完成 live 复核的社区，默认不访问/不参与，而不是用历史 survivor 推断许可。

## 建议新增到 Skill 的社区与动作级路由

本轮不修改 Skill。若未来人工批准更新，建议采用“候选发现”和“可执行路由”分离的结构：

1. 新增候选先进入 `discovery_pending_live_review`，不直接进入 B/B+。
2. `ordinary_comment`、`main_post`、`product_mention` 分开记录；缺一项证据就不得自动放宽其他项。
3. 新增候选的默认值应为 `comment=conditional`、`main_post=closed`、`product_mention=closed`，直到当天规则页、置顶、New/Hot 和 submit composer 都被复核。
4. 只有连续看到普通用户评论存活、规则未要求 local karma/previous activity/approval、主题与 Loci 人设自然一致，才可从 pending 进入人工批准的 comment-first 候选。
5. 所有地点、校园、心理健康、关系危机、未成年人和竞品社区增加 `sensitive_risk` 字段；它不是内容热度的附属备注，而是独立 veto gate。
6. 记录 `verified_at`、`source_kind`（live Chrome / saved evidence / web search only）、`unconfirmed` 和 `failure_reason`；不能把 Web Search 或历史帖子写成 live confirmation。

## suspension 结束后的保守启动顺序（不执行）

1. 先确认账号 suspension 已结束，确认账号仍是预期账号；不使用新账号替代原账号来绕过限制。
2. 只从 shortlist 中挑一个低风险技术/创作社区，重新读取规则、置顶、New/Hot、评论入口和 submit 页面；任何 gate 不明就跳过。
3. 首周只做少量自然评论，内容必须直接回答当前问题，不带 Loci、链接、下载、招募、survey 或 CTA；记录是否被移除和是否出现 mod warning。
4. 观察一段时间无移除后，再逐个测试第二个社区；不跨大量社区复制同一措辞，不把评论当养号脚本。
5. 主帖与产品提及永远后置。只在有真实 build、清楚问题、明确技术/反馈语境且满足社区时间窗时考虑；新发现候选先不发主帖。
6. 任何 local/community karma、previous activity、Request to Post、approval、megathread、AI 禁止或不确定的账号状态出现，立即退回 conditional/research-only。

## 未确认项与覆盖计数

- 现有社区档案覆盖：144 个。
- 上一轮已保存的规则页 live 证据：78 个 B/B+ 社区。
- 上一轮已保存的 New/Top 完整 feed 证据：42 个；36 个未完全确认（18 个曾受 `ERR_BLOCKED_BY_CLIENT` 影响，18 个未完成）。
- 本轮通过公开搜索和本地交叉检查新增名称级候选：29 个；其中 8 个有公开搜索/帖子信号，21 个仅名称级候选。
- 本轮新增真实 Chrome 页面核验：0 个。
- 本轮新账号状态核验：0 个。
- 仍未确认：29 个新增候选的当前规则、账号年龄/Karma/local karma、previous activity、mod approval、New/Hot survivor、submit composer、评论/主帖真实权限；上一轮 36 个未完整 feed 的当日状态；部分旧社区的 local/community karma 精确数值。

## 公开搜索证据入口（仅用于发现，不是 live 版规证据）

- `r/GenZ` 交友/大学讨论：<https://www.reddit.com/r/GenZ/comments/1hnuuel/how_do_gen_z_meet_people/>
- `r/photography` 公开问答与摄影主题讨论：<https://pl.reddit.com/r/photography/comments/m5i9ke/official_question_thread_ask_rphotography/>
- `r/ios` 独立 app 体验讨论：<https://www.reddit.com/r/ios/comments/1ivbi6c/do_you_think_ios_has_better_platform-exclusive_apps/>
- `r/graphic_design` 设计、视频、动画和 AI 交叉讨论：<https://www.reddit.com/r/graphic_design/comments/1lxxxy0/video_editing_is_not_graphic_design/>
- `r/geocaching` 现实地点/户外玩法信号（既有档案，不计入新增）：<https://www.reddit.com/r/geocaching/comments/1aq2fok/geocaching/>
- `r/AfterEffects` motion design 和 AI 工具公开帖子：<https://en.reddit.com/r/AfterEffects/comments/1ujrzhh/i_created_a_product_explainer_video_to_present_my_motion_design_business/>
- `r/apps` 独立 app 使用讨论（既有档案中的 research-only 社区）：<https://www.reddit.com/r/apps/comments/1hmqlr4/are_there_any_indie_apps_you_use_regularly/>

本报告没有修改任何 Skill、reference 或账号状态；没有执行任何 Reddit 写操作。
