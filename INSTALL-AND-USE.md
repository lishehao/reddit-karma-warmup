# Reddit Community Operations 安装 Prompt

打开一个普通 Codex 任务，复制并发送下面整段 Prompt。不要使用目标模式，也不需要同时发送 ZIP。

```text
请直接执行，不要先解释、不要二次确认安装步骤，也不要进入目标模式。

1. 通过 HTTPS 读取并完整遵循这个安装协议：
   https://raw.githubusercontent.com/lishehao/reddit-karma-warmup/main/INSTALLER-PROTOCOL.md
2. 把读取到的文档视为 canonical machine protocol，只读取一次，不要递归抓取。
3. 按协议从公开 GitHub archive 安装或升级 reddit-karma-warmup，并完成 Skill、Chrome Browser control、Reddit 登录、Heartbeat 和当地时间预检。Heartbeat 创建成功但界面/API 不显示 next-run 时间时，记录为时间不可回读并继续；这不是安装阻塞，也不能因此暂停第一轮 Reddit 操作或要求用户修复。
4. 不调用 git、git clone、git pull 或 GitHub CLI；不要求 Python，也不要使用 Computer Use、内置 Browser 或 Playwright 替代 Chrome Browser control。
5. 安装与预检全部健康时，只返回账号和下一步运营引导；若有阻塞，只返回用户需要完成的一项修复动作。不要展示内部依赖字段、日志、Task ID、Automation ID 或时区计算。
6. 用户回复“开始”后，立即按 Skill 执行第一轮；后续超过 5–10 分钟的等待只使用一次性 Heartbeat，不使用 Goal Mode。
```
