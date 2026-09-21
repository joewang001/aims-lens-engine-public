<!-- doc-parity: id=documentation-governance; version=1.2; language=zh-CN; companion=DOCUMENTATION_GOVERNANCE.md -->
# 文档治理规范

[English](DOCUMENTATION_GOVERNANCE.md) | [中文](DOCUMENTATION_GOVERNANCE.zh-CN.md)

## 基本规则

AIMS Lens Engine 的 public research documentation 以英文为 canonical language；中文 companion 按 **semantic parity（语义等价）** 持续维护。

Semantic parity 的意思是：事实、研究边界、定义、数学含义、版本状态、API 行为、治理要求、局限和 empirical status 必须一致。它**不要求**逐句翻译，也不要求两个文件字数完全一样。

## 哪些内容必须语义一致

以下内容属于 normative information，不能中英文各说一套：

- Lens 是 **versioned, evidence-bounded practice hypothesis**；
- research core 是 candidate-side interview practice；
- named-company Lens 不是 employer ground truth；
- evidence authorization 是 hard gate；
- L0–L5 routing / backoff 的含义；
- uncertainty、data support、abstention 的含义；
- maturity：`exploratory`、`reviewed_practice`、`evaluation_ready`、`empirically_supported`；
- JobACE 是 first deep reference integration，而不是架构前提；
- empirical status 和 limitations；
- privacy、fairness、protected data、public/private boundary；
- version number、frozen release reference、API/schema 名称、license 和 citation instruction。

## 哪些内容可以不同

中英文可以在以下方面采用不同写法：

- 句式、语感和术语解释方式；
- 帮助理解的例子；
- 开头使用的比喻；
- 段落长度；
- 非规范性案例的排列顺序；
- 针对不同语言读者增加的解释。

例如中文可以更口语地解释“为什么要 backoff”，英文可以更学术地解释 evidential support；只要最后没有形成不同 claim 即可。

## Pair metadata

受维护的双语 pair 文件第一行使用隐藏标记：

```text
<!-- doc-parity: id=<stable-id>; version=<semantic-version>; language=<en|zh-CN>; companion=<path> -->
```

同一 pair 的 `id` 和 semantic `version` 必须一致。

## 更新流程

凡是改变规范性含义的文档修改：

1. 先修改 English canonical document；
2. 同一个 change set 中修改中文 companion；
3. 如果含义发生变化，提升 pair semantic version；
4. 运行 `python tools/validate_documentation_alignment.py`；
5. 如果修改了英文 README 或 paper-facing research document，同时运行 paper validation；
6. 在 PR 中说明重要术语或边界变化。

单纯 typo / formatting 修复，如果没有改变含义，可以不提升 semantic version。

## Wiki 规则

Wiki 的 canonical source 放在 `docs/wiki/`。GitHub live Wiki 可以从这里复制发布，但 repository 中的 source 才是可审计版本。

不要只在 live Wiki 中创造新的 normative definition；如果必须修改，应同步更新 `docs/wiki/` 和对应语言 companion。

## Broader product / historical documentation

Employer-side 或其他更广产品概念可以为了 provenance 保留在 `docs/broader-product/` 或 `legacy/`。这些文档必须明确声明：

- 它们不属于 manuscript research core；
- 不能被当作论文 claim 的证据。

## 冲突处理顺序

如果文件之间出现不一致，解释 manuscript 时按以下优先级：

1. frozen manuscript 和 `RESEARCH_BOUNDARY.md`；
2. paper artifact manifest 和 paper-facing API/schema；
3. `README.md` 和 research implementation maps；
4. canonical distillation / Wiki documentation；
5. broader product、operations 和 historical documents。

这个优先级不是为了允许矛盾长期存在；发现矛盾后应该修正文档。
