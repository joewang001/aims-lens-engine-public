# AIMS Agent Access API Contract v0.1

契约版本：`0.1.0-draft.2`。日期：2026-10-20（America/Toronto）。状态：**私有后端已实现，尚未部署**。OpenAPI 为字段与响应结构真源；本文规定事务、授权和历史语义。若二者冲突，阻止发布并修正，不由客户端猜测。相对 draft.1，读取既有 Portal 提交时 `handoff_status` 允许真实的 `requested` 状态；Agent Access 新冻结的提交仍为 `not_requested`。

## 1. 产品边界与版本

浏览器 Portal 与第三方 agent 共用服务端业务能力；新增 `/agent/v1` 适配层，不让 agent 自动操作网页。候选生产 origin 为 `https://portal.aimslens.com`。不复用其他产品的域名、用户、Cookie 或凭证；平台管理员身份也不等同于租户机器身份。

Builder v0.1 的冻结、不可变快照、Lens Object schema `0.1`、builder `0.1.0-rules` 和 policy `0.1` 不因本包而改变。API version、skill version、Lens schema version、builder version 分开管理。新增认证/适配器单独评审、迁移、部署和验收。未重新执行 POST_SMOKE_READY，不将 Builder 标为正式 Frozen。

首版范围：创建岗位、保存岗位资料、保存结构化招聘输入、冻结 Submission、同步构建、读取具体 Lens 版本。不提供激活、候选人处理、JD 正文解析、任意数据库操作、账户注册或自动付费接口。组织通用资料可由已有 Portal 预先管理；本阶段只开放岗位资料写入。冻结时仍须按既有规则包含该机构适用的通用资料。

## 2. 机器身份与凭证

`Authorization: Bearer <opaque_machine_key>`，与现有登录 Session token 分开存储、验证和撤销。机器密钥是机构拥有的 service principal，不是平台管理员，也不是自由填写的 user_id。

当前发放通过受控服务端管理命令完成：校验在职、已验证邮箱的机构管理员，明确机构、可访问岗位范围、scopes、到期时间和用途。明文密钥仅写入新建、权限 0600 的文件；stdout 不输出密钥。服务端保存不可逆校验值与非秘密 key_id。默认有效期 30 天，最长 90 天；支持立即撤销和重叠轮换。分发包不提供该管理命令。不允许把明文密钥交给 LLM 提示词；harness secret store 注入环境变量即可。

每次请求检查密钥有效性、principal/机构状态、当前授权、scope 和资源归属。撤销后下一次请求即失效。tenant/actor 从认证上下文确定，载荷中出现组织、调用者或授权字段一律拒绝。每个机器 principal 有独立服务账号 ID，与人类账号不混用；该账号没有网页登录 membership 或 Session。Snapshot 和原有审计的 actor 使用真实服务账号，独立 Agent Access 审计补充 principal/key_id 和发放授权者。不重写历史 Snapshot 或 Lens。

| Scope | 能力 |
|---|---|
| `roles:read` / `roles:write` | 读取 / 创建岗位 |
| `materials:write` | 写入岗位资料 |
| `hiring-inputs:write` | 写入 directives / interview items / rubrics |
| `submissions:write` / `submissions:read` | 冻结 / 读取提交摘要 |
| `lenses:build` / `lenses:read` | 构建 / 读取 Lens |

capabilities 和 me 需要有效机器身份。scope 不替代租户/岗位 ACL；非本租户或不在授权岗位集合中的资源返回 404，不泄漏是否存在。本租户资源但缺少操作 scope 返回 403。构建同时验证原有业务写权限，读取 Lens 保留 reviewer_only 数据访问边界；若不能安全返回完整 Lens，拒绝请求，不能裁剪 Lens 后沿用原哈希。

## 3. 传输和响应

HTTPS，JSON UTF-8；文件接口使用 multipart/form-data。返回 `Cache-Control: no-store`、`X-Request-ID`，每个响应包装为 `{request_id, data}` 或 `{request_id, error:{code,message,retryable,details}}`。错误中不含密钥、原始正文、内部路径或 SQL。鉴权失败返回 401 和 `WWW-Authenticate: Bearer`。

`GET /capabilities` 返回契约版本、允许的 operations（与 OpenAPI operationId 一致）、builder/policy/schema 版本、最大上传字节数与边界标志。operations 只列当前 principal 可用能力。客户端执行操作前探测该响应；未实现接口、契约不匹配或能力关闭必须停止，不退回 `/v1` 登录接口。capabilities 是发现提示；每次业务请求仍独立鉴权。

所有写操作要求 `Idempotency-Key`，8–128 个 `[A-Za-z0-9._:-]` 字符。以机构 + principal + method + 模板路径及实际资源参数 + key 为隔离域；以规范化 JSON 或 multipart 元数据和文件 SHA-256 计算 payload digest。同键同请求重放原来的 HTTP 状态和响应正文（原 request_id），并返回 `Idempotency-Replayed: true`；同键异请求返回 409。不同租户/主体的键不会互相重放。

记录与业务变更必须原子提交；崩溃重试不能产生第二个 Submission。并发同键返回 `IDEMPOTENCY_IN_PROGRESS`（409 / Retry-After），完成后重试原键。鉴权/校验失败无需占用 key；已提交结果至少保留 7 天，实际过期时间通过 `Idempotency-Key-Expires-At` 响应头返回；超期结果不明时停止并由操作者查证，不盲目换 key 重试。构建还须沿用现有 build fingerprint 去重，不能把幂等键当作重建策略。

所有写入前读取并验证资源归属。新 source_revision 只能追加未来状态，不修改过去提交。freeze 的 revision 检查、资料哈希验证、快照生成、审计和幂等结果必须在同一串行化事务边界内完成，不能先独立比较 revision 再创建提交。岗位和机构资料变更均须参加相同的锁/并发控制。

## 4. 端点

所有路径以下表相对 `/agent/v1` 解释。首版同步构建，不创建虚构异步任务、不要求轮询。

| 方法 / 路径 | operationId | 结果 |
|---|---|---|
| GET `/capabilities` | capabilities | 可用操作与固定版本 |
| GET `/me` | whoami | 当前 principal、机构、scope、授权岗位范围与过期时间 |
| POST `/roles` | role-create | 新岗位 ID 和 source_revision |
| GET `/roles/{role_id}` | role-get | 岗位摘要、当前 revision 与资料引用 |
| POST `/roles/{role_id}/materials/text` | material-text | 文档版本引用、哈希、正文未解析标志 |
| POST `/roles/{role_id}/materials/url` | material-url | URL 引用版本；不抓取网页正文 |
| POST `/roles/{role_id}/materials/file` | material-file | 上传文件版本、哈希、安全扫描状态 |
| POST `/roles/{role_id}/directives` | directive-create | 结构化输入引用与新 revision |
| POST `/roles/{role_id}/interview-items` | interview-create | 同上 |
| POST `/roles/{role_id}/rubrics` | rubric-create | 同上；仅评分标准，不含候选人评分 |
| POST `/roles/{role_id}/submissions` | submission-freeze | 不可变提交引用、source_revision、snapshot 哈希 |
| GET `/submissions/{submission_id}` | submission-get | 同一冻结提交的摘要 |
| POST `/submissions/{submission_id}/lens-builds` | lens-build | 完整 Lens Object、其 SHA-256、reused 标志 |
| GET `/lenses/{lens_id}/versions/{lens_version}` | lens-get | 指定版本及其 SHA-256 |

输入 schema 采取 `additionalProperties:false`。示例只作合成使用，ID 以实际响应为准。服务端必须递归拒绝候选人字段；自由文本和二进制内容不能靠字段名扫描证明无候选人数据，材料授权和现有上传控制仍是必要条件。

上传上限 8 MiB；类型仅 PDF、DOCX、TXT。客户端 MIME 只是提示，服务端必须检查文件签名、解压风险和恶意内容，返回 `accepted` 才能进入冻结资料；扫描未完成返回 409 `MATERIAL_NOT_READY`，不能以“上传成功”绕过扫描。文件 SHA-256 由客户端提交且服务端独立计算比较。TEXT 内容按原始 UTF-8 字节计入哈希；URL 只作为引用，遵循现有版本与哈希规则，不引入抓取功能。文件本地路径不会作为服务器 storage_ref。

结构化输入增加独立的 `provenance`：`employer_provided` 或 `agent_extracted`。后者必填 source_document_version_ids 和 extractor；冻结时必须验证这些版本属于该快照的岗位/机构并已固定。provenance 保存于 Agent Access 追加记录中，与输入 ID / Submission 关联，不向冻结 v0.1 schema 塞入额外字段。首版 Lens 内既有 evidence refs 保持不变；新增 provenance 通过独立审计查询或后续明确版本提供，不伪称已在 Lens 内编码。

freeze 必填 `expected_source_revision`。至少存在当前 JOB_POSTING 或 JOB_DESCRIPTION，所有被固定资料通过既有哈希与路径验证。legacy submission 没有快照时 `SNAPSHOT_MISSING`，不得回填当前岗位。响应 `snapshot_status=frozen` 与原 Portal 的 processing/ready 状态是不同维度；此 API 不许把冻结等同于 onboarding 完成。默认不触发既有网页提交路线的 onboarding handoff：新增适配器调用快照服务，并明确记录交接尚未请求。

build 必填 `expected_snapshot_sha256`。只调用该 Submission 的冻结契约，固定 builder/policy 版本。若已有 fingerprint 对应的产物，原样返回；不生成新版本。新构建产生 `validated` 产物并返回 `reused=false`。不存在自动激活、覆盖、删除或重新分配历史 Lens 版本。原始 Lens JSON 不增加 envelope 字段；哈希沿用既有 `canonical_json` / `digest`，不能换另一种 JSON canonicalization 算法。

客户端校验响应 envelope、固定版本、来源 ID / hash、状态、核心边界及 Lens 摘要；真正的 schema/证据验证由服务端现有 validator 执行。客户端对 JSON 重编码不构成所有 Unicode/数字边界下的独立哈希证明，必要时在受控 Python 环境使用现有 canonical_json 验证器。

## 5. 错误、重试、配额和审计

| HTTP | code | 处理 |
|---|---|---|
| 400 | INVALID_REQUEST / CANDIDATE_DATA_PROHIBITED | 修正输入，停止自动重试 |
| 401 | UNAUTHENTICATED | 由拥有者检查过期/撤销；禁止自动登录 |
| 403 | INSUFFICIENT_SCOPE | 由拥有者调整授权；不自动扩权 |
| 404 | NOT_FOUND | 对隐藏或缺失资源同样响应 |
| 409 | SOURCE_REVISION_CONFLICT / SNAPSHOT_HASH_MISMATCH / SNAPSHOT_MISSING | 重新核对来源；不能改用 live role |
| 409 | IDEMPOTENCY_CONFLICT | 同键异请求，停止 |
| 409 | IDEMPOTENCY_IN_PROGRESS / MATERIAL_NOT_READY | 依 Retry-After 有界重试原请求 |
| 413 / 415 | PAYLOAD_TOO_LARGE / UNSUPPORTED_MEDIA_TYPE | 修正文件 |
| 422 | VALIDATION_FAILED | 按 details 字段修正输入 |
| 429 | RATE_LIMITED | 按 Retry-After 等待；使用原 key |
| 503 | SERVICE_UNAVAILABLE | 最多由 harness 重试两次，使用原 key |

初始 pilot：每 principal 60 次/分钟，构建 5 次/分钟，机构同时最多 1 个构建；429 含 Retry-After 秒数。客户端本身不自动重试。无效 JSON/HTML（包括反向代理错误页）输出标准本地错误，不能当业务结果继续。请求 timeout 或网络断开表示写结果未知，保留 key，不能宣称写入失败或自动创建新请求。

本版本不提供计费或付费动作；额度/费用商业规则未冻结。收费上线前必须补齐计量定义、预算上限及用户可见消费信息。幂等重放不能重复计量。

审计至少记录 request_id、organization_id、principal_id、key_id、操作、资源、结果、revision、snapshot hash / fingerprint、时间、幂等摘要；禁止记录 Authorization 或默认记录资料正文。未来统一审计接收这些事件，但此包不实现平台管理系统。

## 6. 实现适配清单与验收门槛

私有后端已实现机器身份/发放/撤销、每资源授权、稳定错误映射、事务性幂等、revision 并发检查、上传控制、provenance 关联、capabilities 和 HTTP 路由。生产尚未启用；隔离环境、目标数据库版本与生产验收分别记录，不能互相替代。

现有 `create_submission` 不能通过 HTTP 层预检查后直接调用来满足本契约的并发要求；应扩展服务层或实现一个受控的原子入口，保留历史 schema/哈希语义。`PortalLensStore.build_for_submission` / `get` 只能接收经可信适配后的授权上下文；不能把客户端字典直接当 session。构建 fingerprint、文档证据语义和不可变存储复用既有实现。

阶段一只验收契约、Skill 和本地 mock。阶段二按 [Pilot Acceptance](../../../docs/PILOT_ACCEPTANCE.md)（仓库文档，独立安装 Skill 时由交付方提供）验证真实 backend；阶段三才讨论生产发布。未通过阶段二时不得对外宣传“安装即可使用”。
