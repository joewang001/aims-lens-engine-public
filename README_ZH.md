# AIMS Lens Engine 中文说明

> 面向公开贡献、合作机构与 JobACE 私有实现的公司 Lens 蒸馏、验证与决策增强系统。

AIMS Lens Engine 的目标不是让 AI “扮演一家公司”，而是把企业公开表达、招聘标准、面试问题、岗位要求、行业语境和真实候选人回答转化为可审计、可验证、可调用的结构化 Lens。

它帮助 Jobace AIMS 和合作方回答一个更具体的问题：

> 同一个候选人回答，在 Amazon、Google、RBC、McKinsey 或 JPMorgan 的语境下，为什么会被不同地追问、评分和判断？

当前版本：`v0.8.1-public-core`

当前状态：`public_released`

当前边界：公开仓库只包含 public-safe core；JobACE 生产服务、候选人数据、租户数据、私有校准与部署配置不进入公开发布。

---

## 快速导航

- 效果示例
- 系统定位
- 如何运行
- AIMS Lens 蒸馏了什么
- 诚实边界
- 已蒸馏公司 Lens
- 持续校准机制
- 工作原理
- 仓库结构
- Public / Private 边界
- 背后的故事
- 治理、隐私与公平性
- 许可证

---

## 效果示例

### 场景一：同一回答，不同公司 Lens

候选人回答：

```text
我负责过一次跨渠道营销活动。前期 LinkedIn 获客成本偏高，我把预算转向 paid search，
并用 MQL、SQL、转化率和 CAC 做了判断。最终 qualified leads 提升了 18%。
```

Amazon Lens 会重点追问：

```text
你在预算调整中个人承担了哪一个不可回避的决策责任？
```

Google Lens 会重点追问：

```text
你如何确认 18% 的提升来自你的渠道调整，而不是市场基线变化？
```

McKinsey Lens 会重点追问：

```text
如果把这个案例拆成问题定义、假设、分析、建议和影响五步，你会如何讲？
```

RBC Risk & Compliance Lens 会重点追问：

```text
在调整渠道预算前，你如何识别合规、声誉或客户适当性风险？
```

这不是把公司名字贴到通用评分表上。Lens 的作用是让同一套 AIMS 能力维度进入不同企业、岗位和行业的真实判断语境。

### 场景二：候选人筛选

输入：

```json
{
  "company": "rbc",
  "role": "Operational Risk Analyst",
  "question": "Describe a time you identified an operational risk.",
  "answer": "I found a recurring reconciliation gap and escalated it after validating the pattern..."
}
```

输出会包含：

- 路由结果：公司 Lens、岗位 Overlay、置信度。
- AIMS 六维评分：结构化思维、分析解决、责任执行、影响结果、协作沟通、成长心态。
- 公司 Lens 调整：RBC 风险合规语境下的判断重点。
- 人工复核标记：低置信、风险信号、弱证据或 fallback 情况。
- 面试官/Reviewer 建议：下一轮追问方向。

候选人端看到的是安全、可解释、面向改进的反馈；面试官和 reviewer 端看到的是更完整的风险、追问和校准信息。

---

## 系统定位

AIMS Lens Engine 是一个独立平台，早期独立于 Jobace 主系统建设，成熟后作为 Jobace AIMS 的知识增强层接入。

它同时支持三类使用者：

1. 内部团队：沉淀公司 Lens、验证评分逻辑、支持 Jobace mock interview 和 candidate screening。
2. 合作机构：通过 API 调用公司 Lens，为职业服务、培训、招聘平台提供增强评估。
3. 企业客户：主动创建和治理自己的企业 Lens，用于一轮或二轮初选、面试培训和校准。

核心产品形态：

- Company Lens：企业文化、价值标准、招聘偏好、面试风格。
- Role Lens：岗位族、职能、级别、能力权重。
- Industry Lens：行业风险、监管语境、业务模式。
- Thinker Lens：名人、思想家、管理者的心智模型和决策方法。
- Question Bank：原创面试题、follow-up 逻辑、评分维度。
- Evidence Layer：证据、来源、置信度、验证记录。
- Human Review Workflow：人工复核、签核和有限试点治理。

---

## 如何运行

### 本地 API

```bash
cd /home/django/myspace/aims-lens-engine
python3 tools/internal_pilot_api.py --host 127.0.0.1 --port 8092
```

健康检查：

```bash
curl http://127.0.0.1:8092/health
```

生成筛选报告：

```bash
curl -X POST http://127.0.0.1:8092/v1/screening-report \
  -H 'Content-Type: application/json' \
  --data @examples/internal-pilot-screening-request.json
```

### 可用端点

- `GET /health`
- `POST /v1/route`
- `POST /v1/screening-report`
- `POST /v1/screen-candidate`
- `GET /v1/review-queue`
- `POST /v1/review-decision`
- `GET /v1/review-decisions`

### LLM Scorer

默认使用 deterministic scorer，便于离线回归和稳定测试。需要启用 OpenAI LLM scorer 时，在 `.env.local` 中配置：

```bash
AIMS_SCORER_MODE=llm
OPENAI_MODEL=gpt-5.4-mini
OPENAI_API_KEY=your_key_here
```

LLM scorer 只能在 limited pilot 控制下增强评分，不允许输出自动拒绝或最终招聘决定。

---

## AIMS Lens 蒸馏了什么

蒸馏类项目强调从人物公开材料中提取“表达方式、心智模型、决策启发、反模式和边界”。AIMS Lens Engine 借鉴这种多层蒸馏思想，但对象从“个人思维方式”扩展为“企业和岗位的招聘判断系统”。

我们提取七层：

| 层次 | 说明 |
| --- | --- |
| 企业怎么说 | 使命、价值观、领导原则、官网叙事、招聘语言 |
| 企业怎么判断 | 面试评估标准、用人理念、人才密度、绩效偏好 |
| 企业问什么 | 已公开面试题、社区经验、题型模式、follow-up 结构 |
| 企业看重什么证据 | AIMS 六维度在该公司和岗位中的权重 |
| 企业警惕什么 | 风险信号、文化冲突、弱证据、不可接受行为 |
| 岗位如何变化 | role overlay、JD 具体要求、级别和行业语境 |
| 系统知道什么不知道 | 证据边界、置信度、公开信息和官方标准的区别 |

AIMS 是底层通用能力语言。Lens 不是替代 AIMS，而是解释 AIMS 在不同企业、岗位、行业中的不同权重和证据标准。

---

## 诚实边界

每个 Lens 必须明确标注不能做什么。

系统不声称：

- 公开资料等于企业官方内部标准。
- Reddit、Glassdoor、Medium 或社区经验等于正式招聘政策。
- 公司文化在不同国家、团队、岗位和年份中完全一致。
- Lens 可以替代人工 interviewer、recruiter 或 hiring manager。
- 评分可以作为自动拒绝或最终录用依据。

系统必须说明：

- 证据来自哪里。
- 哪些证据是官方来源，哪些是社区来源。
- 哪些结论是强证据，哪些只是低置信推断。
- 什么时候需要 human reviewer。
- 什么时候应该 fallback 到 DERIVED_LENS、LIGHTWEIGHT_SCAN 或 GENERIC_AIMS。

一个不能说明自己边界的 Lens，不应该进入生产使用。

---

## 已蒸馏公司 Lens

首批公开发布目标包含 12 个公司 Lens 文件夹，用来证明标准、结构、贡献方式和验证流程可以被外部检查：

| 公司 | 当前用途 |
| --- | --- |
| Amazon | 领导原则、ownership、结果导向、行为面试追问 |
| Google | 分析严谨性、结构化问题解决、collaboration、role fit |
| Apple | 产品品味、端到端责任、用户体验、保密和执行质量 |
| Microsoft | growth mindset、合作、技术与业务结合 |
| McKinsey | case thinking、结构化表达、hypothesis-driven problem solving |
| RBC | 风险合规、客户信任、金融服务判断 |
| TD | 客户体验、银行服务、风险意识 |
| CIBC | 客户关系、金融咨询、合规语境 |
| BMO | 商业银行、客户导向、协作执行 |
| Scotiabank | 国际银行、客户和风险平衡 |
| JPMorgan | 金融专业性、风险控制、执行强度 |
| Shopify | 商家平台、产品执行、创业者服务 |

每个公司 Lens 通常包含：

- `profile.json`
- `evidence.json`
- `evidence.md`
- `question_bank.json`
- `rubric.md`
- `rewrite_rules.md`
- `limits.md`
- `validation_report.md`
- `evidence_audit.md`
- `collection_log.md`

这些文件不是静态内容库，而是可审计的评分、追问和校准资产。

### Lens 状态

系统使用四种状态，避免把所有公司都伪装成同等成熟：

- `FULLY_DISTILLED`：多源采集、归档、交叉验证和 validation 已完成。
- `DERIVED_LENS`：从相似公司、行业模式、岗位 JD 和已有 Lens 推导。
- `LIGHTWEIGHT_SCAN`：有限公开资料或企业提供资料下的轻量 Lens。
- `GENERIC_AIMS`：无有效 Lens 时回到通用 AIMS。

---

## 持续校准机制

AIMS Lens Engine 体系中采用对应持续进化的评估机制。 Calibration Loop：

1. 新证据进入 evidence layer。
2. 多 Agent 独立归档，避免一个 summarizer 混合所有来源。
3. Cross-source audit 检查证据是否互相支持。
4. Question bank 和 rubric 更新。
5. Router、scoring harness、LLM regression 重跑。
6. Human reviewer signoff。
7. Limited pilot 通过后进入下一版本。

目前已完成的生产门槛：

- Phase 2C production gates。
- Human reviewer signoff。
- 230 case LLM regression，`failures=0`。
- Internal pilot API。
- Human review workflow。
- Jobace integration contract。

仍然保持的限制：

- 不做自动拒绝。
- 不做无人监督最终招聘决定。
- 低置信、fallback、风险信号必须进入人工复核。

---

## 工作原理

输入一个公司、岗位或目标人物后，AIMS Lens Engine 做六件事：

1. 多源并行采集

   独立 Agent 分别处理官方资料、招聘页面、公开访谈、企业文化文档、社区面试经验、真实问题、岗位 JD、行业监管或业务背景。每个 Agent 独立归档，不先混合结论。

2. 证据分级和去污染

   官方资料、公司博客、招聘页面、社区帖子、Glassdoor、Reddit、Medium、候选人手动录入资料、企业私有材料采用不同置信等级。系统保留来源、时间、适用范围和限制。

3. 三重验证提炼

   一个 Lens 判断要进入 profile 或 rubric，至少要通过：

   - 多来源支持，而不是单一帖子。
   - 能影响新回答的评分或追问。
   - 相比通用 AIMS 有差异化，不是所有公司都一样。

4. 构建 Lens 资产

   输出结构化文件：企业 profile、AIMS 权重、risk signals、question bank、follow-up logic、rewrite rules、limits、validation report。

5. 路由和评分

   Router 根据 company、role、JD、overlay 和置信度选择目标 Lens。Scorer 生成 AIMS scores、strengths、risks、recommended follow-ups、human review flags。

6. 回归验证和人工复核

   使用固定 validation cases、同答跨公司测试、同答跨岗位测试、LLM regression 和 human reviewer signoff 控制版本质量。

---

## 仓库结构

```text
aims-lens-engine/
├── README.md                         # 英文/工程简版入口
├── README_ZH.md                      # 中文说明
├── LICENSE                           # 代码、schema、工具的 Apache-2.0 许可
├── CONTENT_LICENSE.md                # 公开内容许可边界
├── CONTRIBUTING.md                   # 公开贡献规则
├── public_manifest.yaml              # 公开导出 allowlist
├── private_manifest.yaml             # 私有内容 denylist
├── api/
│   └── openapi.yaml                  # API contract
├── architecture/
│   ├── system-design.md              # 系统设计
│   └── lens-router.md                # Lens routing 逻辑
├── company_lenses/
│   ├── amazon/
│   ├── google/
│   ├── apple/
│   ├── microsoft/
│   ├── mckinsey/
│   ├── rbc/
│   ├── td/
│   ├── cibc/
│   ├── bmo/
│   ├── scotiabank/
│   ├── jpmorgan/
│   └── shopify/
├── docs/
│   ├── project-charter.md
│   ├── implementation-plan.md
│   ├── distillation-playbook.md
│   ├── phase-2c-production-gates.md
│   ├── phase-3a-internal-pilot-integration.md
│   ├── phase-3a1-human-review-workflow.md
│   ├── phase-3b-llm-scorer-integration.md
│   └── phase-3c1-jobace-integration-contract.md
├── governance/
│   ├── evidence-standard.md
│   └── privacy-and-fairness.md
├── routing/
│   └── role_router.json
├── schemas/
│   ├── company_lens.schema.json
│   ├── question_bank.schema.json
│   ├── screening_report.schema.json
│   └── jobace_adapter_contract.schema.json
├── tools/
│   ├── export_public_release.py
│   ├── scan_public_export.py
│   ├── generate_public_release_audit_report.py
│   ├── interview_prep_planner.py
│   ├── llm_scorer.py
│   └── run_scoring_harness.py
└── examples/
    └── internal-pilot-screening-request.json
```

---

## Public / Private 边界

AIMS Lens Engine 可以拆成两层：

- Public core：公司 Lens 结构、公开来源摘要、schema、治理规则、验证工具、贡献流程。
- Private layer：JobACE 生产 workspace、租户上传、候选人材料、review logs、私有评分校准、企业专属 Lens、部署配置。

公开发布使用 `public_manifest.yaml` 和 `private_manifest.yaml` 控制边界：

```bash
python tools/export_public_release.py --execute --clean
python tools/scan_public_export.py --allowlist
python tools/generate_public_release_audit_report.py --allowlist
```

允许进入公开仓库的证据类型：

- `public_source`
- `public_community_aggregate`
- `private_distillation_public_safe`

禁止进入公开仓库的内容：

- `private_only` 证据。
- 原始付费文章、复制的职位全文、未授权企业内部材料。
- 候选人简历、候选人回答、租户上传、用户提交的职位正文。
- API key、token、数据库、部署配置、生产服务细节。

---

## 商业化路径

AIMS Lens Engine 的商业目标不是只做一个面试题库，而是成为企业招聘判断、候选人准备和合作平台评估的 Lens 基础设施。

### 1. Jobace 内部增强

- Mock interview 根据公司 Lens 和 JD 生成更真实的下一题。
- Final assessment 显示公司适配、岗位差距和 priority improvement points。
- Reviewer 看到内部 follow-up、risk signals 和 human review flags。

### 2. B2B API

合作单位可以通过 API 获取：

- 公司 Lens routing。
- 筛选报告。
- 候选人回答评分。
- 下一轮追问建议。
- 人工复核队列。

### 3. 企业自助 Lens

企业可以主动创建自己的 private company lens：

- 上传企业文化、招聘标准、岗位 rubric。
- 录入真实面试问题和面试官反馈。
- 配置私有 risk signals。
- 用 Jobace 平台进行一轮或二轮初选。

私有 Lens 与公开 Lens 隔离。未经授权，企业私有资料不能反向污染公开 Lens。

### 4. 投资价值

系统资产的复利来自：

- Lens 数量扩展。
- Evidence graph 增长。
- Validation case 增长。
- Cross-company calibration 增长。
- Human reviewer decisions 形成校准数据。
- Jobace 前端和 API 场景持续产生真实使用反馈。

---

## 背后的故事

通用 AIMS 解决的是“候选人能力如何表达和评估”的问题。但真实招聘从来不是通用的。

同一段回答：

- 在 Amazon 可能被看作 ownership 不够具体。
- 在 Google 可能被追问 causal validation。
- 在 McKinsey 可能被要求结构化成 case logic。
- 在加拿大银行可能首先进入 risk、compliance 和 customer trust 语境。

因此我们需要的不只是一个评分模型，而是一套能把企业文化、岗位要求、行业风险和候选人证据连接起来的 Lens Engine。

蒸馏类项目证明了“公开材料可以蒸馏为可运行认知框架”。AIMS Lens Engine 把这个方向迁移到招聘和职业决策：不是复制公司，不是假装知道公司内部秘密，而是把可验证的公开与授权信息转化为可审计的判断辅助系统。

---

## 治理、隐私与公平性

本系统的设计原则：

- Public lens 与 private lens 分离。
- 社区证据必须标注低置信或需交叉验证。
- 所有 candidate screening 输出必须包含 evidence notice。
- Limited pilot 下禁止自动拒绝。
- 人工 reviewer 对关键结论负责。
- 不使用受保护属性做评分。
- 不把 company lens 包装成官方认证标准。
- 不把候选人训练反馈和企业筛选反馈混为一体。

候选人端输出应以成长和准备为主；面试官/reviewer 端输出可包含更完整的风险、追问和校准字段。

---


## 关于项目

项目名称：AIMS Lens Engine

公开发布状态：public_released

公开版本：v0.8.1-public-core

应用运行状态：approved for limited pilot

主要使用场景：Jobace 内部 pilot、合作方 API、企业自助 Lens、候选人面试准备、人工 reviewer 决策辅助。

---

## 许可证

代码、schema 和工具采用 Apache-2.0。公开 Lens 内容和文档采用 CC BY 4.0。具体边界见 `LICENSE`、`NOTICE`、`CONTENT_LICENSE.md` 和 `CONTRIBUTING.md`。

任何外部使用都必须遵守：

- 不自动拒绝候选人。
- 不无人监督做最终招聘决定。
- 不把公开 Lens 说成官方公司标准。
- 不用未授权企业私有资料训练公开 Lens。

---

AIMS 评估候选人的能力。  
Lens 解释不同公司如何看这些能力。  
AIMS Lens Engine 把这两者连接成可验证、可治理、可商业化的招聘决策基础设施。
