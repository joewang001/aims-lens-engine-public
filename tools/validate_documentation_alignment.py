#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXPECTED_DOC_SYSTEM_VERSION = "1.2"

PAIRS = [
    ("README.md", "README.zh-CN.md"),
    ("docs/README.md", "docs/README.zh-CN.md"),
    ("docs/DOCUMENTATION_GOVERNANCE.md", "docs/DOCUMENTATION_GOVERNANCE.zh-CN.md"),
    ("docs/aims-lens-distillation-strategy.md", "docs/aims-lens-distillation-strategy-zh.md"),
    ("docs/wiki/AIMS_LENS_ENGINE_WIKI.md", "docs/wiki/AIMS_LENS_ENGINE_WIKI.zh-CN.md"),
    ("docs/broader-product/README.md", "docs/broader-product/README.zh-CN.md"),
]

META_RE = re.compile(
    r"^<!-- doc-parity: id=(?P<id>[^;]+); version=(?P<version>[^;]+); "
    r"language=(?P<language>[^;]+); companion=(?P<companion>[^ ]+) -->$"
)

SHARED_TOKENS = [
    "candidate-side",
    "evidence-bounded",
    "JobACE",
    "L0",
    "L5",
    "abstention",
]

MATURITY_TOKENS = [
    "exploratory",
    "reviewed_practice",
    "evaluation_ready",
    "empirically_supported",
]

CURRENT_FACT_TOKENS = [
    "0.10.0-paper-v1.4",
    "v1.4",
    "c18899b469e1d579391306872d5834ebf6e3caf3",
    "v0.10.0-paper-v1.4",
    "v0.9.2-paper-v1.3",
]

DEPRECATED_CANONICAL_TOKENS = [
    "v0.8.1-public-core",
    "/v1/screening-report",
    "/v1/screen-candidate",
]


def fail(message: str) -> None:
    raise AssertionError(message)


def read(path: str) -> str:
    target = ROOT / path
    if not target.exists():
        fail(f"missing documentation file: {path}")
    return target.read_text(encoding="utf-8")


def metadata(path: str, text: str) -> dict[str, str]:
    first = text.splitlines()[0].strip() if text.splitlines() else ""
    match = META_RE.match(first)
    if not match:
        fail(f"missing or malformed doc-parity metadata: {path}")
    return match.groupdict()


def main() -> int:
    for en_path, zh_path in PAIRS:
        en_text = read(en_path)
        zh_text = read(zh_path)
        en_meta = metadata(en_path, en_text)
        zh_meta = metadata(zh_path, zh_text)

        if en_meta["id"] != zh_meta["id"]:
            fail(f"pair id mismatch: {en_path} vs {zh_path}")
        if en_meta["version"] != zh_meta["version"]:
            fail(f"semantic version mismatch: {en_path} vs {zh_path}")
        if en_meta["version"] != EXPECTED_DOC_SYSTEM_VERSION:
            fail(f"unexpected documentation-system version in {en_path}: {en_meta['version']}")
        if en_meta["language"] != "en":
            fail(f"English pair member must declare language=en: {en_path}")
        if zh_meta["language"] != "zh-CN":
            fail(f"Chinese pair member must declare language=zh-CN: {zh_path}")

        if Path(en_meta["companion"]).name != Path(zh_path).name:
            fail(f"English companion metadata mismatch: {en_path}")
        if Path(zh_meta["companion"]).name != Path(en_path).name:
            fail(f"Chinese companion metadata mismatch: {zh_path}")

    # Core overview and strategy pairs must preserve shared machine-readable concepts.
    for path in [
        "README.md",
        "README.zh-CN.md",
        "docs/aims-lens-distillation-strategy.md",
        "docs/aims-lens-distillation-strategy-zh.md",
        "docs/wiki/AIMS_LENS_ENGINE_WIKI.md",
        "docs/wiki/AIMS_LENS_ENGINE_WIKI.zh-CN.md",
    ]:
        text = read(path)
        for token in SHARED_TOKENS:
            if token not in text:
                fail(f"{path} is missing shared normative token: {token}")

    for path in [
        "README.md",
        "README.zh-CN.md",
        "docs/aims-lens-distillation-strategy.md",
        "docs/aims-lens-distillation-strategy-zh.md",
    ]:
        text = read(path)
        for token in MATURITY_TOKENS:
            if token not in text:
                fail(f"{path} is missing maturity token: {token}")

    # The maintained root READMEs must carry the same v1.4 candidate/freeze identity facts.
    for path in ["README.md", "README.zh-CN.md"]:
        text = read(path)
        for token in CURRENT_FACT_TOKENS:
            if token not in text:
                fail(f"{path} is missing current v1.4 release fact token: {token}")
        for token in DEPRECATED_CANONICAL_TOKENS:
            if token in text:
                fail(f"{path} contains deprecated canonical content: {token}")

    legacy_root = read("README_ZH.md")
    if "README.zh-CN.md" not in legacy_root:
        fail("README_ZH.md must point readers to README.zh-CN.md")
    if "v0.8.1-public-core" in legacy_root:
        fail("README_ZH.md still exposes the deprecated public-core version as current")

    # README must remain a substantive landing page, not only a navigation index.
    landing_requirements = {
        "README.md": [
            "Understand AIMS Lens Engine in five minutes",
            "A simple mental model",
            "Example: candidate-side use",
            "How this differs from a generic LLM or question bank",
            "Relationship to JobACE",
            "Research boundary",
        ],
        "README.zh-CN.md": [
            "5 分钟理解 AIMS Lens Engine",
            "一个最容易理解的模型",
            "一个 candidate-side 使用例子",
            "和通用 LLM / 题库有什么区别",
            "与 JobACE 的关系",
            "论文研究边界",
        ],
    }
    for path, markers in landing_requirements.items():
        text = read(path)
        for marker in markers:
            if marker not in text:
                fail(f"{path} is missing substantive README marker: {marker}")

    if not (ROOT / "docs/archive/README.md").exists():
        fail("missing docs/archive/README.md")

    # The legacy filename must no longer present employer-side screening as the canonical playbook.
    legacy_playbook = read("docs/distillation-playbook.md").lower()
    if "canonical distillation documentation has moved" not in legacy_playbook:
        fail("docs/distillation-playbook.md must be a compatibility notice")
    if "only approved lenses may be used for b2b screening" in legacy_playbook:
        fail("legacy screening rule remains in canonical path")

    print("DOCUMENTATION_ALIGNMENT_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
