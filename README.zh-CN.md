<!-- doc-parity: id=readme-overview; version=1.2; language=zh-CN; companion=README.md -->
# AIMS Lens Engine

[English](README.md) | [中文](README.zh-CN.md)

AIMS Lens Engine 是一个可独立部署、与具体机构无绑定的 **evidence-governed interview reasoning and practice-decision engine（证据治理的面试推理与练习决策引擎）**。它把来源不同、授权状态不同、质量和时效不同的证据转成有版本的练习假设，再通过明确的 uncertainty、routing、backoff 和 abstention 规则，决定下一步最值得练习和追问的方向。

**Release-candidate artifact：** `0.10.0-paper-v1.4`

**对应 manuscript：** `v1.4`

**Candidate experimental baseline：** `c18899b469e1d579391306872d5834ebf6e3caf3`

**Planned immutable tag（尚未创建）：** `v0.10.0-paper-v1.4`

**Release status：** `candidate` — 当前不声称 v1.4 tag 已冻结。

**上一冻结 paper artifact：** `v0.9.2-paper-v1.3`，commit `f7fcb6a3129cb58fe20c414f1abe519376def8e1`

**Public repository：** https://github.com/joewang001/aims-lens-engine-public

> Lens 是一个 **versioned, evidence-bounded practice hypothesis（有版本、受证据边界约束的练习假设）**。它不是企业官方 hiring rubric，不代表系统拥有某家公司的内部面试信息，也不是招聘结果预测。

## 5 分钟理解 AIMS Lens Engine

### 为什么需要 AIMS Lens Engine

通用 LLM 可以根据简历和 JD 生成很像真实面试的问题、追问和回答建议；题库网站也可以提供带公司标签的面试题。这些工具都有价值，但它们往往不会自动回答一个更难的问题：

**为什么系统有资格使用“某公司、某岗位或某行业”的特定假设？证据有多强？当证据不够时，系统什么时候应该承认自己不知道？**

AIMS Lens Engine 把这些问题变成显式机制。它把以下概念分开：

- **证据是否有资格使用**，与证据强不强分开；
- **练习假设**，与企业真实标准分开；
- **候选人状态**，与组织证据分开；
- **更具体的上下文**，与没有依据的高 confidence 分开；
- **概率化的练习优先级**，与 LLM 流畅的语言表达分开。

当证据不足以支持更具体的 Lens 时，系统会从 L0 向 L5 backoff，或者直接 abstention，而不是用语言流畅度掩盖证据缺口。

## 一个最容易理解的模型

```text
公开 / 已授权证据
        │
        ▼
 Evidence packets
 authorization • provenance • quality • recency
        │
        ▼
 有版本的 Lens 假设
 company • role • industry • archetype • general
        │
        ▼
 证据治理的概率推理
 partial pooling • compatibility mask • uncertainty
        │
        ▼
 Routing / backoff
 L0 ──► L1 ──► L2 ──► L3 ──► L4 ──► L5
        │
        ▼
 候选人侧练习决策
 追问优先级 • data support • explanation • abstention
```

最终输出是 **practice priority（练习优先级）**，不是“某公司下一题一定会问什么”的概率，更不是录用概率。

## Lens 到底是什么

Lens 是一套机器可读、可以复核、可以更新的面试上下文表示。根据使用范围，它可以包含：

- 目标岗位、级别、面试阶段和 competency context；
- 与 AIMS 六维能力关联的 follow-up taxonomy；
- 带有来源、授权、质量、时效和 provenance 的 evidence packets；
- compatibility rules 和限制条件；
- uncertainty、routing 和 backoff 设置；
- maturity 和 review state；
- 明确的局限与 anti-claims。

因此，带公司名称的 Lens 应该被理解为：

**从允许使用的证据中推导出来、可被质疑和更新的练习假设，而不是“这家公司真实的内部招聘标准”。**

## Lens 是怎么蒸馏出来的

完整流程见：

- [Distillation Strategy — English](docs/aims-lens-distillation-strategy.md)
- [蒸馏策略 — 中文](docs/aims-lens-distillation-strategy-zh.md)

高层流程如下：

1. **定义练习上下文。** 明确公司 / 岗位 / 行业、地区、级别、面试阶段，以及 candidate-side practice 的用途。
2. **独立采集证据。** 把官方资料、招聘信号、高管语言、社区经验、决策案例、批评与风险证据分开。
3. **规范化证据。** 转为 evidence packet，记录 authorization、provenance、quality、recency、scope 和 expiry。
4. **合成 Lens。** 把有支持的信号映射到 AIMS 能力模型和 follow-up taxonomy；社区经验不能自动升级为“企业官方规则”。
5. **进行概率推理。** 使用 recursive plug-in hierarchical Dirichlet shrinkage、compatibility masking 和显式 uncertainty。
6. **诚实 routing。** 使用 L0–L5 backoff；不够支持的 specificity 必须折扣、降级或 abstention。
7. **验证和维护。** 跟踪 maturity、drift、相互冲突的证据、过期状态和 review history。

## 核心概念

| 概念 | 含义 |
| --- | --- |
| **Lens** | versioned, evidence-bounded practice hypothesis。 |
| **Evidence authorization** | 硬性资格门；未授权证据贡献为零。 |
| **Evidence quality** | 只有通过 authorization 后才参与权重。 |
| **Recency** | 按声明的时间单位进行衰减，不能混用 day / month。 |
| **Compatibility mask** | 去除在当前情境中结构上不允许的 follow-up 类别。 |
| **Partial pooling** | generic → archetype → industry → company 之间共享统计强度，避免稀疏 company cell 被当成确定事实。 |
| **Routing / backoff** | 组合可用的上下文层，并按 backoff distance 对 specificity 进行折扣。 |
| **L0–L5** | L0 是最具体的可用上下文，L5 是 generic practice context。 |
| **Data support** | effective evidence mass 的有界摘要，不是企业行为概率。 |
| **Abstention** | 当 support、compatibility、authorization 或 routing 不充分时 fail-closed。 |
| **Maturity** | `exploratory` → `reviewed_practice` → `evaluation_ready` → `empirically_supported`。 |

## 研究模型

公开 reference implementation 对应论文中的核心数学路径：

- constrained probabilistic DAG；
- logistic stopping model；
- compatibility masking；
- recursive plug-in hierarchical Dirichlet shrinkage；
- authorization × quality × recency 的 effective evidence；
- posterior mean 和 conditional Dirichlet intervals given the plug-in parent distribution；
- 六级 routing / backoff mixture；
- normalized entropy 和 data support；
- Brier score、top-label ECE、log loss；
- KL drift；
- reference information-gain scoring。

对应关系见：

- [`docs/PAPER_TO_CODE_MAP.md`](docs/PAPER_TO_CODE_MAP.md)
- [`docs/MATH_TO_CODE_COMPLETENESS_AUDIT.md`](docs/MATH_TO_CODE_COMPLETENESS_AUDIT.md)

这些可执行函数证明“论文里的数学规范可以被实现和检查”，但**不能单独证明**系统已经具有经验有效性，也不能证明能够预测企业行为或提升就业结果。

## 一个 candidate-side 使用例子

假设一名候选人正在准备某家目标公司的 Senior Product 岗位。

客户端可以提供 JD、résumé、面试阶段和候选人上一轮回答；Lens 可以根据公开或其他已授权证据提供 company / role / industry context。

Lens Engine 先回答：

- 哪些证据被授权用于当前用途？
- 哪些 signal 与当前 stage / competency 兼容？
- 更具体的 context 到底有多少 effective evidence 支持？
- 应该使用 L0、与更宽层级混合、backoff，还是 abstention？
- 哪种 follow-up category 的 **practice priority** 最高？
- 这个决策由哪些 evidence 和 routing path 支持？

之后 LLM 才负责把这个决策表达成自然的问题或解释。也就是说，**LLM 位于治理和推理决策之后，而不是替代它。**

## 和通用 LLM / 题库有什么区别

| 通用方式 | AIMS Lens Engine |
| --- | --- |
| 根据 prompt 生成看起来合理的问题 | 对 target-specific practice 要求明确 evidence 和 routing basis |
| 往往把不同来源混在 prompt 里 | 分离 authorization、quality、recency、provenance、scope |
| 证据很少时语言仍可能很自信 | specificity 不够支持时 backoff 或 abstention |
| context 主要是 prompt text | context 是有版本、带 maturity 和 limits 的 Lens |
| 很难追溯为什么得到某个建议 | 暴露 decision provenance 和 evidence reference |
| 公司标签可能制造“很具体”的错觉 | Named-company Lens 必须声明它只是 evidence-bounded hypothesis |

AIMS Lens Engine 并不是要替代所有通用 AI。它提供的是一个更窄、更可检查的 reasoning / governance layer，适合需要 target-specific interview practice、同时又要求证据纪律的场景。

## 与 JobACE 的关系

JobACE 是 AIMS Lens Engine 的第一个 deep reference integration，**不是 AIMS Lens Engine 的架构前提**。

AIMS Lens Engine 负责研究侧 reasoning layer：

- Lens representation 和 validation；
- evidence lineage 和 authorization；
- routing / backoff；
- probabilistic inference；
- compatibility constraints；
- uncertainty 和 abstention；
- explanation 和 audit provenance。

JobACE 这类 client 可以负责：

- 候选人交互；
- 语音 / 文本练习；
- coaching；
- practice history；
- progress tracking；
- 面向机构的交付。

客户端应通过 versioned API 接入，而不是复制 Lens inference algorithm。

## 论文研究边界

论文对应的 research core 是 **candidate-side interview practice**。

它不做以下事情：

- 为雇主对候选人进行 ranking；
- 推荐 hire / reject；
- 推断 protected characteristics；
- 声称掌握企业机密 hiring rubric；
- 声称某家企业一定遵循 Lens 中的模式；
- 承诺面试成功或录用结果；
- 把 practice priority 解释成 employer-behavior probability。

历史上或探索性的 employer-side 概念继续保留在研究核心之外，见 [Broader Product and Historical Extensions](docs/broader-product/README.zh-CN.md)。

## Reviewer quick start

论文 reference implementation 不依赖外部服务，并使用 synthetic data：

```bash
python tools/validate_paper_artifact.py
python -m unittest discover -s tests -v
python tools/run_paper_artifact_demo.py
python tools/run_exp1a_core_verification.py
python tools/run_exp1b_lens_differentiation.py
python tools/run_exp2_sensitivity_ablation.py
python tools/run_exp3_semantic_regression.py
python tools/run_exp4_adversarial_alignment.py
python tools/run_exp5_hierarchy_approximation.py
```

Manuscript v1.4 保留 Experiments 1A/1B/2/3，并新增 Experiment 4 作为 internal mathematical–implementation correction evidence，以及 Experiment 5 作为 synthetic approximation benchmark。这些结果验证受控输入下的机制行为、corrective alignment、approximation behavior 与可复现性；不能外推为 real-employer validity、population fairness、当前 production LLM accuracy、面试提升或 employment-outcome efficacy。

双语文档一致性单独检查：

```bash
python tools/validate_documentation_alignment.py
```

## Repository map

```text
api/                         candidate-side research API
architecture/                系统边界与 routing 规范
governance/                  evidence / privacy / fairness / authenticity / abstention
research_core/               论文 reference implementation
schemas/                     research 和 supporting public schemas
examples/paper/              synthetic deterministic examples
company_lenses/              supporting public Lens assets
docs/                        research、operations、双语文档
docs/wiki/                   双语 Wiki 的 canonical source
docs/broader-product/        明确不属于论文核心的产品/历史边界
legacy/                      历史或非论文能力
tools/                       validators、demo、public-release tooling
tests/                       reference tests
```

## 文档入口

从 [Documentation Hub](docs/README.zh-CN.md) 开始。

关键文档：

- [Research Boundary](RESEARCH_BOUNDARY.md)
- [Reproducibility Guide](REPRODUCIBILITY.md)
- [Paper Release Readiness](PAPER_RELEASE_READINESS.md)
- [蒸馏策略](docs/aims-lens-distillation-strategy-zh.md)
- [文档治理规范](docs/DOCUMENTATION_GOVERNANCE.zh-CN.md)
- [Wiki Source — English](docs/wiki/AIMS_LENS_ENGINE_WIKI.md)
- [Wiki Source — 中文](docs/wiki/AIMS_LENS_ENGINE_WIKI.zh-CN.md)

英文是 public research documentation 的 canonical language；中文是持续维护的 **semantic-equivalent companion**。两种语言需要事实、边界和规范一致，但不要求逐句翻译。

## Open / protected boundary

公开项目可以包含 protocol、schema、validator、reference code、synthetic examples、public-safe Lens assets 和治理文档。

公开项目不得包含 JobACE 用户数据、候选人真实记录、真实 transcript、tenant-private configuration、机密组织证据、production credential/database 或 proprietary production policy/calibration state。

更广 public export 由 `public_manifest.yaml` 和 `private_manifest.yaml` 管理；论文更窄的 artifact 由 `paper_artifact_manifest.yaml` 管理。

## Public company Lens assets

Company Lens folder 是 supporting public artifact，不是 employer ground truth。公开推导的 Lens 应暴露 provenance、limitations、review state 和 evidence maturity。社区经验可以支持一个练习假设，但不能静默升级成“企业官方标准”。

## Contribution

欢迎对 public core 做贡献，但不能把 private data 或大段受版权保护的 source body 带入公开仓库，详见 `CONTRIBUTING.md`。

涉及规范性含义的双语文档修改，应在同一个 PR 中同时更新英文 canonical document 和中文 companion。

## License

- Code、schemas、tools：Apache-2.0
- Public Lens content 和 documentation：CC BY 4.0

见 `LICENSE`、`NOTICE`、`CONTENT_LICENSE.md`。

## Citation

见 `CITATION.cff`。正式论文投稿或 archival release 应引用 frozen tag / commit，而不是不断变化的 branch。
