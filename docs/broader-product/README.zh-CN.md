<!-- doc-parity: id=broader-product-boundary; version=1.2; language=zh-CN; companion=README.md -->
# 更广产品与历史扩展边界

[English](README.md) | [中文](README.zh-CN.md)

这个目录用于说明 **manuscript research core** 与 AIMS Lens Engine / JobACE 历史开发过程中更广产品构想之间的边界。

## Manuscript core

论文对应的核心是 candidate-side interview practice：

- evidence-governed Lens representation；
- probabilistic practice-priority inference；
- compatibility constraints；
- L0–L5 routing / backoff；
- uncertainty 和 abstention；
- provenance、explanation、auditability。

## 不属于 manuscript core 的内容

Repository history 中曾经探索过 employer-side screening、reviewer assistance、enterprise decision workflow 和其他更广产品用途。

这些材料：

- 不属于 paper artifact；
- 不受论文 empirical claim 的支持；
- 不能被引用成“AIMS Lens Engine 已经是雇主招聘决策系统”的证据；
- 如果未来重新开发，可能需要完全不同的法律、公平性、validation 和 human-oversight 分析。

历史代码或 schema 可以保留在 `legacy/`，这样不会抹去开发 provenance。

## 为什么不简单删除历史

把所有早期产品构想删掉，看起来会更“干净”，但会降低系统演化过程的透明度。

更合理的方式是：

1. 保留历史 artifact；
2. 清楚标记；
3. 从 paper artifact 中排除；
4. public research API 保持 candidate-side；
5. 任何未来 extension 都按自己的 governance / evidence requirement 单独评估。

一个历史 extension 的存在，不等于当前 product claim。
