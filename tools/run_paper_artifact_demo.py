#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research_core import EvidenceRecord, PracticeRequest, RoutingLevel, prioritize_followups


def load_request(path: Path) -> PracticeRequest:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return PracticeRequest(
        categories=raw["categories"],
        parent_distribution=raw["parent_distribution"],
        evidence=[EvidenceRecord(**item) for item in raw["evidence"]],
        permitted_categories=raw["permitted_categories"],
        kappa_company=float(raw["kappa_company"]),
        temporal_decay_rate_per_day=float(raw["temporal_decay_rate_per_day"]),
        routing_levels=[RoutingLevel(**item) for item in raw["routing_levels"]],
        routing_gamma=float(raw.get("routing_gamma", 0.8)),
        support_tau=float(raw.get("support_tau", 8.0)),
    )


def main() -> int:
    request_path = ROOT / "examples" / "paper" / "followup_priority_request.json"
    result = prioritize_followups(load_request(request_path))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
