# Loci Reddit 社区动作级扩展审计

审计日期：2026-07-13（Asia/Shanghai）  
审计方式：公开 Web、公开 Reddit 社区页、公开 rules/sidebar/wiki、置顶和公开帖子；未使用当前 Chrome 新账号  
账号边界：原账号仍处于 sitewide suspension；Chrome 已切换其他账号，本轮不打开、不搜索、不刷新、不读取 Reddit Chrome 页面  
永久不访问：`r/gamedev`、`r/CozyGamers`。这两个社区不参与候选搜索、规则核验或动作评分。

## 结论先行

本轮形成 30 个新增候选。14 个完成了当前或近期的公开 Reddit 规则证据核验，3 个只有较旧或间接的公开规则信号，13 个仍只有名称/方向级发现；没有任何候选因为本轮公开 Web 核验而获得当前账号执行许可。

真正值得 suspension 结束后做 live preflight 的第一批是：`r/photocritique`、`r/ArtCrit`、`r/graphic_design`、`r/videography`、`r/photography`、`r/droidappshowcase`、`r/ShowMeYourApps` 和 `r/solotravel`。其中前五个更适合自然评论或具体作品/技术问题，后两个是产品展示区，摩擦更高；`r/solotravel` 只适合真实旅行讨论，不能承接 Loci 产品叙事。

反向结论同样重要：`r/androidapps`、`r/ArtistLounge`、`r/InternetIsBeautiful`、`r/ios` 的公开规则都把产品化、自推、AI 或低上下文内容挡在主区之外。它们可以产生自然用户语言，但不能因为活跃或相关就升级成产品运营池。

## 方法、状态和证据等级

### 优先级

动作判定顺序为：组织 denylist > 当前账号阻塞 > 最新 action override > 当前公开规则 > 公开活跃信号 > 历史档案。已被 `community-action-routing-overrides.md` 标为 `research-only` 或 `closed` 的社区不自动升级。

本报告使用三种证据状态：

- `public-rule-confirmed`：本轮从公开 Reddit 社区页的 rules/sidebar/wiki/置顶/公开 mod 说明中读到可用于动作判断的规则。
- `public-rule-signal`：有公开帖子或搜索索引中的 Reddit 规则/移除说明，但规则页不完整、较旧或当前性不足；仍需 live preflight。
- `name-only-pending`：只确认社区名称和方向，未确认当前规则、门槛、活跃度或发帖入口。

外部文章没有用于证明发布权限；公开 Web Search 只用于发现相邻社区和定位 Reddit 自身页面。

### 统计

| 项目 | 数量 |
|-|-:|
| 现有本地社区档案 | 144 |
| 本轮新增候选 | 30 |
| `public-rule-confirmed` | 14 |
| `public-rule-signal` | 3（较旧或间接信号，不冒充当前确认） |
| 仅名称级 pending | 13 |
| 本轮真实 Chrome 页面核验 | 0 |
| 本轮新账号状态核验 | 0 |
| 本轮 Reddit 写操作 | 0 |

公开规则页通常不显示某账号的 local/community karma、previous activity 或当前 submit eligibility。因此除明确写出门槛的社区外，其余账号门槛统一记为“未公开/待 Chrome live preflight”，不是“无门槛”。

## 参与优先 shortlist

这是“值得未来 live preflight”的顺序，不是当前可评论或发帖许可。所有候选都要等 suspension 结束、确认使用的是预期账号后，再当天读取规则、置顶、New/Hot 和 submit composer。

### 第一优先：低到中摩擦的真实评论入口

| 社区 | ordinary_comment | main_post | product_mention | 公开规则/活跃依据 | 适合话题 | 主要风险 |
|-|-|-|-|-|-|-|
| `r/photocritique` | conditional：评论必须是有深度的 genuine critique | conditional：只能发自己拍的一张照片，必须跟进意图和具体反馈问题 | closed | 公开社区页显示近期大量 approved 图片帖、Critique Point、New Queue；规则明确一帖一图、必须 follow-up critique、禁止自推 | 构图、光线、叙事、地点照片的隐私处理 | 不能只说“好看”；不能带 Loci/产品；照片中的人物和地点需谨慎 |
| `r/ArtCrit` | conditional：围绕技术和 craftsmanship 给具体反馈 | conditional：原创作品、具体 critique request；一天最多一帖 | closed | 公开规则明确 one post per day、不是分享/自推区、作品需原创且禁止 AI；公开页有持续颜色、构图、渲染问题帖和 Feedback Friday | 视觉层级、颜色、构图、空间叙事 | NSFW/自伤/争议图像需标签或禁止；不得把项目展示伪装成 critique |
| `r/graphic_design` | conditional：只回应设计问题和作品语境 | conditional：作品需绿色 Sharing Work flair、objective/audience/decision context | closed | 公开规则明确 no job/self-promo、no survey/poll、只限 graphic design、禁重度 AI、低 effort 和错误 flair；公开页有持续设计问题 | 信息层级、UI/视觉语言、设计取舍、设计工具实际问题 | topic purity 很强；AI 生成描述和 app/platform 推广容易被移除 |
| `r/videography` | conditional：设备、拍摄、后期的具体技术讨论 | conditional：帮助帖标题必须描述问题；相机购买只能进 monthly megathread | closed | 公开规则明确 no self-promotion/sales/advertising、market research/giveaway/crowdfunding；公开页有技术帮助和 BTS 帖 | 拍摄流程、镜头、色彩、真实地点取景的技术问题 | 商业产品只能先找 mod approval；地点/人物拍摄涉及同意和隐私 |
| `r/photography` | conditional：Technique/Gear/Workflow/Art 等真实问题 | conditional：技术/问题语境可考虑；作品分享受 themed thread、Self-Promotion Sunday 等窗口约束 | closed | 公开页有 Official Question、Anything Goes、Gear/Technique 等近期入口；公开移除说明禁止 advertising/self-promo/spam/survey，并有 manual review 和固定问题线程 | 摄影工作流、备份、地点观察、真实体验和器材选择 | 规则执行有人工审核；商业、调查、产品介绍和可定位地点需避开 |

### 第二优先：产品相关但必须接受较高摩擦

| 社区 | ordinary_comment | main_post | product_mention | 公开规则/活跃依据 | 适合话题 | 主要风险 |
|-|-|-|-|-|-|-|
| `r/droidappshowcase` | conditional：对具体 app 的 bug/UI/体验给建设性反馈 | conditional：专门的 Android app/game showcase | conditional | 公开规则明确 Android-only、模板/高质量、每账号每周 1 个 app、不得 cross-sub spam/affiliate；必须 direct reputable app link；要求账号至少 24h、2+ combined karma、verified email；公开页有 Promo/Giveaway 和反馈帖 | 真实可用 app 的 UI、地图/地点功能、具体 bug 和优缺点 | 1/周、链接白名单、SFW、账号门槛、promo-only 账号限制；Loci 只有在真实 build 且明确 app 语境才可能进入 |
| `r/ShowMeYourApps` | conditional：针对展示 app 的具体问题反馈 | conditional：社区目的就是移动 app 展示 | conditional | 公开规则为 Only promote mobile apps、Respect、No AI content；公开页有连续的 app showcase 和 feedback 讨论 | 已完成 app 的体验、定位、交互和用户理解 | 自推密度高、AI 禁止、产品叙事容易变广告；账号门槛和频率未公开 |
| `r/solotravel` | conditional：真实、具体、做过研究的旅行讨论 | conditional：必须 solo-specific、具体背景和研究；meetup/accommodation/泛新手问题进 weekly thread | closed | 公开规则明确 no self-promo/surveys/market research/app development，低 effort/FAQ/纯图片视频/独立外链会移除；公开页有近期路线规划和学生旅行问题；公开移除说明显示新账号可能进入 manual approval | 真实旅行决策、路线取舍、步行/公共交通体验、地点叙事 | 真实地点和安全风险；不能借“旅行 app”话题导流；账号年龄/人工审核可能阻塞主帖 |

这 8 个是“参与优先”，但不是“可直接操作”。其中 `r/photocritique` 和 `r/ArtCrit` 最适合建立自然兴趣画像；`r/droidappshowcase` 与 `r/ShowMeYourApps` 只适合已经存在的真实 app，不适合作为空泛的 Loci 介绍区。

## 条件参与

这些候选有公开规则信号或明确相邻性，但要先满足额外条件；缺证据就跳过。

| 社区 | ordinary_comment | main_post | product_mention | 条件和摩擦 |
|-|-|-|-|-|
| `r/ArtistLounge` | conditional：艺术技术/学习/材料讨论 | closed：主区 text discussion；图片、作品分享和交友主要走 megathread | closed | 公开规则明确 discussion-based、禁 self-promo、禁 survey/Discord/soliciting、art sharing 仅 megathread；评论可自然但必须非产品化 |
| `r/VideoEditing` | conditional：具体软件、工作流、技术求助 | conditional：Technical/Software/Workflow/Feedback 等准确 flair；Other 需 mod approval | closed | 公开 mod 移除说明明确 self-promotion 禁止，技术帖需模板信息；不能展示 YouTube/服务或做招募 |
| `r/AndroidApps` | conditional：普通 app 推荐、使用和 troubleshooting，不能评论自己的产品 | closed | closed | 当前公开规则明确 self-promotion、tester request、new app idea、app feedback 不允许；主区只保留讨论/推荐/排障，展示转 `r/droidappshowcase` |
| `r/ios` | conditional：iOS/iPadOS 软件讨论、真实使用问题 | conditional：必须 fostering reasonable discussion；开发者推广 app 需先 modmail | closed，除非未来明确 approval | 公开规则明确禁止开发者自推、博客/视频推广和 sketchy links；硬件支持、beta、电池等有专门去处/megathread |
| `r/InternetIsBeautiful` | conditional：普通网站讨论/评价，不把自己网站带入普通评论 | conditional：只能是独特、可直接使用、无需账号/下载/付费的网页 | closed | 公开规则明确禁聚合、低独特性、webgame、图片视频、商店/付费服务、个人信息、下载、AI 功能；90/10 self-promo 规则；产品化 Loci 页面大概率不合格 |
| `r/Anime` | conditional：anime-specific、日常讨论/推荐线程内的正常评论 | closed/conditional：至少 10 r/anime comment karma、flair、无 spoiler；大量主题进入 daily/meta thread | closed | 公开规则信号明确 10 local comment karma、flair、anime-only、禁 AI/非官方流媒体/低 effort；不适合 Loci 露出 |
| `r/BoardGames` | conditional：真实桌游规则、玩法、线下聚会经验 | conditional：产品/内容推广需满足 10:1 activity、每源每周最多一帖、sitewide karma>100 | closed | 公开规则/移除说明把社区定义为 community not audience，反低 effort、AI 和商业推广；桌游是共同创造研究场，不是 Loci 发布池 |
| `r/musicians` | conditional：合作、音乐制作和经验讨论 | closed | closed | 公开规则说明鼓励 collaboration，但禁 sales/self-promo/events/channels 和 AI-generated music；适合观察共同创作语言，不适合产品话题 |

## 评论可用但主帖关闭

这些候选即使未来 live 复核通过，也应默认保持 `ordinary_comment=conditional`、`main_post=closed`、`product_mention=closed`：

- `r/ArtistLounge`：只能讨论技法、材料、学习和艺术生活；不能把 Loci 的作品或 app 带入。
- `r/AndroidApps`：只能评论别人提出的 app 使用/推荐问题；不得评论自己的 app、测试请求或 feedback request。
- `r/ios`：只能做 iOS 语境内的普通使用讨论；产品推广要 modmail approval，当前不进入 Loci outward。
- `r/InternetIsBeautiful`：可讨论网页发现，但 Loci 页面必须同时满足独特、无需登录、无需下载、无 AI 驱动、无付费关键功能和 90/10 参与条件，现实上默认关闭。
- `r/musicians`：自然评论可以围绕合作/制作，但产品、活动或渠道推广关闭。

## 只读研究与默认不访问

### 本轮新增候选中的只读/高风险

| 社区 | 路由 | 原因 |
|-|-|-|
| `r/GenZ`、`r/AskGenZ` | research-only | 年龄混杂、校园/关系/心理健康语境敏感；普通身份和经历不能伪造，Loci 产品进入会像隐性调查 |
| `r/urbanexploration` | research-only | 私闯、危险地点、可定位地址、人物/私人财产隐私风险；当前规则未确认 |
| `r/movies` | research-only | 公开政策历史上对自推有 1:5/20% 规则、要求正常参与并禁止销售；当前规则版本和账号门槛未完整确认 |
| `r/music`、`r/television`、`r/popheads` | research-only | 名称级/间接规则证据，品牌、版权、粉圈和自推风险高；尚未完成当前公开规则核验 |
| `r/OpenSource` | research-only pending | 仅发现社区方向和间接公开规则信号；开源不等于可以推广自己的产品，当前 rules/wiki 未完成确认 |
| `r/animation`、`r/AfterEffects`、`r/Filmmakers`、`r/learnart` | research-only pending | 创作/作品社区相关，但本轮没有获得足够当前规则证据；先观察作品语言、AI、版权和自推边界 |
| `r/photographs`、`r/travel`、`r/Android` | research-only pending | 相邻性成立，但当前 rules、账号门槛、主帖入口和产品限制未完成确认 |

### 既有明确关闭边界

现行 `community-action-routing-overrides.md` 已关闭或 research-only 的社区不得自动升级，包括 `r/apps`、`r/betatesters`、`r/StartupSoloFounder`、`r/gamedesign`、`r/LEGOfortnite`、`r/gmod`、`r/StableDiffusion`、`r/collegeadvice`、`r/Entrepreneur`、`r/iosapps`、`r/CollegeRant`、`r/SaaS`、`r/startups`、`r/GradSchool`、`r/worldbuilding`、`r/vibecoding`，以及评论 conditional/主帖 closed 的技术和工具社区。它们可以继续作为研究对照，但不进入本轮新增 shortlist。

### 永久不访问

`r/gamedev` 和 `r/CozyGamers` 仍是组织级 permanent deny：不打开、不搜索、不读取、不测试、不投票、不 Join、不评论、不发帖。其他社区即使规则很严，也不能因此自动新增 permanent deny。

## 逐候选动作矩阵：未确认项和自然话题

以下 30 个新增候选都已做动作级记录。`pending` 不代表推荐，只代表未来可以在 suspension 结束后人工决定是否做 live preflight。

| subreddit | 方向/用户 | comment | post | product | 活跃/普通入口 | 门槛与格式 | 敏感/自推风险 | 证据状态 |
|-|-|-|-|-|-|-|-|-|
| `r/photography` | 摄影爱好者、技术和艺术讨论 | conditional | conditional | closed | Technique/Gear/Question/Anything Goes 入口明显 | self-promo、survey、manual review、固定线程；地点/人物隐私 | public-rule-confirmed |
| `r/photographs` | 摄影分享 | conditional | closed | closed | 由 photography 侧栏指向；当前活跃未核验 | 版权、图片、地点和作品分享门槛未确认 | name-only-pending |
| `r/graphic_design` | 设计师、学习者、作品反馈 | conditional | conditional | closed | 公开页有持续设计问题和 Sharing Work | green flair、context、no AI、no survey/poll、无商业推广 | public-rule-confirmed |
| `r/animation` | 动画创作者/学习者 | conditional | closed | closed | 名称级作品/流程方向 | AI、版权、showcase、自推和年龄边界未确认 | name-only-pending |
| `r/VideoEditing` | 剪辑学习者、软件/流程用户 | conditional | conditional | closed | 技术求助、Software、Workflow、Feedback 入口 | self-promo closed；flair/模板；Other 要 mod approval | public-rule-confirmed |
| `r/AfterEffects` | motion design/AE 用户 | conditional | closed | closed | 公开搜索有 motion/AI 工具讨论 | showreel、服务、AI、版权规则未确认 | name-only-pending |
| `r/Filmmakers` | 影视制作人 | conditional | closed | closed | 制作流程和器材方向 | 招募、商业项目、版权、项目宣传未确认 | name-only-pending |
| `r/ArtistLounge` | 艺术生活、材料、技法讨论 | conditional | closed | closed | 公开社区有术语、材料、软件 flair 和 megathreads | 禁自推、图片主帖、survey、Discord；禁止心理危机/doom 语境 | public-rule-confirmed |
| `r/learnart` | 学习者、练习和 critique | conditional | closed | closed | 公开搜索有 critique/练习帖 | 作品/年龄/低 effort/AI 规则未完整确认 | name-only-pending |
| `r/photocritique` | 摄影反馈者 | conditional | conditional | closed | 大量 approved 图片和 critique comments | 一图、follow-up、direct photo link、不得 karma whoring | public-rule-confirmed |
| `r/ArtCrit` | 数字/传统艺术 critique | conditional | conditional | closed | 持续 composition/color/rendering 讨论，含 weekly events | 一天一帖、原创、无 AI、具体 critique、NSFW tag | public-rule-confirmed |
| `r/videography` | 视频拍摄/器材/后期 | conditional | conditional | closed | Technical Help、BTS、Feedback 等入口 | 禁商业/调查/众筹；器材购买 monthly megathread；官方参与要 approval | public-rule-confirmed |
| `r/urbanexploration` | 城市空间探索者 | research-only pending | closed | closed | 名称级发现 | 私闯、危险、地点和私产隐私；规则未确认 | name-only-pending |
| `r/solotravel` | 独自旅行和路线规划 | conditional | conditional | closed | 近期有具体学生路线和预算讨论 | solo-only、做过研究、禁 FAQ/低 effort/产品/调查；weekly meetup | public-rule-confirmed |
| `r/travel` | 泛旅行用户 | research-only pending | closed | closed | 名称级方向 | 商业链接、地点安全、低 effort 和规则未确认 | name-only-pending |
| `r/AndroidApps` | Android app 用户/推荐者 | conditional | closed | closed | 公开页有 Looking For App 和 troubleshooting | 明确禁自推、tester request、new idea、app feedback；英文、官方链接 | public-rule-confirmed |
| `r/droidappshowcase` | Android app 创作者/反馈者 | conditional | conditional | conditional | 公开页连续 app showcase 和反馈 | 每周 1 app、24h、2+ karma、verified email、链接白名单、SFW | public-rule-confirmed |
| `r/ShowMeYourApps` | 移动 app 展示者 | conditional | conditional | conditional | 公开页持续展示/反馈帖 | only mobile apps、no AI；账号门槛/频率未公开 | public-rule-confirmed |
| `r/InternetIsBeautiful` | 网站发现者 | conditional | conditional | closed | 公开页有持续独特网站链接 | 禁登录/下载/付费/AI/聚合/低独特性；90/10 | public-rule-confirmed |
| `r/Android` | Android 用户/设备讨论 | conditional | closed | closed | 名称级消费者技术方向 | support、品牌争论、自推和规则未确认 | name-only-pending |
| `r/ios` | iOS/iPadOS 用户 | conditional | conditional | closed | 公开页有 app、软件、support、discussion | 讨论需有内容；开发者 app 推广需 modmail；硬件和 beta 分流 | public-rule-confirmed |
| `r/OpenSource` | FOSS 用户/维护者 | research-only pending | closed | closed | 名称级开发者/工具方向 | 开源项目仍可能是 self-promo；官方 current rules 未确认 | name-only-pending |
| `r/BoardGames` | 桌游玩家和线下游戏群体 | conditional | conditional | closed | 公开帖有规则、社交和玩法问题 | community not audience；10:1 promotion、每周一次、karma>100；AI/低 effort | public-rule-signal |
| `r/Anime` | 动漫用户 | conditional | closed | closed | daily discussion、recommendation、meta 入口 | 10 local comment karma、flair、spoiler、AI/外链/低 effort 禁令 | public-rule-confirmed |
| `r/movies` | 电影讨论者 | research-only | closed | closed | 公开历史规则和内容信号 | 旧版 1:5/20% self-promo、正常参与、禁销售；当前版本未确认 | public-rule-signal |
| `r/music` | 音乐听众 | research-only pending | closed | closed | 名称级发现 | 自推/版权/推广和规则未确认 | name-only-pending |
| `r/television` | 影视观众 | research-only pending | closed | closed | 名称级发现 | 版权、品牌、低 effort 和规则未确认 | name-only-pending |
| `r/GenZ` | 年轻人、校园/社交话题 | research-only | closed | closed | 公开搜索有大学、室友、社交讨论 | 未成年人、心理健康、关系和身份真实性风险 | name-only-pending |
| `r/AskGenZ` | 年龄层问答 | research-only | closed | closed | 名称级发现 | 年龄/调查/身份/关系风险，规则未确认 | name-only-pending |
| `r/musicians` | 音乐创作与协作 | conditional | closed | closed | 公开规则鼓励 collaboration | 禁销售、自推、活动/频道推广、AI music | public-rule-signal |

## 账号门槛与审核机制汇总

本轮公开证据确认了以下具体 gate：

- `r/droidappshowcase`：账号至少 24 小时、2+ combined karma、verified email；每账号每周最多 1 个 app showcase；直接 app link 和 approved domain。
- `r/anime`：发帖需要 10 comment karma from r/anime、flair、anime-specific 内容；很多内容进 daily/meta/merch megathread。
- `r/BoardGames`：公开规则说明推广内容需要 10:1 activity、单一来源每 7 天最多一帖、sitewide karma>100。
- `r/solotravel`：公开移除说明显示小于 48 小时账号可能进入人工审核；FAQ、低 effort、泛社交/meetup 进入 wiki 或 weekly thread。
- `r/photography`：公开移除说明显示 spam prevention manual review；常见器材/价格问题进入固定问题线程。
- `r/videography`：器材购买进入 monthly megathread；商业产品参与需 mod approval；帮助帖标题必须描述具体问题。
- `r/ArtistLounge`：图片/作品和交友进入 megathread，主区 text-only discussion；禁止 self-promo、survey、Discord、soliciting。
- `r/graphic_design`：Sharing Work flair、作品 context、英文/设计主题、禁 AI/调查/低 effort。

未确认项仍包括多数社区的当前 local/community karma、账号年龄、previous activity、comment-only restrictions、submit composer、当前 New/Hot 频率和 mod approval。公开规则缺失时，动作矩阵保持 conservative pending。

## 建议同步进 Skill 的动作级新增行（不执行、不修改）

建议未来人工审批时增加以下 rows，而不是只增加 subreddit 名字：

```text
r/photocritique
  ordinary_comment=conditional
  main_post=conditional
  product_mention=closed
  gate=one_original_photo;follow_up_intent_and_specific_critique;direct_photo_link;no_self_promo

r/ArtCrit
  ordinary_comment=conditional
  main_post=conditional
  product_mention=closed
  gate=one_post_per_day;original_art;specific_critique;no_AI;NSFW_tag_when_needed

r/graphic_design
  ordinary_comment=conditional
  main_post=conditional
  product_mention=closed
  gate=green_Sharing_Work_flair;objective_audience_context;design-only;no_AI;no_survey_poll

r/videography
  ordinary_comment=conditional
  main_post=conditional
  product_mention=closed
  gate=descriptive_title;camera_buying_monthly_megathread;no_self_promo;mod_approval_for_official_commercial_participation

r/droidappshowcase
  ordinary_comment=conditional
  main_post=conditional
  product_mention=conditional
  gate=Android_only;one_app_post_per_week;age_24h;combined_karma_2;verified_email;approved_link;no_AI_or_affiliate

r/androidapps
  ordinary_comment=conditional
  main_post=closed
  product_mention=closed
  gate=no_self_promo;no_tester_request;no_new_app_idea;no_app_feedback;redirect_showcase_to_droidappshowcase
```

对其余 24 个候选建议先写入 `pending_review`，不要直接进入 B/B+。动作级字段必须保持 `ordinary_comment`、`main_post`、`product_mention` 三列独立；缺少其中一列证据不能放宽另外两列。

## Suspension 结束后的 live preflight 顺序（不执行）

1. 先确认原账号 suspension 已结束、账号身份正确；不能用新账号绕过 suspension 或制造关联活动。
2. 第一批只核验 `r/photocritique`、`r/ArtCrit`、`r/graphic_design`、`r/videography`，读取当天规则、置顶、New/Hot、submit composer、账号门槛；任一 gate 未确认就不动作。
3. 若 live 证据一致，先做少量真实技术/作品 critique 评论；评论必须直接回应当前帖子，不带 Loci、链接、下载、调查、招募或 CTA。
4. 第二批才检查 `r/photography`、`r/solotravel` 和 `r/droidappshowcase`。主帖和产品提及永远后置，只有真实内容和明确社区语境才考虑。
5. `r/ShowMeYourApps` 只有在真实 app 已完成、能接受具体反馈且符合当前 AI/频率/链接规则时才进入人工判断；不把它当冷启动广告区。
6. 任何 local karma、previous activity、Request to Post、mod approval、megathread-only、AI 禁止、敏感地点或隐私风险出现，立即退回 conditional/closed。

## 未确认项与报告路径

- 本轮新增候选总数：30。
- 完成当前/近期公开 Reddit 规则证据：14。
- 较旧或间接规则信号：3。
- 仅名称级发现：13。
- 本轮真实 Chrome live preflight：0；新账号状态读取：0。
- 公开规则不能证明当前账号具备发帖资格；所有账号年龄、总 Karma、local/community karma、previous activity 和当前 suspension 结束状态都要等未来同一账号 live preflight。
- 本轮没有修改任何 Skill/reference，没有执行 Reddit 写操作。

报告路径：`/Users/lishehao/Documents/Codex/2026-07-06/chrome/reddit-community-action-expansion-audit-2026-07-13.md`

## 公开 Reddit 证据入口

- [r/photocritique 公开社区页与完整规则](https://www.reddit.com/r/photocritique/)
- [r/ArtCrit 公开社区页与规则/weekly events](https://www.reddit.com/r/ArtCrit/)
- [r/graphic_design 公开社区页与规则](https://www.reddit.com/r/graphic_design/)
- [r/videography 公开社区页与规则](https://www.reddit.com/r/videography/)
- [r/ArtistLounge 公开社区页与规则](https://www.reddit.com/r/ArtistLounge/)
- [r/photography 公开社区页与近期问题/固定线程](https://www.reddit.com/r/photography/)
- [r/solotravel 公开社区页与规则/wiki](https://www.reddit.com/r/solotravel/)
- [r/androidapps 公开社区页与当前规则](https://www.reddit.com/r/androidapps/)
- [r/droidappshowcase 公开社区页与当前规则](https://www.reddit.com/r/droidappshowcase/)
- [r/ShowMeYourApps 公开社区页与规则](https://www.reddit.com/r/ShowMeYourApps/)
- [r/InternetIsBeautiful 公开社区页与规则](https://www.reddit.com/r/InternetIsBeautiful/)
- [r/ios 公开社区页与规则](https://www.reddit.com/r/ios/)
- [r/anime 规则/megathread 公开帖子](https://www.reddit.com/r/anime/comments/1t2r7f4/meta_thread_month_of_may_03_2026/)
- [r/movies self-promotion 公开版规说明](https://www.reddit.com/r/movies/comments/nhxy1n/)
- [r/boardgames promotion/participation 公开规则信号](https://www.reddit.com/r/boardgames/comments/1s3pxea/)
- [r/musicians 公开规则说明](https://www.reddit.com/r/musicians/comments/1lwqil9/introducing_rmusicians_community_rules_finally/)
