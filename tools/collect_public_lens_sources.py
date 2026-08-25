#!/usr/bin/env python3
"""Create public-safe source packets for AIMS public lens maintenance.

The script is deliberately conservative. It can generate seed packets for the
approved expansion backlog and can normalize externally collected packets from
a sourcing agent. It does not copy source bodies or scrape pages.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "docs" / "refresh-candidates" / "source-packets"
COMPANY_LENSES = ROOT / "company_lenses"


SOURCE_POLICY = {
    "public_safe": True,
    "contains_private_material": False,
    "contains_candidate_data": False,
    "contains_raw_job_posting_body": False,
    "contains_paywalled_text": False,
}


CATALOG: dict[str, dict[str, Any]] = {
    "nvidia": {
        "company": "NVIDIA",
        "industries": ["technology", "ai infrastructure", "semiconductors", "cloud computing"],
        "regions": ["north_america", "global"],
        "stage": "large public AI infrastructure and semiconductor company",
        "sources": [
            {
                "source_type": "official_company",
                "title": "NVIDIA company homepage",
                "url": "https://www.nvidia.com/",
                "confidence": 0.82,
                "public_safe_signal": "NVIDIA publicly positions itself around accelerated computing, AI infrastructure, graphics, simulation, and platforms that help organizations build and deploy intelligent systems.",
                "dimensions": ["company_says", "evidence_valued"],
            },
            {
                "source_type": "official_careers",
                "title": "NVIDIA careers page",
                "url": "https://www.nvidia.com/en-us/about-nvidia/careers/",
                "confidence": 0.78,
                "public_safe_signal": "NVIDIA careers messaging emphasizes ambitious technical work, collaboration across disciplines, and impact through products used by developers, researchers, enterprises, and creators.",
                "dimensions": ["company_judges", "evidence_valued", "role_variation"],
            },
            {
                "source_type": "official_investor_relations",
                "title": "NVIDIA investor relations",
                "url": "https://investor.nvidia.com/",
                "confidence": 0.76,
                "public_safe_signal": "Investor materials frame NVIDIA around accelerated computing platforms, ecosystem adoption, product cycles, and execution in fast-moving infrastructure markets.",
                "dimensions": ["company_says", "risk_warnings"],
            },
        ],
        "questions": [
            {
                "type": "behavioral",
                "generated_question": "Tell me about a time you turned a difficult technical or product problem into a measurable user or business result.",
                "aims_dimensions": ["analytical_problem_solving", "ownership_execution", "impact_results"],
                "strong_answer_signals": [
                    "Defines the technical or product problem clearly.",
                    "Explains concrete ownership and tradeoffs.",
                    "Connects the work to measurable user, platform, or business impact.",
                    "Shows what changed after feedback or new evidence.",
                ],
            }
        ],
        "role_overlays": [
            {
                "role_slug": "ai_infrastructure_engineering",
                "role_family": "AI infrastructure engineering",
                "signals": [
                    "Explains systems tradeoffs across model, data, hardware, latency, cost, and reliability.",
                    "Connects engineering decisions to developer, researcher, enterprise, or platform outcomes.",
                ],
            }
        ],
    },
    "accenture": {
        "company": "Accenture",
        "industries": ["consulting", "professional services", "technology services"],
        "regions": ["north_america", "global"],
        "stage": "large public consulting and technology services company",
        "sources": [
            {
                "source_type": "official_company",
                "title": "Accenture company homepage",
                "url": "https://www.accenture.com/us-en",
                "confidence": 0.8,
                "public_safe_signal": "Accenture publicly emphasizes reinvention, consulting, technology, operations, and helping clients apply digital, cloud, data, and AI capabilities.",
                "dimensions": ["company_says", "evidence_valued"],
            },
            {
                "source_type": "official_careers",
                "title": "Accenture careers page",
                "url": "https://www.accenture.com/us-en/careers",
                "confidence": 0.76,
                "public_safe_signal": "Careers messaging points toward client impact, continuous learning, collaboration, inclusion, and applying technology to practical business problems.",
                "dimensions": ["company_judges", "company_asks", "role_variation"],
            },
        ],
        "questions": [
            {
                "type": "consulting_behavioral",
                "generated_question": "Describe a client or stakeholder problem where you had to convert ambiguity into a practical execution plan.",
                "aims_dimensions": ["structured_thinking", "collaboration_communication", "ownership_execution"],
                "strong_answer_signals": [
                    "Structures the ambiguous situation into clear workstreams.",
                    "Shows stakeholder communication and tradeoff handling.",
                    "Defines execution steps and evidence of progress.",
                    "Connects the result to client or business value.",
                ],
            }
        ],
        "role_overlays": [
            {
                "role_slug": "technology_consulting",
                "role_family": "Technology consulting",
                "signals": [
                    "Frames technology choices through client outcomes and implementation constraints.",
                    "Balances structured analysis, communication, and delivery ownership.",
                ],
            }
        ],
    },
    "salesforce": {
        "company": "Salesforce",
        "industries": ["technology", "enterprise software", "crm", "saas"],
        "regions": ["north_america", "global"],
        "stage": "large public enterprise software company",
        "sources": [
            {
                "source_type": "official_company",
                "title": "Salesforce company homepage",
                "url": "https://www.salesforce.com/",
                "confidence": 0.8,
                "public_safe_signal": "Salesforce publicly positions itself around customer relationship management, trusted enterprise AI, data, automation, and customer success across business functions.",
                "dimensions": ["company_says", "evidence_valued"],
            },
            {
                "source_type": "official_careers",
                "title": "Salesforce careers page",
                "url": "https://careers.salesforce.com/",
                "confidence": 0.76,
                "public_safe_signal": "Careers messaging emphasizes customer impact, trust, innovation, equality, learning, and work that helps organizations connect with customers.",
                "dimensions": ["company_judges", "company_asks", "role_variation"],
            },
        ],
        "questions": [
            {
                "type": "behavioral",
                "generated_question": "Tell me about a time you improved a process, product, or customer experience while protecting trust and reliability.",
                "aims_dimensions": ["impact_results", "structured_thinking", "collaboration_communication"],
                "strong_answer_signals": [
                    "Names the customer or business outcome.",
                    "Explains the trust or reliability constraint.",
                    "Shows cross-functional execution.",
                    "Measures the resulting improvement.",
                ],
            }
        ],
        "role_overlays": [
            {
                "role_slug": "customer_platform",
                "role_family": "Customer platform roles",
                "signals": [
                    "Links technical or operational decisions to customer success and trusted adoption.",
                    "Shows practical judgment around data, automation, reliability, and stakeholder alignment.",
                ],
            }
        ],
    },
}


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug:
        raise ValueError("empty slug")
    return slug


def source_id(slug: str, source_type: str, index: int) -> str:
    prefix = slug.upper().replace("-", "_")
    short_type = {
        "official_company": "OFFICIAL",
        "official_careers": "CAREERS",
        "official_investor_relations": "IR",
        "official_engineering_blog": "ENG",
        "official_product_blog": "PRODUCT",
        "official_leadership_letter": "LEADERSHIP",
        "public_community_aggregate": "COMMUNITY",
    }.get(source_type, "SOURCE")
    return f"{prefix}-{short_type}-{index:03d}"


def build_packet(slug: str, *, accessed_date: str) -> dict[str, Any]:
    if slug not in CATALOG:
        raise KeyError(f"unknown expansion candidate: {slug}")
    spec = CATALOG[slug]
    sources = []
    for index, source in enumerate(spec["sources"], start=1):
        item = dict(source)
        item["evidence_id"] = source_id(slug, str(source["source_type"]), index)
        item["date_accessed"] = accessed_date
        sources.append(item)

    return {
        "company_slug": slug,
        "company": spec["company"],
        "collected_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_policy": dict(SOURCE_POLICY),
        "company_profile": {
            "industries": spec["industries"],
            "regions": spec["regions"],
            "company_stage": spec["stage"],
        },
        "sources": sources,
        "lens_updates": {
            "culture_principles": [],
            "hiring_signals": [],
            "anti_signals": [],
            "questions": spec["questions"],
            "role_overlays": spec["role_overlays"],
        },
    }


def normalize_packet(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"packet must be a JSON object: {path}")
    slug = slugify(str(payload.get("company_slug") or payload.get("company") or path.stem))
    payload["company_slug"] = slug
    payload.setdefault("collected_at", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    payload.setdefault("source_policy", dict(SOURCE_POLICY))
    payload.setdefault("lens_updates", {})
    for key in ("culture_principles", "hiring_signals", "anti_signals", "questions", "role_overlays"):
        payload["lens_updates"].setdefault(key, [])
    return payload


def write_packet(packet: dict[str, Any], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = str(packet["company_slug"])
    path = output_dir / f"{slug}.source-packet.json"
    path.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return path


def choose_expansion(limit: int) -> list[str]:
    existing = {path.name for path in COMPANY_LENSES.iterdir() if path.is_dir() and not path.name.startswith("_")}
    return [slug for slug in CATALOG if slug not in existing][:limit]


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect public-safe lens source packets.")
    parser.add_argument("--company", action="append", help="Expansion catalog company slug to collect.")
    parser.add_argument("--expansion-limit", type=int, default=0, help="Collect this many approved backlog companies.")
    parser.add_argument("--input-packet", type=Path, action="append", help="Normalize an externally collected packet.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--date-accessed", default=datetime.now(timezone.utc).date().isoformat())
    args = parser.parse_args()

    packets: list[dict[str, Any]] = []
    for path in args.input_packet or []:
        packets.append(normalize_packet(path))
    for slug in args.company or []:
        packets.append(build_packet(slugify(slug), accessed_date=args.date_accessed))
    if args.expansion_limit:
        packets.extend(build_packet(slug, accessed_date=args.date_accessed) for slug in choose_expansion(args.expansion_limit))

    if not packets:
        raise SystemExit("No packets requested. Use --company, --expansion-limit, or --input-packet.")

    for packet in packets:
        path = write_packet(packet, args.output_dir)
        print(f"source_packet={path.relative_to(ROOT)} company={packet['company']} sources={len(packet['sources'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
