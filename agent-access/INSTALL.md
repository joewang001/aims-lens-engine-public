# Install AIMS Lens Skill

先在 [Portal](https://portal.aimslens.com) 的 **API & Skills** 申请 API。获批后，把这一句话发给你的 Agent：

```text
从 https://github.com/joewang001/aims-lens-engine-public 安装 AIMS Lens Skill。
```

First request API access in Portal → **API & Skills**. Once approved, send your agent:

```text
Install the AIMS Lens Skill from https://github.com/joewang001/aims-lens-engine-public
```

安装后按浏览器提示授权设备即可。 / Follow the browser prompt to authorize your device.

## For the installing agent

These are the steps for the agent, not a prompt the user needs to copy. Use the official native installer in the user's current existing project.

1. Read [the access guide](README.md) and [release manifest](downloads/release.json). Identify the actual host (`codex`, `deepseek-harness`, or `claude-code`) and operating system. Preserve the existing project, provider configuration and host sandbox/execution policy.
2. Check `https://portal.aimslens.com/v1/public-config`: `agent_onboarding_enabled` must be true before enrollment. If disabled, offer install-only and report that the API is unavailable; do not generate or submit credentials.
3. API approval precedes connection. If the user has not yet obtained institution approval, direct them to Portal → **API & Skills** and pause connection until approved. Do not ask them to repeat approval already established in the conversation.
4. Download [install.ps1](install.ps1) for Windows or [install.sh](install.sh) for macOS/Linux from this official repository. Verify its SHA-256 against the release manifest, then run it with the actual host in the current project. Python 3.10+ is required. Do not pipe a network response into a shell or install global dependencies. See the access guide for host compatibility and protected credential-store requirements.
5. For device consent, open the local browser and let the user confirm the institution, permissions and device code. Never request, print or paste an API key. Credentials are generated locally and protected by the OS store; no plaintext fallback.
6. Validate only capabilities and whoami using the installed setup flow. Report READY only after actual authenticated responses. Do not collect or upload workspace files during installation. If enrollment is pending, report it and resume with the same installer command.

Manual download and installer commands: [access guide](README.md).
