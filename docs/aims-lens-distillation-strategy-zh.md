<!-- doc-parity: id=distillation-strategy; version=1.2; language=zh-CN; companion=aims-lens-distillation-strategy.md -->
# AIMS Lens Engine · 证据蒸馏策略

[English](aims-lens-distillation-strategy.md) | [中文](aims-lens-distillation-strategy-zh.md)

> 只蒸馏允许使用的证据真正支持的内容；证据到哪里，certainty 就到哪里。

## 1. 目的与边界

Distillation 的目标，是把来源不同、质量不同、授权状态不同的材料变成一个 **versioned, evidence-bounded practice hypothesis**，让 AIMS Lens Engine 可以检查、验证、routing、更新并解释它。

论文对应的使用场景是 **candidate-side interview practice**。蒸馏不是“找到企业真正的秘密招聘标准”，也不能因为文件里写了某家公司名字，就把社区经验或系统推断升级成企业官方规则。

一个合格 Lens 至少要回答五个问题：

1. **Scope：** 它试图描述什么面试上下文？
2. **Evidence：** 哪些材料被授权、可归因、可以用于支持这个上下文？
3. **Interpretation：** 哪些 AIMS dimension 和 follow-up category 真正有证据支持？
4. **Uncertainty：** 哪些部分资料稀疏、相互矛盾、过期或只是间接证据？
5. **不确定时怎么做：** 什么时候必须与更宽层级混合、从 L0 向 L5 backoff，或者 abstention？

## 2. 最重要的认识论规则

我们真正蒸馏的对象，不应该写成：

> “这家公司实际上就是这样判断候选人的。”

更准确的表述是：

> **在明确 scope 和 maturity 下，根据允许使用的证据，可以合理形成哪些 interview-practice hypothesis。**

这个区别非常重要。官网文化内容、JD、高管访谈、候选人面经、Reddit/Glassdoor 社区讨论、第三方分析的证据角色不同，不能全部混成一个“company standard”。

## 3. Phase 0 — 定义目标上下文

在调研之前先建立 intake，至少写清楚：

- Lens type：company / role / industry / archetype / derived / general practice；
- 如果有目标公司，公司是谁；
- region；
- role family 和 level；
- interview stage；
- competency focus；
- candidate-side intended use；
- source cutoff date；
- 是否存在已授权 private material；
- 已知 limitations。

“做一个 Amazon Lens”并不是一个完整需求。Amazon 全球文化、加拿大 SDE 面试、美国 Senior PM、Executive interview 都不是同一个 context。

### 默认解释

如果只给了公司名，没有其他范围，public-safe 默认值应是：

- 只用 public evidence；
- 用于 candidate-side practice；
- 明确 limitations；
- 不声称 official endorsement；
- 不声称 Lens 等于这家公司当前内部 hiring rubric。

## 4. Phase 0.5 — 创建可审计工作区

Company Lens 可以采用：

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
├── limits.md
├── validation_report.md
├── evidence_audit.md
└── research/
    ├── 01-official-culture.md
    ├── 02-executive-thought.md
    ├── 03-hiring-signals.md
    ├── 04-interview-questions.md
    ├── 05-employee-voice.md
    ├── 06-decision-cases.md
    └── 07-critic-risk.md
```

这是一套 auditable distillation 的目标 contract，并不意味着当前每一个 public Lens 都已经拥有全部文件。

Private / tenant-scoped source body 不能复制进 public Lens folder。

## 5. Phase 1 — 独立证据采集

好的 Lens 不应该让一种 source class 单独决定结论。原来的 multi-agent 设计保留七个相互独立的 evidence dimension。

| Evidence dimension | 典型公开来源 | 可以支持什么 | 单独不能证明什么 |
| --- | --- | --- | --- |
| Official culture | career pages、values、annual reports | 企业公开表达的原则与语言 | 面试官实际行为 |
| Executive thought | public letters、interviews、speeches | 决策语言与战略重点 | 通用 hiring criteria |
| Hiring signals | job posts、career guidance | 岗位期待和重复出现的能力语言 | 隐藏评分权重 |
| Interview experience | 候选人公开面经、视频、社区帖子 | 可能的问题 / follow-up pattern | 官方或当前真实流程 |
| Employee voice | 访谈、社区讨论 | 文化张力和体验 hypothesis | 全组织真实结论 |
| Decision cases | 公开产品 / 业务决策 | 可观察的 trade-off pattern | 招聘逻辑的因果解释 |
| Critic & risk | 监管、争议、失败案例 | counter-evidence、避免过度美化 | 直接的面试政策 |

### Source discipline

每条 material signal 尽量保留：

- source URL 或稳定 reference；
- source type；
- access / collection date；
- declared scope；
- transformation history；
- evidence quality；
- authorization / permitted use；
- expiry / refresh condition（如适用）。

发现矛盾时应保留矛盾，不要为了得到漂亮的 company story 强行平均掉。

## 6. Phase 2 — Evidence normalization 与 authorization

Raw material 进入 inference 前，先转成 evidence packet。

概念上的 gate 是：

```text
eligible evidence
= authorization
× quality
× recency
```

这里最重要的是：**authorization 不是 confidence score，而是 hard gate。**

如果证据没有被授权用于当前用途，不管看起来多有说服力，它贡献的 effective mass 都应该是 0。

只有通过 authorization 的证据，quality 和 recency 才参与权重。Recency 的时间单位必须和 decay rate 一致，不能公式写 per-month，代码却按 days 直接套用。

社区来源通常应该有更窄 scope、更低 evidential authority。大量重复面经可以增加对“某种 pattern 可能存在”的支持，但不能自动把它变成“企业官方标准”。

## 7. Phase 3 — 合成 AIMS 与 follow-up hypothesis

蒸馏后的 evidence 需要进入可运行结构：

- AIMS dimension signals；
- follow-up taxonomy；
- stage / role compatibility constraints；
- supported anti-signals；
- known contradictions；
- explicit limits；
- uncertainty settings；
- evidence lineage。

AIMS 六个 capability dimension：

- structured thinking；
- analytical problem solving；
- ownership and execution；
- impact and results；
- collaboration and communication；
- growth mindset。

不同 company / role Lens 可以有不同 emphasis，但必须能解释“为什么这个 dimension 或 follow-up category 值得更高练习优先级”。

同时要避免把“大公司”写成一种单一人格。业务线、岗位、地区、面试官、时间都会产生差异。

## 8. Phase 4 — Hierarchical inference 与 partial pooling

Company-level evidence 很少时，不能把稀疏样本直接当确定事实。reference framework 使用更宽 context 进行 hierarchical borrowing。

简化层级：

```text
generic practice
      ↓
archetype
      ↓
industry
      ↓
company / target context
```

Dirichlet-style reference implementation 以上一级 distribution 作为 prior center，再加入 narrower level 的 eligible effective evidence。

好处有两个：

1. company Lens 很稀疏时，不会轻易变成 0/1 式的武断结论；
2. broader pattern 可以提供基础，但真正有足够 company evidence 时，narrower distribution 仍然可以被数据推动。

这个 hierarchy 是透明 baseline，不是说 Dirichlet-multinomial 永远是唯一最佳模型。

## 9. Phase 5 — Compatibility、routing、backoff 与 abstention

Raw priority 高，并不代表该 follow-up 在当前情境下一定可以用。Compatibility mask 先去掉结构上不允许的类别。

Routing 再处理 eligible level：

| Level | 含义 | Backoff distance |
| --- | --- | ---: |
| L0 | full eligible parent context | 0 |
| L1 | drop one parent / context component | 1 |
| L2 | drop two | 2 |
| L3 | industry context | 3 |
| L4 | role/company archetype | 4 |
| L5 | generic practice | 5 |

L0 最具体，L5 是 generic fallback。

Routing weight 考虑 authorization、applicability、evidence coverage 和 backoff discount。最终是 practice mixture，而不是宣布“某一级就是企业真相”。

### Abstention

以下情况应该 fail closed：

- compatibility 后没有任何 category；
- 没有 eligible routing level；
- data support 低于声明的 abstention threshold；
- 所需 evidence 未授权或已过期；
- 用户要求的 specificity 超过 Lens maturity 能支持的范围。

Abstention 是有价值的输出，因为它阻止 LLM 用流畅语言制造不存在的 specificity。

## 10. Phase 6 — Maturity 与 validation

Research-facing maturity：

1. `exploratory`
2. `reviewed_practice`
3. `evaluation_ready`
4. `empirically_supported`

Maturity 说明“完成了什么 review / validation”，不能被当成 marketing 语言中的“准确率等级”。

推荐 validation layer：

- schema validation；
- source / provenance review；
- authorization review；
- contradiction review；
- cross-Lens differentiation tests；
- strong / average / weak synthetic cases；
- no-evidence / low-support abstention cases；
- fairness review of masks and exclusions；
- 有 labeled data 后再做 calibration evaluation；
- 随时间做 drift review。

`empirically_supported` 应该要求真实 empirical evidence，并且要说明 population 和 use case；不能因为内部审批通过就使用这个标签。

## 11. Phase 7 — Refresh 与 drift

Lens 必须 versioned，因为证据会变化。

可能的 refresh trigger：

- evidence expiry；
- 组织发生重大变化；
- 出现大量新的 official material；
- 重复出现新的公开面试 pattern；
- material KL drift 或 calibration degradation；
- reviewer 记录到重要 contradiction；
- schema / model version 更新。

更新时应保留 previous version、evidence lineage 和 change rationale。

## 12. Public 与 protected evidence

公开 repository 可以展示：

- schema；
- evidence standard；
- public-safe Lens assets；
- synthetic examples；
- reference inference code；
- validation tooling。

不能公开：

- candidate data；
- JobACE 真实 conversation；
- tenant-private evidence；
- 企业机密材料；
- production credential；
- proprietary production calibration state。

在受保护 deployment 中可以存在已授权 private evidence，但它不属于 public paper artifact。

## 13. 蒸馏绝不能暗示什么

Public company Lens 不应该暗示：

- “这是企业官方 rubric”，除非有明确 authoritative evidence；
- “这家公司下一题会问 X”，并把它包装成 calibrated employer-behavior probability；
- “这个候选人应该 hire / reject”；
- 系统拥有 confidential interview material；
- protected-trait inference；
- 帮候选人 fabricate experience；
- 没有测量过却声称 empirical effectiveness。

## 14. 与 broader product history 的关系

早期开发探索过 employer-side、reviewer-assist 等更广产品概念。它们可以为了 provenance 保留，但**不属于 manuscript research core**。

它们不能被当成论文 candidate-side claim 的证据。

见：

- `docs/broader-product/README.zh-CN.md`
- `legacy/employer_decision_support/`
- `RESEARCH_BOUNDARY.md`

## 15. Operational checklist

一个 public practice Lens 在标记 ready 前，至少检查：

- scope 是否明确；
- source 是否可归因；
- permitted use 是否明确；
- unauthorized evidence 是否确实贡献为 0；
- 不同 source type 是否被静默混成一种“真相”；
- contradiction 是否记录；
- AIMS / follow-up mapping 是否可追溯；
- compatibility rule 是否可 review；
- maturity 是否声明；
- limitations 是否显眼；
- routing / backoff 是否定义；
- low-support 是否可以 abstention；
- named-company wording 是否避免暗示 employer truth；
- public-safe evidence record 是否足以重建 Lens，或者是否明确说明哪些 protected evidence 不公开。

这套蒸馏纪律可以用一句话总结：

**specificity 必须由 evidence 赚出来，不能由语言生成出来。**
