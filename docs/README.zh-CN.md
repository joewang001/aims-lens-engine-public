<!-- doc-parity: id=documentation-hub; version=1.2; language=zh-CN; companion=README.md -->
# AIMS Lens Engine 文档中心

[English](README.md) | [中文](README.zh-CN.md)

`docs/` 下的文件承担不同角色，不能把所有文件都当成同一级别的“产品事实”。

## 文档分层

| 层级 | 作用 | 主要文件 |
| --- | --- | --- |
| **Research boundary** | 定义论文做什么、不做什么、能声称什么 | `../RESEARCH_BOUNDARY.md`, `../REPRODUCIBILITY.md` |
| **Research implementation** | 把公式、算法、schema、test、demo 对应到代码 | `PAPER_TO_CODE_MAP.md`, `MATH_TO_CODE_COMPLETENESS_AUDIT.md` |
| **Lens distillation** | 说明证据怎样成为受治理的 practice Lens | `aims-lens-distillation-strategy-zh.md` |
| **Public Lens operations** | 维护 public-safe supporting Lens assets | `public-lens-operations-plan.md`, `public-lens-refresh-and-expansion.md` |
| **Product/history boundary** | 保存更广或历史概念，但不把它们变成论文 claim | `broader-product/README.zh-CN.md`, `../legacy/` |
| **Wiki source** | 面向 GitHub Wiki / onboarding 的易读说明 | `wiki/AIMS_LENS_ENGINE_WIKI.zh-CN.md` |

## Canonical 双语 pair

英文是 public research wording 的 canonical document；中文是 semantic-equivalent companion。

| English | 中文 |
| --- | --- |
| `../README.md` | `../README.zh-CN.md` |
| `README.md` | `README.zh-CN.md` |
| `DOCUMENTATION_GOVERNANCE.md` | `DOCUMENTATION_GOVERNANCE.zh-CN.md` |
| `aims-lens-distillation-strategy.md` | `aims-lens-distillation-strategy-zh.md` |
| `wiki/AIMS_LENS_ENGINE_WIKI.md` | `wiki/AIMS_LENS_ENGINE_WIKI.zh-CN.md` |
| `broader-product/README.md` | `broader-product/README.zh-CN.md` |

在 repository root 运行：

```bash
python tools/validate_documentation_alignment.py
```

可以检查 pair metadata 和共享的 machine-readable terminology。

## 新 reviewer 建议阅读顺序

1. `../README.md`
2. `../RESEARCH_BOUNDARY.md`
3. `aims-lens-distillation-strategy.md`
4. `PAPER_TO_CODE_MAP.md`
5. `../REPRODUCIBILITY.md`
6. `wiki/AIMS_LENS_ENGINE_WIKI.md`

## Authority rule

如果 broader product / historical document 与论文 research boundary 冲突，**论文相关 claim 以 paper-facing research documentation 为准**。

如果英文和中文 companion 在规范性含义上发生冲突，应在同一个 PR 中修正两边，而不是选择其中一个作为方便的解释。
