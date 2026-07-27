# Public / Private 拆分策略

状态：已批准的 public-release preparation 方向。

## 目的

AIMS Lens Engine 需要同时支持两个目标：

- 建立一个开放、可信的 lens 标准，让外部贡献者可以检查、使用和扩展。
- 保留 JobACE 的私有评估优势、生产数据和专有面试辅导逻辑。

这次拆分不应该被当成一次简单的仓库清理。它是产品边界和治理边界。Public 资产应该增强 lens 生态；Private 资产应该保护 JobACE 的数据、租户流程、评分校准和生产集成。

## 战略定位

Public 项目应定位为：

> 一个开放框架，用于构建有证据支撑的公司、岗位、行业和思想家 lens，服务于面试准备、候选人评估辅助和战略职业决策。

Private JobACE 层应定位为：

> 一个专有评估和辅导层，结合 public lens 标准、private evidence、JobACE 专属评分校准和生产面试流程。

## 目标架构

```text
Public Open Source Core
  schemas
  governance standards
  public distillation playbooks
  public company lens examples
  validation tools
  contribution workflow

Private JobACE Intelligence Layer
  private materials
  tenant uploads
  workspace database
  audit and review logs
  JobACE scoring adapters
  production deployment configs
  private calibration data

Commercial / Enterprise Extension Layer
  API contracts may be public
  reference service may be limited public
  production workspace and tenant operations stay private
  enterprise private lenses stay tenant-private
```

## Public 发布范围

以下区域在审计后可以作为 public release 候选。

### Public Schemas

发布：

- `schemas/company_lens.schema.json`
- `schemas/evidence.schema.json`
- `schemas/question_bank.schema.json`
- `schemas/derived_lens.schema.json`
- `schemas/role_lens.schema.json`
- `schemas/interview_prep_plan.schema.json`

目的：

- 定义可移植的 lens artifact 格式。
- 让贡献者可以验证 company lens submission。
- 让项目在不依赖 JobACE 的情况下也可使用。

Public schemas 不得包含 JobACE tenant ID、生产 endpoint secret、private scoring weight，或来自真实用户的候选人示例。

### Public Governance

发布：

- `governance/evidence-standard.md`
- `governance/privacy-and-fairness.md`
- public lens 状态和 confidence 规则

目的：

- 解释 evidence 要求。
- 防止 public lens 被表述成官方公司标准。
- 要求使用 `FULLY_DISTILLED`、`DERIVED_LENS`、`LIGHTWEIGHT_SCAN` 和 `GENERIC_AIMS` 等 confidence state。

### Public Documentation

发布 public-safe 版本：

- system design
- distillation playbook
- implementation roadmap
- role routing principles
- validation checklist
- contributor guide

移除或改写：

- JobACE 生产 URL，除非这些 URL 被明确批准公开。
- internal deployment notes。
- private material workflows。
- tenant-specific API key instructions。
- 会暴露生产行为的 operational details。

### Public Company Lenses

发布基于 public source、public community aggregate，或来自高价值 private source 的 public-safe distilled summary 的 lens 内容。

Public repository 发布的是结构化、可验证的洞察，而不是原始材料仓库。Private 或付费材料可能非常有战略价值，也可以在转化后支持 public lens，但原文、完整来源结构、复制题库、用户提交的 job posting 和 candidate data 必须继续保持 private。

第一批 public release 目标：

- `company_lenses/amazon`
- `company_lenses/google`
- `company_lenses/mckinsey`
- `company_lenses/microsoft`
- `company_lenses/apple`
- `company_lenses/jpmorgan`
- `company_lenses/rbc`
- `company_lenses/td`
- `company_lenses/bmo`
- `company_lenses/cibc`
- `company_lenses/scotiabank`
- `company_lenses/shopify`

第一批 public set 应至少包含 12 家公司，这样项目才能展示跨行业覆盖、可重复结构和更广泛的外部可验证性。如果某个候选 lens 审计不通过，应以另一个 public-safe lens 替换，而不是把发布规模缩小到 10 家以下。

发布前，每个 lens 必须通过 public-safety audit：

- 不把 private Medium article text 复制到 public files
- 不把 user-submitted job posting text 复制到 public files
- 不包含 candidate answer 或 resume content
- 不逐字复制 raw scraped interview posts
- public export 中不包含 `private_only` evidence ID
- 不声称该 lens 代表官方公司招聘政策

允许 public 的 evidence visibility classes：

- `public_source`：official pages、public reports、public blogs、public job descriptions 和可以安全引用的 public documentation。
- `public_community_aggregate`：聚合后的 public interview 或 employee signals，confidence 较低，不复制个人帖子原文。
- `private_distillation_public_safe`：从 private、paid 或 owner-authorized materials 中提炼出的非逐字 signals；raw source bodies 继续留在 private。

禁止 public 的 evidence visibility class：

- `private_only`：tenant uploads、raw paid material、user-submitted job postings、candidate data、internal review records、private scoring calibration 和 enterprise-specific content。

Public company lenses 应包含：

- `profile.json`
- `evidence.md`，并带有 public-safe references
- `rubric.md`
- `question_bank.json`，前提是问题为生成问题或 public-safe 问题
- `rewrite_rules.md`
- `limits.md`
- `validation_report.md`

### Public Tools

发布：

- schema validators
- lens structure checkers
- public-safe lint tools
- export audit tools

不发布：

- production tenant admin tools
- 带真实 contract 的 JobACE API adapters
- 访问 private local paths 的 scripts
- 依赖 private databases 或 private materials 的 tools

## Private 范围

以下区域必须保持 private，除非被明确批准公开。

### Private Materials

保持 private：

- `private_materials/`
- private Medium distillations
- manually copied job postings
- tenant uploads
- enterprise-provided material
- 未获得再分发许可的 copyrighted source bodies

规则：

Private evidence 可以用于 private JobACE lens 或 tenant-specific lens，但不得复制到 public lens 中，除非它已被转化为 public-safe、非逐字、且权限兼容的 summary。

### Workspace And Production Data

保持 private：

- `workspace_data/`
- `audit_logs/`
- `review_logs/`
- production SQLite 或 Postgres data
- tenant API keys
- review decisions
- raw material paths

规则：

这些 artifact 是运营记录，不是 open source content。

### JobACE Integration

保持 private：

- real JobACE scoring adapters
- production request / response mappings
- 与 JobACE interview flows 绑定的 prompt routing
- candidate evaluation calibration
- 基于 JobACE data 的 improvement plan personalization logic
- `lens.jobace.ca` 和 `lens-api.jobace.ca` 的 deployment configs

Public version：

- 只暴露 mock adapter 或 interface contract。
- 只包含 synthetic candidate data 示例。

### Private Calibration

保持 private：

- 从真实用户派生的 candidate personas
- historical scoring outputs
- reviewer calibration decisions
- 来自 JobACE 用户的 false positive / false negative analysis
- 任何 enterprise screening outcomes

Public version：

- 使用明确标记为 synthetic 的 fixtures。

## Commercial / Enterprise 边界

一部分 enterprise-facing 功能可以公开接口，但不公开实现。

可以 public：

- source material submission 的 OpenAPI contract。
- 使用 fake data 的 sample tenant flow。
- review decisions 的 schema。
- high-level workspace architecture。

应保持 private：

- production authentication implementation details。
- tenant key rotation operations。
- internal review queue data。
- enterprise-specific lens content。
- deployment and scaling configuration。

这样可以让项目对 B2B partners 保持可信，同时不暴露 JobACE 的 operating system。

## 仓库策略

采用分阶段拆分，而不是突然 hard fork。

### Stage 1: Define Release Manifests

创建：

```text
public_manifest.yaml
private_manifest.yaml
```

`public_manifest.yaml` 应列出可以 export 的 files 和 directories。

`private_manifest.yaml` 应列出绝不能 export 的 files 和 patterns。

private manifest 至少应包括：

```text
private_materials/
workspace_data/
audit_logs/
review_logs/
.env
.env.*
.venv-lens-workspace/
tenant_uploads/
candidate_data/
```

### Stage 2: Build Public Export

创建一个 export script，只把 manifest 允许的文件复制到干净的 release directory：

```text
dist/public/aims-lens-engine/
```

如果出现以下情况，export script 应该失败：

- export 中出现 private path。
- 文件包含已知 private markers。
- lens 引用了 private-only evidence ID，但没有 public-safe explanation。
- 生成文件包含 API keys、local database paths 或 production secrets。

### Stage 3: Public Safety Audit

第一次 push public repository 之前：

- 对 exported lenses 运行 schema validation。
- 运行 private marker scan。
- 人工检查每一个 public company lens。
- 验证每个 public artifact 的 license compatibility。
- 确认没有复制 raw interview posts 或 copyrighted article bodies。

### Stage 4: Create Public Repository

export 干净后，创建独立 public repository。

推荐 public repository name：

```text
aims-lens-engine
```

推荐 private repository name：

```text
aims-lens-engine-private
```

如果当前 repository 保持 private，则把它作为 source repository，并从它 export public releases。

### Stage 5: Contribution Workflow

Public contributions 应通过以下入口进入：

- company lens proposals
- evidence additions
- schema improvements
- validation rules
- public documentation fixes

Contribution rules：

- contributors 必须引用 sources。
- 不得提交 copyrighted raw article bodies。
- 不得提交 confidential employer documents。
- 不得提交 personal candidate data。
- 不得声称 inferred lenses 是官方公司标准。
- maintainers 可以降低 evidence confidence，或拒绝 unsupported claims。

## License 策略

使用 split license model。

已批准的 public license 方向：

- schemas、tools 和 framework code 使用 Apache-2.0。
- documentation 和 public lens text 使用 CC BY 4.0 或可比较的 content license，最终措辞等待 legal review。

已批准的 private license 方向：

- proprietary JobACE internal license。
- enterprise private lens terms 通过合同处理。

第一批 public release 应明确 license split，不要把 code 和 lens text 当成同一种 artifact class。

## Public Lens Status Rules

每个 public lens 必须包含：

- lens status
- version
- evidence date
- evidence confidence
- limitations
- public / private visibility marker
- evidence visibility class

推荐 visibility field：

```json
{
  "visibility": "public"
}
```

Private 和 tenant lenses 应使用：

```json
{
  "visibility": "private",
  "tenant_scope": "tenant_id_or_internal_scope"
}
```

Public release tooling 应拒绝任何包含 `visibility: private` 的 public export。

Public release tooling 也应拒绝任何标记为以下内容的 exported evidence entry：

```json
{
  "evidence_visibility": "private_only"
}
```

Public release tooling 可以允许：

```json
{
  "evidence_visibility": "private_distillation_public_safe"
}
```

但前提是该 entry 是非逐字 distilled signal，并且不包含 raw private text、copied paid content、user-submitted job posting bodies、candidate records 或 tenant-specific details。

## JobACE 使用规则

JobACE 可以使用：

- public lenses
- private JobACE lenses
- tenant-authorized private lenses
- 基于用户 target role 和 job description 生成的 derived lenses

当系统依赖 `DERIVED_LENS`、`LIGHTWEIGHT_SCAN` 或 sparse evidence 时，JobACE 必须在用户可见输出中披露 lens confidence。

JobACE 不得把 public inferred lenses 表述成官方公司招聘标准。

## 近期下一步

1. 添加 `public_manifest.yaml` 和 `private_manifest.yaml`。
2. 添加 public export script。
3. 添加 private marker scanner。
4. 审计当前 `company_lenses/` 的 public safety。
5. 决定哪些 initial lenses 可以作为 public release candidates。
6. 起草 `CONTRIBUTING.md`。
7. 起草 public `LICENSE` 和 documentation license decision。
8. 创建 clean public export，并在 push 前进行 review。

## 已批准决策

第一轮 public-release preparation 已批准方向：

- Public code license：Apache-2.0。
- Public content license：CC BY 4.0 或可比较的 content license，等待最终 legal review。
- 第一批 public lens set：12+ 家公司，从 Amazon、Google、McKinsey、Microsoft、Apple、JPMorgan、RBC、TD、BMO、CIBC、Scotiabank 和 Shopify 开始。
- Private-derived signals：只允许作为 `private_distillation_public_safe` summary。
- Raw private materials：永不 export。
- Workspace API：第一步发布 API contracts、schemas、examples 和可选 mock/reference adapter；production tenant operations 保持 private。
- JobACE mention：允许作为 commercial reference implementation，但不能表述成 JobACE 的 private evaluation layer 已经 open source。
- Private-to-public promotion：必须 owner-approved 和 checklist-gated，绝不自动发生。

Public repository 创建前仍需确认：

- public lens text 的最终 content license wording。
- 第一批 public export 是否包含 limited mock `services/lens_workspace_api/` implementation，还是推迟到后续版本。
- 指定有权批准 private-to-public lens promotion 的 maintainers。

## 当前建议

当前 private repository 暂时继续作为 source of truth。

先构建基于 manifest 的 public export pipeline。只有当 exported tree 通过自动和人工 safety checks 后，才把它变成 public GitHub repository。

第一批 public release 必须足够有说服力：至少 12 个 company lenses，覆盖 technology、consulting、global finance、Canadian banking 和 Canadian growth companies。发布应通过 public-safe synthesis 保留高价值 private-derived insight，同时仍然防止 private materials、tenant data、JobACE scoring logic 或 production configuration 泄漏。
