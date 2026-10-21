# Install and connect

The official Portal **API & Skills** page guides the user through application, installation and local browser consent. Use its reviewed, fixed-version installer and digest; do not invent a download URL or assume access is enabled by installing the Skill.

From a verified extracted distribution, the shared entry is `python setup.py --host codex --project-root <project>` (DSH: `deepseek-harness`; Claude: `claude-code`). It installs only the selected host, opens local browser consent, persists the locally generated machine key in protected OS storage and validates capabilities/whoami. The server receives the key's digest rather than its plaintext. The proof-bound enrollment is an AIMS-specific protocol, not general OAuth.

Use only the approved institution and permissions shown in the browser. Match the device code before consenting. Never ask for a key in chat. `AUTHORIZATION_PENDING` resumes using the same command and saved request. Errors or pending authorization are not READY. `--install-only` installs without a credential; `--status` rechecks the saved identity. A pending request can be cancelled with `--cancel`; the worker acknowledges revocation before it is complete.

After Portal revocation is acknowledged or an enrollment is declined/cancelled/expired, `--reconnect` starts a fresh browser consent. It refuses to replace an active credential or a still-pending authorization. Do not delete saved state to bypass reconciliation. A connected project can install for another supported host using the same protected machine identity; it does not mint another key.

An existing different Skill version is preserved by default. Explicit `--upgrade` stages and verifies the new files, keeps the old folder under ignored `.aims-lens/skill-backups/` outside Skill discovery, and restores it if publishing the new folder fails. Existing linked installations are refused. The shell entry uses the same flags; PowerShell exposes `-Upgrade` and `-Reconnect`.

Example after connection, paths resolved to the installed Skill:

```shell
python scripts/aims_setup.py --status
python scripts/aims_setup.py --run capabilities --execute
python scripts/aims_setup.py --run whoami --execute
```

The setup uses the current working project by default; pass `--project-root` before `--run` when running elsewhere. The API command's body, resource and persistent operation-key options follow `--run`. The origin is bound to the OS-protected connection and cannot be overridden by operation arguments.

Windows uses per-user DPAPI-protected storage; macOS uses Keychain; Linux requires an existing Secret Service (`secret-tool`). No plaintext fallback or automatic global runtime installation occurs. A missing dependency, permission denial or unsupported local UI must be reported. Do not bypass the sandbox, change execution policy, expose environment variables or read other user configuration to proceed.

Initial setup performs only capabilities/whoami. Uploads and all writes require the user's separate task authorization and persistent idempotency keys. Installation does not authorize workspace scanning, collection or continuous synchronization.
