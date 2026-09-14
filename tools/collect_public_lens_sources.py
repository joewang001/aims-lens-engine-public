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
    "johnson-johnson": {
        "company": "Johnson & Johnson",
        "industries": ["healthcare", "pharma", "medical devices", "life sciences"],
        "regions": ["north_america", "global"],
        "stage": "large public healthcare, pharmaceutical, and medical technology company",
        "sources": [
            {
                "source_type": "official_company",
                "title": "Johnson & Johnson company homepage",
                "url": "https://www.jnj.com/",
                "confidence": 0.8,
                "public_safe_signal": "Johnson & Johnson publicly frames its work around health, medicine, medical technology, science, and improving outcomes for patients and communities.",
                "dimensions": ["company_says", "evidence_valued"],
            },
            {
                "source_type": "official_careers",
                "title": "Johnson & Johnson careers page",
                "url": "https://www.careers.jnj.com/",
                "confidence": 0.72,
                "public_safe_signal": "Careers messaging points toward purpose-driven healthcare work, collaboration, learning, innovation, and impact across science, technology, operations, and commercial roles.",
                "dimensions": ["company_judges", "company_asks", "role_variation"],
            },
            {
                "source_type": "official_investor_relations",
                "title": "Johnson & Johnson investor relations",
                "url": "https://www.investor.jnj.com/",
                "confidence": 0.7,
                "public_safe_signal": "Investor materials provide public context for portfolio focus, regulated execution, innovation priorities, and risk factors in healthcare markets.",
                "dimensions": ["company_says", "risk_warnings"],
            },
        ],
        "questions": [
            {
                "type": "regulated_healthcare_behavioral",
                "generated_question": "Tell me about a time you improved an outcome while working within a regulated, safety-sensitive, or quality-sensitive environment.",
                "aims_dimensions": ["structured_thinking", "ownership_execution", "impact_results"],
                "strong_answer_signals": [
                    "Defines the patient, customer, quality, or compliance stakes clearly.",
                    "Explains how evidence and constraints shaped the decision.",
                    "Shows ownership without bypassing safety or review standards.",
                    "Connects the work to a measurable quality, user, or operational result.",
                ],
            }
        ],
        "role_overlays": [
            {
                "role_slug": "healthcare_operations",
                "role_family": "Healthcare operations and product roles",
                "signals": [
                    "Balances speed, quality, compliance, and stakeholder trust.",
                    "Connects operational or product decisions to patient, clinician, customer, or community outcomes.",
                ],
            }
        ],
    },
    "enbridge": {
        "company": "Enbridge",
        "industries": ["energy", "utilities", "infrastructure", "sustainability"],
        "regions": ["canada", "north_america"],
        "stage": "large North American energy infrastructure and utilities company",
        "sources": [
            {
                "source_type": "official_company",
                "title": "Enbridge company homepage",
                "url": "https://www.enbridge.com/",
                "confidence": 0.8,
                "public_safe_signal": "Enbridge publicly describes its work around energy infrastructure, reliability, safety, energy delivery, and the transition toward lower-emission energy systems.",
                "dimensions": ["company_says", "evidence_valued"],
            },
            {
                "source_type": "official_careers",
                "title": "Enbridge careers page",
                "url": "https://www.enbridge.com/careers",
                "confidence": 0.76,
                "public_safe_signal": "Careers messaging emphasizes safety, inclusion, technical and operational work, community impact, and opportunities across engineering, operations, business, and field roles.",
                "dimensions": ["company_judges", "company_asks", "role_variation"],
            },
            {
                "source_type": "official_investor_relations",
                "title": "Enbridge investment center",
                "url": "https://www.enbridge.com/investment-center",
                "confidence": 0.76,
                "public_safe_signal": "Investor materials provide public context for infrastructure assets, capital allocation, risk management, reliability, growth, and energy transition priorities.",
                "dimensions": ["company_says", "risk_warnings"],
            },
        ],
        "questions": [
            {
                "type": "operations_behavioral",
                "generated_question": "Describe a situation where you had to make a practical decision while balancing reliability, safety, cost, and stakeholder impact.",
                "aims_dimensions": ["analytical_problem_solving", "ownership_execution", "collaboration_communication"],
                "strong_answer_signals": [
                    "Names the operational risk and affected stakeholders.",
                    "Explains the tradeoff between reliability, safety, cost, and timing.",
                    "Shows coordination across technical and non-technical groups.",
                    "Defines how the result was monitored or improved.",
                ],
            }
        ],
        "role_overlays": [
            {
                "role_slug": "energy_infrastructure",
                "role_family": "Energy infrastructure roles",
                "signals": [
                    "Treats safety, reliability, and community impact as core decision constraints.",
                    "Uses evidence to balance operational execution with long-term infrastructure outcomes.",
                ],
            }
        ],
    },
    "walmart": {
        "company": "Walmart",
        "industries": ["retail", "ecommerce", "logistics", "consumer services"],
        "regions": ["north_america", "global"],
        "stage": "large public retail, ecommerce, and supply chain company",
        "sources": [
            {
                "source_type": "official_company",
                "title": "Walmart corporate homepage",
                "url": "https://corporate.walmart.com/",
                "confidence": 0.8,
                "public_safe_signal": "Walmart publicly emphasizes serving customers, everyday value, stores, ecommerce, supply chain scale, communities, and technology-enabled retail operations.",
                "dimensions": ["company_says", "evidence_valued"],
            },
            {
                "source_type": "official_careers",
                "title": "Walmart careers page",
                "url": "https://careers.walmart.com/",
                "confidence": 0.76,
                "public_safe_signal": "Careers messaging points toward customer service, frontline execution, logistics, technology, growth opportunities, and operational teamwork at large scale.",
                "dimensions": ["company_judges", "company_asks", "role_variation"],
            },
            {
                "source_type": "official_investor_relations",
                "title": "Walmart investor relations",
                "url": "https://stock.walmart.com/",
                "confidence": 0.74,
                "public_safe_signal": "Investor materials give public context for omnichannel retail, margin discipline, supply chain investment, digital growth, and operating scale.",
                "dimensions": ["company_says", "risk_warnings"],
            },
        ],
        "questions": [
            {
                "type": "retail_operations_behavioral",
                "generated_question": "Tell me about a time you improved a customer or operational metric in a high-volume environment.",
                "aims_dimensions": ["impact_results", "ownership_execution", "analytical_problem_solving"],
                "strong_answer_signals": [
                    "Identifies the customer or operational metric.",
                    "Explains the root cause and action taken.",
                    "Shows how teams or frontline constraints were handled.",
                    "Quantifies the improvement or learning.",
                ],
            }
        ],
        "role_overlays": [
            {
                "role_slug": "retail_operations",
                "role_family": "Retail operations and supply chain roles",
                "signals": [
                    "Links decisions to customer value, availability, cost, and operational consistency.",
                    "Shows execution discipline in high-volume, cross-functional environments.",
                ],
            }
        ],
    },
    "costco": {
        "company": "Costco",
        "industries": ["retail", "wholesale", "consumer services", "operations"],
        "regions": ["north_america", "global"],
        "stage": "large public membership warehouse retail company",
        "sources": [
            {
                "source_type": "official_company",
                "title": "Costco homepage",
                "url": "https://www.costco.com/",
                "confidence": 0.78,
                "public_safe_signal": "Costco publicly presents a membership warehouse model centered on value, quality, operations, member trust, and efficient merchandising.",
                "dimensions": ["company_says", "evidence_valued"],
            },
            {
                "source_type": "official_careers",
                "title": "Costco jobs page",
                "url": "https://www.costco.com/jobs.html",
                "confidence": 0.74,
                "public_safe_signal": "Careers materials provide public context for warehouse operations, service roles, promotion pathways, benefits, and team-based execution.",
                "dimensions": ["company_judges", "company_asks", "role_variation"],
            },
            {
                "source_type": "official_investor_relations",
                "title": "Costco investor relations",
                "url": "https://investor.costco.com/",
                "confidence": 0.7,
                "public_safe_signal": "Investor materials offer public context for membership economics, merchandising discipline, warehouse growth, and operating performance.",
                "dimensions": ["company_says", "risk_warnings"],
            },
        ],
        "questions": [
            {
                "type": "service_operations_behavioral",
                "generated_question": "Describe a time you protected customer trust while improving speed, quality, or cost in an operating process.",
                "aims_dimensions": ["ownership_execution", "impact_results", "collaboration_communication"],
                "strong_answer_signals": [
                    "Names the customer or member trust issue.",
                    "Explains the process constraint and improvement path.",
                    "Shows practical coordination with the people doing the work.",
                    "Connects the change to service, quality, or cost evidence.",
                ],
            }
        ],
        "role_overlays": [
            {
                "role_slug": "membership_retail",
                "role_family": "Membership retail roles",
                "signals": [
                    "Balances member value, process reliability, and disciplined execution.",
                    "Shows respect for frontline realities and measurable service outcomes.",
                ],
            }
        ],
    },
    "tesla": {
        "company": "Tesla",
        "industries": ["automotive", "energy", "manufacturing", "ai"],
        "regions": ["north_america", "global"],
        "stage": "large public electric vehicle, energy, manufacturing, and AI company",
        "sources": [
            {
                "source_type": "official_company",
                "title": "Tesla homepage",
                "url": "https://www.tesla.com/",
                "confidence": 0.76,
                "public_safe_signal": "Tesla publicly positions itself around electric vehicles, energy products, manufacturing, software, autonomy, and accelerating sustainable energy.",
                "dimensions": ["company_says", "evidence_valued"],
            },
            {
                "source_type": "official_careers",
                "title": "Tesla careers page",
                "url": "https://www.tesla.com/careers",
                "confidence": 0.72,
                "public_safe_signal": "Careers messaging emphasizes fast execution, engineering, manufacturing, operations, software, energy, and mission-aligned work across technical and business functions.",
                "dimensions": ["company_judges", "company_asks", "role_variation"],
            },
            {
                "source_type": "official_investor_relations",
                "title": "Tesla investor relations",
                "url": "https://ir.tesla.com/",
                "confidence": 0.74,
                "public_safe_signal": "Investor materials give public context for vehicle programs, energy products, manufacturing scale, software, margins, delivery volatility, and execution risk.",
                "dimensions": ["company_says", "risk_warnings"],
            },
        ],
        "questions": [
            {
                "type": "execution_behavioral",
                "generated_question": "Tell me about a time you moved quickly on a difficult technical or operating problem without losing control of quality or risk.",
                "aims_dimensions": ["analytical_problem_solving", "ownership_execution", "impact_results"],
                "strong_answer_signals": [
                    "Defines the time pressure and technical or operating constraint.",
                    "Explains the quality or risk control used while moving fast.",
                    "Shows direct ownership and iteration.",
                    "Measures the result and what changed afterward.",
                ],
            }
        ],
        "role_overlays": [
            {
                "role_slug": "manufacturing_and_autonomy",
                "role_family": "Manufacturing, software, and autonomy roles",
                "signals": [
                    "Connects speed of execution to measurable product, manufacturing, energy, or software outcomes.",
                    "Shows judgment around quality, reliability, safety, and system-level tradeoffs.",
                ],
            }
        ],
    },
    "pfizer": {
        "company": "Pfizer",
        "industries": ["healthcare", "pharma", "biotechnology", "life sciences"],
        "regions": ["north_america", "global"],
        "stage": "large public pharmaceutical and biotechnology company",
        "sources": [
            {
                "source_type": "official_company",
                "title": "Pfizer homepage",
                "url": "https://www.pfizer.com/",
                "confidence": 0.8,
                "public_safe_signal": "Pfizer publicly frames its work around medicines, vaccines, science, innovation, health outcomes, and bringing therapies to patients.",
                "dimensions": ["company_says", "evidence_valued"],
            },
            {
                "source_type": "official_careers",
                "title": "Pfizer careers page",
                "url": "https://www.pfizer.com/about/careers",
                "confidence": 0.76,
                "public_safe_signal": "Careers messaging emphasizes science, patient impact, inclusion, learning, cross-functional work, and roles across research, manufacturing, commercial, and enabling functions.",
                "dimensions": ["company_judges", "company_asks", "role_variation"],
            },
            {
                "source_type": "official_investor_relations",
                "title": "Pfizer investor relations",
                "url": "https://investors.pfizer.com/",
                "confidence": 0.7,
                "public_safe_signal": "Investor materials offer public context for research portfolio, product lifecycle, regulatory risk, commercial execution, and capital allocation.",
                "dimensions": ["company_says", "risk_warnings"],
            },
        ],
        "questions": [
            {
                "type": "life_sciences_behavioral",
                "generated_question": "Describe a time you used scientific, customer, or operating evidence to make a decision with real stakeholder impact.",
                "aims_dimensions": ["structured_thinking", "analytical_problem_solving", "impact_results"],
                "strong_answer_signals": [
                    "Clarifies the evidence base and uncertainty.",
                    "Explains how stakeholders or patients could be affected.",
                    "Shows cross-functional decision-making.",
                    "Links action to a concrete result or learning.",
                ],
            }
        ],
        "role_overlays": [
            {
                "role_slug": "life_sciences",
                "role_family": "Life sciences roles",
                "signals": [
                    "Uses evidence carefully under scientific, regulatory, commercial, or quality constraints.",
                    "Connects work to patient, provider, business, or public-health outcomes.",
                ],
            }
        ],
    },
    "deloitte": {
        "company": "Deloitte",
        "industries": ["consulting", "professional services", "technology services", "audit"],
        "regions": ["north_america", "global"],
        "stage": "large global professional services and consulting organization",
        "sources": [
            {
                "source_type": "official_company",
                "title": "Deloitte global homepage",
                "url": "https://www2.deloitte.com/global/en.html",
                "confidence": 0.78,
                "public_safe_signal": "Deloitte publicly describes work across consulting, audit, tax, risk, technology, transformation, and helping clients address complex business issues.",
                "dimensions": ["company_says", "evidence_valued"],
            },
            {
                "source_type": "official_careers",
                "title": "Deloitte global careers page",
                "url": "https://www.deloitte.com/global/en/careers.html",
                "confidence": 0.74,
                "public_safe_signal": "Careers messaging emphasizes client impact, learning, collaboration, inclusion, multidisciplinary work, and development across consulting and professional services roles.",
                "dimensions": ["company_judges", "company_asks", "role_variation"],
            },
        ],
        "questions": [
            {
                "type": "consulting_behavioral",
                "generated_question": "Tell me about a time you helped a stakeholder move from a complex problem to a practical recommendation and execution path.",
                "aims_dimensions": ["structured_thinking", "collaboration_communication", "impact_results"],
                "strong_answer_signals": [
                    "Structures the problem and assumptions clearly.",
                    "Explains stakeholder alignment and tradeoffs.",
                    "Connects recommendation to execution reality.",
                    "Shows evidence of client or business impact.",
                ],
            }
        ],
        "role_overlays": [
            {
                "role_slug": "professional_services",
                "role_family": "Professional services roles",
                "signals": [
                    "Combines structured analysis with client-ready communication.",
                    "Shows practical ownership across ambiguity, stakeholder pressure, and delivery constraints.",
                ],
            }
        ],
    },
    "ibm": {
        "company": "IBM",
        "industries": ["technology", "enterprise software", "cloud", "ai consulting"],
        "regions": ["north_america", "global"],
        "stage": "large public enterprise technology, cloud, AI, and consulting company",
        "sources": [
            {
                "source_type": "official_company",
                "title": "IBM homepage",
                "url": "https://www.ibm.com/",
                "confidence": 0.8,
                "public_safe_signal": "IBM publicly positions itself around hybrid cloud, AI, enterprise technology, consulting, research, automation, and trusted transformation for organizations.",
                "dimensions": ["company_says", "evidence_valued"],
            },
            {
                "source_type": "official_careers",
                "title": "IBM careers page",
                "url": "https://www.ibm.com/careers",
                "confidence": 0.76,
                "public_safe_signal": "Careers messaging emphasizes technology, consulting, learning, client work, inclusion, and opportunities across engineering, sales, research, operations, and services.",
                "dimensions": ["company_judges", "company_asks", "role_variation"],
            },
            {
                "source_type": "official_investor_relations",
                "title": "IBM investor relations",
                "url": "https://www.ibm.com/investor/",
                "confidence": 0.76,
                "public_safe_signal": "Investor materials provide public context for hybrid cloud, AI, consulting performance, enterprise clients, margins, and execution priorities.",
                "dimensions": ["company_says", "risk_warnings"],
            },
        ],
        "questions": [
            {
                "type": "enterprise_technology_behavioral",
                "generated_question": "Describe a time you solved an enterprise customer or platform problem where trust, integration, and measurable impact mattered.",
                "aims_dimensions": ["analytical_problem_solving", "collaboration_communication", "impact_results"],
                "strong_answer_signals": [
                    "Defines the enterprise context and stakeholder constraints.",
                    "Explains integration, trust, or reliability tradeoffs.",
                    "Shows cross-functional execution.",
                    "Measures customer, platform, or business impact.",
                ],
            }
        ],
        "role_overlays": [
            {
                "role_slug": "enterprise_ai_cloud",
                "role_family": "Enterprise AI, cloud, and consulting roles",
                "signals": [
                    "Frames technical decisions around enterprise trust, integration, client outcomes, and adoption.",
                    "Shows ability to translate complex systems into practical stakeholder decisions.",
                ],
            }
        ],
    },
    "oracle": {
        "company": "Oracle",
        "industries": ["technology", "enterprise software", "cloud", "database"],
        "regions": ["north_america", "global"],
        "stage": "large public enterprise software, database, and cloud infrastructure company",
        "sources": [
            {
                "source_type": "official_company",
                "title": "Oracle homepage",
                "url": "https://www.oracle.com/",
                "confidence": 0.8,
                "public_safe_signal": "Oracle publicly positions itself around cloud applications, database technology, infrastructure, enterprise software, data, automation, and business operations.",
                "dimensions": ["company_says", "evidence_valued"],
            },
            {
                "source_type": "official_careers",
                "title": "Oracle careers page",
                "url": "https://www.oracle.com/careers/",
                "confidence": 0.76,
                "public_safe_signal": "Careers messaging points toward enterprise technology work, customer impact, cloud, applications, engineering, sales, support, and global collaboration.",
                "dimensions": ["company_judges", "company_asks", "role_variation"],
            },
            {
                "source_type": "official_investor_relations",
                "title": "Oracle investor relations",
                "url": "https://investor.oracle.com/",
                "confidence": 0.7,
                "public_safe_signal": "Investor materials provide public context for cloud growth, database and application businesses, capital allocation, margin priorities, and market risk.",
                "dimensions": ["company_says", "risk_warnings"],
            },
        ],
        "questions": [
            {
                "type": "enterprise_software_behavioral",
                "generated_question": "Tell me about a time you improved reliability, adoption, or business value in an enterprise software or data environment.",
                "aims_dimensions": ["structured_thinking", "analytical_problem_solving", "impact_results"],
                "strong_answer_signals": [
                    "Names the enterprise user or customer need.",
                    "Explains technical or operational constraints.",
                    "Shows how adoption, reliability, or value was improved.",
                    "Uses concrete evidence rather than generic platform claims.",
                ],
            }
        ],
        "role_overlays": [
            {
                "role_slug": "enterprise_data_cloud",
                "role_family": "Enterprise data, applications, and cloud roles",
                "signals": [
                    "Links platform or data decisions to customer operations, reliability, and measurable value.",
                    "Shows practical judgment across legacy systems, integration, cost, and adoption.",
                ],
            }
        ],
    },
    "adobe": {
        "company": "Adobe",
        "industries": ["technology", "creative software", "digital experience", "ai"],
        "regions": ["north_america", "global"],
        "stage": "large public creative software, document cloud, and digital experience company",
        "sources": [
            {
                "source_type": "official_company",
                "title": "Adobe homepage",
                "url": "https://www.adobe.com/",
                "confidence": 0.76,
                "public_safe_signal": "Adobe publicly positions itself around creativity, documents, digital experience, content workflows, marketing technology, and AI-supported creative and business tools.",
                "dimensions": ["company_says", "evidence_valued"],
            },
            {
                "source_type": "official_careers",
                "title": "Adobe careers page",
                "url": "https://careers.adobe.com/",
                "confidence": 0.76,
                "public_safe_signal": "Careers messaging emphasizes creativity, customer impact, innovation, inclusion, learning, and work across product, engineering, sales, design, and operations.",
                "dimensions": ["company_judges", "company_asks", "role_variation"],
            },
            {
                "source_type": "official_investor_relations",
                "title": "Adobe investor relations",
                "url": "https://www.adobe.com/investor-relations.html",
                "confidence": 0.7,
                "public_safe_signal": "Investor materials provide public context for subscription businesses, digital media, digital experience, AI strategy, customer retention, and growth risk.",
                "dimensions": ["company_says", "risk_warnings"],
            },
        ],
        "questions": [
            {
                "type": "product_behavioral",
                "generated_question": "Describe a time you improved a creative, content, document, or customer experience workflow using evidence from users or customers.",
                "aims_dimensions": ["impact_results", "structured_thinking", "collaboration_communication"],
                "strong_answer_signals": [
                    "Defines the user or customer workflow clearly.",
                    "Explains evidence used to decide what mattered.",
                    "Shows cross-functional product or operational execution.",
                    "Measures adoption, quality, efficiency, or customer impact.",
                ],
            }
        ],
        "role_overlays": [
            {
                "role_slug": "creative_and_experience_cloud",
                "role_family": "Creative software and digital experience roles",
                "signals": [
                    "Connects product choices to creator, document, marketer, or enterprise customer workflows.",
                    "Shows evidence-based judgment around usability, trust, content, AI, or customer experience.",
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


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


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
    parser.add_argument("--allow-empty", action="store_true", help="Exit successfully when no packet is requested.")
    args = parser.parse_args()

    packets: list[dict[str, Any]] = []
    for path in args.input_packet or []:
        packets.append(normalize_packet(path))
    for slug in args.company or []:
        packets.append(build_packet(slugify(slug), accessed_date=args.date_accessed))
    if args.expansion_limit:
        packets.extend(build_packet(slug, accessed_date=args.date_accessed) for slug in choose_expansion(args.expansion_limit))

    if not packets and args.allow_empty:
        print("source_packet_status=empty")
        return 0
    if not packets:
        raise SystemExit("No packets requested. Use --company, --expansion-limit, or --input-packet.")

    for packet in packets:
        path = write_packet(packet, args.output_dir)
        print(f"source_packet={display_path(path)} company={packet['company']} sources={len(packet['sources'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
