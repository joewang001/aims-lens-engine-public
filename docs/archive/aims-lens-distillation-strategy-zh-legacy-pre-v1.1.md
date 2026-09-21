---
name: AIMS-Lens-Engine-distillation
description: |
  AIMS Lens Engine 策略和路线图：输入公司、岗位、行业、思想家或模糊招聘/决策需求，
  自动完成需求分流、多源采集、独立归档、证据分级、AIMS 映射、Lens 构建、质量验证、
  人工复核和持续更新。适用于内部团队、合作方、企业客户和投资人理解系统如何从材料变成可运行 Lens。
---

# AIMS Lens Engine · 蒸馏策略和路线图

> 写不进模型参数里的判断标准，必须写进可审计的 Lens。

## 核心理念

AIMS Lens Engine 不是复制公司，也不是替代面试官，而是提炼企业、岗位、行业和思想家的判断框架。

一个好的 Lens 是一套可运行的招聘和决策辅助系统：

- 它用什么价值标准看候选人？（企业镜片）
- 它用什么证据判断能力？（AIMS 映射）
- 它如何追问、验证和校准？（面试 DNA）
- 它绝对不能把什么当作结论？（反模式）
- 它在什么情况下必须降级或进入人工复核？（诚实边界）

关键区分：捕捉的是 how this organization judges，不是复制 what this organization says。

---

## 执行流程

### Phase 0: 入口分流

收到内部、合作方或企业客户输入后，先判断属于哪条路径：

| 用户输入 | 路径 | 示例 |
| --- | --- | --- |
| 明确公司 | 公司 Lens 直接路径 -> Phase 0A | “蒸馏 Amazon”“做 RBC lens” |
| 明确岗位或行业 | Role / Industry Lens 路径 -> Phase 0A | “做 Risk Compliance overlay”“做 Canadian banking lens” |
| 明确思想家或管理者 | Thinker Lens 路径 -> Phase 0A | “蒸馏 Charlie Munger 的决策方式” |
| 模糊需求或业务困惑 | 诊断路径 -> Phase 0B | “我想筛选更适合银行风控的人”“我们要提升面试质量” |
| 已有 Lens 更新 | 更新路径 -> 更新已有 Lens | “Google lens 最近要更新”“补 Reddit 面试经验” |

### Phase 0A: 需求澄清（直接路径）

收到明确对象后，确认：

1. 对象是谁：公司、岗位族、行业、思想家或混合 Lens。
2. 适用范围：全球、加拿大、美国、某业务线、某级别、某岗位族。
3. 使用场景：候选人 mock、screening、reviewer assist、B2B API、企业私有初筛。
4. 新建或更新：是否已有 `company_lenses/<company>/` 或 role overlay。
5. 资料模式：公开资料、用户手动材料、企业授权私有资料，或混合模式。
6. 风险等级：是否涉及招聘筛选、合规、受保护属性或高风险自动化。

默认规则：

- 如果用户只说“就做某公司”，默认做 public company lens + 面试准备 + reviewer assist，不做自动拒绝。
- 如果用户提供企业内部材料，标记为 private / tenant-scoped，不能进入 public lens。
- 如果资料不足，允许先做 `LIGHTWEIGHT_SCAN`，但必须显式标注低置信。

确认后进入 Phase 0.5。

---

### Phase 0B: 需求诊断（模糊路径）

当用户不知道该蒸馏什么，只表达业务目标或招聘困惑时，系统要从需求反推最合适的 Lens。

#### Step 1: 需求定位

最多用 1-2 个追问定位核心需求：

| 需求维度 | 典型表达 | Lens 方向 |
| --- | --- | --- |
| 目标公司面试准备 | “我要面 Amazon/Google/RBC” | Company Lens + Role Lens |
| 岗位能力校准 | “如何判断 PMM 是否够强” | Role Lens + JD overlay |
| 企业初筛 | “我们想用 Jobace 做一轮筛选” | Private Company Lens + Screening Contract |
| 行业语境 | “加拿大银行和科技公司判断差异是什么” | Industry Lens |
| 高管/思想家决策 | “想用某个思想家的判断方式做决策” | Thinker Lens |
| 问题库建设 | “需要真实面试问题和 follow-up” | Question Bank Lens |
| 公平性和风险控制 | “如何避免 AI 误判候选人” | Governance Lens + Human Review |

追问原则：

- 最多问 2 轮，不做问卷调查。
- 如果需求清晰，直接推荐路径。
- 追问目的是区分“候选人训练”还是“企业筛选”，因为治理边界不同。

示例：

```text
用户：我们想让银行客户用 Jobace 做初筛，但不知道该先做什么。

AIMS Lens Engine：这里核心需求是“受控企业筛选”，不是普通 mock interview。
我建议先做三个 Lens：目标银行 private company lens、目标岗位 role overlay、human review workflow。
公开社区题库只能作为低置信补充，不能当作银行官方标准。
```

#### Step 2: 候选推荐

基于需求推荐 2-3 个候选方案：

```text
### 候选 1: RBC Risk Compliance Lens  需要蒸馏 / 可从已有 RBC public lens 扩展
核心镜片：风险意识、客户信任、合规升级路径。
为什么适合你：直接对应银行风控岗位的一轮筛选。
局限：公开资料不能代表 RBC 内部正式 hiring rubric，需企业授权或 reviewer 校准。
```

推荐原则：

- 不超过 3 个候选。
- 已有 Lens 优先展示，能复用就不重做。
- 候选之间要有差异：公司 Lens、岗位 Lens、行业 Lens 不要混成一团。
- 必须说明局限和置信状态。

#### Step 3: 用户选择

- 选已有 Lens：进入 routing / pilot 使用。
- 选新 Lens：进入 Phase 0A 确认细节。
- 选更新：进入“更新已有 Lens”流程。
- 都不满意：回到需求定位，或用户提供新对象。

---

### Phase 0.5: 创建 Lens 工作区

收到确认后立即创建工作区，在调研之前完成：

```text
company_lenses/<company>/
├── README.md
├── intake.md
├── collection_log.md
├── profile.json
├── evidence.json
├── evidence.md
├── rubric.md
├── question_bank.json
├── rewrite_rules.md
├── limits.md
├── validation_report.md
├── evidence_audit.md
├── research/
│   ├── 01-official-culture.md
│   ├── 02-executive-thought.md
│   ├── 03-hiring-signals.md
│   ├── 04-interview-questions.md
│   ├── 05-employee-voice.md
│   ├── 06-decision-cases.md
│   └── 07-critic-risk.md
└── sources/
    ├── official/
    ├── community/
    ├── transcripts/
    ├── job_descriptions/
    └── private_materials/
```

完成检查：

- 工作区已创建。
- 更新模式下已读取旧 profile、rubric、question bank 和 validation report。
- 私有资料已标记 tenant scope，不进入 public folder。
- 所有 agent 输出都必须写入 `research/` 或明确归档文件。
- Evidence ID 命名规则已确定。

关键规则：

- 不存文件的调研等于没做。
- 公开 Lens 和私有 Lens 必须隔离。
- Lens 必须自包含：复制整个 company folder 后，能看到证据、限制、题库和验证报告。

---

### Phase 1: 多源信息采集（并行 Agent Swarm）

#### 模式判断：公开资料 vs 私有资料

| 模式 | 触发条件 | 策略 |
| --- | --- | --- |
| 纯公开资料 | 没有企业授权材料 | 多 Agent 全部使用公开资料，标注 public lens |
| 私有资料优先 | 企业提供 rubric、面试题、文化文档 | 先分析私有材料，公开资料只做补充 |
| 纯私有资料 | 企业明确要求仅用内部材料 | 不做公开搜索，tenant-scoped lens |
| 手动材料录入 | 用户从 Medium、Glassdoor、Reddit 等复制材料 | 清洗、去污染、摘要、版权控制 |
| 轻量扫描 | 时间短或资料少 | 生成 `LIGHTWEIGHT_SCAN`，不得声称完整 |

私有资料优先模式：

1. 先读取企业授权材料。
2. 识别资料覆盖了哪些维度。
3. 只对缺失维度做公开补充。
4. 明确区分“企业授权材料”“公开资料”“社区经验”“系统推断”。

#### 本地/手动资料处理

| 素材类型 | 处理方式 | 覆盖维度 |
| --- | --- | --- |
| 企业文化 PDF | 提取价值观、行为标准、反模式 | official culture |
| 面试官 rubric | 转成 AIMS 权重和评分 anchors | hiring signals |
| JD | 提取 role overlay、能力要求、scope | role lens |
| Medium 文章 | 摘要经验、提取问题，不复制长文 | community interview |
| Reddit / Glassdoor | 聚合模式，低置信标注 | community evidence |
| 面试 transcript | 提取追问逻辑和评分证据 | interview DNA |
| 企业内部反馈 | 私有 evidence，tenant-scoped | private calibration |

本地和授权材料通常比网络摘要质量更高，但版权、隐私和租户隔离要求也更高。

---

#### 7 个 Agent 的任务分配

启动 7 个并行 Agent，每个负责不同证据维度。

| Agent | 搜索目标 | 提取重点 | 输出文件 |
| --- | --- | --- | --- |
| 1 Official Culture | 官网、招聘页、价值观、年报 | 公司公开自我叙事、价值标准、业务语言 | `01-official-culture.md` |
| 2 Executive Thought | CEO/高管访谈、公开信、演讲 | 决策语言、战略取舍、领导期待 | `02-executive-thought.md` |
| 3 Hiring Signals | 招聘页、job posts、career docs | 用人理念、岗位能力、AIMS 映射 | `03-hiring-signals.md` |
| 4 Interview Questions | 公开面试题、社区经验、题库 | 真实问题模式、follow-up、题型频率 | `04-interview-questions.md` |
| 5 Employee Voice | 员工评价、访谈、社区反馈 | 内部体验、文化张力、候选人风险 | `05-employee-voice.md` |
| 6 Decision Cases | 公司重大决策、产品/业务案例 | 言行一致性、执行方式、风险取舍 | `06-decision-cases.md` |
| 7 Critic & Risk | 争议、监管、批评、失败案例 | 盲点、反模式、不可过度美化处 | `07-critic-risk.md` |

#### 每个 Agent 的硬性要求

- 调研结果必须写入对应文件。
- 每条证据标注来源 URL、访问日期、来源类型、置信度。
- 区分“公司官方表达”“员工/候选人经验”“第三方分析”“系统推断”。
- 发现矛盾时保留矛盾，不强行调和。
- 社区来源不得直接升级为官方标准。
- 引用受版权保护内容时只做短摘录或摘要。

#### Agent prompt 模板

以 Agent 4 为例：

```text
你的任务：调研 [公司] 的公开面试问题和候选人经验。

搜索方向：
- 公司 career site 是否公开面试流程
- Glassdoor / Reddit / Blind / Medium / YouTube 中可验证的面试经验
- 高频题型、真实问题、follow-up 方式
- 不同岗位族之间的差异
- 候选人反复提到的风险或误区

输出要求：
- 写入 company_lenses/[company]/research/04-interview-questions.md
- 每条问题必须标注来源和置信度
- 区分“真实原问题”“候选人转述”“系统原创改写题”
- 不复制长篇付费文章正文
- 不把社区经验说成官方标准
```

其他 6 个 Agent 按同样结构调整搜索方向和输出文件。

#### 工具辅助

- 网页：优先读取原文，不依赖搜索摘要。
- PDF：提取企业报告、文化手册、JD、rubric。
- 表格：用于问题库、evidence manifest、validation case。
- 视频/播客：提取 transcript，存入 sources/transcripts。
- 手动录入页：用于快速录入 Medium / community article 全文，再二次处理。
- QA 工具：运行 schema validation、routing validation、scoring harness、LLM regression。

#### 信息源优先级

| 来源类型 | 揭示什么 | 权重 |
| --- | --- | --- |
| 企业授权私有材料 | 实际 rubric、内部标准 | 最高+，但 tenant scoped |
| 官方招聘页/价值观 | 企业公开标准 | 最高 |
| 高管访谈/公开信 | 决策语言、战略取舍 | 高 |
| JD 和岗位说明 | 当前岗位要求 | 高 |
| 真实面试 transcript | 实际问答和追问 | 高，但需授权 |
| 多平台社区经验 | 题型模式、候选人体验 | 中，需交叉验证 |
| 单篇社区文章 | 线索 | 低到中 |
| 二手总结 | 只作参考 | 低 |

#### 信息源黑名单和降权规则

永远不能作为强证据：

- 无来源转载。
- 明显 SEO 洗稿。
- 无法验证的“内部爆料”。
- 把个人失败经验包装成公司通用标准的帖子。
- 过期太久且无法证明仍适用的面试经验。

可用但必须降权：

- Reddit、Glassdoor、Blind、Medium 等社区材料。
- YouTube 面经。
- 候选人口述回忆。
- 招聘机构整理的题库。

#### Agent 超时与失败处理

- 单个 Agent 超时：继续推进，但在 review checkpoint 标注信息不足。
- 可用来源少于 10 条：只允许 `LIGHTWEIGHT_SCAN` 或 `DERIVED_LENS`。
- Agent 结果冲突：写入 `evidence_audit.md`，作为文化张力或证据冲突。
- 社区题库噪声过高：只提取题型模式，不采纳具体题目。

关键规则：宁可生成一个诚实标注局限的 60 分 Lens，也不要生成一个看起来完整但证据虚弱的 90 分 Lens。

---

### Phase 1.5: 调研 Review 检查点

所有 Agent 完成后，暂停并生成调研质量摘要：

```text
┌────────────────────┬──────────┬──────────────────────────────┐
│ Agent              │ 来源数量 │ 关键发现                     │
├────────────────────┼──────────┼──────────────────────────────┤
│ Official Culture   │ 8        │ 价值观：customer trust...     │
│ Executive Thought  │ 5        │ 高管强调 long-term thinking  │
│ Hiring Signals     │ 12       │ JD 高频要求 data + ownership │
│ Interview Questions│ 34       │ 高频题型：behavioral + case  │
│ Employee Voice     │ 18       │ 文化张力：速度 vs 风险       │
│ Decision Cases     │ 6        │ 关键决策：产品/市场取舍      │
│ Critic & Risk      │ 9        │ 风险：社区证据偏差           │
├────────────────────┼──────────┼──────────────────────────────┤
│ 矛盾点             │ 3        │ 官方强调X，员工反馈Y         │
│ 信息不足维度       │ 1        │ 缺少该岗位真实 transcript    │
└────────────────────┴──────────┴──────────────────────────────┘
```

判断：

- 质量足够 -> 进入 Phase 2。
- 某维度不足 -> 定向补充 Agent。
- 私有资料污染 public lens -> 停止并拆分 public/private。
- 证据太弱 -> 降级为 `LIGHTWEIGHT_SCAN`。

这个检查点的意义：调研质量决定 Lens 上限，必须在 synthesis 前拦截。

---

### Phase 2: 框架提炼（Synthesis）

7 个 Agent 材料汇总后，执行结构化提炼。

#### 2.1 企业判断模型提取（3-7 个）

操作步骤：

1. 扫描所有 research 文件，列出候选判断原则。
2. 三重验证：
   - 跨来源复现：官方、JD、社区、案例是否至少两类支持？
   - 生成力：能否影响新回答的评分、追问或 rewrite？
   - 排他性：是否区别于所有公司都说的通用好话？
3. 排序取舍：取最能改变评分和追问的 3-7 个。
4. 每个模型记录名称、描述、证据、AIMS 映射、适用场景、失效条件。

#### 2.2 Hiring Heuristics 提取（5-10 条）

即企业或岗位做招聘判断时的快速规则，可表述为：

```text
如果候选人只说团队成果但无法说明个人不可替代贡献，则 ownership_execution 降权。
如果候选人给出指标但无法解释 attribution，则 analytical_problem_solving 降权。
```

每条 heuristic 必须有证据来源和反例边界。

#### 2.3 Interview DNA 分析

| 维度 | 提取内容 |
| --- | --- |
| 问题形态 | behavioral、case、technical、scenario、values |
| 追问方式 | 深挖 ownership、metric、trade-off、risk、stakeholder |
| 语言风格 | 直接、结构化、挑战式、合作式、合规式 |
| 证据偏好 | 数字、案例、因果链、反思、role fit |
| 停止条件 | 证据足够、风险明确、候选人偏题 |
| 不该问 | 受保护属性、暗示性问题、无法公平比较的问题 |

#### 2.4 价值观与反模式

- 价值观：3-5 条企业或岗位核心判断标准。
- 反模式：该 Lens 明确不认可的回答模式。
- 张力：例如 speed vs risk、innovation vs compliance、individual impact vs collaboration。

#### 2.5 组织和行业谱系

记录该公司或岗位在行业地图中的位置：

- 对标公司。
- 行业 archetype。
- 地域差异。
- 岗位族差异。
- 与已有 Lens 的相似和差异。

#### 2.6 诚实边界

必须写明：

- public lens 不代表企业官方标准。
- community evidence 需要低置信或交叉验证。
- 不预测某个具体面试官会如何判断。
- 信息截止日期。
- 不做自动拒绝或最终招聘决定。
- 私有资料不能污染公开 Lens。

---

### Phase 2.5: 提炼确认检查点

Phase 2 完成后，展示提炼摘要：

```text
提炼结果摘要：
- 企业判断模型：N 个
- Hiring heuristics：N 条
- Interview DNA：3 个关键特征
- AIMS 权重变化：structured_thinking + analytical_problem_solving...
- 核心张力：N 对
- 诚实边界：N 条
- 推荐状态：FULLY_DISTILLED / DERIVED_LENS / LIGHTWEIGHT_SCAN
```

确认后进入 Phase 3。若模型不清或证据不足，回到 Phase 2 调整。

这个检查点的意义：Lens synthesis 主观判断最重，必须在构建 profile 和 question bank 前确认。

---

### Phase 3: Lens 构建

将 Phase 2 提炼结果组装为可运行 Lens 资产。

#### Step 1: 读取模板和 schema

读取：

- `schemas/company_lens.schema.json`
- `schemas/question_bank.schema.json`
- `schemas/role_lens.schema.json`
- `schemas/screening_report.schema.json`
- `company_lenses/_template/profile.json`

#### Step 2: 填充内容

| 资产 | 填充来源 |
| --- | --- |
| `profile.json` | 企业判断模型、AIMS 权重、状态、证据摘要 |
| `evidence.json` | 规范化 evidence records |
| `rubric.md` | AIMS 维度解释、评分 anchors、公司调整 |
| `question_bank.json` | 原创问题、follow-up、AIMS target、risk signals |
| `rewrite_rules.md` | 如何把普通回答改成目标公司可接受表达 |
| `limits.md` | 诚实边界、不可用场景、证据缺口 |
| `validation_report.md` | 验证结果、失败项、批准状态 |
| `evidence_audit.md` | 矛盾、低置信来源、版权/隐私检查 |

#### Lens Agentic Protocol 生成指引

Lens 必须包含运行协议，让系统知道遇到不同请求时怎么行动。

核心原则：Lens 不凭感觉输出结论。涉及公司、岗位、当前 JD 或高风险筛选时，必须先看证据和状态。

```text
## Lens 工作流（Agentic Protocol）

### Step 1: 请求分类

| 类型 | 特征 | 行动 |
| --- | --- | --- |
| 候选人训练 | mock、rewrite、follow-up | 使用 candidate-safe lens |
| 企业筛选 | screening、review queue | 使用 limited-pilot controls |
| 高风险决策 | reject、hire、rank | 必须 human review，不自动决定 |
| 新公司 | 无 lens 或低证据 | route to DERIVED/LIGHTWEIGHT/GENERIC |
| 私有企业 Lens | tenant material | 隔离 public lens |

### Step 2: Lens 研究/路由

读取 company、role、JD、overlay、lens_status、confidence 和 evidence notice。

### Step 3: AIMS 输出

基于 AIMS 六维、公司权重、JD 要求和候选人证据生成输出。
```

Step 2 的研究维度必须来自 Lens 本身，而不是通用搜索：

| Lens 类型 | 研究维度 |
| --- | --- |
| Amazon | leadership principles、ownership、metrics、scope |
| Google | analytical rigor、collaboration、role-related knowledge、ambiguity |
| McKinsey | issue tree、hypothesis、client impact、structured communication |
| Canadian Bank | risk, compliance, customer trust, escalation |
| Private Enterprise | tenant rubric、interviewer guidance、approved score anchors |

#### Step 3: 质量自检

构建后必须检查：

- JSON schema 是否通过。
- AIMS 映射是否完整。
- question bank 是否全部原创或合规摘要。
- limits 是否写明。
- private/public 是否隔离。
- evidence notice 是否存在。

#### Step 4: 输出

写入对应 Lens 目录。未验证前不得标记 `FULLY_DISTILLED`。

---

### Phase 4: 质量验证

生成 Lens 后，用独立验证流程执行测试，避免主 Agent 自评。

#### 4.1 已知测试（Sanity Check）

选择 3 个有强证据支持的公司判断模式，检查 Lens 是否能正确追问或评分。

通过：Lens 输出方向与证据一致。
不通过：回溯调整企业判断模型和 AIMS 权重。

#### 4.2 边缘测试（Edge Case）

选择证据不足或跨区域/跨岗位问题。

期望输出：

```text
基于当前 public lens，只能低置信推断。此处需要 human reviewer 或企业私有 rubric。
```

不应该斩钉截铁。

#### 4.3 同答跨 Lens 测试

同一候选人回答分别进入 Amazon、Google、McKinsey、RBC Lens。

通过标准：

- 评分差异有证据解释。
- follow-up 不完全相同。
- company lens adjustment 明确。
- 不出现伪公司化的通用话术。

#### 4.4 Live Transcript Validation

用真实 mock conversation 或 screening transcript 检查：

- 10 题限制是否执行。
- 一个 bot turn 是否只有一个问题。
- 非回答 turn 是否不进入 InterviewEvaluation。
- reviewer-only 字段是否不暴露给候选人。
- final assessment 是否包含 JD fit、priority improvement points。

#### 4.5 通过标准

| 检查项 | 通过标准 | 不通过信号 |
| --- | --- | --- |
| 企业判断模型 | 3-7 个，每个有证据和局限 | 全是通用价值观 |
| AIMS 映射 | 六维至少覆盖关键维度 | 无法解释评分差异 |
| Question Bank | 原创题 + follow-up + score target | 复制社区题或过度堆问题 |
| 诚实边界 | 明确 public/private/fallback | 声称官方标准 |
| 证据质量 | 强来源和社区来源分级 | Reddit 单帖直接当结论 |
| 同答跨 Lens | 输出有差异且可解释 | 所有公司反馈一样 |
| 人工复核 | low-confidence 进入 review | 自动做最终决定 |

验证通过 -> 进入 limited pilot 或 approved state。
不通过 -> 回到 Phase 2 或 Phase 3。
迭代上限：Phase 2 -> 4 最多循环 2 次。仍不通过则降级状态并记录限制。

---

### Phase 5: 双 Agent 精炼（标准后置工序）

Phase 4 通过后，自动启动双 Agent 精炼。

Agent A：Lens Quality Optimizer

- 检查 evidence coverage、AIMS mapping、routing clarity、review gates。
- 干跑 3 个典型 screening payload。
- 输出最弱 2 个维度的具体改进建议。

Agent B：Product / Partner Readiness Reviewer

- 检查 API 输出是否适合 Jobace、合作方和企业客户。
- 检查 candidate-safe 和 reviewer-only 字段隔离。
- 检查文档是否说明商业边界。
- 输出 2-3 处具体文本或 schema 改动建议。

主 Agent 综合两份报告，应用不冲突改进，并写入变更摘要。

精炼标准：改动必须让 Lens “接入即能运行”，不是单纯增加说明文字。

---

## 更新已有 Lens

当用户说“更新某公司 Lens”“最近有新面试经验”“补加拿大银行题库”时：

1. 读取现有 `profile.json`、`validation_report.md`、`limits.md`，确认版本、状态和 cutoff date。
2. 只启动相关 Agent：
   - 新面试经验 -> Agent 4 + Agent 5。
   - 新官方价值观 -> Agent 1 + Agent 2。
   - 新风险或争议 -> Agent 7。
   - 新岗位 -> Role Lens / JD overlay。
3. 对比新旧信息：
   - 强化现有模型 -> 补 evidence 和案例。
   - 与现有模型冲突 -> 写入 evidence audit，必要时调整模型。
   - 出现新题型 -> 更新 question bank。
   - 出现新风险 -> 更新 limits 和 human review flags。
4. 重跑 validation。
5. 不重写整个 Lens，优先增量更新。

---

## 品味守则（速查）

遇到判断困难时回看。

| 原则 | 一句话 |
| --- | --- |
| 证据 > 叙事 | 漂亮故事不如可追溯证据 |
| 行为 > 口号 | 公司如何行动比怎么宣传更有信息量 |
| 差异 > 通用 | 所有公司都说的不是 Lens |
| 矛盾 > 粉饰 | 文化张力是判断的重要材料 |
| 最新 > 过时 | 招聘标准和面试流程会变化 |
| 边界 > 幻觉 | 不知道就标注，不要编造 |

### 绝不做的事

- 编造公司没有公开或授权表达过的标准。
- 把社区面经当作官方 hiring rubric。
- 把通用 AIMS 反馈包装成公司差异。
- 忽略负面评价、争议和风险。
- 在信息不足时强行标记 `FULLY_DISTILLED`。
- 把 private lens 信息泄露到 public lens。
- 自动拒绝候选人或做无人监督最终招聘决定。

---

## 特殊场景

### 公开公司 vs 私有企业

- 公开公司：public evidence 多，但不能代表内部标准。
- 私有企业：必须依赖授权材料，tenant-scoped，不进入公开库。

### 大公司 vs 小公司

- 大公司：按地区、业务线、岗位族拆分 overlay。
- 小公司：公开信息少，优先企业自助材料和 JD。

### 科技公司 vs 金融/银行

- 科技公司：强调 ownership、impact、technical/product judgment。
- 银行金融：必须加入 risk、compliance、customer trust、escalation。

### Company Lens vs Role Lens vs Industry Lens

| Phase | Company Lens | Role Lens | Industry Lens |
| --- | --- | --- | --- |
| 0A | 确认公司和地区 | 确认岗位族和级别 | 确认行业边界 |
| 1 | 7 Agent 围绕公司 | Agent 围绕 JD 和能力模型 | Agent 围绕监管、业务、客户 |
| 2 | 提取企业判断模型 | 提取岗位成功信号 | 提取行业风险和常识 |
| 3 | profile/rubric/question bank | role overlay/routing | archetype/derived lens |
| 4 | 同答跨公司测试 | 同答跨岗位测试 | 跨行业迁移测试 |

### 思想家 Lens

当目标是名人、思想家或管理者时，可复用类似 Nuwa 的人物蒸馏流程，但输出必须适配 AIMS：

- 决策模型。
- 表达 DNA。
- 反模式。
- 可用于候选人 coaching 或 leadership judgment。
- 不用于招聘筛选中的受保护属性判断。

### 冷门公司

可用来源少于 10 条时：

1. 提醒用户 Lens 质量受限。
2. 只能生成 `LIGHTWEIGHT_SCAN`。
3. question bank 以原创 scenario 为主，不声称真实题。
4. 建议企业提供私有材料或收集更多 JD/面试 transcript。

### 蒸馏企业自己

企业主动蒸馏自己的 Lens 时：

1. 引导企业提供文化文档、rubric、JD、面试题、评价表。
2. 明确 private tenant scope。
3. 建立 reviewer signoff。
4. 输出企业可用的一轮/二轮初选配置。
5. 禁止未经授权把私有标准用于其他企业或公开 Lens。

---

## 路线图

### v0.1-v0.3: File-first Lens Library

- 建立公司目录结构。
- 完成 Amazon、Google、McKinsey 初版。
- 建立 evidence、rubric、question bank、limits。

### v0.4-v0.5: Production Gates

- 扩展 Apple、Microsoft、加拿大银行、JPMorgan。
- 增加 role overlays。
- 建立 routing validation、scoring harness、human reviewer signoff。

### v0.6-v0.7: Internal Pilot Integration

- Internal pilot API。
- LLM scorer behind gate。
- Jobace adapter contract。
- Candidate-safe output 和 reviewer workflow。

### v0.8: Calibration and Partner Pilot

- 扩大内部 mock QA。
- 完成更多 live transcript validation。
- 建立 partner API sandbox。
- 企业自助 Lens intake prototype。

### v0.9: Enterprise Lens Governance

- Tenant-scoped private lens。
- Reviewer portal。
- Lens versioning 和 approval workflow。
- Evidence graph 和 audit dashboard。

### v1.0: Controlled Production

- B2B API SLA。
- Full governance gates。
- Enterprise self-service onboarding。
- Jobace AIMS 深度集成。
- 仍然保留 no automated rejection 和 human review policies，除非未来法律、合规和产品治理另行批准。

---

## 最后

AIMS Lens Engine 蒸馏的不是公司本身，而是一面判断镜片。

一个好的 Lens 让候选人、面试官、reviewer 和企业客户更清楚地看到：

- 什么证据真正重要。
- 什么追问真正有价值。
- 什么判断只是幻觉。
- 什么决定必须交给人类负责。

AIMS 是能力语言。
Lens 是语境和判断标准。
Engine 是让它们可审计、可验证、可商业化运行的系统。
