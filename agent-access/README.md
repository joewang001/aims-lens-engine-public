# AIMS Agent Access / AI Agent 接入

[简体中文](#三步接入) · [English](#connect-your-agent) · [Install prompt](INSTALL.md) · [Downloads](downloads/)

Connect Codex, DeepSeek Harness or Claude Code to the hosted AIMS Lens Builder through one portable Skill. Python 3.10+ is required. The hosted API is separate from the public core; installing this Skill does not enable a hosted account.

## 三步接入

1. **申请 API**：打开 [Portal](https://portal.aimslens.com)，以已验证的机构管理员账号登录，在 **API & Skills** 填写一句话用途。审批后查看岗位范围与有效期。如果菜单尚未出现，表示生产接入尚未激活。
2. **安装 Skill**：把 [安装提示词](INSTALL.md) 复制给 Codex / DSH，或下载一个安装文件： [Windows](https://raw.githubusercontent.com/joewang001/aims-lens-engine-public/main/agent-access/install.ps1) · [macOS / Linux](https://raw.githubusercontent.com/joewang001/aims-lens-engine-public/main/agent-access/install.sh) · [Skill ZIP](https://github.com/joewang001/aims-lens-engine-public/raw/refs/heads/main/agent-access/downloads/aims-lens-agent-access-0.1.0.zip)。在已有项目目录运行。
3. **确认连接**：核对浏览器显示的机构、权限和设备码后授权。安装器取得 capabilities / whoami 的实际响应后才显示 READY。安装期间不上传工作目录。

不需要编辑 JSON、设置 Key 环境变量或把 Key 粘贴到聊天。凭证在本机生成并由系统存储保护。批准是机构级 API 访问许可，每台设备另行授权；凭证可以在 Portal 撤销。

## Connect your agent

Request access as a verified organization administrator in Portal → API & Skills. After approval, use [the install prompt](INSTALL.md) or run a downloaded installer from an existing project:

```sh
sh install.sh --host codex
# DeepSeek Harness: --host deepseek-harness
```

```powershell
.\install.ps1 -HostName codex
# DeepSeek Harness: -HostName deepseek-harness
```

Download files first; do not pipe network responses into a shell. Compare SHA-256 with [the download manifest](downloads/SHA256SUMS.txt). Optional `--install-only` / `-InstallOnly` installs without connecting. A disabled hosted service reports SERVICE_NOT_ENABLED, never READY. Re-run the same command to resume an authorization request. Explicit upgrades use --upgrade / -Upgrade and preserve a backup outside host discovery.

## Current compatibility

- Windows native installer, Codex Desktop tools, and DeepSeek Harness headless with an existing local model: actual authenticated capabilities/whoami verified in isolated acceptance.
- Codex CLI Windows workspace-write: protected credential access remains unavailable; use a supported credential integration when available. Do not disable its sandbox or copy secrets into the project.
- Claude Code model execution and native macOS/Linux credential stores require separate acceptance. Install-only is available without credentials.

Windows uses DPAPI, macOS uses Keychain, Linux requires an existing Secret Service (`secret-tool`). No plaintext fallback or global provider/account changes. Model authentication belongs to the host and is separate from AIMS authorization.

## Scope and contract

The [Skill](skills/aims-lens/SKILL.md) and [wire contract](skills/aims-lens/references/openapi.json) cover authorized source preparation, immutable Submission freeze, deterministic Lens building and exact-version retrieval. All writes require persisted idempotency keys and provenance. Initial setup only reads connection status. No Lens activation, candidate processing or claim of JD body parsing is added.

[Reproducible packaging](../tools/package_agent_access.py) builds the small ZIP from the reviewed source in this directory; the download manifest pins every package file and generated entrypoint. The API runtime, approvals, owner operations, credentials and institution materials are outside this public distribution.
