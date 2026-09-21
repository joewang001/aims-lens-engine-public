<!-- doc-parity: id=wiki-core; version=1.2; language=zh-CN; companion=AIMS_LENS_ENGINE_WIKI.md -->
# AIMS Lens Engine Wiki — 中文 Canonical Companion

[English](AIMS_LENS_ENGINE_WIKI.md) | [中文](AIMS_LENS_ENGINE_WIKI.zh-CN.md)

这个文件是 public Wiki 的 repository source，主要给还没有读论文和代码的人快速理解系统。

## 1. AIMS Lens Engine 是什么？

AIMS Lens Engine 是一个用于 target-specific interview practice 的 evidence-governed reasoning layer。

它最核心的工作并不是“写面试题”。通用 LLM 已经很擅长生成问题。

更难的问题是：

- 哪些 contextual assumption 真正有依据？
- 哪些 evidence 被允许参与当前决策？
- company evidence 很少时，应该怎样从 broader context 借力？
- 哪些 follow-up category 在结构上不兼容？
- 什么时候应该降低 specificity？
- 什么时候应该 abstention？
- 事后怎样重建“为什么当时得到这个结论”？

Lens 是一个 **versioned, evidence-bounded practice hypothesis**。

## 2. 它解决什么问题

Targeted interview preparation 很容易制造一种“过度具体”的错觉。

系统只要看到 “Amazon”“RBC”“McKinsey”，就可以立刻生成很像某家公司风格的问题。语言越流畅，用户越容易误以为它知道真实内部流程，即使证据其实很少。

AIMS Lens Engine 把这个问题视为 governance problem。

它首先判断 company-specific assumption 是否真的有足够支持；如果没有，就应该向 industry / archetype / generic practice backoff，而不是继续制造 specificity。

## 3. 核心对象

### Lens

Lens 包含一个受边界约束的表示：

- target context；
- follow-up categories；
- AIMS capability mappings；
- evidence references；
- constraints；
- uncertainty settings；
- maturity；
- limitations。

### Evidence packet

Evidence packet 不只记录“来源说了什么”，还记录：

- 是否被授权用于当前目的；
- 质量与时效；
- 支持什么 scope；
- 经过什么 transformation。

### Candidate state

候选人的回答证据、practice history 等 candidate-side data，和 organization evidence 是不同 epistemic object。Candidate state 不能静默改写 company Lens。

### Practice decision

系统输出的是带 support、uncertainty、routing provenance 和 disclaimer 的 ordered practice priority。

它不是 hiring recommendation，也不是 employer-behavior probability。

## 4. AIMS capability model

Reference material 使用六个 capability dimension：

1. structured thinking；
2. analytical problem solving；
3. ownership and execution；
4. impact and results；
5. collaboration and communication；
6. growth mindset。

Lens 可以改变在某个 context 下哪些 dimension 更值得关注，但不能替候选人编造他真实经历中不存在的 evidence。

## 5. Evidence 如何变成 Lens

蒸馏流程：

```text
定义 scope
   ↓
独立采集 evidence
   ↓
normalize + authorize
   ↓
把有支持的 signal 映射到 AIMS / follow-up taxonomy
   ↓
记录 uncertainty、contradiction、limits
   ↓
验证 Lens structure 和 maturity
   ↓
version + maintenance
```

完整流程见 `docs/aims-lens-distillation-strategy-zh.md`。

## 6. Evidence governance

最简单的概念公式：

```text
effective contribution
= authorization gate
× quality
× recency
```

Authorization 是 binary eligibility，不是“低 confidence”。

Unauthorized evidence 的贡献必须是 0。

Quality 和 recency 只有在 evidence 通过资格门后才有意义。

这样可以避免一个“不允许使用但看起来很强”的 source，被一个高 confidence 数字重新救回来。

## 7. Hierarchical partial pooling

Company-specific evidence 往往很 sparse，所以 reference model 从 broader level 借力：

```text
generic
  ↓
archetype
  ↓
industry
  ↓
company / target context
```

这就是 partial pooling：broader knowledge 稳定 narrow estimate，但真正有足够 narrower evidence 时，结果仍然可以被 company evidence 推动。

## 8. Compatibility masking

不是所有 follow-up category 在所有 context 下都合理。

Compatibility rule 可以在 routing 和 prioritization 前，把当前 stage/context 下结构上不允许的 category 去掉。

这里的“去掉”不能解释成“企业永远不会问这个问题”。它只表示当前 model contract 不允许它进入这次 practice decision。

## 9. Routing 与 backoff

Reference routing sequence：

| Level | 含义 |
| --- | --- |
| L0 | full eligible parent context |
| L1 | drop one parent/context component |
| L2 | drop two |
| L3 | industry context |
| L4 | role/company archetype |
| L5 | generic practice |

L0 最具体，L5 最 generic。

Routing 会考虑 authorization、applicability、coverage 和 distance discount。Sparse evidence 因此不会自动得到最高 specificity。

## 10. Uncertainty、data support 与 abstention

AIMS Lens Engine 的原则是把 uncertainty 暴露出来，而不是用 fluent language 把它藏起来。

`data_support` 是 effective evidence mass 的摘要，不是 employer behavior 或 interview success 的概率。

当 justified support 不够、没有 valid route、或者没有 compatible category 时，可以触发 `abstention`。

一个系统能够明确说“我没有足够 evidence 让这个结论更 company-specific”，比永远给出自信答案更可靠。

## 11. Maturity

Research-facing maturity：

- `exploratory`
- `reviewed_practice`
- `evaluation_ready`
- `empirically_supported`

这些状态说明 review/evidence 到了什么程度。`empirically_supported` 必须通过真实 empirical evaluation 获得，不能等同于“内部批准”。

## 12. 与 JobACE 的关系

JobACE 是 first deep reference integration。

AIMS Lens Engine 可以决定并解释 practice priority；JobACE 可以把这个结果转成候选人的 learning loop：

```text
practice
  → 收到 evidence-linked feedback
  → 修改
  → 再答
  → track improvement
```

因此，Lens Engine 是 reasoning/governance layer；JobACE 是可以提供 interaction、coaching、history、progress tracking 的 reference client。

AIMS Lens Engine 的架构不依赖 JobACE。

## 13. Research core 不做什么

Manuscript research core 不：

- 为雇主 rank candidate；
- 推荐 hire / reject；
- 推断 protected trait；
- 声称拥有 confidential employer access；
- 承诺 employment outcome；
- 把 company Lens 说成企业 official rubric。

更广历史概念单独记录，不属于 paper claim。

## 14. Reproducibility

Reviewer 可以运行：

```bash
python tools/validate_paper_artifact.py
python -m unittest discover -s tests -v
python tools/run_paper_artifact_demo.py
```

Reference implementation 特意保持小型、dependency-free。

它证明数学规范有可执行 counterpart，但不能代替 empirical validation。

## 15. Public 与 protected information

Public-safe 内容可以包括 schema、protocol、synthetic example、public Lens asset、evidence standard 和 reference code。

Protected material 包括真实 candidate data、tenant-private configuration、confidential company evidence、production credential 和 proprietary production calibration state。

## 16. 最容易混淆的几个词

**Priority vs probability**

高 practice priority 不等于企业更大概率会问这个问题。

**Company Lens vs company truth**

Company Lens 是 evidence-bounded hypothesis，不是 employer official description。

**Support vs confidence**

Data support 总结 effective evidence mass；没有 calibration 时不应该随便把它叫 confidence。

**Backoff vs failure**

Backoff 是设计好的行为。它让系统降低没有依据的 specificity，同时仍然保持 useful。

**Abstention vs missing feature**

Abstention 是 governance feature，用于阻止 fabricated certainty。

## 17. 下一步看什么

- `README.zh-CN.md` — 项目总览
- `RESEARCH_BOUNDARY.md` — manuscript scope
- `docs/aims-lens-distillation-strategy-zh.md` — Lens construction
- `docs/PAPER_TO_CODE_MAP.md` — equation / code traceability
- `REPRODUCIBILITY.md` — reviewer execution path
- `docs/DOCUMENTATION_GOVERNANCE.zh-CN.md` — 双语一致性规范
