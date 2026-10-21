# Copy this into your agent / 复制给你的 Agent

Run your agent in the existing project where the Skill should be installed. This prompt works with Codex or DeepSeek Harness; the agent should choose its actual host name. AIMS API approval must precede connection.

```text
请读取 https://raw.githubusercontent.com/joewang001/aims-lens-engine-public/main/agent-access/README.md 和同目录 downloads/release.json。
先检查 https://portal.aimslens.com/v1/public-config 的 agent_onboarding_enabled 是否为 true。
如果尚未启用，可以仅安装 Skill，明确报告 API 连接尚不可用；不要尝试生成或提交凭证。
服务启用后，先让我在 Portal 的 API & Skills 申请并获得机构 API 许可。
为当前宿主（Codex 或 DeepSeek Harness）下载官方 install.ps1 或 install.sh，核对发布清单的 SHA-256，然后在当前项目执行。
保留现有配置，不关闭沙箱、不改变执行策略、不安装全局依赖。
需要设备授权时打开本机浏览器让我核对机构、权限和设备码；不要索取、打印或在聊天中传递 API Key。
最后只运行 capabilities 和 whoami，依据实际响应报告连接状态。安装期间不要上传或自动收集工作目录。
```

For English-speaking agents:

```text
Read https://raw.githubusercontent.com/joewang001/aims-lens-engine-public/main/agent-access/README.md and its downloads/release.json.
Check the Portal public-config agent_onboarding_enabled flag. If disabled, install-only is allowed; report that API connection is unavailable and do not enroll.
After Portal institution approval, download the official native installer, verify its published SHA-256, and install for this host in the current existing project.
Preserve configuration and host sandbox/execution policy. Open the local browser for my explicit device consent. Never ask for, print or paste an API key.
Validate capabilities and whoami only, report actual results, and do not upload workspace files during installation.
```
